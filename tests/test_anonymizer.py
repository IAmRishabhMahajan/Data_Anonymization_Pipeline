import pandas as pd

from data_anonymizer.anonymizer import Anonymizer
from data_anonymizer.llm import parse_header_list


def test_anonymize_only_personal_columns_and_strip_suffix():
    df = pd.DataFrame({
        "first_name_personal": ["Aurora", "Susan"],
        "plan": ["Premium", "Basic"],
        "card_number_personal": [8776728282828939, 7674931473733445],
    })
    out = Anonymizer(seed=1).anonymize(df)

    assert list(out.columns) == ["first_name", "plan", "card_number"]
    assert out["plan"].tolist() == ["Premium", "Basic"]
    assert out["first_name"].map(len).tolist() == [6, 5]
    assert all(len(str(v)) == 16 for v in out["card_number"])


def test_empty_values_untouched():
    a = Anonymizer()
    assert a.fake_value("", "name") == ""
    assert pd.isna(a.fake_value(float("nan"), "name"))


def test_date_column():
    value = Anonymizer().fake_value("1990-05-01", "dob")
    assert len(value) == 10 and value[4] == "-"


def test_parse_header_list():
    assert parse_header_list("`a, b ,'c'`") == ["a", "b", "c"]
