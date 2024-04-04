import csv
from tempfile import NamedTemporaryFile
import shutil
import os
from uuid import uuid4

class CSVManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.actions = {}  # To store actions for undo

    def read_file(self):
        with open(self.filepath, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

    def search_row(self, column_name, value, match_type='same'):
        results = []
        with open(self.filepath, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                col_value = row.get(column_name, '')
                if match_type == 'like' and value.lower() in col_value.lower():
                    results.append(row)
                elif match_type == 'unlike' and value.lower() not in col_value.lower():
                    results.append(row)
                elif match_type == 'include' and value in col_value:
                    results.append(row)
                elif match_type == 'same' and value == col_value:
                    results.append(row)
        return results

    def modify_file(self, action, row=None, column_name=None, value=None, condition=None):
        action_id = str(uuid4())
        tempfile = NamedTemporaryFile(mode='w', delete=False, newline='')
        with open(self.filepath, 'r', newline='') as csvfile, tempfile:
            reader = csv.DictReader(csvfile)
            writer = csv.DictWriter(tempfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row_data in reader:
                if action == 'update' and row_data.get(column_name) == condition:
                    row_data[column_name] = value
                    self.actions[action_id] = ('update', dict(row_data))  # Store a copy for undo
                elif action == 'delete' and row_data.get(column_name) == condition:
                    self.actions[action_id] = ('insert', dict(row_data))  # Store a copy for undo
                    continue  # Skip writing this row to effectively delete it
                writer.writerow(row_data)
            if action == 'insert':
                writer.writerow(row)  # Append the new row at the end
                self.actions[action_id] = ('delete', dict(row))  # Store a copy for undo

        shutil.move(tempfile.name, self.filepath)
        return action_id

    def undo_action(self, action_id):
        action, row = self.actions.get(action_id, (None, None))
        if action:
            if action == 'delete':
                self.modify_file('insert', row=row)
            elif action == 'insert':
                self.modify_file('delete', condition=row)
            elif action == 'update':
                # Implement undo for update if necessary
                pass
            del self.actions[action_id]

if __name__ == '__main__':
    manager = CSVManager('users.csv')
    manager.read_file()
    results = manager.search_row('username', 'brandon', 'like')
    print(results)
    action_id = manager.modify_file('insert', row={'username': 'john', 'email': 'john@outlook.com', 'age': 29})
