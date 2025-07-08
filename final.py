from tkinter import *
import tkinter as tk
import subprocess  # Import subprocess to open external files
import sqlite3
from tkinter import messagebox
from reportlab.pdfgen import canvas

# Database Connection
conn = sqlite3.connect("shg.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, username TEXT, password TEXT);
CREATE TABLE IF NOT EXISTS contributions (id INTEGER PRIMARY KEY, donor_name TEXT, amount REAL, details TEXT);
CREATE TABLE IF NOT EXISTS bank_info (id INTEGER PRIMARY KEY, bank_name TEXT, account_number TEXT);
""")
conn.commit()

cursor.execute("INSERT OR REPLACE INTO users (id, name, email, username, password) VALUES (1, 'Self Help Group', 'shg@example.com', 'selfhelpgroup', 'selfhelp123')")
conn.commit()


class Employee:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x800+0+0")
        self.root.title("Self Help Group (SHG) Application")
        self.login_screen()  # Show login screen on startup

    def login_screen(self):
        """Display the login screen"""
        self.clear_frame()
        frame = tk.Frame(self.root, bg="#3498db", padx=20, pady=20)
        frame.pack(pady=100)

        tk.Label(frame, text="Login", font=("Arial", 20, "bold"), fg="white", bg="#3498db").pack()
        tk.Label(frame, text="Username", bg="#3498db", fg="white").pack()
        self.username_entry = tk.Entry(frame)
        self.username_entry.pack()
        tk.Label(frame, text="Password", bg="#3498db", fg="white").pack()
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.pack()
        tk.Button(frame, text="Login", command=self.check_login, bg="#2ecc71", fg="white").pack(pady=10)

    def check_login(self):
        """Verify user credentials"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        if cursor.fetchone():
            self.main_menu()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def main_menu(self):
        """Display the main menu after login"""
        self.clear_frame()
        tk.Label(self.root, text="Self Help Group Application", font=("Arial", 20, "bold"), bg="#f4f4f4").pack(pady=10)

        menu_frame = tk.Frame(self.root, bg="white")
        menu_frame.pack(pady=20)

        buttons = [
            ("Manage Members", self.manage_members, "#e67e22"),
            ("Manage Contributions", self.manage_contributions, "#e74c3c"),
            ("Manage Bank Info", self.manage_bank_info, "#9b59b6"),
        ]

        for text, command, color in buttons:
            tk.Button(menu_frame, text=text, font=("Arial", 14), bg=color, fg="white", width=25, height=1, command=command).pack(pady=5)

    def manage_members(self):
        """Open basicdetails.py when clicking on Manage Members"""
        subprocess.Popen(["python", "basicdetails.py"])  # Opens the external file

    def manage_contributions(self):
        """Open the Contributions Management Form"""
      #  self.open_form("contributions", ["donor_name", "amount", "details"], "Manage Contributions", generate_receipt=True)
        subprocess.Popen(["python", "Managedonar.py"])  # Opens the external file

    def manage_bank_info(self):
        """Open the Bank Info Management Form"""
        subprocess.Popen(["python", "BankInfo.py"])  # Opens the external file

    def clear_frame(self):
        """Clear the screen before switching views"""
        for widget in self.root.winfo_children():
            widget.destroy()


# Main Function
if __name__ == "__main__":
    root = Tk()
    obj = Employee(root)
    root.mainloop()
