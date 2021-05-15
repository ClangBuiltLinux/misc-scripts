#!/usr/bin/env bash

trap 'exit' INT

# Make sure we have the required binaries
for NAME in podman docker; do
    command -v "${NAME}" &>/dev/null && BINARY=${NAME}
done
if [[ -z ${BINARY} ]]; then
    echo "Neither podman nor docker could be found on your system! Please install one to use this script."
    exit 1
fi

DOCKER_DISTROS=(
    archlinux/archlinux
    debian:oldstable-slim
    debian:stable-slim
    debian:testing-slim
    debian:unstable-slim
    fedora
    fedora:rawhide
    opensuse/leap
    opensuse/tumbleweed
    ubuntu:18.04
    ubuntu:20.04
    ubuntu
    ubuntu:rolling
    ubuntu:devel
)

BASE=$(dirname "$(readlink -f "${0}")")
RUN_SCRIPT=${BASE}/run.sh

cat <<'EOF' >"${RUN_SCRIPT}"
#!/usr/bin/env bash

RESULTS=$(dirname "$(readlink -f "${0}")")/results.log

set -x

# Debian/Ubuntu
if command -v apt-get &>/dev/null; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y clang
# Fedora
elif command -v dnf &>/dev/null; then
    dnf update -y
    dnf install -y clang
# Arch
elif command -v pacman &>/dev/null; then
    pacman -Syyu --noconfirm
    pacman -S --noconfirm clang
# OpenSUSE Leap/Tumbleweed
elif command -v zypper &>/dev/null; then
    zypper -n up
    zypper -n in clang
fi

echo "${1}: $(clang --version | head -n1)" >> "${RESULTS}"
EOF
chmod +x "${RUN_SCRIPT}"

rm "${BASE}"/results.log
for DISTRO in "${DOCKER_DISTROS[@]}"; do
    DISTRO=docker.io/${DISTRO}
    "${BINARY}" pull "${DISTRO}"
    "${BINARY}" run \
        --rm \
        --init \
        --volume="${BASE}:${BASE}" \
        --workdir="${BASE}" \
        "${DISTRO}" \
        "${BASE}"/run.sh "${DISTRO}"
done

echo
cat "${BASE}"/results.log
