import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Database setup
def setup_database():
    conn = sqlite3.connect('bankdb.db')
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS bank_details (
        id INTEGER PRIMARY KEY,
        bank_name TEXT NOT NULL,
        branch_name TEXT NOT NULL,
        branch_address TEXT NOT NULL,
        ifsc_code TEXT CHECK(LENGTH(ifsc_code) = 11),
        micr_code TEXT CHECK(LENGTH(micr_code) = 9),
        bank_account_number TEXT NOT NULL,
        account_type TEXT CHECK(account_type IN ('Savings', 'Current')),
        account_holder_name TEXT NOT NULL,
        account_opening_date TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

class SHGBankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SHG Bank Details Application")
        self.root.geometry("900x500")
        self.root.configure(bg="#f4f4f4")
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, bg="white")
        self.frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="SHG Bank Details", font=("Arial", 16, "bold"), bg="white").grid(row=0, column=0, columnspan=4, pady=5)

        fields = [
            ("Bank Name", "bank_name"),
            ("Branch Name", "branch_name"),
            ("Branch Address", "branch_address"),
            ("IFSC Code", "ifsc_code"),
            ("MICR Code", "micr_code"),
            ("Bank Account Number", "bank_account_number"),
            ("Name of the Account Holder", "account_holder_name"),
            ("Date of Account Opening", "account_opening_date")
        ]

        self.entries = {}

        for i, (label_text, var_name) in enumerate(fields):
            tk.Label(self.frame, text=label_text, bg="white").grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
            self.entries[var_name] = tk.Entry(self.frame, width=30)
            self.entries[var_name].grid(row=i+1, column=1, padx=5, pady=5)

        tk.Label(self.frame, text="Account Type", bg="white").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        self.account_type_var = tk.StringVar()
        self.account_type_combobox = ttk.Combobox(self.frame, textvariable=self.account_type_var, values=["Savings", "Current"], width=27, state="readonly")
        self.account_type_combobox.grid(row=9, column=1, padx=5, pady=5)

        self.add_button = tk.Button(self.frame, text="Add Bank Details", command=self.add_bank_details, bg="#2ecc71", fg="white", width=20)
        self.add_button.grid(row=10, column=0, pady=5)

        self.update_button = tk.Button(self.frame, text="Update Bank Details", command=self.update_bank_details, bg="#f39c12", fg="white", width=20)
        self.update_button.grid(row=10, column=1, pady=5)

        self.delete_button = tk.Button(self.frame, text="Delete Bank Details", command=self.delete_bank_details, bg="#e74c3c", fg="white", width=20)
        self.delete_button.grid(row=10, column=2, pady=5)

        self.clear_button = tk.Button(self.frame, text="Clear Fields", command=self.clear_fields, bg="#95a5a6", fg="white", width=20)
        self.clear_button.grid(row=10, column=3, pady=5)

        self.bank_list = ttk.Treeview(self.frame, columns=("ID", "Bank Name", "Branch Name", "Branch Address", "IFSC Code", "MICR Code", "Bank Account Number", "Account Type", "Account Holder Name", "Date of Account Opening"), show="headings")
        for col in self.bank_list["columns"]:
            self.bank_list.heading(col, text=col)
            self.bank_list.column(col, width=100)
        self.bank_list.grid(row=11, column=0, columnspan=4, pady=5, sticky="nsew")
        self.view_bank_details()

    def add_bank_details(self):
        values = [self.entries[field].get() for field in self.entries]
        values.insert(6, self.account_type_var.get())

        if not all(values):
            messagebox.showwarning("Input Error", "Please fill in all fields correctly.")
            return
        
        query = 'INSERT INTO bank_details (bank_name, branch_name, branch_address, ifsc_code, micr_code, bank_account_number, account_type, account_holder_name, account_opening_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        
        conn = sqlite3.connect('bankdb.db')
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        self.view_bank_details()

    def update_bank_details(self):
        selected_item = self.bank_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record to update.")
            return
        
        values = [self.entries[field].get() for field in self.entries]
        values.insert(6, self.account_type_var.get())
        member_id = self.bank_list.item(selected_item)['values'][0]

        query = 'UPDATE bank_details SET bank_name=?, branch_name=?, branch_address=?, ifsc_code=?, micr_code=?, bank_account_number=?, account_type=?, account_holder_name=?, account_opening_date=? WHERE id=?'
        values.append(member_id)

        conn = sqlite3.connect('bankdb.db')
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        self.view_bank_details()

    def delete_bank_details(self):
        selected_item = self.bank_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return
        member_id = self.bank_list.item(selected_item)['values'][0]
        
        conn = sqlite3.connect('bankdb.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bank_details WHERE id=?', (member_id,))
        conn.commit()
        conn.close()
        self.view_bank_details()

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.account_type_var.set("")

    def view_bank_details(self):
        for item in self.bank_list.get_children():
            self.bank_list.delete(item)
        conn = sqlite3.connect('bankdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bank_details')
        bank_details = cursor.fetchall()
        for detail in bank_details:
            self.bank_list.insert("", "end", values=detail)
        conn.close()

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = SHGBankApp(root)
    root.mainloop()
