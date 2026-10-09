"""Replace values in personal-data columns with realistic fake values."""

import re
from datetime import datetime

import pandas as pd
from faker import Faker

from data_anonymizer.llm import PERSONAL_SUFFIX

PHONE_RE = re.compile(r"^\+?\d{7,15}$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Anonymizer:
    def __init__(self, seed: int | None = None):
        self.fake = Faker()
        if seed is not None:
            Faker.seed(seed)

    def fake_value(self, value, column: str):
        """Return a fake value shaped like ``value``, guided by the column name."""
        if value is None or (not isinstance(value, str) and pd.isna(value)) or value == "":
            return value

        name = column.lower()

        if any(k in name for k in ("phone", "mobile")) or PHONE_RE.match(str(value)):
            return self.fake.phone_number()

        if "address" in name:
            return self.fake.address().replace("\n", ", ")

        if any(k in name for k in ("dob", "birth", "date")) or (
            isinstance(value, str) and ISO_DATE_RE.match(value)
        ):
            try:
                datetime.strptime(str(value), "%Y-%m-%d")
            except ValueError:
                return value
            return self.fake.date_of_birth(minimum_age=18, maximum_age=100).isoformat()

        if isinstance(value, (int, float)):
            digits = len(str(abs(int(value))))
            return self.fake.random_number(digits=digits, fix_len=True)

        if isinstance(value, str):
            # Keep the original length so fixed-width consumers aren't broken.
            return self.fake.name()[: len(value)].ljust(len(value))

        return value

    def anonymize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fake every column whose name ends with ``_personal`` and drop the suffix."""
        out = df.copy()
        renames = {}
        for column in out.columns:
            if column.lower().endswith(PERSONAL_SUFFIX):
                out[column] = out[column].map(lambda v, c=column: self.fake_value(v, c))
                renames[column] = column[: -len(PERSONAL_SUFFIX)]
        return out.rename(columns=renames)
