import argparse
from os import chdir
from pathlib import Path
import re
import shutil
import subprocess
import sys


try:
    from .cli import error, info, success, validate_path_from_cli
except ImportError:
    """
    This is necessary to safeguard the user from running this script directly
    which will generate errors due to relative importing rules in Python
    """
    print(
        f"You should not run {__file__} as a standalone script.\n"
        f"Use `$ python3 reduce.py {Path(__file__).stem}` instead!",
        file=sys.stderr,
    )
    sys.exit(1)


class FlagReducer:
    ABSOLUTE_FLAG_PATTERN = r"\$\(.*\)"
    DOT_I_PATTERN = r"\w+\.i"
    PREMADE_TEST_PATTERN = r"<your test here>"

    def __init__(self, cli_args: argparse.Namespace):
        self.cli_args = cli_args
        self.flags_txt: Path = self.cli_args.path_to_flags / Path("flags.txt")
        self.test_sh: Path = self.cli_args.path_to_flags / Path("test.sh")
        self.flags_sh: Path = self.cli_args.path_to_flags / Path("flags.sh")

    @classmethod
    def setup_argparser(cls, parser: argparse.ArgumentParser) -> None:
        """
        Subparser setup utilized by ../reduce.py
        This is a classmethod since there will not be an instance of FlagReducer
        during argument parsing time.
        """
        cls.argparser = parser
        parser.add_argument(
            "-p",
            "--path-to-flags",
            help="Path to flags.txt",
            default="./",
            type=lambda arg: validate_path_from_cli(arg, "-p/--path-to-flags"),
        )

    def ensure_file_exists(self, file: Path) -> None:
        """
        Make sure `file` exists, otherwise write descriptive error
        """
        if not file.exists():
            error(
                f"Couldn't find {file.name} be sure to run `prep` first or "
                "specify a directory containing flags.txt, test.sh, and target.i with -p\n"
                "Example: python reduce.py flags -p /path/to/flags.txt"
            )
        success(f"Found {file.name}")

    def ensure_flags_txt_exists(self) -> None:
        self.ensure_file_exists(file=self.flags_txt)

    def ensure_test_sh_exists(self) -> None:
        self.ensure_file_exists(file=self.test_sh)

    def check_interestingness_written(self, file: Path) -> bool:
        """
        Determine if the user has written an interestingness test or not in `file`
        """
        file_raw = file.read_text()
        matches = re.findall(FlagReducer.PREMADE_TEST_PATTERN, file_raw)
        return len(matches) == 0  # True if can't find premade test

    def write_flags_script(self) -> None:
        """
        Copy test.sh to flags.sh and overwrite relative/absolute pathing to support
        cvise semantics.

        test.sh wants an absolute flags.txt and a relative target.i
        flags.sh wants a relative flags.txt and an absolute target.i
        """
        has_interestingness_test = self.check_interestingness_written(self.test_sh)
        if not has_interestingness_test:
            error(
                f"Please write an interestingness test in {self.test_sh} "
                "before attempting flag reduction"
            )
        info("Creating flags.sh based on interestingness test from test.sh")
        shutil.copy2(self.test_sh, self.flags_sh)
        success("Copied test.sh to flags.sh")
        info("Modifying absolute and relative pathing to support flag reduction")

        test_sh_raw = self.test_sh.read_text()
        flags_sh_text = test_sh_raw

        flags_sh_text = re.sub(
            FlagReducer.ABSOLUTE_FLAG_PATTERN,
            f"$(cat flags.txt)",
            flags_sh_text,
        )

        matches = re.findall(FlagReducer.DOT_I_PATTERN, flags_sh_text)

        absolute_target_path = (
            self.cli_args.path_to_flags / Path(matches[0])
        ).absolute()

        flags_sh_text = re.sub(
            FlagReducer.DOT_I_PATTERN, str(absolute_target_path), flags_sh_text
        )
        self.flags_sh.write_text(flags_sh_text)
        success("Wrote flags.sh")

    def run_flag_reduction_with_cvise(self) -> None:
        """
        Use cvise to reduce flags using flags.sh and flags.txt
        """
        info("Using cvise to reduce flags")
        chdir(self.cli_args.path_to_flags)
        command = ["cvise", self.flags_sh.name, self.flags_txt.name]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        if result.returncode != 0:
            error(
                "cvise failed. Make sure you have it installed https://github.com/marxin/cvise"
            )

        if "hard-coded" in result.stdout.decode("utf-8"):
            error("interestingness test does not return 0 for first run-through")

        success("flags.txt has been reduced")
        info(
            f"There's a copy of your original flags at {self.flags_txt.with_suffix(self.flags_txt.suffix + '.orig')}"
        )
        info("Now deleting flags.sh")
        self.flags_sh.unlink()


def main(args):
    flag_reducer = FlagReducer(cli_args=args)
    flag_reducer.ensure_flags_txt_exists()
    flag_reducer.ensure_test_sh_exists()
    flag_reducer.write_flags_script()
    flag_reducer.run_flag_reduction_with_cvise()


if __name__ == "__main__":
    sys.exit(1)
