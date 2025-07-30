"""FIT file parsing and import functionality."""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Generator
from datetime import datetime
import fitparse

from .database import GraFITDatabase, calculate_file_hash

logger = logging.getLogger(__name__)


class FitImporter:
    """Handles importing FIT files into the GraFIT database."""

    def __init__(self, database: GraFITDatabase):
        """Initialize the FIT importer."""
        self.db = database

    def import_fit_file(self, fit_file_path: str, force_reimport: bool = False) -> Dict[str, Any]:
        """
        Import a single FIT file into the database.

        Args:
            fit_file_path: Path to the FIT file
            force_reimport: If True, import even if file already exists

        Returns:
            Dictionary with import statistics and status
        """
        fit_path = Path(fit_file_path)
        if not fit_path.exists():
            raise FileNotFoundError(f"FIT file not found: {fit_file_path}")

        # Calculate file hash for deduplication
        file_hash = calculate_file_hash(str(fit_path))

        # Check if already imported
        if not force_reimport and self.db.is_file_imported(file_hash):
            logger.info(f"File already imported, skipping: {fit_path.name}")
            return {
                "status": "skipped",
                "reason": "already_imported",
                "file": str(fit_path),
                "file_hash": file_hash,
                "messages_imported": 0,
                "tables_affected": [],
            }

        logger.info(f"Importing FIT file: {fit_path.name}")

        try:
            # Parse FIT file
            with fitparse.FitFile(str(fit_path)) as fit_file:
                # Generate file_id
                file_id = self._generate_file_id(fit_path, fit_file)
                import_stats = self._import_fit_messages(fit_file, file_hash, file_id)

            import_stats.update(
                {
                    "status": "success",
                    "file": str(fit_path),
                    "file_hash": file_hash,
                    "file_id": file_id,
                }
            )

            logger.info(
                f"Successfully imported {fit_path.name}: {import_stats['messages_imported']} messages"
            )
            return import_stats

        except Exception as e:
            logger.error(f"Failed to import {fit_path.name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "file": str(fit_path),
                "file_hash": file_hash,
                "messages_imported": 0,
                "tables_affected": [],
            }

    def _generate_file_id(self, fit_path: Path, fit_file) -> str:
        """Generate a human-readable file ID: dirname_filename_startdate."""
        try:
            # Get directory name (Activity, Location, etc.)
            dir_name = fit_path.parent.name

            # Get filename without extension
            file_name = fit_path.stem

            # Try to find start date from the FIT file
            start_date = None
            try:
                # Look for session or activity messages that might have a timestamp
                for message in fit_file.get_messages(["session", "activity", "file_id"]):
                    if hasattr(message, "start_time") and message.start_time:
                        start_date = message.start_time.strftime("%Y%m%d")
                        break
                    elif hasattr(message, "timestamp") and message.timestamp:
                        start_date = message.timestamp.strftime("%Y%m%d")
                        break

                # If no date found in messages, try to extract from filename if it looks like a date
                if not start_date:
                    # Common Garmin filename patterns include dates
                    date_match = re.search(r"(\d{4}-\d{2}-\d{2}|\d{8})", file_name)
                    if date_match:
                        date_str = date_match.group(1).replace("-", "")
                        if len(date_str) == 8:
                            start_date = date_str

            except Exception as e:
                logger.debug(f"Could not extract start date from {fit_path.name}: {e}")

            # Build file_id
            if start_date:
                file_id = f"{dir_name}_{file_name}_{start_date}"
            else:
                file_id = f"{dir_name}_{file_name}"

            # Clean up the file_id (remove invalid characters)
            file_id = re.sub(r"[^\w\-_]", "_", file_id)

            return file_id

        except Exception as e:
            logger.warning(f"Failed to generate file_id for {fit_path.name}: {e}")
            # Fallback to simple naming
            return f"{fit_path.parent.name}_{fit_path.stem}"

    def _import_fit_messages(self, fit_file, file_hash: str, file_id: str) -> Dict[str, Any]:
        """Import all messages from a parsed FIT file."""
        messages_imported = 0
        tables_affected = set()
        message_batches = {}  # Group messages by type for bulk insert

        # Process all messages
        for message in fit_file.get_messages():
            # Skip invalid messages
            if not hasattr(message, "name") or not message.name:
                continue

            table_name = message.name.lower()

            try:
                # Extract message data
                message_data = self._extract_message_data(message)

                if message_data:
                    # Group messages for bulk insert (except certain types that should be inserted immediately)
                    if self._should_bulk_insert(table_name):
                        if table_name not in message_batches:
                            message_batches[table_name] = []
                        message_batches[table_name].append(message_data)
                    else:
                        # Insert immediately for important messages
                        self.db.insert_message_data(table_name, message_data, file_hash, file_id)

                    messages_imported += 1
                    tables_affected.add(table_name)

            except Exception as e:
                logger.warning(f"Failed to process {table_name} message: {e}")
                continue

        # Bulk insert batched messages
        for table_name, data_list in message_batches.items():
            try:
                self.db.bulk_insert_message_data(table_name, data_list, file_hash, file_id)
                logger.debug(f"Bulk inserted {len(data_list)} records into {table_name}")
            except Exception as e:
                logger.error(f"Failed to bulk insert into {table_name}: {e}")
                # Try individual inserts as fallback
                for data in data_list:
                    try:
                        self.db.insert_message_data(table_name, data, file_hash, file_id)
                    except Exception as e2:
                        logger.warning(f"Failed individual insert to {table_name}: {e2}")

        return {"messages_imported": messages_imported, "tables_affected": list(tables_affected)}

    def _extract_message_data(self, message) -> Dict[str, Any]:
        """Extract data from a FIT message."""
        data = {}

        # Extract all fields
        for field in message.fields:
            if field.value is None:
                continue

            field_name = field.name.lower()

            # Convert field value to appropriate Python type
            value = self._convert_field_value(field)
            if value is not None:
                data[field_name] = value

        # Handle subfields - these are conditional fields that provide
        # manufacturer-specific or context-specific data
        for field in message.fields:
            if hasattr(field, "subfields") and field.subfields:
                for subfield in field.subfields:
                    if subfield.value is not None:
                        # Try both naming conventions:
                        # 1. Direct subfield name (garmin_product)
                        # 2. Combined name (product_garmin_product)
                        subfield_name = subfield.name.lower()
                        combined_name = f"{field.name}_{subfield.name}".lower()

                        subfield_value = self._convert_field_value(subfield)
                        if subfield_value is not None:
                            # Store under direct name primarily
                            data[subfield_name] = subfield_value
                            # Also store under combined name for compatibility
                            data[combined_name] = subfield_value

        return data

    def _convert_field_value(self, field) -> Any:
        """Convert FIT field value to appropriate Python type for SQLite."""
        value = field.value

        if value is None:
            return None

        if field.name == "timestamp":
            return int(field.value.timestamp())

        # Handle different value types
        if isinstance(value, (int, float, str)):
            return value
        elif isinstance(value, bytes):
            return value  # Store as BLOB
        elif isinstance(value, datetime):
            return int(value.timestamp())
        elif hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
            # Convert lists/tuples to comma-separated strings
            try:
                return ",".join(str(v) for v in value)
            except:
                return str(value)
        else:
            # Convert other types to string
            return str(value)

    def _should_bulk_insert(self, table_name: str) -> bool:
        """Determine if messages should be bulk inserted or inserted immediately."""
        # Insert immediately for important/small tables
        immediate_tables = {
            "file_id",
            "activity",
            "session",
            "lap",
            "device_info",
            "user_profile",
            "hrv",
            "sleep_assessment",
        }

        # Bulk insert for high-volume data
        return table_name not in immediate_tables

    def import_directory(
        self,
        directory_path: str,
        pattern: str = "*.fit",
        force_reimport: bool = False,
        recursive: bool = True,
    ) -> Dict[str, Any]:
        """
        Import all FIT files from a directory.

        Args:
            directory_path: Path to directory containing FIT files
            pattern: File pattern to match (default: "*.fit")
            force_reimport: If True, reimport existing files
            recursive: If True, search subdirectories

        Returns:
            Dictionary with overall import statistics
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        # Find all FIT files
        if recursive:
            fit_files = list(dir_path.rglob(pattern))
        else:
            fit_files = list(dir_path.glob(pattern))

        if not fit_files:
            logger.warning(f"No FIT files found in {directory_path}")
            return {
                "status": "success",
                "files_processed": 0,
                "files_imported": 0,
                "files_skipped": 0,
                "files_failed": 0,
                "total_messages": 0,
                "tables_affected": [],
            }

        logger.info(f"Found {len(fit_files)} FIT files to process")

        # Track overall statistics
        total_stats = {
            "status": "success",
            "files_processed": 0,
            "files_imported": 0,
            "files_skipped": 0,
            "files_failed": 0,
            "total_messages": 0,
            "tables_affected": set(),
            "failed_files": [],
        }

        # Process each file
        for fit_file in fit_files:
            try:
                result = self.import_fit_file(str(fit_file), force_reimport)
                total_stats["files_processed"] += 1

                if result["status"] == "success":
                    total_stats["files_imported"] += 1
                    total_stats["total_messages"] += result["messages_imported"]
                    total_stats["tables_affected"].update(result["tables_affected"])
                elif result["status"] == "skipped":
                    total_stats["files_skipped"] += 1
                else:
                    total_stats["files_failed"] += 1
                    total_stats["failed_files"].append(
                        {"file": str(fit_file), "error": result.get("error", "Unknown error")}
                    )

            except Exception as e:
                logger.error(f"Unexpected error processing {fit_file}: {e}")
                total_stats["files_processed"] += 1
                total_stats["files_failed"] += 1
                total_stats["failed_files"].append({"file": str(fit_file), "error": str(e)})

        # Convert set to list for JSON serialization
        total_stats["tables_affected"] = list(total_stats["tables_affected"])

        logger.info(
            f"Directory import complete: {total_stats['files_imported']} imported, "
            f"{total_stats['files_skipped']} skipped, {total_stats['files_failed']} failed"
        )

        return total_stats
