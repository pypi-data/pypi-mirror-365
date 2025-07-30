"""Database connection and initialization for GraFIT."""

import sqlite3
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class GraFITDatabase:
    """Manages SQLite database connections and operations for GraFIT."""

    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure SQLite connection
        self.connection = sqlite3.connect(
            str(self.db_path), isolation_level=None  # Autocommit mode
        )
        self.connection.row_factory = sqlite3.Row  # Access columns by name

        # Enable WAL mode and other optimizations
        self._configure_database()

    def _configure_database(self):
        """Configure SQLite database settings."""
        cursor = self.connection.cursor()

        # Enable optimizations
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store = MEMORY")

        cursor.close()

    def initialize_schema(self, schema_file: str):
        """Initialize database schema from SQL file."""
        schema_path = Path(schema_file)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")

        with open(schema_path, "r") as f:
            schema_sql = f.read()

        self.execute_schema(schema_sql)
        logger.info(f"Database schema initialized from {schema_file}")

    def execute_schema(self, schema_sql: str):
        """Execute schema SQL directly."""
        cursor = self.connection.cursor()
        try:
            cursor.executescript(schema_sql)
            logger.info("Database schema executed successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to execute schema: {e}")
            raise
        finally:
            cursor.close()

    def is_file_imported(self, file_hash: str) -> bool:
        """Check if a file has already been imported."""
        cursor = self.connection.cursor()
        try:
            # Check any table for this _file_hash
            cursor.execute(
                """
                SELECT 1 FROM file_id WHERE _file_hash = ? LIMIT 1
            """,
                (file_hash,),
            )
            return cursor.fetchone() is not None
        except sqlite3.Error:
            # If file_id table doesn't exist, file hasn't been imported
            return False
        finally:
            cursor.close()

    def insert_message_data(
        self, table_name: str, data: Dict[str, Any], file_hash: str, file_id: str
    ):
        """Insert message data into the specified table."""
        if not data:
            return

        # Add _file_hash, _file_id and current timestamp
        data = data.copy()
        data["_file_hash"] = file_hash
        data["_file_id"] = file_id

        # Get valid columns for this table to filter out unknown fields
        valid_columns = self._get_table_columns(table_name)
        if not valid_columns:
            logger.warning(f"Could not get column info for table {table_name}")
            return

        # Filter data to only include columns that exist in the table
        filtered_data = {}
        for key, value in data.items():
            if key in valid_columns:
                filtered_data[key] = value
            else:
                logger.debug(f"Skipping unknown column {key} for table {table_name}")

        if not filtered_data:
            logger.debug(f"No valid data to insert into {table_name}")
            return

        # Build INSERT statement
        columns = list(filtered_data.keys())
        placeholders = ["?" for _ in columns]
        values = [filtered_data[col] for col in columns]

        # Handle quoted table names
        table_ref = (
            f'"{table_name}"' if table_name in ["set", "user", "group", "order"] else table_name
        )

        sql = f"""
            INSERT INTO {table_ref} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            logger.debug(f"Inserted data into {table_name}: {len(values)} fields")
        except sqlite3.Error as e:
            logger.error(f"Failed to insert into {table_name}: {e}")
            logger.debug(f"Filtered data: {filtered_data}")
            raise
        finally:
            cursor.close()

    def _get_table_columns(self, table_name: str) -> set:
        """Get set of column names for a table."""
        cursor = self.connection.cursor()
        try:
            # Handle quoted table names
            table_ref = (
                f'"{table_name}"' if table_name in ["set", "user", "group", "order"] else table_name
            )
            cursor.execute(f"PRAGMA table_info({table_ref})")
            return {row[1] for row in cursor.fetchall()}  # row[1] is column name
        except sqlite3.Error as e:
            logger.error(f"Failed to get column info for {table_name}: {e}")
            return set()
        finally:
            cursor.close()

    def bulk_insert_message_data(
        self, table_name: str, data_list: List[Dict[str, Any]], file_hash: str, file_id: str
    ):
        """Bulk insert multiple records for better performance."""
        if not data_list:
            return

        # Get valid columns for this table
        valid_columns = self._get_table_columns(table_name)
        if not valid_columns:
            logger.warning(f"Could not get column info for table {table_name}")
            return

        # Filter and prepare all records
        filtered_data_list = []
        for data in data_list:
            # Add _file_hash and _file_id
            data = data.copy()
            data["_file_hash"] = file_hash
            data["_file_id"] = file_id

            # Filter to valid columns
            filtered_data = {k: v for k, v in data.items() if k in valid_columns}
            if filtered_data:
                filtered_data_list.append(filtered_data)

        if not filtered_data_list:
            logger.debug(f"No valid data to bulk insert into {table_name}")
            return

        # Collect all possible columns from all records
        all_columns = set()
        for data in filtered_data_list:
            all_columns.update(data.keys())
        
        columns = sorted(list(all_columns))  # Sort for consistent ordering
        placeholders = ["?" for _ in columns]

        # Handle quoted table names
        table_ref = (
            f'"{table_name}"' if table_name in ["set", "user", "group", "order"] else table_name
        )

        sql = f"""
            INSERT INTO {table_ref} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        # Prepare all value tuples
        values_list = [[data.get(col) for col in columns] for data in filtered_data_list]

        cursor = self.connection.cursor()
        try:
            cursor.executemany(sql, values_list)
            logger.debug(f"Bulk inserted {len(filtered_data_list)} records into {table_name}")
        except sqlite3.Error as e:
            logger.error(f"Failed to bulk insert into {table_name}: {e}")
            raise
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("BEGIN")
            yield cursor
            cursor.execute("COMMIT")
        except Exception:
            cursor.execute("ROLLBACK")
            raise
        finally:
            cursor.close()

    def get_schema_version(self) -> Optional[str]:
        """Get current schema version from metadata table."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT value FROM _grafit_metadata
                WHERE key = 'schema_version'
            """
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error:
            return None
        finally:
            cursor.close()

    def get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                AND name != '_grafit_metadata'  -- Exclude only our metadata table
                ORDER BY name
            """
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()

    def get_import_stats(self) -> Dict[str, int]:
        """Get statistics about imported data."""
        stats = {}
        tables = self.get_table_names()

        cursor = self.connection.cursor()
        try:
            for table in tables:
                # Handle reserved words like 'set'
                table_name = f'"{table}"' if table in ["set", "user", "group", "order"] else table
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                stats[table] = cursor.fetchone()[0]
        finally:
            cursor.close()

        return stats

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file for deduplication."""
    hash_sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()
