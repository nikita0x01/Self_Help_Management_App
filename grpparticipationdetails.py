import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess

# Database setup
def setup_database():
    conn = sqlite3.connect('grpparticipation.db')
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS group_participation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shg_name TEXT NOT NULL,
        joining_date TEXT NOT NULL,
        role_in_shg TEXT CHECK(role_in_shg IN ('Member', 'Treasurer', 'President', 'Secretary')),
        savings_contribution REAL CHECK(savings_contribution >= 0),
        loan_taken TEXT CHECK(loan_taken IN ('Yes', 'No')),
        loan_amount REAL CHECK(loan_amount >= 0) DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()

class SHGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Self Help Group - Group Participation Details")
        self.root.geometry("900x450")
        self.root.configure(bg="#f4f4f4")
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, bg="white")
        self.frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Group Participation Details", font=("Arial", 16, "bold"), bg="white").grid(row=0, column=0, columnspan=4, pady=5)

        fields = [
            ("SHG Name", "shg_name_entry"),
            ("Joining Date (YYYY-MM-DD)", "joining_date_entry"),
            ("Role in SHG", "role_combobox"),
            ("Savings Contribution Per Month", "savings_contribution_entry"),
            ("Loan Taken", "loan_taken_combobox"),
            ("Loan Amount (if applicable)", "loan_amount_entry")
        ]

        self.entries = {}

        for i, (label_text, var_name) in enumerate(fields):
            tk.Label(self.frame, text=label_text, bg="white").grid(row=i+1, column=0, padx=2, pady=2, sticky="w")
            if var_name == "role_combobox":
                self.entries[var_name] = ttk.Combobox(self.frame, values=["Member", "Treasurer", "President", "Secretary"], width=20, state="readonly")
            elif var_name == "loan_taken_combobox":
                self.entries[var_name] = ttk.Combobox(self.frame, values=["Yes", "No"], width=20, state="readonly")
                self.entries[var_name].bind("<<ComboboxSelected>>", self.toggle_loan_amount)
            else:
                self.entries[var_name] = tk.Entry(self.frame, width=22)
            self.entries[var_name].grid(row=i+1, column=1, padx=2, pady=2)

        self.add_button = tk.Button(self.frame, text="Add", command=self.add_transaction, bg="#2ecc71", fg="white", width=15)
        self.add_button.grid(row=7, column=0, pady=5)

        self.update_button = tk.Button(self.frame, text="Update", command=self.update_transaction, bg="#f39c12", fg="white", width=15)
        self.update_button.grid(row=7, column=1, pady=5)

        self.delete_button = tk.Button(self.frame, text="Delete", command=self.delete_transaction, bg="#e74c3c", fg="white", width=15)
        self.delete_button.grid(row=7, column=2, pady=5)

        self.clear_button = tk.Button(self.frame, text="Clear Fields", command=self.clear_fields, bg="#95a5a6", fg="white", width=15)
        self.clear_button.grid(row=7, column=3, pady=5)

        self.transactions_list = ttk.Treeview(self.frame, columns=("ID", "SHG Name", "Joining Date", "Role", "Savings Contribution", "Loan Taken", "Loan Amount"), show="headings")
        for col in self.transactions_list["columns"]:
            self.transactions_list.heading(col, text=col)
            self.transactions_list.column(col, width=120)
        self.transactions_list.grid(row=8, column=0, columnspan=4, pady=5, sticky="nsew")

        # New Buttons
        self.family_details_button = tk.Button(self.frame, text="Back", command=self.go_back, bg="#3498db", fg="white", width=30)
        self.family_details_button.grid(row=9, column=0, columnspan=2, pady=10)

        self.back_button = tk.Button(self.frame, text="Add Family Details", command=self.open_family_details, bg="#34495e", fg="white", width=30)
        self.back_button.grid(row=9, column=2, columnspan=2, pady=10)

        self.view_transactions()

    def toggle_loan_amount(self, event=None):
        if self.entries["loan_taken_combobox"].get() == "No":
            self.entries["loan_amount_entry"].delete(0, tk.END)
            self.entries["loan_amount_entry"].config(state="disabled")
        else:
            self.entries["loan_amount_entry"].config(state="normal")

    def clear_fields(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)

    def add_transaction(self):
        values = [self.entries[field].get() for field in self.entries]
        if not values[5]:  # Loan amount should be 0 if loan taken is "No"
            values[5] = "0"
        if not all(values[:5]):  # Ensure all fields except loan amount are filled
            messagebox.showwarning("Input Error", "Please fill in all required fields correctly.")
            return

        query = '''INSERT INTO group_participation (shg_name, joining_date, role_in_shg, savings_contribution, loan_taken, loan_amount) 
                   VALUES (?, ?, ?, ?, ?, ?)'''
        conn = sqlite3.connect('grpparticipation.db')
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        self.view_transactions()

    def update_transaction(self):
        selected_item = self.transactions_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record to update.")
            return
        transaction_id = self.transactions_list.item(selected_item)['values'][0]
        values = [self.entries[field].get() for field in self.entries]
        if not values[5]:
            values[5] = "0"

        query = '''UPDATE group_participation 
                   SET shg_name=?, joining_date=?, role_in_shg=?, savings_contribution=?, loan_taken=?, loan_amount=? 
                   WHERE id=?'''
        
        conn = sqlite3.connect('grpparticipation.db')
        cursor = conn.cursor()
        cursor.execute(query, tuple(values + [transaction_id]))
        conn.commit()
        conn.close()
        self.view_transactions()

    def delete_transaction(self):
        selected_item = self.transactions_list.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return
        transaction_id = self.transactions_list.item(selected_item)['values'][0]
        conn = sqlite3.connect('grpparticipation.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM group_participation WHERE id=?', (transaction_id,))
        conn.commit()
        conn.close()
        self.view_transactions()

    def view_transactions(self):
        for item in self.transactions_list.get_children():
            self.transactions_list.delete(item)
        conn = sqlite3.connect('grpparticipation.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM group_participation')
        transactions = cursor.fetchall()
        for transaction in transactions:
            self.transactions_list.insert("", "end", values=transaction)
        conn.close()

    def open_family_details(self):
        self.root.destroy()
        subprocess.run(["python", "familydetails.py"])

    def go_back(self):
        self.root.destroy()
        subprocess.run(["python", "financialdetails.py"])

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = SHGApp(root)
    root.mainloop()
