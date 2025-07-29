
# heartbreak_code/the_archives.py

import sqlite3

class TheArchives:
    def __init__(self, db_name='heartbreak_data.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def open_connection(self):
        """Opens a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"The Archives: Connection to {self.db_name} opened.")
        except sqlite3.Error as e:
            print(f"The Archives: Error opening connection: {e}")

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("The Archives: Connection closed.")

    def execute_query(self, query, params=()):
        """Executes an SQL query and returns results if any."""
        if not self.conn:
            print("The Archives: No active connection. Please open a connection first.")
            return None
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.conn.commit()
                print("The Archives: Query executed and committed.")
                return self.cursor.rowcount # Return number of rows affected
            else:
                results = self.cursor.fetchall()
                print("The Archives: Query executed. Results retrieved.")
                return results
        except sqlite3.Error as e:
            print(f"The Archives: Error executing query: {e}")
            return None

    def create_table(self, table_name, columns):
        """Creates a table in the database.
        columns should be a dictionary like {'column_name': 'DATATYPE'}
        """
        cols_str = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_str})"
        return self.execute_query(query)

    def insert_data(self, table_name, data):
        """Inserts data into a table.
        data should be a dictionary like {'column_name': 'value'}
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data.values()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, tuple(data.values()))

    def select_data(self, table_name, columns='*', where_clause=None, params=()):
        """Selects data from a table.
        columns can be a list of column names or '*'.
        """
        cols_str = ", ".join(columns) if isinstance(columns, list) else columns
        query = f"SELECT {cols_str} FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        return self.execute_query(query, params)

    def update_data(self, table_name, set_clause, where_clause, params=()):
        """Updates data in a table.
        set_clause should be like 'column1 = ?, column2 = ?'
        """
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        return self.execute_query(query, params)

    def delete_data(self, table_name, where_clause, params=()):
        """Deletes data from a table.
        """
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        return self.execute_query(query, params)
