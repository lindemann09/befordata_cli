import argparse
from os.path import isfile

from . import __version__
from .xdf import convert_data, xdf_info


def run() -> None:

    parser = argparse.ArgumentParser(
        prog="befordata_cli",
        description="Command-line tool for befordata",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument("FILE", default="", help="data file")

    parser.add_argument(
        "-i", "--info",
        action="store_true",
        default=False,
        help="Print detailed XDF stream info",
    )

    parser.add_argument(
        "--arrow",
        action="store_true",
        default=False,
        help="Convert file to Arrow format (.arrow)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        default=False,
        help="Convert file to CSV format (.csv)",
    )
    parser.add_argument(
        "-s", "--streams",
        nargs="+",
        metavar="stream",
        help="XDF stream(s) to process (stream names or stream ids)",
    )

    args = parser.parse_args()

    if len(args.FILE) < 2:
        print("No data FILE specified.")
        parser.print_help()
        exit()

    if not isfile(args.FILE):
        print(f"File {args.FILE} does not exist.")

    elif args.FILE.endswith(".xdf"):
        xdf_info(args.FILE, info_dict=args.info, streams=args.streams)

        if args.arrow or args.csv:
            convert_data(args.FILE, streams=args.streams, arrow=args.arrow, csv=args.csv)


if __name__ == "__main__":
    run()