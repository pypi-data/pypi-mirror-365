"""Generate SQLite schema from FIT profile definitions."""

import sys
from pathlib import Path
from typing import Dict, List, Set
import importlib.util


def load_profile_module(profile_path: str):
    """Load the profile.py module dynamically."""
    spec = importlib.util.spec_from_file_location("profile", profile_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load profile from {profile_path}")

    profile = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profile)
    return profile


def get_sqlite_type(field_type) -> str:
    """Convert FIT field type to SQLite type."""
    base_type = getattr(field_type, "base_type", field_type)

    if hasattr(base_type, "type_num"):
        type_num = base_type.type_num

        # Map FIT base types to SQLite types
        type_mapping = {
            0x00: "STRING",  # enum
            0x01: "INTEGER",  # sint8
            0x02: "INTEGER",  # uint8
            0x83: "INTEGER",  # sint16
            0x84: "INTEGER",  # uint16
            0x85: "INTEGER",  # sint32
            0x86: "INTEGER",  # uint32
            0x8C: "INTEGER",  # uint32z
            0x88: "REAL",  # float32
            0x89: "REAL",  # float64
            0x07: "TEXT",  # string
            0x0D: "BLOB",  # byte
        }

        return type_mapping.get(type_num, "TEXT")

    return "TEXT"


def generate_table_schema(message_name: str, message_type, profile) -> str:
    """Generate CREATE TABLE statement for a message type."""
    table_name = message_name.lower()

    # Handle SQL reserved words by quoting table names
    if table_name in ["set", "user", "group", "order", "select", "table"]:
        table_name = f'"{table_name}"'

    # Start with common fields - use leading _ to avoid conflicts with FIT fields (except id)
    columns = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "_file_hash TEXT NOT NULL",  # For deduplication
        "_file_id TEXT",  # Human-readable identifier: dirname_filename_startdate
        "timestamp DATETIME",  # FIT timestamp if available
        "_local_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP",  # When imported
    ]

    # Add message-specific fields
    for field_num, field in message_type.fields.items():
        field_name = field.name.lower()

        # Skip timestamp field as we handle it specially
        if field_name == "timestamp":
            continue

        # Skip fields that would conflict with our standard columns
        if field_name in ["id", "_file_hash", "_file_id", "_local_timestamp"]:
            field_name = f"fit_{field_name}"

        sqlite_type = get_sqlite_type(field.type)

        # Note: Not adding comments for now to avoid SQL syntax issues
        # TODO: Add proper column comments in future schema versions
        columns.append(f"    {field_name} {sqlite_type}")

    # Add subfields if they exist
    for field_num, field in message_type.fields.items():
        if hasattr(field, "subfields") and field.subfields:
            for subfield in field.subfields:
                # Add both naming conventions for subfields
                direct_name = subfield.name.lower()
                combined_name = f"{field.name}_{subfield.name}".lower()

                sqlite_type = get_sqlite_type(subfield.type)

                # Add direct subfield name (e.g., garmin_product)
                if direct_name not in [
                    "id",
                    "_file_hash",
                    "_file_id",
                    "_local_timestamp",
                    "timestamp",
                ]:
                    columns.append(f"    {direct_name} {sqlite_type}")

                # Add combined name for compatibility (e.g., product_garmin_product)
                if combined_name not in [
                    "id",
                    "_file_hash",
                    "_file_id",
                    "_local_timestamp",
                    "timestamp",
                ]:
                    if combined_name != direct_name:  # Avoid duplicates
                        columns.append(f"    {combined_name} {sqlite_type}")

    columns_str = ",\n".join(columns)
    create_statement = f"""CREATE TABLE IF NOT EXISTS {table_name} (
{columns_str}
);"""

    # Add indexes for common query patterns
    indexes = []

    # Get table name for indexes (remove quotes if present)
    index_table_name = table_name.strip('"')

    # Index on _file_hash for deduplication
    indexes.append(
        f"CREATE INDEX IF NOT EXISTS idx_{index_table_name}_file_hash ON {table_name}(_file_hash);"
    )

    # Index on timestamp if the table has it
    if "timestamp" in [field.name.lower() for field in message_type.fields.values()]:
        indexes.append(
            f"CREATE INDEX IF NOT EXISTS idx_{index_table_name}_timestamp ON {table_name}(timestamp);"
        )

    return create_statement + "\n\n" + "\n".join(indexes)


def generate_schema(profile_path: str) -> str:
    """Generate complete SQLite schema from profile.py."""
    profile = load_profile_module(profile_path)

    schema_parts = [
        "-- SQLite schema generated from FIT profile",
        "-- This file is auto-generated. Do not edit manually.",
        "",
        "PRAGMA foreign_keys = ON;",
        "PRAGMA journal_mode = WAL;",
        "",
    ]

    # Generate tables for each message type
    for mesg_num, message_type in profile.MESSAGE_TYPES.items():
        message_name = message_type.name

        # Skip certain system messages that we might not want to store
        skip_messages = {"pad", "software"}
        if message_name in skip_messages:
            continue

        table_schema = generate_table_schema(message_name, message_type, profile)
        schema_parts.append(f"-- {message_name.upper()} MESSAGE (#{mesg_num})")
        schema_parts.append(table_schema)
        schema_parts.append("")

    # Add metadata table for tracking schema version and migrations
    metadata_table = """-- METADATA TABLE for schema versioning
CREATE TABLE IF NOT EXISTS _grafit_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial schema version
INSERT OR IGNORE INTO _grafit_metadata (key, value) VALUES ('schema_version', '1.0.0');
INSERT OR IGNORE INTO _grafit_metadata (key, value) VALUES ('generated_from_sdk', '21.141');"""

    schema_parts.append(metadata_table)

    return "\n".join(schema_parts)


def main():
    """CLI entry point for schema generation."""
    if len(sys.argv) != 3:
        print("Usage: python schema_generator.py <profile.py> <output.sql>")
        sys.exit(1)

    profile_path = sys.argv[1]
    output_path = sys.argv[2]

    if not Path(profile_path).exists():
        print(f"Error: Profile file {profile_path} not found")
        sys.exit(1)

    try:
        schema = generate_schema(profile_path)

        with open(output_path, "w") as f:
            f.write(schema)

        print(f"Schema generated successfully: {output_path}")

    except Exception as e:
        print(f"Error generating schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
