"""Anonymize personal data in CSV files, inferring column headers when missing."""

from data_anonymizer.pipeline import anonymize_file

__all__ = ["anonymize_file"]
__version__ = "1.0.0"
