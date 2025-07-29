import random
import string
import datetime

def generate_name():
    first = ["Alice", "Bob", "Charlie", "Diana"]
    last = ["Smith", "Johnson", "Lee", "Nguyen"]
    return f"{random.choice(first)} {random.choice(last)}"

def generate_email():
    domains = ["test.com", "mail.org", "demo.net"]
    user = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{user}@{random.choice(domains)}"

def generate_date():
    start = datetime.date(2020, 1, 1)
    end = datetime.date.today()
    delta = (end - start).days
    return str(start + datetime.timedelta(days=random.randint(0, delta)))

def generate_boolean():
    return random.choice([True, False])

def generate_sin(formatted: bool = True) -> str:
    digits = [str(random.randint(0, 9)) for _ in range(9)]
    sin = ''.join(digits)
    if formatted:
        return f"{sin[0:3]} {sin[3:6]} {sin[6:9]}"
    else:
        return sin

def generate_postal_code() -> str:
    letters = "ABCEGHJKLMNPRSTVXY"
    digits = "0123456789"
    def random_letter():
        return random.choice(letters)
    def random_digit():
        return random.choice(digits)
    return f"{random_letter()}{random_digit()}{random_letter()} {random_digit()}{random_letter()}{random_digit()}"

def generate_province() -> str:
    provinces = [
        "AB", "BC", "MB", "NB", "NL", "NS", "ON",
        "PE", "QC", "SK", "NT", "NU", "YT"
    ]
    return random.choice(provinces)

# maps schema field types to generator functions
FIELD_MAP = {
    "name": generate_name,
    "email": generate_email,
    "date": generate_date,
    "boolean": generate_boolean,
    "sin": generate_sin,
    "postal_code": generate_postal_code,
    "province": generate_province,
}
