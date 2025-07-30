import os
from pokeops.ingest import ingest


def test_ingest_creates_file_and_returns_count(tmp_path, monkeypatch):
    
    monkeypatch.setenv("RAW_DIR", str(tmp_path))

    file_path, record_count = ingest(count=2)

    assert file_path.startswith(str(tmp_path))

    assert record_count > 0

    assert os.path.isfile(file_path)

    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == record_count