import json
from .core import FIELD_MAP

def generate_row(schema: dict) -> dict:
    row = {}
    for field, field_type in schema.items():
        generator = FIELD_MAP.get(field_type)
        if not generator:
            raise ValueError(f"Unknown field type: {field_type}")
        row[field] = generator()
    return row

def generate_data(schema_file: str, count: int = 10) -> list:
    with open(schema_file, "r") as f:
        schema = json.load(f)

    return [generate_row(schema) for _ in range(count)]
