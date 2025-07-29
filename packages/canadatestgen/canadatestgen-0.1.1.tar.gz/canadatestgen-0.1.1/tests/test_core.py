import re
from canadatestgen.core import (
    generate_name,
    generate_email,
    generate_date,
    generate_boolean,
    generate_sin,
    generate_postal_code,
    generate_province
)

def test_generate_name():
    name = generate_name()
    assert isinstance(name, str)
    assert " " in name  # Should have first and last name

def test_generate_email():
    email = generate_email()
    assert isinstance(email, str)
    assert "@" in email

def test_generate_date():
    date = generate_date()
    # Basic check for ISO date format YYYY-MM-DD
    assert re.match(r"\d{4}-\d{2}-\d{2}", date)

def test_generate_boolean():
    val = generate_boolean()
    assert val in [True, False]

def test_generate_sin():
    sin = generate_sin()
    # Check length and spacing
    assert isinstance(sin, str)
    assert len(sin) == 11
    assert sin[3] == " "
    assert sin[7] == " "
    # Check digits
    parts = sin.split(" ")
    assert all(part.isdigit() for part in parts)

def test_generate_postal_code():
    postal = generate_postal_code()
    # Canadian postal code format: LetterDigitLetter DigitLetterDigit
    pattern = r"^[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVXY] \d[ABCEGHJKLMNPRSTVXY]\d$"
    assert re.match(pattern, postal)

def test_generate_province():
    province = generate_province()
    valid_provinces = {
        "AB", "BC", "MB", "NB", "NL", "NS", "ON",
        "PE", "QC", "SK", "NT", "NU", "YT"
    }
    assert province in valid_provinces
