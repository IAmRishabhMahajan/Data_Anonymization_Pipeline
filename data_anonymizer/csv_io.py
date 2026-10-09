"""Reading CSV files of unknown encoding, delimiter and header presence."""

import logging
from pathlib import Path

import chardet
import pandas as pd

log = logging.getLogger(__name__)

CANDIDATE_DELIMITERS = [",", "\t", "|", ";"]


def detect_encoding(path: Path, sample_size: int = 10_000) -> str:
    """Return the file's encoding, falling back to chardet when UTF-8 fails."""
    raw = path.read_bytes()[:sample_size]
    try:
        raw.decode("utf-8")
        return "utf-8-sig"  # handles an optional BOM transparently
    except UnicodeDecodeError:
        encoding = chardet.detect(raw)["encoding"] or "latin-1"
        log.info("Detected non-UTF-8 encoding: %s", encoding)
        return encoding


def read_first_lines(path: Path, encoding: str, n: int = 2) -> list[str]:
    with path.open("r", encoding=encoding, errors="replace") as f:
        return [f.readline().rstrip("\r\n") for _ in range(n)]


def detect_delimiter(first_line: str) -> str:
    """Pick the candidate delimiter that occurs most often in the first line."""
    counts = {d: first_line.count(d) for d in CANDIDATE_DELIMITERS}
    delimiter = max(counts, key=counts.get)
    return delimiter if counts[delimiter] else ","


def _is_label(value: str) -> bool:
    return value.replace("_", "").replace(" ", "").isalpha()


def has_header(first_line: str, second_line: str, delimiter: str) -> bool:
    """Heuristic: a header row is all alphabetic labels, while the next row is not."""
    first = [v.strip() for v in first_line.split(delimiter) if v.strip()]
    second = [v.strip() for v in second_line.split(delimiter) if v.strip()]
    return bool(first) and all(map(_is_label, first)) and not all(map(_is_label, second))


def load_csv(path: Path) -> tuple[pd.DataFrame, bool]:
    """Load a CSV and report whether it already had a header row.

    Data is always read with ``header=None`` so the first row is never
    silently consumed as column names for header-less files.
    """
    encoding = detect_encoding(path)
    first, second = read_first_lines(path, encoding)
    delimiter = detect_delimiter(first)
    header = has_header(first, second, delimiter)
    log.info("Delimiter=%r, has header=%s", delimiter, header)

    df = pd.read_csv(path, sep=delimiter, header=0 if header else None, encoding=encoding)
    return df, header
