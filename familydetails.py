import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess

# Database setup
def setup_database():
    conn = sqlite3.connect('familydb.db')
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS family_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        num_dependents INTEGER CHECK(num_dependents >= 0),
        guardian_name TEXT NOT NULL,
        guardian_occupation TEXT NOT NULL,
        emergency_contact TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

class FamilyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Family Details")
        self.root.geometry("900x450")
        self.root.configure(bg="#f4f4f4")
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, bg="white")
        self.frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Family Details", font=("Arial", 16, "bold"), bg="white").grid(row=0, column=0, columnspan=4, pady=5)

        fields = [
            ("Number of Dependents", "num_dependents_entry"),
            ("Husband's/Father's Name", "guardian_name_entry"),
            ("Husband's/Father's Occupation", "guardian_occupation_entry"),
            ("Emergency Contact (Name & Number)", "emergency_contact_entry")
        ]

        self.entries = {}

        for i, (label_text, var_name) in enumerate(fields):
            tk.Label(self.frame, text=label_text, bg="white").grid(row=i+1, column=0, padx=2, pady=2, sticky="w")
            self.entries[var_name] = tk.Entry(self.frame, width=22)
            self.entries[var_name].grid(row=i+1, column=1, padx=2, pady=2)

        self.add_button = tk.Button(self.frame, text="Add", command=self.add_family_details, bg="#2ecc71", fg="white", width=15)
        self.add_button.grid(row=6, column=0, pady=5)

        self.update_button = tk.Button(self.frame, text="Update", command=self.update_family_details, bg="#f39c12", fg="white", width=15)
        self.update_button.grid(row=6, column=1, pady=5)

        self.delete_button = tk.Button(self.frame, text="Delete", command=self.delete_family_details, bg="#e74c3c", fg="white", width=15)
        self.delete_button.grid(row=6, column=2, pady=5)

        self.clear_button = tk.Button(self.frame, text="Clear Fields", command=self.clear_fields, bg="#95a5a6", fg="white", width=15)
        self.clear_button.grid(row=6, column=3, pady=5)

        self.details_list = ttk.Treeview(self.frame, columns=("ID", "Dependents", "Guardian Name", "Guardian Occupation", "Emergency Contact"), show="headings")
        for col in self.details_list["columns"]:
            self.details_list.heading(col, text=col)
            self.details_list.column(col, width=160)
        self.details_list.grid(row=7, column=0, columnspan=4, pady=5, sticky="nsew")

        # Navigation Buttons
        self.back_button = tk.Button(self.frame, text="Back", command=self.go_back, bg="#34495e", fg="white", width=30)
        self.back_button.grid(row=8, column=1, columnspan=2, pady=10)

        self.view_family_details()

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def add_family_details(self):
        values = [self.entries[field].get() for field in self.entries]
        if not all(values):
            messagebox.showwarning("Input Error", "Please fill in all fields correctly.")
            return

        try:
            values[0] = int(values[0])  # Convert dependents to integer
        except ValueError:
            messagebox.showerror("Input Error", "Number of Dependents should be a number.")
            return

        query = '''INSERT INTO family_details (num_dependents, guardian_name, guardian_occupation, emergency_contact) 
                   VALUES (?, ?, ?, ?)'''
        conn = sqlite3.connect('familydb.db')
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        self.view_family_details()

    def update_family_details(self):
        selected_item = self.details_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record to update.")
            return
        detail_id = self.details_list.item(selected_item)['values'][0]
        values = [self.entries[field].get() for field in self.entries]

        try:
            values[0] = int(values[0])  # Convert dependents to integer
        except ValueError:
            messagebox.showerror("Input Error", "Number of Dependents should be a number.")
            return

        query = '''UPDATE family_details 
                   SET num_dependents=?, guardian_name=?, guardian_occupation=?, emergency_contact=? 
                   WHERE id=?'''
        
        conn = sqlite3.connect('familydb.db')
        cursor = conn.cursor()
        cursor.execute(query, tuple(values + [detail_id]))
        conn.commit()
        conn.close()
        self.view_family_details()

    def delete_family_details(self):
        selected_item = self.details_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return
        detail_id = self.details_list.item(selected_item)['values'][0]
        conn = sqlite3.connect('familydb.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM family_details WHERE id=?', (detail_id,))
        conn.commit()
        conn.close()
        self.view_family_details()

    def view_family_details(self):
        for item in self.details_list.get_children():
            self.details_list.delete(item)
        conn = sqlite3.connect('familydb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM family_details')
        details = cursor.fetchall()
        for detail in details:
            self.details_list.insert("", "end", values=detail)
        conn.close()

    def go_back(self):
        """Go back to Group Participation Details"""
        self.root.destroy()
        subprocess.run(["python", "grpparticipationdetails.py"])

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = FamilyApp(root)
    root.mainloop()
