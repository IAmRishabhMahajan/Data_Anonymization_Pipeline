"""LLM calls: suggest column headers and flag columns containing personal data."""

import logging
from functools import lru_cache

import pandas as pd

from data_anonymizer.config import AzureOpenAIConfig

log = logging.getLogger(__name__)

PERSONAL_SUFFIX = "_personal"


@lru_cache(maxsize=1)
def _client_and_deployment():
    from openai import AzureOpenAI

    cfg = AzureOpenAIConfig.from_env()
    client = AzureOpenAI(
        azure_endpoint=cfg.endpoint, api_key=cfg.api_key, api_version=cfg.api_version
    )
    return client, cfg.deployment


def _complete(system: str, prompt: str, temperature: float) -> str:
    client, deployment = _client_and_deployment()
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def parse_header_list(text: str) -> list[str]:
    """Turn the model's comma-separated reply into a clean list of names."""
    return [h.strip().strip("`'\"") for h in text.strip().strip("`").split(",")]


def suggest_headers(df: pd.DataFrame, sample_rows: int = 10) -> list[str]:
    sample = df.head(sample_rows).to_string(index=False, header=False)
    prompt = (
        "Based on the following data sample, suggest appropriate headers for the columns. "
        f"There are exactly {df.shape[1]} columns, so return exactly {df.shape[1]} headers. "
        "Headers should be specific and informative, not generic. "
        "Reply only in the format: header1,header2,...,headerN with no other text.\n"
        f"Data sample:\n{sample}"
    )
    return parse_header_list(
        _complete("Generate concise, clear headers for datasets.", prompt, temperature=0.2)
    )


def flag_personal_columns(headers: list[str], df: pd.DataFrame, sample_rows: int = 5) -> list[str]:
    """Return ``headers`` with ``_personal`` appended to columns holding PII."""
    sample = df.head(sample_rows).to_string(index=False, header=False)
    prompt = (
        f"Append '{PERSONAL_SUFFIX}' to any column names that relate to personal data "
        "(e.g. human names, social security numbers, phone numbers, dates of birth, "
        "addresses, credit card numbers). Return the same number of column names "
        f"({len(headers)}) as a comma-separated list with no other text.\n"
        f"Column names: {','.join(headers)}\n"
        f"Data sample (first {sample_rows} rows):\n{sample}"
    )
    return parse_header_list(
        _complete("Identify personal information columns.", prompt, temperature=0.1)
    )
