#!/usr/bin/env python3
# pylint: disable=invalid-name

from argparse import ArgumentParser
import re
import shlex
import shutil
import subprocess


def print_cmd(args, command):
    if not args.quiet:
        print(f"$ {' '.join([shlex.quote(str(elem)) for elem in command])}",
              flush=True)


def chronic(*args, **kwargs):
    try:
        return subprocess.run(*args,
                              **kwargs,
                              capture_output=True,
                              check=True,
                              text=True)
    except subprocess.CalledProcessError as err:
        print(err.stdout)
        print(err.stderr)
        raise err


PARSER = ArgumentParser(
    description=
    'Get clang version from various Linux distributions through docker/podman)'
)
PARSER.add_argument('-m',
                    '--markdown',
                    action='store_true',
                    help='Output results as a Markdown table')
PARSER.add_argument('-q',
                    '--quiet',
                    action='store_true',
                    help='Do not print commands being run')
ARGS = PARSER.parse_args()

if ARGS.markdown:
    # pylint: disable-next=import-error
    from py_markdown_table.markdown_table import markdown_table

for MANAGER in (MANAGERS := ['podman', 'docker']):
    if shutil.which(MANAGER):
        break
else:
    raise RuntimeError(
        f"Neither {' nor '.join(MANAGERS)} could be found on your system!")

# This list should only include versions that are actively being supported.
#
# Tags such as "latest", "stable", or "rolling" are preferred so that the list
# does not have to be constantly updated. Old but supported releases like
# Fedora or OpenSUSE are the exception.
IMAGES = [
    # Arch Linux is rolling release, it only has one supported version at a time.
    ('archlinux', 'latest'),
    # Debian:
    #   * https://www.debian.org/releases/
    #   * https://wiki.debian.org/LTS
    #   * https://hub.docker.com/_/debian
    *[('debian', f"{ver}-slim") for ver in
      ['oldoldstable', 'oldstable', 'stable', 'testing', 'unstable']],
    # Fedora:
    #   * https://fedoraproject.org/wiki/Releases
    #   * https://fedoraproject.org/wiki/End_of_life
    #   * https://hub.docker.com/_/fedora
    *[('fedora', ver) for ver in ['38', 'latest', 'rawhide']],
    # OpenSUSE:
    #   * https://en.opensuse.org/openSUSE:Roadmap
    #   * https://en.opensuse.org/Lifetime
    #   * https://hub.docker.com/r/opensuse/leap
    ('opensuse/leap', 'latest'),
    ('opensuse/tumbleweed', 'latest'),
    # Ubuntu:
    #   * https://wiki.ubuntu.com/Releases
    #   * https://hub.docker.com/_/ubuntu
    *[('ubuntu', ver) for ver in ['focal', 'latest', 'rolling', 'devel']],
]

RESULTS = {}
for ITEM in IMAGES:
    DISTRO = ITEM[0]
    IMAGE = ':'.join(ITEM)
    FULL_IMAGE = f"docker.io/{IMAGE}"

    # Make sure image is up to date
    PULL_CMD = [MANAGER, 'pull', FULL_IMAGE]
    print_cmd(ARGS, PULL_CMD)
    chronic(PULL_CMD)

    # Build command to update the distribution, install clang, and get its
    # version.
    ENV_VARS = {}
    CMDS = []
    if DISTRO == 'archlinux':
        CMDS.append('pacman -Syyu --noconfirm')
        CMDS.append('pacman -S --noconfirm clang')
    elif DISTRO in ('debian', 'ubuntu'):
        ENV_VARS['DEBIAN_FRONTEND'] = 'noninteractive'

        CMDS.append('apt-get update')
        CMDS.append('apt-get upgrade -y')
        CMDS.append('apt-get install --no-install-recommends -y clang')
    elif DISTRO == 'fedora':
        CMDS.append('dnf update -y')
        CMDS.append('dnf install -y clang')
    elif 'opensuse' in DISTRO:
        CMDS.append('zypper -n up')
        CMDS.append('zypper -n in clang')
    else:
        raise RuntimeError(f"Don't know how to install clang on {DISTRO}?")
    CMDS.append('clang --version')

    # Run container manager with commands generated above.
    RUN_CMD = [
        MANAGER,
        'run',
        *[f"--env={key}={value}" for key, value in ENV_VARS.items()],
        '--rm',
        FULL_IMAGE,
        'sh',
        '-c',
        ' && '.join(CMDS),
    ]
    print_cmd(ARGS, RUN_CMD)
    RESULT = chronic(RUN_CMD)

    # Locate clang version in output and add it to results
    if not (match := re.search(
            r'^[A-Za-z ]*?clang version [0-9]+\.[0-9]+\.[0-9]+.*$',
            RESULT.stdout,
            flags=re.M)):
        raise RuntimeError('Could not find clang version in output?')
    RESULTS[IMAGE] = match[0]

print()

# Pretty print results
if ARGS.markdown:
    MD_DATA = [{
        "Container image": f"`{key}`",
        "Compiler version": f"`{value}`",
    } for key, value in RESULTS.items()]
    print(
        markdown_table(MD_DATA).set_params(padding_weight='right',
                                           quote=False,
                                           row_sep='markdown').get_markdown())
else:
    WIDTH = len(max(RESULTS.keys(), key=len))
    for IMAGE, VERSION in RESULTS.items():
        print(f"{IMAGE:{WIDTH}}    {VERSION}")
