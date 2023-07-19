#!/usr/bin/env python
# -------------------------------------
# ClangBuiltLinux/misc-scripts/reduce
# Author: Justin Stitt <justinstitt@google.com
# As Part Of: ClangBuiltLinux and Google LLC
# License: Apache v2.0 -- see ./LICENSE
# -------------------------------------

import argparse
from collections.abc import Callable
import sys

from src import flags, prep


VERSION = "0.2.1"

ENTRY_POINTS: dict[str, Callable] = {"prep": prep.main, "flags": flags.main}


def parse_cli_args() -> argparse.Namespace:
    """
    Parse out CLI args for top-level script `reduce` other scripts have their
    own CLI arg parsing
    """
    parser = argparse.ArgumentParser(
        prog="reduce",
        description=f"reduce v{VERSION}",
        usage="python3 reduce.py [prep | flags | -h]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(required=True)

    flags_parser = subparsers.add_parser(
        "flags",
        description="A script to minimize the CC flags required to reproduce "
        "behavior. Use after $ python reduce prep",
    )
    flags.FlagReducer.setup_argparser(flags_parser)
    flags_parser.set_defaults(func=flags.main)

    prep_parser = subparsers.add_parser(
        "prep",
        prog="prepreduce",
        description=f"A script to setup testing files (target.i and test.sh) "
        "for use in reduction via (cvise, llvm-reduce, reduce flags)",
        epilog="Example Usage: $ python3 prepreduce.py -p ~/path/to/linux -Ff "
        "-o test2 -- make -j8 LLVM=1 V=1 lib/string",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    prep.setup_argparser(prep_parser)

    prep_parser.set_defaults(func=prep.main)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_cli_args()
    args.func(args)
