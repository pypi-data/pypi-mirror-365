"""Command-line interface for GraFIT."""

import argparse
import sys
import logging
import json
from pathlib import Path

from .schema_generator import generate_schema
from .database import GraFITDatabase
from .fit_importer import FitImporter


def cmd_generate_schema(args):
    """Generate SQLite schema from profile.py."""
    profile_path = Path(args.profile)
    output_path = Path(args.output)

    if not profile_path.exists():
        print(f"Error: Profile file {profile_path} not found")
        sys.exit(1)

    try:
        schema = generate_schema(str(profile_path))

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(schema)

        print(f"Schema generated successfully: {output_path}")

    except Exception as e:
        print(f"Error generating schema: {e}")
        sys.exit(1)


def cmd_init_database(args):
    """Initialize database with schema."""
    db_path = Path(args.database)
    schema_path = Path(args.schema)

    if not schema_path.exists():
        print(f"Error: Schema file {schema_path} not found")
        sys.exit(1)

    try:
        db = GraFITDatabase(str(db_path))
        db.initialize_schema(str(schema_path))

        version = db.get_schema_version()
        print(f"Database initialized successfully: {db_path}")
        print(f"Schema version: {version}")

        db.close()

    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


def cmd_import(args):
    """Import FIT files - automatically detects if path is file or directory."""
    input_path = Path(args.path)
    db_path = Path(args.database)

    if not input_path.exists():
        print(f"Error: Path {input_path} not found")
        sys.exit(1)

    # Setup logging
    setup_logging(args.verbose)

    try:
        # Auto-create database if it doesn't exist
        if not db_path.exists():
            print(f"Database {db_path} not found, creating with schema...")

            # Generate schema on the fly
            profile_path = Path(__file__).parent.parent.parent / "extra" / "profile.py"
            if not profile_path.exists():
                print(f"Error: Profile file {profile_path} not found")
                sys.exit(1)

            schema = generate_schema(str(profile_path))

            # Create database and initialize with schema
            db = GraFITDatabase(str(db_path))
            db.execute_schema(schema)
            print(f"✓ Database created and initialized: {db_path}")
        else:
            db = GraFITDatabase(str(db_path))

        importer = FitImporter(db)

        if input_path.is_file():
            # Import single file
            print(f"Importing file: {input_path}")
            result = importer.import_fit_file(str(input_path), args.force)

            # Print results
            if result["status"] == "success":
                print(f"✓ Imported {input_path.name}")
                print(f"  Messages: {result['messages_imported']}")
                print(f"  Tables: {', '.join(result['tables_affected'])}")
            elif result["status"] == "skipped":
                print(f"⏭ Skipped {input_path.name} (already imported)")
            else:
                print(
                    f"✗ Failed to import {input_path.name}: {result.get('error', 'Unknown error')}"
                )
                sys.exit(1)

        elif input_path.is_dir():
            # Import directory
            print(f"Importing directory: {input_path}")
            result = importer.import_directory(
                str(input_path), args.pattern, args.force, args.recursive
            )

            # Print results
            print(f"Import complete:")
            print(f"  Files processed: {result['files_processed']}")
            print(f"  Files imported: {result['files_imported']}")
            print(f"  Files skipped: {result['files_skipped']}")
            print(f"  Files failed: {result['files_failed']}")
            print(f"  Total messages: {result['total_messages']}")

            if result["failed_files"]:
                print("\\nFailed files:")
                for failure in result["failed_files"]:
                    print(f"  ✗ {failure['file']}: {failure['error']}")

            if result["tables_affected"]:
                print(f"\\nTables updated: {', '.join(sorted(result['tables_affected']))}")
        else:
            print(f"Error: {input_path} is neither a file nor a directory")
            sys.exit(1)

        db.close()

    except Exception as e:
        print(f"Error importing: {e}")
        sys.exit(1)


def cmd_database_stats(args):
    """Show database statistics."""
    db_path = Path(args.database)

    if not db_path.exists():
        print(f"Error: Database {db_path} not found")
        sys.exit(1)

    try:
        db = GraFITDatabase(str(db_path))

        version = db.get_schema_version()
        stats = db.get_import_stats()

        print(f"Database: {db_path}")
        print(f"Schema version: {version}")
        print(f"Tables: {len(stats)}")

        total_records = sum(stats.values())
        print(f"Total records: {total_records:,}")

        if args.detailed:
            print("\\nTable breakdown:")
            for table, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"  {table}: {count:,}")

        db.close()

    except Exception as e:
        print(f"Error reading database stats: {e}")
        sys.exit(1)


def setup_logging(verbose: bool):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="grafit", description="Import Garmin FIT files into SQLite database"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Schema generation command
    schema_parser = subparsers.add_parser(
        "generate-schema", help="Generate SQLite schema from FIT profile"
    )
    schema_parser.add_argument("profile", help="Path to profile.py file")
    schema_parser.add_argument("output", help="Output SQL file path")
    schema_parser.set_defaults(func=cmd_generate_schema)

    # Database initialization command
    init_parser = subparsers.add_parser("init-database", help="Initialize database with schema")
    init_parser.add_argument("database", help="Path to SQLite database file")
    init_parser.add_argument("schema", help="Path to schema SQL file")
    init_parser.set_defaults(func=cmd_init_database)

    # Import command (handles both files and directories)
    import_parser = subparsers.add_parser(
        "import", help="Import FIT file(s) - automatically detects file or directory"
    )
    import_parser.add_argument("path", help="Path to FIT file or directory containing FIT files")
    import_parser.add_argument(
        "database",
        nargs="?",
        default="fit_data.db",
        help="Path to SQLite database file (default: fit_data.db)",
    )
    import_parser.add_argument(
        "--pattern", default="*.fit", help="File pattern to match for directories (default: *.fit)"
    )
    import_parser.add_argument(
        "--force", action="store_true", help="Force reimport even if files already exist"
    )
    import_parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Don't search subdirectories when importing directories",
    )
    import_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    import_parser.set_defaults(func=cmd_import)

    # Database stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.add_argument("database", help="Path to SQLite database file")
    stats_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed table breakdown"
    )
    stats_parser.set_defaults(func=cmd_database_stats)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute the command
    args.func(args)


if __name__ == "__main__":
    main()
