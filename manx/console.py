"""CLI entrypoint for manx."""

# Standard library imports
from __future__ import annotations
import argparse
import multiprocessing
from pathlib import Path
import sys

# Local library imports
from manx import download, embedding, Format, load, write, writing


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
        "-m",
        "--model",
        help="fastText model file path",
        required=False,
    )
    parse.add_argument(
        "-f",
        "--format",
        help="corpus output format",
        choices=[f.value for f in list(writing.Format)],
        default=writing.Format.StripText.value,
    )
    parse.add_argument(
        "-o", "--output", type=argparse.FileType("w"), default="-"
    )
    ft = subparsers.add_parser(
        "fasttext",
        help="train fastText model on LAEME data",
        description="manx-fasttext - Train fastText LAEME model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[verbose_parser],
    )
    ft.add_argument(
        "-i",
        "--input",
        help="training file path",
        required=True,
    )
    ft.add_argument(
        "--model",
        choices=["skipgram", "cbow"],
        default="skipgram",
        help="unsupervised fastText model",
    )
    ft.add_argument("--lrate", type=float, default=0.05, help="learning rate")
    ft.add_argument(
        "--dim",
        type=int,
        default=100,
        help="size of word vectors",
    )
    ft.add_argument(
        "--ws",
        type=int,
        default=5,
        help="size of the context window",
    )
    ft.add_argument("--epoch", type=int, default=5, help="number of epochs")
    ft.add_argument(
        "--min-count",
        type=int,
        default=5,
        help="minimal number of word occurences",
    )
    ft.add_argument(
        "--minn",
        type=int,
        default=3,
        help="min length of char ngram",
    )
    ft.add_argument(
        "--maxn",
        type=int,
        default=6,
        help="max length of char ngram",
    )
    ft.add_argument(
        "--neg",
        type=int,
        default=5,
        help="number of negatives sampled",
    )
    ft.add_argument(
        "--word-ngrams",
        type=int,
        default=1,
        help="max length of word ngram",
    )
    ft.add_argument(
        "--loss",
        choices=["ns", "hs", "softmax", "ova"],
        default="ns",
        help="loss function",
    )
    ft.add_argument(
        "--bucket",
        type=int,
        default=2_000_000,
        help="number of buckets",
    )
    ft.add_argument(
        "--thread",
        type=int,
        default=multiprocessing.cpu_count() - 1,
        help="number of threads",
    )
    ft.add_argument(
        "--lrate-update-rate",
        type=int,
        default=100,
        help="change the rate of updates for the learning rate",
    )
    ft.add_argument(
        "--sample-thresh",
        type=int,
        default=1e-4,
        help="sampling threshold",
    )
    ft.add_argument(
        "-o",
        "--output",
        help="output file path",
        default="laeme.bin",
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
                model_path=args.model,
                from_web=args.from_web,
                verbose=args.verbose,
                root=args.root,
            )
            fmt = Format(args.format)
            write(
                fp=args.output,
                docs=laeme,
                fmt=fmt,
                verbose=args.verbose,
                ngram_size=args.ngram_size,
            )

        case "fasttext":
            params = embedding.Parameters(
                input=args.input,
                model=args.model,
                lr=args.lrate,
                dim=args.dim,
                ws=args.ws,
                epoch=args.epoch,
                minCount=args.min_count,
                minn=args.minn,
                maxn=args.maxn,
                neg=args.neg,
                wordNgrams=args.word_ngrams,
                loss=args.loss,
                bucket=args.bucket,
                thread=args.thread,
                lrUpdateRate=args.lrate_update_rate,
                t=args.sample_thresh,
                verbose=2 if args.verbose else 0,
            )

            if Path(args.output).exists():
                print(
                    f"{args.output} exists!\n"
                    "Do you want to overwrite it? [yN]\n",
                    file=sys.stderr,
                )
                match input().lower():
                    case "y" | "yes":
                        pass
                    case _:
                        return

            model = embedding.train(params)
            model.save(args.output)


if __name__ == "__main__":
    main()
