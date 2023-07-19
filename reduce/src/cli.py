import argparse
from pathlib import Path
from .types import Command


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    MAGENTA = "\u001b[35m"


# ]]]]]]]]]] this comment is necessary because my lsp thinks all those unclosed
# square brackets from the escape codes are not in a string and thus my
# auto-indent is broken (hence, why I closed them all in a comment) (vim is weird.)


def error(msg: str) -> None:
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")
    exit(1)


def warn(msg: str, ret_only: bool = False) -> str:
    msg = f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}"
    if ret_only:
        return msg
    print(msg)
    return msg


def success(msg: str) -> None:
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")


def info(msg: str) -> None:
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")


def todo(msg: str) -> None:
    print(f"{Colors.MAGENTA + Colors.BOLD}[TODO]{Colors.ENDC} {msg}")


def validate_path_from_cli(
    _path: str, argument: str, allow_mkdir: bool = False
) -> Path:
    """
    Allow argparse to actually validate -p/--path-to-linux argument and
    provide helpful feedback
    """
    try:
        posix_path = Path(_path.strip())
    except:
        raise argparse.ArgumentTypeError(
            f"Invalid {argument} argument provided: {_path} doesn't parse "
            "into a PosixPath"
        )

    if not posix_path.is_dir():
        if not allow_mkdir:
            raise argparse.ArgumentTypeError(
                f"Invalid {argument} argument provided: {_path} is not a "
                "directory or it doesn't exist"
            )
        info(f"Making directory for prepreduce's output files: {posix_path}")
        posix_path.mkdir()

    return posix_path


def validate_target_from_cli(_target: str) -> Path:
    """
    Allow argparse to actually validate the target argument as well as convert
    to PosixPath
    """
    posix_path = Path(_target)
    if posix_path.suffix != ".i" and len(posix_path.suffix):
        error(
            f"target file has {posix_path.suffix} extension instead of `.i`. "
            "Either have no suffix or add `.i` -- quitting now."
        )

    return posix_path.with_suffix(".i")


def validate_build_cmd_from_cli(build_cmd: Command) -> None:
    """
    We need V=1 to find original compiler invocation
    """
    if "V=1" not in build_cmd:
        raise RuntimeError("Need V=1 in your make build command")

    if any([".i" in str(part) for part in build_cmd]):  # cast is *necessary*
        raise RuntimeError("Don't include the target .i file in your build command")
