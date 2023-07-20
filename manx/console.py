"""CLI entrypoint for manx."""

# Standard library imports
from __future__ import annotations
import argparse
import sys

# Local library imports
from manx import download, Format, load, write, writing, api
from manx.config import settings


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
        default=settings.DEFAULT_NGRAM_SIZE,
    )
    parse.add_argument(
        "--chunk-size",
        help="the size of document chunk for T5 CSV",
        default=settings.DEFAULT_CHUNK_SIZE,
    )
    parse.add_argument(
        "-f",
        "--format",
        help="corpus output format",
        choices=[f.value for f in list(writing.Format)],
        default=writing.Format.StripText.value,
    )
    parse.add_argument(
        "-p",
        "--t5prefix",
        help="T5 model family finetuning prefix",
        default=settings.T5_PREFIX,
        dest="prefix",
    )
    parse.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default="-",
        help="all-round output file",
    )

    api = subparsers.add_parser(
        "api",
        help="run lemmatization API",
        description="Manx-API - Run lemmatization API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    api.add_argument(
        "-H",
        "--host",
        help="server host",
        default=settings.API_HOST,
    )
    api.add_argument(
        "-p",
        "--port",
        help="server port",
        default=settings.API_PORT,
        type=int,
    )

    result = parser.parse_args()
    return result


def main():
    """Manx - Early Middle English lemmatization pipeline based on LAEME."""
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
                output=args.output,
                fmt=fmt,
                verbose=args.verbose,
                ngram_size=args.ngram_size,
                t5prefix=args.prefix,
            )
        case "api":
            api.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
