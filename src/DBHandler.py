import os.path
import sqlite3

class DBHandler:
    """
    Thanks Phi-4!
    """
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_table()

    def _execute_query(self, query, params=(), commit=False):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                return cursor
            except Exception as e:
                print(f"Error: {e}")

    def create_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS files (
                filepath TEXT PRIMARY KEY,
                fileid INTEGER NOT NULL
            )
        '''
        self._execute_query(query, commit=True)

    def add_file(self, filepath, fileid):
        query = 'INSERT INTO files (filepath, fileid) VALUES (?, ?)'
        cursor = self._execute_query(query, (filepath, fileid), commit=True)
        if cursor:
            #print("File added successfully.")
            pass

    def update_file(self, filepath, new_fileid):
        query = 'UPDATE files SET fileid = ? WHERE filepath = ?'
        cursor = self._execute_query(query, (new_fileid, filepath), commit=True)
        if cursor and cursor.rowcount > 0:
            #print("File updated successfully.")
            pass
        elif cursor:
            print("No record found with the given filepath:", filepath)

    def retrieve_file(self, filepath=None):
        query = 'SELECT * FROM files WHERE filepath = ?' if filepath else 'SELECT * FROM files'
        params = (filepath,) if filepath else ()
        try:
            cursor = self._execute_query(query, params)
            records = cursor.fetchall() if cursor else []
            return records
        except Exception as e:
            print(f"Error retrieving files: {e}")
            return []

    def delete_file(self, filepath):
        query = 'DELETE FROM files WHERE filepath = ?'
        cursor = self._execute_query(query, (filepath,), commit=True)
        if cursor and cursor.rowcount > 0:
            pass
            #print("File deleted successfully.")
        elif cursor:
            print("No record found with the given filepath:", filepath)