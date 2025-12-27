import duckdb
import os
import sys
current_dir = os.getcwd()
project_root = os.path.dirname(current_dir)

class Exe_SQL:
    def __init__(self, 
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        secure: bool = False,
        url_style: str = "path",
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.url_style = url_style
        self.conn = None

    def connect(self):
        try:
            conn = duckdb.connect()
            conn.execute("INSTALL httpfs")
            conn.execute("LOAD httpfs")
            conn.execute(f"SET s3_endpoint='{self.endpoint}'")
            conn.execute(f"SET s3_access_key_id='{self.access_key}'")
            conn.execute(f"SET s3_secret_access_key='{self.secret_key}'")
            conn.execute(f"SET s3_use_ssl={self.secure}")
            conn.execute(f"SET s3_url_style='{self.url_style}'")
            return conn
        except Exception as e:
            print(f"Error connecting to DuckDB: {e}")
            return None
    
    def execute_sql(self, sql_text: str):
        try:
            if self.conn is None:
                self.conn = self.connect()
            return self.conn.execute(sql_text).fetchdf()
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return None
    

    def execute_sql_file(self, sql_file_name: str):
        sql_file_path = os.path.join(project_root, 'Lib', 'SQL_script', sql_file_name)
        try:
            with open(sql_file_path, 'r') as file:
                sql_text = file.read()
            return self.execute_sql(sql_text)
        except Exception as e:
            print(f"Error executing SQL file: {e}")
            return None

    def close(self):
        try:
            if self.conn is not None:
                self.conn.close()
            return True
        except Exception as e:
            print(f"Error closing DuckDB connection: {e}")
            return False