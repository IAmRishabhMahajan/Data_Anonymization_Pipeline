from data_anonymizer.csv_io import detect_delimiter, has_header, load_csv


def test_detect_delimiter():
    assert detect_delimiter("a,b,c") == ","
    assert detect_delimiter("a|b|c") == "|"
    assert detect_delimiter("a\tb\tc") == "\t"
    assert detect_delimiter("single") == ","


def test_has_header():
    assert has_header("first_name,last_name,age", "Ana,Maria,57", ",")
    assert not has_header("Ana,Maria,57", "Susan,Lambert,73", ",")


def test_headerless_file_keeps_first_row(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("Ana,Maria,57\nSusan,Lambert,73\n", encoding="utf-8")
    df, had_header = load_csv(f)
    assert not had_header
    assert len(df) == 2
    assert df.iloc[0, 0] == "Ana"


def test_file_with_header_and_pipe_delimiter(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("name|age\nAna|57\n", encoding="utf-8")
    df, had_header = load_csv(f)
    assert had_header
    assert list(df.columns) == ["name", "age"]


def test_latin1_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_bytes("José,Müller,30\nAna,Peña,40\n".encode("latin-1"))
    df, _ = load_csv(f)
    assert len(df) == 2
