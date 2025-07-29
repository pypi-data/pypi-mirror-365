import argparse
import json
import csv
from .schema_loader import generate_data

def main():
    parser = argparse.ArgumentParser(description="CanadaTestGen CLI")
    parser.add_argument("--schema", required=True, help="Path to schema JSON file")
    parser.add_argument("--count", type=int, default=10, help="Number of rows to generate")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("--output", help="Output file (optional)")

    args = parser.parse_args()
    data = generate_data(args.schema, args.count)

    if args.output:
        with open(args.output, "w", newline="") as f:
            if args.format == "json":
                json.dump(data, f, indent=2)
            else:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    else:
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
