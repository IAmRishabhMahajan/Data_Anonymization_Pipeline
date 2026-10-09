import argparse
import logging
import sys
from pathlib import Path

from data_anonymizer.pipeline import HeaderGenerationError, anonymize_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="data-anonymizer",
        description="Anonymize personal data in a CSV file (adds column headers first if the file has none).",
    )
    parser.add_argument("input", type=Path, help="CSV file to process")
    parser.add_argument("-o", "--output", type=Path, help="output path (default: <input>_anonymized.csv)")
    parser.add_argument("--headers-only", action="store_true", help="only add headers, keep data as-is")
    parser.add_argument("--retries", type=int, default=5, help="LLM retries for header generation")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(levelname)s %(message)s")

    if not args.input.is_file() or args.input.suffix.lower() != ".csv":
        parser.error(f"{args.input} is not an existing .csv file")

    try:
        out = anonymize_file(args.input, args.output, not args.headers_only, args.retries)
    except (HeaderGenerationError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"Saved: {out}")
    return 0
