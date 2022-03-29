"""CLI entrypoint for manx."""

# Standard library imports
import argparse
import sys

# Local library imports
from manx import corpus, parsing


def main():
    """Manx - Early Middle English lemmatizer based on ELAEME."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    subparsers = parser.add_subparsers(
        dest="command", help="These are manx subcommands"
    )
    download = subparsers.add_parser(
        "download", description="manx-download - Download ELAEME corpus files"
    )
    download.add_argument(
        "-r", "--root", help="root directory for corpus files", required=True
    )
    download.add_argument("-v", "--verbose", action="store_true")
    parse = subparsers.add_parser(
        "parse", description="manx-parse Parse ELAEME corpus files"
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
    parse.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    match args.command:
        case "download":
            downloader = corpus.Downloader()
            files = downloader.download(args.verbose)
            root = corpus.Dir(args.root, files=[])
            root / corpus.Dir(
                "dicts",
                files=[f for f in files if f.type == corpus.FileType.Dict],
            )
            root / corpus.Dir(
                "texts",
                files=[f for f in files if f.type == corpus.FileType.Text],
            )
            corpus.traverse(root)
        case "parse":
            if args.from_web:
                downloader = corpus.Downloader()
                files = downloader.download(args.verbose)
                texts = [
                    f.as_io() for f in files if f.type == corpus.FileType.Dict
                ]
                p = parsing.DictParser()
                parsed = [list(p.parse(t)) for t in texts]
            else:
                print("parsing file from file system")
                parser.exit(0)


if __name__ == "__main__":
    main()
