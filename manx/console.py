"""CLI entrypoint for manx."""

# Standard library imports
from __future__ import annotations
import argparse
import sys

# Local library imports
from manx import download, Format, load, write, writing


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=main.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(title="actions", dest="command")

    verbose_parser = argparse.ArgumentParser(add_help=False)
    verbose_parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose output"
    )

    dl = subparsers.add_parser(
        "download",
        help="download LAEME corpus files",
        description="Manx-download - Download LAEME corpus files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[verbose_parser],
    )
    dl.add_argument(
        "-r", "--root", help="root directory for corpus files", required=True
    )
    parse = subparsers.add_parser(
        "parse",
        help="parse LAEME corpus files",
        description="manx-parse - Parse LAEME corpus files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[verbose_parser],
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
        "--ngram-size",
        help="the size of ngram line for T5 CSV",
        default=writing.DEFAULT_NGRAM_SIZE,
    )
    parse.add_argument(
        "--chunk-size",
        help="the size of document chunk for T5 CSV",
        default=writing.DEFAULT_CHUNK_SIZE,
    )
    parse.add_argument(
        "-f",
        "--format",
        help="corpus output format",
        choices=[f.value for f in list(writing.Format)],
        default=writing.Format.StripText.value,
    )
    parse.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default="-",
        help="all-round output file",
    )
    parse.add_argument(
        "--train",
        type=argparse.FileType("w"),
        required="t5" in sys.argv,
        help="train output file",
    )
    parse.add_argument(
        "--valid",
        type=argparse.FileType("w"),
        required="t5" in sys.argv,
        help="validation output file",
    )
    parse.add_argument(
        "--test",
        type=argparse.FileType("w"),
        required="t5" in sys.argv,
        help="test output file",
    )
    result = parser.parse_args()
    return result


def main():
    """Manx - Early Middle English lemmatizer based on LAEME."""
    args = get_args()
    match args.command:
        case "download":
            download(args.root, args.verbose)

        case "parse":
            laeme = load(
                from_web=args.from_web,
                verbose=args.verbose,
                root=args.root,
            )
            fmt = Format(args.format)
            write(
                docs=laeme,
                fmt=fmt,
                verbose=args.verbose,
                ngram_size=args.ngram_size,
                output=args.output,
                train=args.train,
                valid=args.valid,
                test=args.test,
            )


if __name__ == "__main__":
    main()
