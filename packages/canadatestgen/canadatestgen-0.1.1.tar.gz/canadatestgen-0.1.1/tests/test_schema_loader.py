import json
import os
import tempfile
import pytest
from canadatestgen.schema_loader import generate_row, generate_data

# A simple schema dictionary for testing
sample_schema = {
    "full_name": "name",
    "email_address": "email",
    "signup_date": "date",
    "is_active": "boolean"
}

def test_generate_row_returns_correct_keys():
    row = generate_row(sample_schema)
    assert set(row.keys()) == set(sample_schema.keys())
    # Check value types for known fields
    assert isinstance(row["full_name"], str)
    assert "@" in row["email_address"]
    assert isinstance(row["signup_date"], str)
    assert row["is_active"] in [True, False]

def test_generate_data_creates_multiple_rows(tmp_path):
    # Write the schema to a temporary file
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(sample_schema))

    data = generate_data(str(schema_file), count=5)
    assert isinstance(data, list)
    assert len(data) == 5

    # Each item should be a dict with the schema keys
    for row in data:
        assert isinstance(row, dict)
        assert set(row.keys()) == set(sample_schema.keys())

def test_generate_data_raises_on_unknown_field(tmp_path):
    bad_schema = {
        "field1": "unknown_type"
    }
    schema_file = tmp_path / "bad_schema.json"
    schema_file.write_text(json.dumps(bad_schema))

    with pytest.raises(ValueError, match="Unknown field type"):
        generate_data(str(schema_file), count=1)
