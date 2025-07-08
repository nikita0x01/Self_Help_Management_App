import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from time import strftime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random

def generate_receipt_number():
    return f"REC-{random.randint(1000, 9999)}"

def update_amount_field(*args):
    if donation_type_var.get() == "Monetary":
        entries["7. Amount Donated"].config(state="normal")
    else:
        entries["7. Amount Donated"].delete(0, tk.END)
        entries["7. Amount Donated"].config(state="disabled")

def select_time():
    current_time = strftime('%H:%M:%S')
    entries["11. Donation Time"].delete(0, tk.END)
    entries["11. Donation Time"].insert(0, current_time)

def clear_fields():
    for field in entries:
        widget = entries[field]
        if isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)
        elif isinstance(widget, ttk.Combobox):
            widget.set("")
        elif isinstance(widget, DateEntry):
            widget.set_date("")
    
    entries["13. Receipt Number"].config(state="normal")
    entries["13. Receipt Number"].delete(0, tk.END)
    entries["13. Receipt Number"].insert(0, generate_receipt_number())
    entries["13. Receipt Number"].config(state="readonly")

def generate_pdf():
    data = {}
    for field in fields:
        widget = entries[field]
        if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Combobox):
            data[field] = widget.get()
        elif isinstance(widget, DateEntry):
            data[field] = widget.get_date()
        else:
            data[field] = ""
    
    if not data['1. Full Name'] or not data['3. Contact Number'] or not data['4. Email ID'] or not data['6. Type of Donation']:
        messagebox.showerror("Error", "Please fill all required fields.")
        return
    
    pdf_filename = f"donation_receipt_{data['1. Full Name'].replace(' ', '_')}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, "Donation Receipt")
    
    y = 780
    for key, value in data.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 20
    
    c.save()
    messagebox.showinfo("Success", f"PDF generated: {pdf_filename}")

app = tk.Tk()
app.title("Donation Form")
app.configure(bg='light pink')

fields = [
    "1. Full Name", "2. Organization Name", "3. Contact Number", "4. Email ID", "5. Address",
    "6. Type of Donation", "7. Amount Donated", "8. Mode of Payment", "9. Transaction ID/Reference Number",
    "10. Donation Date", "11. Donation Time", "12. Purpose of Donation", "13. Receipt Number", "14. Tax Exemption Certificate Issued?",
    "15. Consent for Public Recognition", "16. Preferred Communication Mode", "17. Recurring Donor?", "18. Donor Category",
    "19. Special Requests/Comments"
]

entries = {}
main_frame = tk.Frame(app, bg='light pink')
main_frame.pack(padx=20, pady=20)

for idx, field in enumerate(fields):
    tk.Label(main_frame, text=field, bg='light pink').grid(row=idx, column=0, sticky='w', padx=10, pady=5)
    
    if field == "6. Type of Donation":
        donation_type_var = tk.StringVar()
        entry = ttk.Combobox(main_frame, textvariable=donation_type_var, values=["Monetary", "Goods", "Services"], state="readonly")
        donation_type_var.trace_add("write", update_amount_field)
    elif field == "8. Mode of Payment":
        entry = ttk.Combobox(main_frame, values=["UPI", "Bank Transfer", "Cash", "Cheque", "Online Payment Gateway"], state="readonly")
    elif field == "12. Purpose of Donation":
        entry = ttk.Combobox(main_frame, values=["General Fund", "Women Empowerment", "Education", "Healthcare", "Environmental Protection", "Disaster Relief"], state="readonly")
    elif field in ["14. Tax Exemption Certificate Issued?", "15. Consent for Public Recognition", "17. Recurring Donor?", "16. Preferred Communication Mode", "18. Donor Category"]:
        values_map = {
            "14. Tax Exemption Certificate Issued?": ["Yes", "No"],
            "15. Consent for Public Recognition": ["Yes", "No"],
            "16. Preferred Communication Mode": ["Email", "SMS", "WhatsApp"],
            "17. Recurring Donor?": ["One-time", "Monthly", "Annual"],
            "18. Donor Category": ["Individual", "Corporate", "NGO", "Government Agency"]
        }
        entry = ttk.Combobox(main_frame, values=values_map[field], state="readonly")
    elif field == "10. Donation Date":
        entry = DateEntry(main_frame, selectmode='day', year=2025, month=3, day=27, width=12)
    elif field == "11. Donation Time":
        entry = tk.Entry(main_frame, width=40)
        entry.insert(0, strftime('%H:%M:%S'))
    elif field == "13. Receipt Number":
        entry = tk.Entry(main_frame, width=40)
        entry.insert(0, generate_receipt_number())
        entry.config(state="readonly")
    elif field == "7. Amount Donated":
        entry = tk.Entry(main_frame, width=40, state="disabled")
    else:
        entry = tk.Entry(main_frame, width=40)
    
    entry.grid(row=idx, column=1, padx=10, pady=5)
    entries[field] = entry

generate_btn = tk.Button(app, text="Generate PDF", command=generate_pdf, bg="#ff69b4", fg="white")
generate_btn.pack(pady=10)

clear_btn = tk.Button(app, text="Clear Fields", command=clear_fields, bg="#ff4500", fg="white")
clear_btn.pack(pady=10)

app.mainloop()
