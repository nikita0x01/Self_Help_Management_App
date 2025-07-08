import sqlite3
import tkinter as tk
import subprocess
from tkinter import messagebox, ttk

# Database setup
def setup_database():
    conn = sqlite3.connect('basicdetailsdb.db')
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        age INTEGER CHECK(age > 0),
        dob TEXT NOT NULL,
        gender TEXT DEFAULT 'Female',
        marital_status TEXT CHECK(marital_status IN ('Single', 'Married', 'Widowed', 'Divorced')),
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        pincode TEXT CHECK(LENGTH(pincode) = 6),
        phone TEXT CHECK(LENGTH(phone) = 10)
    );
    """)
    conn.commit()
    conn.close()

class SHGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Self Help Group Application")
        self.root.geometry("1100x550")
        self.root.configure(bg="#f4f4f4")
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, bg="white")
        self.frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Basic Details", font=("Arial", 16, "bold"), bg="white").grid(row=0, column=0, columnspan=6, pady=5)

        fields = [
            ("Full Name", "name_entry"),
            ("Age", "age_entry"),
            ("Date of Birth (DOB)", "dob_entry"),
            ("Address", "address_entry"),
            ("City/Town/Village", "city_entry"),
            ("State", "state_entry"),
            ("Pincode", "pincode_entry"),
            ("Phone", "phone_entry")
        ]

        self.entries = {}

        for i, (label_text, var_name) in enumerate(fields):
            tk.Label(self.frame, text=label_text, bg="white").grid(row=(i // 3) + 1, column=(i % 3) * 2, padx=2, pady=2, sticky="w")
            self.entries[var_name] = tk.Entry(self.frame, width=20)
            self.entries[var_name].grid(row=(i // 3) + 1, column=(i % 3) * 2 + 1, padx=2, pady=2)

        tk.Label(self.frame, text="Gender", bg="white").grid(row=4, column=0, padx=2, pady=2, sticky="w")
        self.gender_var = tk.StringVar(value="Female")
        tk.Entry(self.frame, textvariable=self.gender_var, state='readonly', width=20).grid(row=4, column=1, padx=2, pady=2)

        tk.Label(self.frame, text="Marital Status", bg="white").grid(row=4, column=2, padx=2, pady=2, sticky="w")
        self.marital_status_var = tk.StringVar()
        self.marital_status_combobox = ttk.Combobox(self.frame, textvariable=self.marital_status_var, values=["Single", "Married", "Widowed", "Divorced"], width=18, state="readonly")
        self.marital_status_combobox.grid(row=4, column=3, padx=2, pady=2)

        self.add_button = tk.Button(self.frame, text="Add Member", command=self.add_member, bg="#2ecc71", fg="white", width=15)
        self.add_button.grid(row=5, column=0, columnspan=2, pady=2)

        self.update_button = tk.Button(self.frame, text="Update Member", command=self.update_member, bg="#f39c12", fg="white", width=15)
        self.update_button.grid(row=5, column=2, columnspan=2, pady=2)

        self.delete_button = tk.Button(self.frame, text="Delete Member", command=self.delete_member, bg="#e74c3c", fg="white", width=15)
        self.delete_button.grid(row=5, column=4, columnspan=2, pady=2)

        self.clear_button = tk.Button(self.frame, text="Clear Fields", command=self.clear_fields, bg="#95a5a6", fg="white", width=15, state=tk.DISABLED)
        self.clear_button.grid(row=5, column=6, columnspan=2, pady=2)

        self.members_list = ttk.Treeview(self.frame, columns=("ID", "Full Name", "Age", "DOB", "Gender", "Marital Status", "Address", "City", "State", "Pincode", "Phone"), show="headings")
        for col in self.members_list["columns"]:
            self.members_list.heading(col, text=col)
            self.members_list.column(col, width=90)
        self.members_list.grid(row=6, column=0, columnspan=6, pady=5, sticky="nsew")

        self.view_members()

        # New Buttons
        self.financial_button = tk.Button(self.root, text="Add Financial Details", command=self.open_financial_details, bg="#3498db", fg="white", width=20)
        self.financial_button.pack(pady=5)

        self.back_button = tk.Button(self.root, text="Back", command=self.open_final, bg="#34495e", fg="white", width=20)
        self.back_button.pack(pady=5)

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.marital_status_var.set("")
        self.clear_button.config(state=tk.DISABLED)  # Disable button after clearing

    def add_member(self):
        if self.process_member(action="add"):
            self.clear_button.config(state=tk.NORMAL)  # Enable clear button

    def update_member(self):
        if self.process_member(action="update"):
            self.clear_button.config(state=tk.NORMAL)  # Enable clear button

    def delete_member(self):
        selected_item = self.members_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a member to delete.")
            return
        member_id = self.members_list.item(selected_item)['values'][0]
        conn = sqlite3.connect('basicdetailsdb.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM members WHERE id=?', (member_id,))
        conn.commit()
        conn.close()
        self.view_members()

    def process_member(self, action):
        values = [self.entries[field].get() for field in self.entries]
        values.insert(3, self.gender_var.get())
        values.insert(4, self.marital_status_var.get())

        if not all(values):
            messagebox.showwarning("Input Error", "Please fill in all fields correctly.")
            return False
        if not values[-1].isdigit() or len(values[-1]) != 10:
            messagebox.showwarning("Input Error", "Phone number must be exactly 10 digits.")
            return False
        if action == "add":
            query = 'INSERT INTO members (full_name, age, dob, gender, marital_status, address, city, state, pincode, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        else:
            selected_item = self.members_list.selection()
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select a member to update.")
                return False
            member_id = self.members_list.item(selected_item)['values'][0]
            query = f'UPDATE members SET full_name=?, age=?, dob=?, gender=?, marital_status=?, address=?, city=?, state=?, pincode=?, phone=? WHERE id={member_id}'
        
        conn = sqlite3.connect('basicdetailsdb.db')
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        self.view_members()
        return True  # Successfully added/updated member
    
    def view_members(self):
        for item in self.members_list.get_children():
            self.members_list.delete(item)
        conn = sqlite3.connect('basicdetailsdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members')
        members = cursor.fetchall()
        for member in members:
            self.members_list.insert("", "end", values=member)
        conn.close()

    def open_financial_details(self):
        subprocess.run(["python", "financialdetails.py"])

    def open_final(self):
        subprocess.run(["python", "final.py"])

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = SHGApp(root)
    root.mainloop()
