from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

class BillingSystem:
    def __init__(self, master_frame, conn, c):
        self.master_frame = master_frame
        self.conn = conn
        self.c = c

        # Clear any existing widgets in the master_frame (content_frame)
        for widget in self.master_frame.winfo_children():
            widget.destroy()

        # Main Frame within the master_frame
        self.main_frame = Frame(self.master_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Left Frame (Form)
        self.left_frame = Frame(self.main_frame, padx=10, pady=10, bg='#eaf7f7', relief=GROOVE, bd=2)
        self.left_frame.pack(side=LEFT, fill=BOTH, ipadx=10, ipady=10)

        # Right Frame (List)
        self.right_frame = Frame(self.main_frame, padx=10, pady=10, bg='#e0f0f0', relief=GROOVE, bd=2)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5,0))

        # Form Elements
        ttk.Label(self.left_frame, text="Billing System",
                  font=('Arial', 18, 'bold'), background='#eaf7f7', foreground='#2c3e50').grid(row=0, columnspan=2, pady=15)

        # Patient selection
        ttk.Label(self.left_frame, text="Patient:", background='#eaf7f7').grid(row=1, column=0, sticky=W, pady=5, padx=5)
        self.patient_var = StringVar()
        self.patient_combo = ttk.Combobox(self.left_frame, textvariable=self.patient_var, width=27, state="readonly")
        self.patient_combo.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.patient_map = {}
        self.load_patients()

        # Service Description
        ttk.Label(self.left_frame, text="Service Description:", background='#eaf7f7').grid(row=2, column=0, sticky=W, pady=5, padx=5)
        self.service_entry = ttk.Entry(self.left_frame, width=30)
        self.service_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        # Amount
        ttk.Label(self.left_frame, text="Amount:", background='#eaf7f7').grid(row=3, column=0, sticky=W, pady=5, padx=5)
        self.amount_entry = ttk.Entry(self.left_frame, width=30)
        self.amount_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

        # Date Issued
        ttk.Label(self.left_frame, text="Date Issued (YYYY-MM-DD):", background='#eaf7f7').grid(row=4, column=0, sticky=W, pady=5, padx=5)
        self.date_issued_entry = ttk.Entry(self.left_frame, width=30)
        self.date_issued_entry.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
        self.date_issued_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Due Date (default to 30 days from now)
        ttk.Label(self.left_frame, text="Due Date (YYYY-MM-DD):", background='#eaf7f7').grid(row=5, column=0, sticky=W, pady=5, padx=5)
        self.due_date_entry = ttk.Entry(self.left_frame, width=30)
        self.due_date_entry.grid(row=5, column=1, pady=5, padx=5, sticky="ew")
        default_due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.due_date_entry.insert(0, default_due_date)

        # Status
        ttk.Label(self.left_frame, text="Status:", background='#eaf7f7').grid(row=6, column=0, sticky=W, pady=5, padx=5)
        self.status_var = StringVar()
        self.status_combo = ttk.Combobox(self.left_frame, textvariable=self.status_var,
                                        values=["Pending", "Paid", "Partially Paid"], width=27, state="readonly")
        self.status_combo.grid(row=6, column=1, pady=5, padx=5, sticky="ew")
        self.status_combo.current(0)

        # Configure left_frame columns to expand
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=3)

        # Buttons
        ttk.Button(self.left_frame, text="Add Bill", command=self.add_bill).grid(row=7, column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Update Bill", command=self.update_bill).grid(row=7, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Clear Form", command=self.clear_form).grid(row=8, column=0, pady=5, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Delete Bill", command=self.delete_bill, style='Danger.TButton').grid(row=8, column=1, pady=5, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Mark as Paid", command=self.mark_as_paid).grid(row=9, columnspan=2, pady=10, padx=5, sticky="ew")

        # Search
        ttk.Label(self.left_frame, text="Search Bills:", background='#eaf7f7').grid(row=10, column=0, sticky=W, pady=10, padx=5)
        self.search_entry = ttk.Entry(self.left_frame, width=30)
        self.search_entry.grid(row=10, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Search", command=self.search_bills).grid(row=11, columnspan=2, pady=5, padx=5, sticky="ew")

        # Bills List (Treeview)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#4a69bd', foreground='white')
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

        self.tree = ttk.Treeview(self.right_frame, columns=("ID", "Patient", "Amount", "Issued", "Due", "Status"), show="headings")

        # Define headings
        self.tree.heading("ID", text="ID", anchor=CENTER)
        self.tree.heading("Patient", text="Patient", anchor=W)
        self.tree.heading("Amount", text="Amount", anchor=CENTER)
        self.tree.heading("Issued", text="Date Issued", anchor=CENTER)
        self.tree.heading("Due", text="Due Date", anchor=CENTER)
        self.tree.heading("Status", text="Status", anchor=CENTER)

        # Set column widths
        self.tree.column("ID", width=50, stretch=NO, anchor=CENTER)
        self.tree.column("Patient", width=150, stretch=YES)
        self.tree.column("Amount", width=100, stretch=NO, anchor=CENTER)
        self.tree.column("Issued", width=100, stretch=NO, anchor=CENTER)
        self.tree.column("Due", width=100, stretch=NO, anchor=CENTER)
        self.tree.column("Status", width=100, stretch=NO, anchor=CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill=BOTH, expand=True)

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_bill_select)

        # Load initial data
        self.current_bill_id = None
        self.load_bills()

    def load_patients(self):
        try:
            self.c.execute("SELECT patient_id, name FROM patients ORDER BY name ASC")
            patients = self.c.fetchall()
            self.patient_map = {f"{pid} - {name}": pid for pid, name in patients}
            self.patient_combo['values'] = list(self.patient_map.keys())
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading patients: {e}\nEnsure 'patients' table exists.")
            print(f"Error loading patients: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading patients: {e}")
            print(f"An unexpected error occurred while loading patients: {e}")

    def load_bills(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Fetch data from database
            self.c.execute('''SELECT b.bill_id, p.name, b.amount, b.bill_date, b.due_date, b.status
                           FROM billing b
                           JOIN patients p ON b.patient_id = p.patient_id
                           ORDER BY b.bill_date DESC''')
            rows = self.c.fetchall()

            # Insert data into treeview
            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                self.tree.insert("", END, values=("", "", "No bills found.", "", "", ""))
                self.tree.item(self.tree.get_children()[0], tags=('no_data',))
                self.tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading bills: {e}\nEnsure 'billing' and 'patients' tables exist with correct columns.")
            print(f"Error loading bills: {e}")
            self.tree.insert("", END, values=("", "", "Error loading bills.", "", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading bills: {e}")
            print(f"An unexpected error occurred while loading bills: {e}")
            self.tree.insert("", END, values=("", "", "Unexpected error loading bills.", "", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))

    def on_bill_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.current_bill_id = values[0]

            try:
                self.c.execute('''SELECT b.patient_id, p.name, b.amount, b.service_description,
                               b.bill_date, b.due_date, b.status
                               FROM billing b
                               JOIN patients p ON b.patient_id = p.patient_id
                               WHERE b.bill_id=?''', (self.current_bill_id,))
                bill_data = self.c.fetchone()

                if bill_data:
                    self.clear_form()

                    patient_display_str = f"{bill_data[0]} - {bill_data[1]}"
                    if patient_display_str in self.patient_map:
                        self.patient_var.set(patient_display_str)
                    else:
                        self.patient_var.set("")

                    self.service_entry.insert(0, bill_data[3] if bill_data[3] else "")
                    self.amount_entry.insert(0, bill_data[2] if bill_data[2] else "")
                    self.date_issued_entry.insert(0, bill_data[4] if bill_data[4] else "")
                    self.due_date_entry.insert(0, bill_data[5] if bill_data[5] else "")
                    self.status_var.set(bill_data[6] if bill_data[6] else "Pending")

                else:
                    messagebox.showwarning("Bill Not Found", "Selected bill data could not be retrieved.")
                    self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to retrieve bill details: {str(e)}")
                self.clear_form()

    def add_bill(self):
        patient_full_str = self.patient_var.get()
        patient_id = self.patient_map.get(patient_full_str)

        if patient_id is None:
            messagebox.showerror("Input Error", "Please select a valid patient.")
            return

        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                messagebox.showerror("Validation Error", "Amount must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid numeric amount.")
            return

        service = self.service_entry.get().strip()
        bill_date = self.date_issued_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        status = self.status_var.get()

        if not service:
            messagebox.showerror("Validation Error", "Service description is required.")
            return
        if not bill_date:
            messagebox.showerror("Validation Error", "Bill Date is required.")
            return
        try:
            datetime.strptime(bill_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Bill Date must be in YYYY-MM-DD format.")
            return
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Due Date must be in YYYY-MM-DD format if provided.")
                return

        try:
            self.c.execute('''INSERT INTO billing
                          (patient_id, amount, bill_date, due_date, status, service_description)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                          (patient_id, amount, bill_date, due_date,
                           status, service))
            self.conn.commit()
            messagebox.showinfo("Success", "Bill added successfully.")
            self.load_bills()
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add bill: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def update_bill(self):
        if not hasattr(self, 'current_bill_id') or self.current_bill_id is None:
            messagebox.showerror("Update Error", "Please select a bill to update.")
            return

        patient_full_str = self.patient_var.get()
        patient_id = self.patient_map.get(patient_full_str)

        if patient_id is None:
            messagebox.showerror("Input Error", "Please select a valid patient.")
            return

        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                messagebox.showerror("Validation Error", "Amount must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid numeric amount.")
            return

        service = self.service_entry.get().strip()
        bill_date = self.date_issued_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        status = self.status_var.get()

        if not service:
            messagebox.showerror("Validation Error", "Service description is required.")
            return
        if not bill_date:
            messagebox.showerror("Validation Error", "Bill Date is required.")
            return
        try:
            datetime.strptime(bill_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Bill Date must be in YYYY-MM-DD format.")
            return
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Due Date must be in YYYY-MM-DD format if provided.")
                return

        if not messagebox.askyesno("Confirm Update", "Are you sure you want to update this bill?"):
            return

        try:
            self.c.execute('''UPDATE billing SET
                          patient_id=?, amount=?, bill_date=?, due_date=?, status=?, service_description=?
                          WHERE bill_id=?''',
                          (patient_id, amount, bill_date, due_date,
                           status, service, self.current_bill_id))

            if self.c.rowcount == 0:
                messagebox.showwarning("Update Warning", "No bill was updated. The bill might have been deleted by another user or does not exist.")
            else:
                self.conn.commit()
                messagebox.showinfo("Update Success", "Bill updated successfully.")
                self.load_bills()
                self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update bill: {str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def delete_bill(self):
        if not hasattr(self, 'current_bill_id') or self.current_bill_id is None:
            messagebox.showerror("Error", "No bill selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this bill? This action cannot be undone."):
            try:
                self.c.execute("DELETE FROM billing WHERE bill_id=?", (self.current_bill_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Bill deleted successfully.")
                self.load_bills()
                self.clear_form()
                self.current_bill_id = None
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete bill: {str(e)}")

    def mark_as_paid(self):
        if not hasattr(self, 'current_bill_id') or self.current_bill_id is None:
            messagebox.showerror("Error", "No bill selected.")
            return

        try:
            self.c.execute("UPDATE billing SET status='Paid' WHERE bill_id=?", (self.current_bill_id,))
            if self.c.rowcount == 0:
                messagebox.showwarning("Update Warning", "No bill was updated. The bill might have been deleted by another user or does not exist.")
            else:
                self.conn.commit()
                messagebox.showinfo("Success", "Bill marked as paid.")
                self.load_bills()
                if hasattr(self, 'current_bill_id') and self.current_bill_id == self.tree.item(self.tree.focus())['values'][0]:
                    self.status_var.set("Paid")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update bill status: {str(e)}")

    def search_bills(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_bills()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute('''SELECT b.bill_id, p.name, b.amount, b.bill_date, b.due_date, b.status
                           FROM billing b
                           JOIN patients p ON b.patient_id = p.patient_id
                           WHERE p.name LIKE ? OR b.service_description LIKE ? OR b.status LIKE ?''',
                          (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                messagebox.showinfo("No Results", "No bills found matching your search criteria.")
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error searching bills: {e}")
            print(f"Error searching bills: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during search: {str(e)}")
            print(f"An unexpected error occurred during search: {str(e)}")

    def clear_form(self):
        self.patient_var.set("")
        self.service_entry.delete(0, END)
        self.amount_entry.delete(0, END)
        self.date_issued_entry.delete(0, END)
        self.date_issued_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.due_date_entry.delete(0, END)
        default_due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.due_date_entry.insert(0, default_due_date)
        self.status_combo.set("Pending")

        if self.tree.focus():
            self.tree.selection_remove(self.tree.focus())

        self.current_bill_id = None