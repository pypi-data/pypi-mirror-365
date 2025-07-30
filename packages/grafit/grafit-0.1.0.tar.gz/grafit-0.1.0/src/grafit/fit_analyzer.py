"""Analyze FIT files to understand field structures and mismatches."""

import sys
from collections import defaultdict, Counter
from pathlib import Path
import fitparse


def analyze_fit_file(fit_file_path: str) -> dict:
    """Analyze a FIT file to understand its structure."""

    analysis = {
        "messages": defaultdict(
            lambda: {"count": 0, "fields": set(), "subfields": set(), "sample_data": None}
        ),
        "total_messages": 0,
        "message_counts": Counter(),
        "field_types": defaultdict(set),
        "unknown_messages": set(),
    }

    print(f"Analyzing FIT file: {fit_file_path}")

    with fitparse.FitFile(fit_file_path) as fit_file:
        for message in fit_file.get_messages():
            analysis["total_messages"] += 1

            # Get message name
            if hasattr(message, "name") and message.name:
                msg_name = message.name
            else:
                msg_name = f"unknown_{getattr(message, 'mesg_num', 'unknown')}"
                analysis["unknown_messages"].add(msg_name)

            analysis["message_counts"][msg_name] += 1
            msg_info = analysis["messages"][msg_name]
            msg_info["count"] += 1

            # Store first sample for inspection
            if msg_info["sample_data"] is None:
                msg_info["sample_data"] = {}

            # Analyze fields
            for field in message.fields:
                if field.name and field.value is not None:
                    field_name = field.name.lower()
                    msg_info["fields"].add(field_name)
                    analysis["field_types"][field_name].add(type(field.value).__name__)

                    # Store sample data for first few records
                    if len(msg_info["sample_data"]) < 5:
                        msg_info["sample_data"][field_name] = field.value

            # Check for subfields - these are conditional fields
            for field in message.fields:
                if hasattr(field, "subfields") and field.subfields:
                    for subfield in field.subfields:
                        if subfield.name:
                            subfield_name = f"{field.name}_{subfield.name}".lower()
                            msg_info["subfields"].add(subfield_name)

    return analysis


def compare_with_schema(analysis: dict, schema_file: str):
    """Compare analysis results with generated schema."""
    print(f"\n=== FIELD MAPPING ANALYSIS ===")

    # Read schema to get table structure
    schema_tables = {}
    with open(schema_file, "r") as f:
        content = f.read()

    # Parse table definitions (simplified)
    import re

    table_pattern = r'CREATE TABLE IF NOT EXISTS (\w+|"[^"]+") \((.*?)\);'
    matches = re.findall(table_pattern, content, re.DOTALL)

    for table_name, columns_text in matches:
        table_name = table_name.strip('"')
        # Extract column names (simplified parsing)
        columns = set()
        for line in columns_text.split("\n"):
            line = line.strip()
            if (
                line
                and not line.startswith("id ")
                and not line.startswith("file_hash")
                and not line.startswith("timestamp")
                and not line.startswith("local_timestamp")
            ):
                # Extract column name
                parts = line.split()
                if parts:
                    col_name = parts[0].rstrip(",")
                    if col_name not in ["id", "file_hash", "timestamp", "local_timestamp"]:
                        columns.add(col_name)
        schema_tables[table_name] = columns

    print(f"Found {len(schema_tables)} tables in schema")

    # Compare critical message types
    critical_messages = ["record", "session", "lap", "activity", "file_id", "device_info"]

    for msg_name in critical_messages:
        if msg_name in analysis["messages"]:
            print(f"\n--- {msg_name.upper()} MESSAGE ---")

            actual_fields = analysis["messages"][msg_name]["fields"]
            schema_fields = schema_tables.get(msg_name, set())

            missing_in_schema = actual_fields - schema_fields
            missing_in_data = schema_fields - actual_fields

            print(f"Fields in FIT file: {len(actual_fields)}")
            print(f"Fields in schema: {len(schema_fields)}")
            print(f"Sample count: {analysis['messages'][msg_name]['count']}")

            if missing_in_schema:
                print(f"Missing in schema: {sorted(missing_in_schema)}")

            if missing_in_data:
                print(f"Missing in FIT data: {sorted(missing_in_data)}")

            # Show sample data
            sample = analysis["messages"][msg_name]["sample_data"]
            if sample:
                print("Sample fields:")
                for field, value in list(sample.items())[:10]:
                    print(f"  {field}: {value} ({type(value).__name__})")


def main():
    """CLI entry point for FIT analysis."""
    if len(sys.argv) != 3:
        print("Usage: python fit_analyzer.py <fit_file> <schema_file>")
        sys.exit(1)

    fit_file = sys.argv[1]
    schema_file = sys.argv[2]

    if not Path(fit_file).exists():
        print(f"FIT file not found: {fit_file}")
        sys.exit(1)

    if not Path(schema_file).exists():
        print(f"Schema file not found: {schema_file}")
        sys.exit(1)

    # Analyze FIT file
    analysis = analyze_fit_file(fit_file)

    # Show summary
    print(f"\n=== ANALYSIS SUMMARY ===")
    print(f"Total messages: {analysis['total_messages']}")
    print(f"Message types: {len(analysis['messages'])}")
    print(f"Unknown messages: {analysis['unknown_messages']}")

    print(f"\nTop message types:")
    for msg_name, count in analysis["message_counts"].most_common(10):
        print(f"  {msg_name}: {count}")

    # Compare with schema
    compare_with_schema(analysis, schema_file)


if __name__ == "__main__":
    main()
