import sys
import json
import tempfile
import pytest
from unittest import mock
from canadatestgen.cli import main

# Sample schema for testing
sample_schema = {
    "full_name": "name",
    "email_address": "email",
    "signup_date": "date",
    "is_active": "boolean"
}

def write_temp_schema(tmp_path, schema_data):
    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text(json.dumps(schema_data))
    return str(schema_file)

def read_output_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

@mock.patch("sys.argv", new=["canadatestgen"])
def test_cli_no_args_prints_error(capsys):
    with pytest.raises(SystemExit):
        main()
    out, err = capsys.readouterr()
    assert "error" in err.lower() or "required" in err.lower()

def test_cli_generates_output(tmp_path):
    schema_path = write_temp_schema(tmp_path, sample_schema)
    output_path = tmp_path / "output.json"

    test_args = [
        "canadatestgen",
        "--schema", str(schema_path),
        "--output", str(output_path),
        "--count", "3"
    ]

    with mock.patch.object(sys, "argv", test_args):
        main()

    assert output_path.exists()
    output_data = read_output_file(output_path)
    assert isinstance(output_data, list)
    assert len(output_data) == 3
    for item in output_data:
        assert set(item.keys()) == set(sample_schema.keys())
