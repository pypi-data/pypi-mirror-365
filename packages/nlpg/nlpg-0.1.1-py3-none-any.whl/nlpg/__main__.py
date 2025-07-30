import argparse
import logging

from . import __version__
from . import get_password


def main() -> None:
    logging_level_map = {
        1: 50,
        2: 40,
        3: 30,
        4: 20,
        5: 10,
    }

    parser = argparse.ArgumentParser(prog="nlpg")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "-l",
        "--length",
        help="The Number of Adjective & noun pairs wanted. (Default: 3)",
        type=int,
        default=3,
    )
    parser.add_argument(
        "-c",
        "--count",
        help="The number of password wanted. (Default: 1)",
        type=int,
        default=1,
    )
    log_out = parser.add_mutually_exclusive_group()
    log_out.add_argument(
        "--verbose",
        type=int,
        default=0,
        choices=range(6),
        metavar="[0-5]",
        help="Set the logging level. 0=Off, 1=Critical, 2=Error, 3=Warning, 4=Info, 5=Debug",
    )
    log_out.add_argument(
        "-s",
        "--silence",
        help="Enable script/silence mode. Only prints the password",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    if args.verbose:
        level = logging_level_map.get(args.verbose, logging.NOTSET)
        logging.basicConfig(level=level)

    indent = "" if args.silence else "   "
    p_end = "" if args.silence is True else "\n"

    if not args.silence:
        print("Your Password(s) is:\n", end="", flush=True)
    for _ in range(args.count):
        print(f"{indent}{get_password(args.length)}", end=p_end)

if __name__ == "__main__":
    main()