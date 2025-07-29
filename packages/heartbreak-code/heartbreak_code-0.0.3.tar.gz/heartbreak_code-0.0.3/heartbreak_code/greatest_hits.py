
import os
import sqlite3
from heartbreak_code.the_archives import TheArchives
class GreatestHits:
    def __init__(self, interpreter, setlist_instance):
        self.interpreter = interpreter
        self.the_archives = TheArchives()
        self.the_setlist = setlist_instance

    def change_the_key(self, text, case_type):
        if not isinstance(text, str):
            raise Exception("Type error: 'Change The Key' expects a string for 'text'.")
        if not isinstance(case_type, str):
            raise Exception("Type error: 'Change The Key' expects a string for 'case_type'.")

        if case_type == "upper":
            return text.upper()
        elif case_type == "lower":
            return text.lower()
        elif case_type == "title":
            return text.title()
        else:
            raise Exception(f"Invalid case type: {case_type}. Expected 'upper', 'lower', or 'title'.")

    def calculate_the_score(self, num1, num2, operation):
        if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
            raise Exception("Type error: 'Calculate The Score' expects numbers for 'num1' and 'num2'.")
        if not isinstance(operation, str):
            raise Exception("Type error: 'Calculate The Score' expects a string for 'operation'.")

        if operation == "add":
            return num1 + num2
        elif operation == "subtract":
            return num1 - num2
        elif operation == "multiply":
            return num1 * num2
        elif operation == "divide":
            if num2 == 0:
                raise Exception("Division by zero error in 'Calculate The Score'.")
            return num1 / num2
        else:
            raise Exception(f"Invalid operation: {operation}. Expected 'add', 'subtract', 'multiply', or 'divide'.")

    def rewrite_history(self, value, target_type):
        if not isinstance(target_type, str):
            raise Exception("Type error: 'Rewrite History' expects a string for 'target_type'.")

        if target_type == "string":
            return str(value)
        elif target_type == "number":
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    raise Exception(f"Cannot convert '{value}' to a number.")
        elif target_type == "boolean":
            if isinstance(value, str):
                if value.lower() in ("true", "yes", "1"):
                    return True
                elif value.lower() in ("false", "no", "0"):
                    return False
                else:
                    raise Exception(f"Cannot convert string '{value}' to boolean.")
            return bool(value)
        else:
            raise Exception(f"Invalid target type: {target_type}. Expected 'string', 'number', or 'boolean'.")

    def read_the_letter(self, file_path):
        if not isinstance(file_path, str):
            raise Exception("Type error: 'Read The Letter' expects a string for file path.")
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")

    def write_in_the_diary(self, file_path, content):
        if not isinstance(file_path, str):
            raise Exception("Type error: 'Write In The Diary' expects a string for file path.")
        if not isinstance(content, str):
            raise Exception("Type error: 'Write In The Diary' expects a string for content.")
        try:
            with open(file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Error writing to file {file_path}: {e}")

    def does_the_vault_contain(self, file_path):
        if not isinstance(file_path, str):
            raise Exception("Type error: 'Does The Vault Contain' expects a string for file path.")
        return os.path.exists(file_path)

    # The Archives: Native Database Connectivity
    def open_the_archives(self, db_name):
        self.the_archives.db_name = db_name
        self.the_archives.open_connection()

    def close_the_archives(self):
        self.the_archives.close_connection()

    def query_the_archives(self, query, params=()):
        return self.the_archives.execute_query(query, params)

    def create_archive_table(self, table_name, columns):
        return self.the_archives.create_table(table_name, columns)

    def insert_into_archive(self, table_name, data):
        return self.the_archives.insert_data(table_name, data)

    def select_from_archive(self, table_name, columns='*', where_clause=None, params=()):
        return self.the_archives.select_data(table_name, columns, where_clause, params)

    def update_archive(self, table_name, set_clause, where_clause, params=()):
        return self.the_archives.update_data(table_name, set_clause, where_clause, params)

    def delete_from_archive(self, table_name, where_clause, params=()):
        return self.the_archives.delete_data(table_name, where_clause, params)

    # The Setlist: A Web Server Micro-framework
    def define_setlist_route(self, method, path, handler_verse_name):
        def handler_wrapper(req, res):
            # Store req and res in interpreter for HeartbreakCode access
            self.interpreter.current_request = req
            self.interpreter.current_response = res
            # Execute the HeartbreakCode verse
            self.interpreter.execute_verse_by_name(handler_verse_name)
            # Clear after handling
            self.interpreter.current_request = None
            self.interpreter.current_response = None

        if method.upper() == 'GET':
            self.the_setlist.get(path, handler_wrapper)
        elif method.upper() == 'POST':
            self.the_setlist.post(path, handler_wrapper)
        elif method.upper() == 'PUT':
            self.the_setlist.put(path, handler_wrapper)
        elif method.upper() == 'DELETE':
            self.the_setlist.delete(path, handler_wrapper)
        else:
            raise Exception(f"Unsupported HTTP method for Setlist: {method}")

    def start_the_setlist(self, port=8000):
        self.the_setlist.start_server(port)

    def stop_the_setlist(self):
        self.the_setlist.stop_server()

    def setlist_response_send(self, content):
        if self.interpreter.current_response:
            self.interpreter.current_response.send(content)
        else:
            print("Error: No active HTTP response to send content to.")

    def setlist_response_json(self, data):
        if self.interpreter.current_response:
            self.interpreter.current_response.json(data)
        else:
            print("Error: No active HTTP response to send JSON to.")

    def setlist_response_status(self, code):
        if self.interpreter.current_response:
            self.interpreter.current_response.status(code)
        else:
            print("Error: No active HTTP response to set status for.")

    def setlist_request_path(self):
        if self.interpreter.current_request:
            return self.interpreter.current_request.path
        return None

    def setlist_request_method(self):
        if self.interpreter.current_request:
            return self.interpreter.current_request.method
        return None

    def setlist_request_body(self):
        if self.interpreter.current_request:
            return self.interpreter.current_request.body
        return None

    def setlist_request_header(self, header_name):
        if self.interpreter.current_request:
            return self.interpreter.current_request.headers.get(header_name)
        return None
