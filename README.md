# Data Anonymization

This tool makes CSV files safe to share. An LLM (Azure OpenAI) finds the columns that hold personal data: names, phone numbers, addresses, dates of birth, card numbers and so on. Their values are then replaced with realistic fake values of the same shape.

Raw exports often arrive without a header row, which makes them hard to classify. For those files the tool first infers the column names, then anonymizes.

```
Aurora,Bravo,88588,Wanda Mission,...,8776728282828939          first_name,last_name,customer_id,street_address,...,credit_card_number
Ana,María,69,Laura Gateway,...,7656848484848484        ──▶     Jessica,Ramos,69,"512 Diaz Mills, ...",...,4417203958810274
```

## How it works

```
CSV ──▶ detect encoding / delimiter / header row
            │
            ├─ no header row? ──▶ LLM suggests one name per column (retries until counts match)
            ▼
        LLM tags personal-data columns with a `_personal` suffix
            │
            ▼
        Faker replaces tagged values (names, phones, addresses, dates, numbers),
        keeping each value's type and length; other columns stay untouched
            │
            ▼
        <input>_anonymized.csv
```

| Module | Responsibility |
| --- | --- |
| [`anonymizer.py`](data_anonymizer/anonymizer.py) | Type-aware fake data generation that preserves value shape/length |
| [`llm.py`](data_anonymizer/llm.py) | Azure OpenAI prompts for PII tagging and header suggestion |
| [`csv_io.py`](data_anonymizer/csv_io.py) | Encoding detection (UTF-8 → chardet fallback), delimiter sniffing, header-row heuristic, loading |
| [`pipeline.py`](data_anonymizer/pipeline.py) | Orchestrates the steps above |
| [`cli.py`](data_anonymizer/cli.py) | Command-line interface |
| [`config.py`](data_anonymizer/config.py) | Reads credentials from environment / `.env` |

## Setup

```bash
git clone https://github.com/iamrishabhmahajan/Data-Anonymization.git
cd Data-Anonymization
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

cp .env.example .env    # then fill in your Azure OpenAI endpoint, key, version and deployment
```

## Usage

```bash
# Anonymize (headers are inferred automatically if the file has none)
data-anonymizer examples/sample_no_headers.csv

# Custom output path, verbose logging
data-anonymizer examples/sample_no_headers.csv -o shareable.csv -v

# Only infer headers, leave the data as-is
data-anonymizer examples/sample_no_headers.csv --headers-only

# Or without installing
python -m data_anonymizer examples/sample_no_headers.csv
```

From Python:

```python
from data_anonymizer import anonymize_file

anonymize_file("raw_export.csv", "shareable.csv")
```

## Tests

The tests mock the LLM, so you don't need any credentials to run them.

```bash
pytest
```

## Notes

- Only a few sample rows are sent to the LLM, to classify the columns. All anonymization runs locally, so the full dataset never leaves your machine.
- Non-personal columns (quantities, plans, categories, etc.) are left unchanged, so the anonymized file is still useful for analysis.
- Fake strings are trimmed or padded to the length of the original, so fixed-width consumers keep working.
- A header row is detected with a heuristic: if every value in the first row is purely alphabetic and the second row isn't, the first row is treated as headers.
