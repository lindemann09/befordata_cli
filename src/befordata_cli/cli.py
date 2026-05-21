import argparse
from os.path import isfile

from befordata import xdf

from . import __version__
from .xdf import load_xdf, xdf_info


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
        "-o", "--output",
        metavar="dest",
        help="Output file",
    )
    parser.add_argument(
        "-i", "--info",
        action="store_true",
        default=False,
        help="Print detailed stream info",
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

    args = parser.parse_args()

    if len(args.FILE) < 2:
        print("No data FILE specified.")
        parser.print_help()
        exit()


    if not isfile(args.FILE):
        print(f"File {args.FILE} does not exist.")

    elif args.FILE.endswith(".xdf"):
        xdf_info(args.FILE, info_dict=args.info)

        if args.arrow or args.csv:
            streams, header = load_xdf(args.FILE)
            rec = xdf.before_record(streams, args.force_stream, 1000)

            if args.arrow:
                print(f"Converting to Arrow")

            if args.csv:
                print(f"Converting to CSV")


if __name__ == "__main__":
    run()