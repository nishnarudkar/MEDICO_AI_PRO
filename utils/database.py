import sqlite3
import pandas as pd
import hashlib
from pathlib import Path
import json
from datetime import datetime
import io

class DatabaseManager:
    """Enhanced database manager with advanced features"""

    def __init__(self, db_path="healthgenai.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Create metadata table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS table_metadata (
                table_name TEXT PRIMARY KEY,
                original_filename TEXT,
                upload_timestamp TEXT,
                row_count INTEGER,
                column_count INTEGER,
                file_hash TEXT,
                schema_info TEXT
            )
            """)

            # Create query history table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT,
                query_type TEXT,
                execution_time REAL,
                timestamp TEXT,
                success BOOLEAN,
                error_message TEXT
            )
            """)

            conn.commit()

    def store_dataframe(self, df, table_name, original_filename=None):
        """Store DataFrame with metadata"""
        start_time = datetime.now()

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store the dataframe
                df.to_sql(table_name, conn, if_exists="replace", index=False)

                # Calculate file hash for integrity
                file_hash = hashlib.md5(df.to_string().encode()).hexdigest()

                # Store metadata
                metadata = {
                    'table_name': table_name,
                    'original_filename': original_filename or table_name,
                    'upload_timestamp': start_time.isoformat(),
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'file_hash': file_hash,
                    'schema_info': json.dumps({
                        col: str(dtype) for col, dtype in df.dtypes.items()
                    })
                }

                conn.execute("""
                INSERT OR REPLACE INTO table_metadata
                VALUES (:table_name, :original_filename, :upload_timestamp,
                        :row_count, :column_count, :file_hash, :schema_info)
                """, metadata)

                conn.commit()

            return True

        except Exception as e:
            self.log_error(f"store_dataframe", str(e))
            return False

    def execute_query(self, query, params=None):
        """Execute query with logging and error handling"""
        start_time = datetime.now()

        try:
            with sqlite3.connect(self.db_path) as conn:
                if params:
                    cursor = conn.execute(query, params)
                else:
                    cursor = conn.execute(query)

                # Get results
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]

                # Create DataFrame
                df = pd.DataFrame(results, columns=columns)

                # Log successful query
                execution_time = (datetime.now() - start_time).total_seconds()
                self.log_query(query, execution_time, True)

                return df

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_query(query, execution_time, False, str(e))
            raise e

    def log_query(self, query, execution_time, success, error_message=None):
        """Log query execution details"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                INSERT INTO query_history
                (query_text, execution_time, timestamp, success, error_message)
                VALUES (?, ?, ?, ?, ?)
                """, (query[:1000], execution_time, datetime.now().isoformat(),
                      success, error_message))
                conn.commit()
        except:
            pass  # Don't fail if logging fails

    def get_table_info(self, table_name):
        """Get comprehensive table information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get basic info
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                # Get row count
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                # Get metadata if available
                cursor = conn.execute(
                    "SELECT * FROM table_metadata WHERE table_name = ?",
                    (table_name,)
                )
                metadata = cursor.fetchone()

                return {
                    'table_name': table_name,
                    'columns': columns,
                    'row_count': row_count,
                    'metadata': metadata
                }

        except Exception as e:
            return None

    def get_available_tables(self):
        """Get all available tables with their info"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                AND name NOT IN ('table_metadata', 'query_history')
                """)

                tables = cursor.fetchall()

                table_info = []
                for (table_name,) in tables:
                    info = self.get_table_info(table_name)
                    if info:
                        table_info.append(info)

                return table_info

        except Exception as e:
            return []

    def optimize_database(self):
        """Optimize database performance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
                conn.commit()
            return True
        except:
            return False

    def export_table(self, table_name, format='csv'):
        """Export table in various formats"""
        try:
            df = self.execute_query(f"SELECT * FROM {table_name}")

            if format.lower() == 'csv':
                return df.to_csv(index=False)
            elif format.lower() == 'json':
                return df.to_json(orient='records', indent=2)
            elif format.lower() == 'excel':
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name=table_name, index=False)
                return output.getvalue()

        except Exception as e:
            return None

    def log_error(self, operation, error_message):
        """Log errors for debugging"""
        try:
            with open("healthgenai_errors.log", "a") as f:
                f.write(f"{datetime.now().isoformat()} - {operation}: {error_message}\n")
        except:
            pass