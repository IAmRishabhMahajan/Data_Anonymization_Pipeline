import pandas as pd

from data_anonymizer import llm, pipeline


def test_anonymize_file_with_mocked_llm(tmp_path, monkeypatch):
    src = tmp_path / "people.csv"
    src.write_text("Ana,Maria,57\nSusan,Lambert,73\n", encoding="utf-8")

    replies = iter([["first_name", "last_name"], ["first_name", "last_name", "age"]])
    monkeypatch.setattr(llm, "suggest_headers", lambda df: next(replies))
    monkeypatch.setattr(llm, "flag_personal_columns",
                        lambda h, df: ["first_name_personal", "last_name_personal", "age"])

    out = pipeline.anonymize_file(src)
    df = pd.read_csv(out)

    assert list(df.columns) == ["first_name", "last_name", "age"]
    assert df["age"].tolist() == [57, 73]
    assert df["first_name"].tolist() != ["Ana", "Susan"]

    # Re-running overwrites rather than appending.
    replies = iter([["first_name", "last_name", "age"]])
    pipeline.anonymize_file(src)
    assert len(pd.read_csv(out)) == 2


def test_file_with_headers_skips_header_generation(tmp_path, monkeypatch):
    src = tmp_path / "people.csv"
    src.write_text("first_name,plan\nAna,Basic\nSusan,Premium\n", encoding="utf-8")

    def fail(df):
        raise AssertionError("headers should not be generated for a file that has them")

    monkeypatch.setattr(llm, "suggest_headers", fail)
    monkeypatch.setattr(llm, "flag_personal_columns", lambda h, df: ["first_name_personal", "plan"])

    df = pd.read_csv(pipeline.anonymize_file(src))

    assert list(df.columns) == ["first_name", "plan"]
    assert df["plan"].tolist() == ["Basic", "Premium"]
    assert df["first_name"].tolist() != ["Ana", "Susan"]
