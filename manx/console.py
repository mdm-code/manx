"""CLI entrypoint for manx."""

# Standard library imports
import argparse

# Local library imports
from manx import corpus


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


if __name__ == "__main__":
    main()
