# CanadaTestGen

**CanadaTestGen** is a Python CLI tool and library to generate realistic Canadian-themed test data based on customizable JSON schemas. It supports generating data such as names, email addresses, SIN numbers, postal codes, provinces, and more — outputting results in JSON or CSV format.

---

## Features

- Generate realistic Canadian test data quickly and easily
- Supports JSON and CSV output formats
- Customizable schema for flexible data generation
- Command-line interface (CLI) for easy use
- Can be used as a Python library for integration in your projects

---

## Installation

You can install CanadaTestGen via pip:

```bash
pip install canadatestgen
```

Or clone this repo and install locally:

```bash
git clone https://github.com/GuiNom16/canadatestgen.git
cd canadatestgen
pip install -e .
```

---

## Usage

### CLI

```bash
canadatestgen --schema path/to/schema.json --count 10 --format json --output output.json
```

#### Arguments

| Option     | Description                                              | Default | Example       |
| ---------- | -------------------------------------------------------- | ------- | ------------- |
| `--schema` | Path to the JSON schema file (required)                  | N/A     | `schema.json` |
| `--count`  | Number of records to generate                            | 10      | 50            |
| `--format` | Output format: json or csv                               | json    | csv           |
| `--output` | Output file path (optional; prints to stdout if omitted) | N/A     | `data.csv`    |

### Schema Example

The schema defines fields and their types. Example `schema.json`:

```json
{
  "full_name": "name",
  "email_address": "email",
  "sin_number": "sin",
  "postal_code": "postal_code",
  "province": "province",
  "signup_date": "date",
  "is_active": "boolean"
}
```

### Python Usage

You can also use CanadaTestGen as a Python library:

```python
from canadatestgen.schema_loader import generate_data

data = generate_data("schema.json", count=5)
print(data)
```

---

## Running Tests

To run unit tests:

```bash
pytest
```

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Author

**Jeremie Nombro**  
Email: guillaumenombro@gmail.com  
Location: Fredericton, New Brunswick, Canada

---

## Contributions

Contributions, issues, and feature requests are welcome!
