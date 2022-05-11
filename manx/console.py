"""CLI entrypoint for manx."""

# Standard library imports
import argparse
import sys

# Local library imports
from manx import download, Format, load, write


def main():
    """Manx - Early Middle English lemmatizer based on LAEME."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose output"
    )
    subparsers = parser.add_subparsers(dest="command", help="manx subcommands")
    dl = subparsers.add_parser(
        "download",
        help="download LAEME corpus files",
        description="Manx-download - Download LAEME corpus files",
    )
    dl.add_argument(
        "-r", "--root", help="root directory for corpus files", required=True
    )
    parse = subparsers.add_parser(
        "parse",
        help="parse LAEME corpus files",
        description="manx-parse - Parse LAEME corpus files",
    )
    parse.add_argument(
        "--from-web",
        help="parse files directly from the web",
        action="store_true",
    )
    parse.add_argument(
        "-r",
        "--root",
        help="root directory for corpus files",
        required=(False if "--from-web" in sys.argv[1:] else True),
    )
    parse.add_argument(
        "-o", "--output", type=argparse.FileType("w"), default="-"
    )
    args = parser.parse_args()

    match args.command:
        case "download":
            download(args.root, args.verbose)
        case "parse":
            laeme = load(
                from_web=args.from_web, verbose=args.verbose, root=args.root
            )
            write(fp=args.output, docs=laeme, fmt=Format.StripText)


if __name__ == "__main__":
    main()
