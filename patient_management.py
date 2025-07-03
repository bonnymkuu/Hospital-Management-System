# patient_management.py
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class PatientManagement:
    def __init__(self, master_frame, conn, c): # Accept conn and c from main_menu
        self.master_frame = master_frame # This is the content_frame from main_menu
        self.conn = conn  # Use the connection passed from main_menu
        self.c = c        # Use the cursor passed from main_menu

        # Clear any existing widgets in the master_frame
        for widget in self.master_frame.winfo_children():
            widget.destroy()

        # Main Frame (this frame fills the master_frame passed from main_menu)
        self.main_frame = Frame(self.master_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Left Frame (Form)
        self.left_frame = Frame(self.main_frame, padx=10, pady=10, bg='#eaf7f7', relief=GROOVE, bd=2)
        self.left_frame.pack(side=LEFT, fill=Y, ipadx=10, ipady=10)

        # Right Frame (List)
        self.right_frame = Frame(self.main_frame, padx=10, pady=10, bg='#e0f0f0', relief=GROOVE, bd=2)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5,0))

        # Form Elements
        ttk.Label(self.left_frame, text="Patient Management", font=('Arial', 18, 'bold'), background='#eaf7f7', foreground='#2c3e50').grid(row=0, columnspan=2, pady=15)

        fields = [
            ("Name", "name"), ("Date of Birth (YYYY-MM-DD)", "date_of_birth"), ("Gender", "gender"),
            ("Address", "address"), ("Phone", "phone"), ("Email", "email")
        ]

        self.entries = {}
        for i, (label_text, key) in enumerate(fields, start=1):
            ttk.Label(self.left_frame, text=f"{label_text}:", background='#eaf7f7').grid(row=i, column=0, sticky=W, pady=5, padx=5)
            entry = ttk.Entry(self.left_frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.entries[key] = entry

        # Text widget for medical_history
        ttk.Label(self.left_frame, text="Medical History:", background='#eaf7f7').grid(row=7, column=0, sticky=NW, pady=5, padx=5)
        self.entries['medical_history'] = Text(self.left_frame, width=30, height=4, wrap=WORD)
        self.entries['medical_history'].grid(row=7, column=1, pady=5, padx=5, sticky="ew")

        # Configure left_frame columns to expand
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=3)

        # Buttons
        ttk.Button(self.left_frame, text="Add Patient", command=self.add_patient).grid(row=8, column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Update Patient", command=self.update_patient).grid(row=8, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Clear Form", command=self.clear_form).grid(row=9, column=0, pady=5, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Delete Patient", command=self.delete_patient, style='Danger.TButton').grid(row=9, column=1, pady=5, padx=5, sticky="ew")

        # Search
        ttk.Label(self.left_frame, text="Search Patient:", background='#eaf7f7').grid(row=10, column=0, sticky=W, pady=10, padx=5)
        self.search_entry = ttk.Entry(self.left_frame, width=30)
        self.search_entry.grid(row=10, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Search", command=self.search_patient).grid(row=11, columnspan=2, pady=5, padx=5, sticky="ew")

        # Patient List (Treeview)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#4a69bd', foreground='white')
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

        self.tree = ttk.Treeview(self.right_frame,
                                 columns=("ID", "Name", "Gender", "Phone", "DOB"),
                                 show="headings")

        self.tree.heading("ID", text="ID", anchor=CENTER)
        self.tree.heading("Name", text="Name", anchor=W)
        self.tree.heading("Gender", text="Gender", anchor=CENTER)
        self.tree.heading("Phone", text="Phone", anchor=W)
        self.tree.heading("DOB", text="D.O.B", anchor=CENTER)

        self.tree.column("ID", width=50, stretch=NO, anchor=CENTER)
        self.tree.column("Name", width=150, stretch=YES)
        self.tree.column("Gender", width=80, stretch=NO, anchor=CENTER)
        self.tree.column("Phone", width=120, stretch=NO, anchor=W)
        self.tree.column("DOB", width=100, stretch=NO, anchor=CENTER)

        vsb = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(fill=BOTH, expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_patient_select)

        self.current_patient_id = None

        self.load_patients()

    def load_patients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute("SELECT patient_id, name, gender, phone, date_of_birth FROM patients ORDER BY name ASC")
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                self.tree.insert("", END, values=("", "", "No patients found.", "", ""))
                self.tree.item(self.tree.get_children()[0], tags=('no_data',))
                self.tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading patients: {e}\nEnsure 'patients' table exists with correct columns.")
            print(f"Error loading patients: {e}")
            self.tree.insert("", END, values=("", "", "Error loading patients.", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading patients: {e}")
            print(f"An unexpected error occurred while loading patients: {e}")
            self.tree.insert("", END, values=("", "", "Unexpected error loading patients.", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))

    def on_patient_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.current_patient_id = values[0]

            self.c.execute("SELECT patient_id, name, date_of_birth, gender, address, phone, email, admission_date, medical_history FROM patients WHERE patient_id=?", (self.current_patient_id,))
            patient_data = self.c.fetchone()

            if patient_data:
                self.clear_form()

                self.entries['name'].insert(0, patient_data[1] if patient_data[1] else "")
                self.entries['date_of_birth'].insert(0, patient_data[2] if patient_data[2] else "")
                self.entries['gender'].insert(0, patient_data[3] if patient_data[3] else "")
                self.entries['address'].insert(0, patient_data[4] if patient_data[4] else "")
                self.entries['phone'].insert(0, patient_data[5] if patient_data[5] else "")
                self.entries['email'].insert(0, patient_data[6] if patient_data[6] else "")
                self.entries['medical_history'].insert(END, patient_data[8] if patient_data[8] else "")
            else:
                messagebox.showwarning("Record Not Found", "Selected patient data could not be retrieved.")
                self.clear_form()

    def add_patient(self):
        data = {key: (self.entries[key].get().strip() if isinstance(self.entries[key], ttk.Entry) else self.entries[key].get(1.0, END).strip()) for key in self.entries}

        if not data['name'] or not data['phone']:
            messagebox.showerror("Validation Error", "Name and Phone are required fields.")
            return

        if not data['phone'].isdigit() or len(data['phone']) < 7:
             messagebox.showerror("Validation Error", "Please enter a valid phone number (digits only, at least 7).")
             return

        if data['date_of_birth']:
            try:
                datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Validation Error", "Date of Birth must be in YYYY-MM-DD format.")
                return

        try:
            self.c.execute('''INSERT INTO patients
                          (name, date_of_birth, gender, address, phone, email, admission_date, medical_history)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (data['name'], data['date_of_birth'], data['gender'], data['address'],
                           data['phone'], data['email'], datetime.now().strftime("%Y-%m-%d"), data['medical_history']))
            self.conn.commit()
            messagebox.showinfo("Success", "Patient added successfully.")
            self.load_patients()
            self.clear_form()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: patients.phone" in str(e):
                messagebox.showerror("Database Error", "A patient with this phone number already exists.")
            elif "UNIQUE constraint failed: patients.email" in str(e):
                messagebox.showerror("Database Error", "A patient with this email already exists.")
            else:
                messagebox.showerror("Database Error", f"Failed to add patient: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while adding patient: {str(e)}")

    def update_patient(self):
        if not hasattr(self, 'current_patient_id') or self.current_patient_id is None:
            messagebox.showerror("Error", "No patient selected for update.")
            return

        data = {key: (self.entries[key].get().strip() if isinstance(self.entries[key], ttk.Entry) else self.entries[key].get(1.0, END).strip()) for key in self.entries}

        if not data['name'] or not data['phone']:
            messagebox.showerror("Validation Error", "Name and Phone are required fields.")
            return

        if not data['phone'].isdigit() or len(data['phone']) < 7:
             messagebox.showerror("Validation Error", "Please enter a valid phone number (digits only, at least 7).")
             return

        if data['date_of_birth']:
            try:
                datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Validation Error", "Date of Birth must be in YYYY-MM-DD format.")
                return

        if not messagebox.askyesno("Confirm Update", "Are you sure you want to update this patient's record?"):
            return

        try:
            self.c.execute('''UPDATE patients SET
                          name=?, date_of_birth=?, gender=?, address=?, phone=?, email=?, medical_history=?
                          WHERE patient_id=?''',
                          (data['name'], data['date_of_birth'], data['gender'], data['address'],
                           data['phone'], data['email'], data['medical_history'], self.current_patient_id))
            if self.c.rowcount == 0:
                messagebox.showwarning("Update Warning", "No patient record was updated. The record might have been deleted by another user or does not exist.")
            else:
                self.conn.commit()
                messagebox.showinfo("Success", "Patient updated successfully.")
                self.load_patients()
                self.clear_form()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: patients.phone" in str(e):
                messagebox.showerror("Database Error", "A patient with this phone number already exists.")
            elif "UNIQUE constraint failed: patients.email" in str(e):
                messagebox.showerror("Database Error", "A patient with this email already exists.")
            else:
                messagebox.showerror("Database Error", f"Failed to update patient: {str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred while updating patient: {str(e)}")

    def delete_patient(self):
        if not hasattr(self, 'current_patient_id') or self.current_patient_id is None:
            messagebox.showerror("Error", "No patient selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this patient? This action cannot be undone and will also delete related appointments or records due to cascading deletes."):
            try:
                self.c.execute("DELETE FROM patients WHERE patient_id=?", (self.current_patient_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Patient deleted successfully.")
                self.load_patients()
                self.clear_form()
                self.current_patient_id = None
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete patient: {str(e)}")

    def search_patient(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_patients()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            patient_id_search = int(search_term) # Try to convert to int for ID search
        except ValueError:
            patient_id_search = -1 # A value that won't match any ID

        try:
            self.c.execute("SELECT patient_id, name, gender, phone, date_of_birth FROM patients WHERE name LIKE ? OR phone LIKE ? OR patient_id = ? ORDER BY name ASC",
                          (f"%{search_term}%", f"%{search_term}%", patient_id_search))
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                messagebox.showinfo("No Results", "No patients found matching your search criteria.")
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error searching patients: {e}")
            print(f"Error searching patients: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during search: {str(e)}")
            print(f"An unexpected error occurred during search: {str(e)}")

    def clear_form(self):
        for key in self.entries:
            if isinstance(self.entries[key], ttk.Entry):
                self.entries[key].delete(0, END)
            elif isinstance(self.entries[key], Text):
                self.entries[key].delete(1.0, END)

        self.search_entry.delete(0, END)

        if self.tree.focus():
            self.tree.selection_remove(self.tree.focus())

        self.current_patient_id = None