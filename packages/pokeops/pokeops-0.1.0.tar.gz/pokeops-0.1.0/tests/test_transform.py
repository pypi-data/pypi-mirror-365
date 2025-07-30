import json
from pokeops.transform import read_raw_json  # replace with actual import path

def test_read_raw_json_normal(tmp_path):
    # Arrange: create a JSON file in the temporary directory
    data = {"pokemon": ["pikachu", "bulbasaur"]}
    file_path = tmp_path / "data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    # Act: call function with the path
    result = read_raw_json(str(file_path))

    # Assert: the returned data matches what was written
    assert result == data


def test_read_raw_json_file_not_found(capfd):
    invalid_path = "/does/not/exist.json"

    # Act
    result = read_raw_json(invalid_path)

    assert result is None

    # Assert: the function printed the appropriate message
    captured = capfd.readouterr()
    assert f"File not found : {invalid_path}" in captured.out
