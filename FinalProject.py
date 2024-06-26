import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector as MySQL

def connect_to_db():
    conn = MySQL.connect(
        host="localhost",
        user="root",
        password='root',
        database="goathospitals"
    )
    return conn

def get_table_names():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return tables

#Fetch column names for a given table
def get_column_names(table_name):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = [column[0] for column in cursor.fetchall()]
    conn.close()
    return columns

class MySQLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DreemHospitals")

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.label = ttk.Label(self.frame, text="Dreem Hospitals Database")
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.table_label = ttk.Label(self.frame, text="Select Table:")
        self.table_label.grid(row=1, column=0, pady=5)

        self.table_combobox = ttk.Combobox(self.frame)
        self.table_combobox['values'] = get_table_names()
        self.table_combobox.grid(row=1, column=1, pady=5)
        self.table_combobox.current(0)

        self.show_table_button = ttk.Button(self.frame, text="Show Table", command=self.show_table)
        self.show_table_button.grid(row=2, column=0, pady=5)

        self.add_row_button = ttk.Button(self.frame, text="Add Row", command=self.add_row)
        self.add_row_button.grid(row=2, column=1, pady=5)

        self.delete_row_button = ttk.Button(self.frame, text="Delete Row", command=self.delete_row)
        self.delete_row_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.edit_data_button = ttk.Button(self.frame, text="Edit Data", command=self.edit_data)
        self.edit_data_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.result_text = tk.Text(self.frame, height=20, width=80)
        self.result_text.grid(row=5, column=0, columnspan=2, pady=10)

    def show_table(self):
        selected_table = self.table_combobox.get()
        if not selected_table:
            messagebox.showwarning("Warning", "Please select a table")
            return
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            # Fetch column names
            cursor.execute(f"SHOW COLUMNS FROM {selected_table}")
            columns = [column[0] for column in cursor.fetchall()]

            # Fetch table data
            cursor.execute(f"SELECT * FROM {selected_table}")
            results = cursor.fetchall()

            # Clear the text area
            self.result_text.delete('1.0', tk.END)

            # Display column headers
            self.result_text.insert(tk.END, ' | '.join(columns) + '\n')
            self.result_text.insert(tk.END, '-' * (len(columns) * 10) + '\n')

            # Display table data
            for row in results:
                self.result_text.insert(tk.END, ' | '.join(str(item) for item in row) + '\n')

            conn.close()
        except MySQL.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")

    def add_row(self):
        selected_table = self.table_combobox.get()
        if not selected_table:
            messagebox.showwarning("Warning", "Please select a table")
            return

        columns = get_column_names(selected_table)

        # Define popup for row entry
        def submit():
            try:
                conn = connect_to_db()
                cursor = conn.cursor()
                values = tuple(entries[col].get() for col in columns)
                cursor.execute(
                    f"INSERT INTO {selected_table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                    values
                )
                conn.commit()
                conn.close()
                popup.destroy()
                messagebox.showinfo("Success", "Row added successfully")
            except MySQL.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")

        popup = tk.Toplevel()
        popup.title("Add Row")

        entries = {}
        for i, col in enumerate(columns):
            tk.Label(popup, text=f"{col}:").grid(row=i, column=0)
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1)
            entries[col] = entry

        submit_button = tk.Button(popup, text="Submit", command=submit)
        submit_button.grid(row=len(columns), column=0, columnspan=2)

    def delete_row(self):
        selected_table = self.table_combobox.get()
        if not selected_table:
            messagebox.showwarning("Warning", "Please select a table")
            return

        columns = get_column_names(selected_table)

        # Define popup for row deletion
        def submit():
            try:
                conn = connect_to_db()
                cursor = conn.cursor()
                # Example: Assuming you are deleting by a unique ID
                cursor.execute(f"DELETE FROM {selected_table} WHERE {columns[0]} = %s", (entry_id.get(),))
                conn.commit()
                conn.close()
                popup.destroy()
                messagebox.showinfo("Success", "Row deleted successfully")
            except MySQL.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")

        popup = tk.Toplevel()
        popup.title("Delete Row")

        tk.Label(popup, text=f"Row {columns[0]} to delete:").grid(row=0, column=0)
        
        entry_id = tk.Entry(popup)
        entry_id.grid(row=0, column=1)

        submit_button = tk.Button(popup, text="Submit", command=submit)
        submit_button.grid(row=1, column=0, columnspan=2)

    def edit_data(self):
        selected_table = self.table_combobox.get()
        if not selected_table:
            messagebox.showwarning("Warning", "Please select a table")
            return

        columns = get_column_names(selected_table)

        # Define popup for data editing
        def submit():
            try:
                conn = connect_to_db()
                cursor = conn.cursor()
                column_to_edit = column_combobox.get()
                row_id = entry_id.get()
                new_value = entry_new_value.get()
                cursor.execute(
                    f"UPDATE {selected_table} SET {column_to_edit} = %s WHERE {columns[0]} = %s",
                    (new_value, row_id)
                )
                conn.commit()
                conn.close()
                popup.destroy()
                messagebox.showinfo("Success", "Data updated successfully")
            except MySQL.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")

        popup = tk.Toplevel()
        popup.title("Edit Data")

        tk.Label(popup, text=f"Row {columns[0]} to edit:").grid(row=0, column=0)
        
        entry_id = tk.Entry(popup)
        entry_id.grid(row=0, column=1)

        tk.Label(popup, text="Column to edit:").grid(row=1, column=0)
        
        column_combobox = ttk.Combobox(popup)
        column_combobox['values'] = columns
        column_combobox.grid(row=1, column=1)
        column_combobox.current(0)

        tk.Label(popup, text="New value:").grid(row=2, column=0)
        
        entry_new_value = tk.Entry(popup)
        entry_new_value.grid(row=2, column=1)

        submit_button = tk.Button(popup, text="Submit", command=submit)
        submit_button.grid(row=3, column=0, columnspan=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = MySQLApp(root)
    root.mainloop()