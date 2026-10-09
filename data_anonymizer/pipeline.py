"""Anonymization flow: load -> name columns (if missing) -> flag PII -> fake it -> save."""

import logging
from pathlib import Path

from data_anonymizer import llm
from data_anonymizer.anonymizer import Anonymizer
from data_anonymizer.csv_io import load_csv

log = logging.getLogger(__name__)


class HeaderGenerationError(RuntimeError):
    pass


def generate_headers(df, max_retries: int = 5) -> list[str]:
    """Ask the LLM for headers until it returns one per column."""
    for attempt in range(1, max_retries + 1):
        headers = llm.suggest_headers(df)
        if len(headers) == df.shape[1]:
            return headers
        log.warning(
            "Attempt %d: got %d headers for %d columns, retrying",
            attempt, len(headers), df.shape[1],
        )
    raise HeaderGenerationError(f"No valid headers after {max_retries} attempts")


def anonymize_file(input_path: str | Path, output_path: str | Path | None = None,
                 anonymize: bool = True, max_retries: int = 5) -> Path:
    input_path = Path(input_path)
    output_path = Path(output_path or input_path.with_name(f"{input_path.stem}_anonymized.csv"))

    df, had_header = load_csv(input_path)
    headers = [str(c) for c in df.columns] if had_header else generate_headers(df, max_retries)

    if anonymize:
        flagged = llm.flag_personal_columns(headers, df)
        if len(flagged) != len(headers):
            raise HeaderGenerationError("PII tagging changed the number of columns")
        df.columns = flagged
        df = Anonymizer().anonymize(df)
    else:
        df.columns = headers

    df.to_csv(output_path, index=False)  # overwrite, never append
    log.info("Saved %s", output_path)
    return output_path
