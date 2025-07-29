import sqlite3
from colorama import *

init(autoreset=True)

import sqlite3
from colorama import *

init(autoreset=True)
# /////////////////////////////////////////////////////////////
class DBManager:
    def __init__(self, **kwargs):
        self.connection = kwargs['connection']
        self.dbname = kwargs['dbname']
        print(Style.BRIGHT+Fore.GREEN+f"DBMNGRX 0.1.0;\n")
        try:
            self.connection = sqlite3.connect(self.dbname + ".db")
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT 1")
            print(Style.BRIGHT+Fore.GREEN+f"{self.dbname}.db: Connected.")
        except sqlite3.Error as e:
            print(Style.BRIGHT+Fore.RED+"Error in connection: ", e)

    def db_info(self):
        res = self.cursor.execute("PRAGMA database_list").fetchall()[0]
        return f"Database ID: {res[0]}\nDatabase name: {res[1]}\nDatabase path: {res[2]}"

    def create_table(self, name):
        try:
            self.cursor.execute(f"CREATE TABLE {name} (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
            print(f"Table {name} created successfully.")
        except sqlite3.Error as e:
            print(f"Error in creating table {name}: ", e)
        return ""

    def get_tables(self):
        res = self.cursor.execute("SELECT * FROM sqlite_master WHERE type='table'").fetchall()
        print(Style.BRIGHT+f"Table list in {self.dbname}.db :")
        return "\n".join([str(x[1]) for x in res])

    def get_table(self, name):
        try:
            exists = self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}';").fetchall()
            if len(exists):
                res = self.cursor.execute(f"SELECT * FROM {name}").fetchall()
                if not res:
                    print(Fore.YELLOW + f"Table {name} is empty.")
                else:
                    for row in res:
                        print(row)
            else:
                print(f"Table {name} does not exist.")
        except sqlite3.Error as e:
            print(Style.BRIGHT + Fore.RED + f"Error in get_table(): ", e)

    def get_cols(self, name):
        try:
            ex = self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'").fetchall()
            if len(ex):
                columns = self.cursor.execute(f"PRAGMA table_info({name})").fetchall()
                for col in columns:
                    print(f"{col[1]} ({col[2]})")
            else:
                print(Fore.YELLOW + f"Table {name} does not exist.")
        except sqlite3.Error as e:
            print(Style.BRIGHT+Fore.RED +f"Error in get_cols(): ", e)
        return ''

    def add_col(self, table_name, col_name):
        self._col_def = {
            'table': table_name,
            'name': col_name,
            'type': '',
            'nullable': True,
            'default': None,
            'primary_key':False,
            'unique':False
        }
        return self

    def text(self): self._col_def['type'] = 'TEXT'; return self
    def integer(self): self._col_def['type'] = 'INTEGER'; return self
    def real(self): self._col_def['type'] = 'REAL'; return self
    def numeric(self): self._col_def['type'] = 'NUMERIC'; return self
    def blob(self): self._col_def['type'] = 'BLOB'; return self
    def unnullable(self): self._col_def['nullable'] = False; return self
    def nullable(self): self._col_def['nullable'] = True; return self
    def primary_key(self): self._col_def['primary_key'] = True; return self
    def unique(self): self._col_def["unique"] = True; return self

    def default(self, value):
        if isinstance(value, str): value = f"'{value}'"
        elif value is None: value = "NULL"
        elif isinstance(value, bool): value = "1" if value else "0"
        self._col_def['default'] = value
        return self

    def commit(self):
        try:
            col = self._col_def
            sql = f"ALTER TABLE {col['table']} ADD COLUMN {col['name']} {col['type']}"
            if not col['nullable'] and not col['primary_key']:
                sql += " NOT NULL"
            if col['default'] is not None:
                sql += f" DEFAULT {col['default']}"
            if col['primary_key']:
                sql += " PRIMARY KEY"
            if col['unique']:
                sql += " UNIQUE"
            self.cursor.execute(sql)
            self.connection.commit()
            print(Fore.GREEN + f"Column '{col['name']}' added to '{col['table']}' as {col['type']}.")
        except sqlite3.Error as e:
            print(Fore.RED + "Error in commit():", e)
        finally:
            self._col_def = None
        return ''

    def insert_row(self, name, data):
        try:
            keys = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())
            self.cursor.execute(f"INSERT INTO {name} ({keys}) VALUES ({placeholders})", values)
            self.connection.commit()
            print(Fore.GREEN + "Row inserted successfully.")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in insert_row(): {e}")

    def update_row(self, name, set_data, where):
        try:
            set_clause = ', '.join([f"{k}=?" for k in set_data])
            values = list(set_data.values())
            sql = f"UPDATE {name} SET {set_clause} WHERE {where}"
            self.cursor.execute(sql, values)
            self.connection.commit()
            print(Fore.GREEN + "Row(s) updated.")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in update_row(): {e}")

    def delete_rows(self, name, where):
        try:
            self.cursor.execute(f"DELETE FROM {name} WHERE {where}")
            self.connection.commit()
            print(Fore.GREEN + "Row(s) deleted.")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in delete_rows(): {e}")

    def filter(self, name, where):
        try:
            rows = self.cursor.execute(f"SELECT * FROM {name} WHERE {where}").fetchall()
            for row in rows:
                print(row)
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in filter(): {e}")

    def count_rows(self, name):
        try:
            count = self.cursor.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            print(f"Total rows in {name}: {count}")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in count_rows(): {e}")

    def get_schema(self, name):
        try:
            schema = self.cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{name}'").fetchone()
            if schema:
                print(schema[0])
            else:
                print(f"Table {name} does not exist.")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in get_schema(): {e}")

    def rename_table(self, old, new):
        try:
            self.cursor.execute(f"ALTER TABLE {old} RENAME TO {new}")
            self.connection.commit()
            print(Fore.GREEN + f"Table {old} renamed to {new}.")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in rename_table(): {e}")

    def drop_table(self, name):
        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS {name}")
            self.connection.commit()
            print(Fore.GREEN + f"Table {name} dropped.")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in drop_table(): {e}")

    def execute_raw(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(Fore.GREEN + "Raw query executed.")
        except sqlite3.Error as e:
            print(Fore.RED + f"Error in execute_raw(): {e}")

    def close(self):
        self.connection.close()
        print(Fore.BLUE + "Database connection closed.")