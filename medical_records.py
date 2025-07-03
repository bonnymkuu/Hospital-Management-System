# medical_records.py
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class MedicalRecords:
    def __init__(self, master_frame, conn, c): # Accept master_frame, conn, and c
        self.master_frame = master_frame
        self.conn = conn  # Use the shared connection
        self.c = c        # Use the shared cursor

        # Clear any existing widgets in the master_frame (content_frame)
        for widget in self.master_frame.winfo_children():
            widget.destroy()

        # Main Frame within the master_frame
        self.main_frame = Frame(self.master_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Left Frame (Form)
        self.left_frame = Frame(self.main_frame, padx=10, pady=10, bg='#eaf7f7', relief=GROOVE, bd=2)
        self.left_frame.pack(side=LEFT, fill=Y, ipadx=10, ipady=10)

        # Right Frame (List)
        self.right_frame = Frame(self.main_frame, padx=10, pady=10, bg='#e0f0f0', relief=GROOVE, bd=2)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5,0))

        # Form Elements
        ttk.Label(self.left_frame, text="Medical Records Management",
                  font=('Arial', 18, 'bold'), background='#eaf7f7', foreground='#2c3e50').grid(row=0, columnspan=2, pady=15)

        self.inputs = {}

        # Patient selection
        ttk.Label(self.left_frame, text="Patient:", background='#eaf7f7').grid(row=1, column=0, sticky=W, pady=5, padx=5)
        self.inputs['patient_var'] = StringVar()
        self.inputs['patient_combo'] = ttk.Combobox(self.left_frame, textvariable=self.inputs['patient_var'], width=27, state="readonly")
        self.inputs['patient_combo'].grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.patient_map = {}
        self.load_patients()

        # Doctor selection
        ttk.Label(self.left_frame, text="Doctor:", background='#eaf7f7').grid(row=2, column=0, sticky=W, pady=5, padx=5)
        self.inputs['doctor_var'] = StringVar()
        self.inputs['doctor_combo'] = ttk.Combobox(self.left_frame, textvariable=self.inputs['doctor_var'], width=27, state="readonly")
        self.inputs['doctor_combo'].grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        self.doctor_map = {}
        self.load_doctors()

        # Date
        ttk.Label(self.left_frame, text="Record Date (YYYY-MM-DD):", background='#eaf7f7').grid(row=3, column=0, sticky=W, pady=5, padx=5)
        self.inputs['date_entry'] = ttk.Entry(self.left_frame, width=30)
        self.inputs['date_entry'].grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        self.inputs['date_entry'].insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Diagnosis
        ttk.Label(self.left_frame, text="Diagnosis:", background='#eaf7f7').grid(row=4, column=0, sticky=NW, pady=5, padx=5)
        self.inputs['diagnosis_text'] = Text(self.left_frame, width=30, height=5, wrap=WORD)
        self.inputs['diagnosis_text'].grid(row=4, column=1, pady=5, padx=5, sticky="ew")

        # Treatment
        ttk.Label(self.left_frame, text="Treatment:", background='#eaf7f7').grid(row=5, column=0, sticky=NW, pady=5, padx=5)
        self.inputs['treatment_text'] = Text(self.left_frame, width=30, height=5, wrap=WORD)
        self.inputs['treatment_text'].grid(row=5, column=1, pady=5, padx=5, sticky="ew")

        # Prescription
        ttk.Label(self.left_frame, text="Prescription:", background='#eaf7f7').grid(row=6, column=0, sticky=NW, pady=5, padx=5)
        self.inputs['prescription_text'] = Text(self.left_frame, width=30, height=5, wrap=WORD)
        self.inputs['prescription_text'].grid(row=6, column=1, pady=5, padx=5, sticky="ew")

        # Notes
        ttk.Label(self.left_frame, text="Notes:", background='#eaf7f7').grid(row=7, column=0, sticky=NW, pady=5, padx=5)
        self.inputs['notes_text'] = Text(self.left_frame, width=30, height=5, wrap=WORD)
        self.inputs['notes_text'].grid(row=7, column=1, pady=5, padx=5, sticky="ew")

        # Configure left_frame columns to expand
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=3)


        # Buttons
        ttk.Button(self.left_frame, text="Add Record", command=self.add_record).grid(row=8, column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Update Record", command=self.update_record).grid(row=8, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Clear Form", command=self.clear_form).grid(row=9, column=0, pady=5, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Delete Record", command=self.delete_record, style='Danger.TButton').grid(row=9, column=1, pady=5, padx=5, sticky="ew")

        # Search
        ttk.Label(self.left_frame, text="Search Records:", background='#eaf7f7').grid(row=10, column=0, sticky=W, pady=10, padx=5)
        self.inputs['search_entry'] = ttk.Entry(self.left_frame, width=30)
        self.inputs['search_entry'].grid(row=10, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Search", command=self.search_records).grid(row=11, columnspan=2, pady=5, padx=5, sticky="ew")


        # Records List (Treeview)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#4a69bd', foreground='white')
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

        self.tree = ttk.Treeview(self.right_frame, columns=("ID", "Patient", "Doctor", "Date", "Diagnosis"), show="headings")

        self.tree.heading("ID", text="ID", anchor=CENTER)
        self.tree.heading("Patient", text="Patient", anchor=W)
        self.tree.heading("Doctor", text="Doctor", anchor=W)
        self.tree.heading("Date", text="Date", anchor=CENTER)
        self.tree.heading("Diagnosis", text="Diagnosis", anchor=W)

        self.tree.column("ID", width=50, stretch=NO, anchor=CENTER)
        self.tree.column("Patient", width=150, stretch=YES)
        self.tree.column("Doctor", width=150, stretch=YES)
        self.tree.column("Date", width=100, stretch=NO, anchor=CENTER)
        self.tree.column("Diagnosis", width=250, stretch=YES)

        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill=BOTH, expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_record_select)

        self.current_record_id = None

        self.load_records()

    def load_patients(self):
        try:
            self.c.execute("SELECT patient_id, name FROM patients ORDER BY name ASC")
            patients = self.c.fetchall()
            self.patient_map = {f"{pid} - {name}": pid for pid, name in patients}
            self.inputs['patient_combo']['values'] = list(self.patient_map.keys())
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading patients: {e}\nEnsure 'patients' table exists.")
            print(f"Error loading patients: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading patients: {e}")
            print(f"An unexpected error occurred while loading patients: {e}")

    def load_doctors(self):
        try:
            self.c.execute("SELECT doctor_id, name FROM doctors ORDER BY name ASC")
            doctors = self.c.fetchall()
            self.doctor_map = {f"{did} - {name}": did for did, name in doctors}
            self.inputs['doctor_combo']['values'] = list(self.doctor_map.keys())
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading doctors: {e}\nEnsure 'doctors' table exists.")
            print(f"Error loading doctors: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading doctors: {e}")
            print(f"An unexpected error occurred while loading doctors: {e}")

    def load_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute('''SELECT mr.record_id, p.name, d.name, mr.record_date, mr.diagnosis
                           FROM medical_records mr
                           JOIN patients p ON mr.patient_id = p.patient_id
                           JOIN doctors d ON mr.doctor_id = d.doctor_id
                           ORDER BY mr.record_date DESC''')
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                self.tree.insert("", END, values=("", "", "No medical records found.", "", ""))
                self.tree.item(self.tree.get_children()[0], tags=('no_data',))
                self.tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading medical records: {e}\nEnsure 'medical_records', 'patients', and 'doctors' tables exist with correct columns.")
            print(f"Error loading medical records: {e}")
            self.tree.insert("", END, values=("", "", "Error loading medical records.", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading medical records: {e}")
            print(f"An unexpected error occurred while loading medical records: {e}")
            self.tree.insert("", END, values=("", "", "Unexpected error loading medical records.", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))

    def on_record_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.current_record_id = values[0]

            self.c.execute('''SELECT mr.patient_id, p.name, mr.doctor_id, d.name,
                           mr.record_date, mr.diagnosis, mr.treatment, mr.prescription, mr.notes
                           FROM medical_records mr
                           JOIN patients p ON mr.patient_id = p.patient_id
                           JOIN doctors d ON mr.doctor_id = d.doctor_id
                           WHERE mr.record_id=?''', (self.current_record_id,))
            record_data = self.c.fetchone()

            if record_data:
                self.clear_form()

                patient_display_str = f"{record_data[0]} - {record_data[1]}"
                if patient_display_str in self.patient_map:
                    self.inputs['patient_var'].set(patient_display_str)
                else:
                    self.inputs['patient_var'].set("")

                doctor_display_str = f"{record_data[2]} - {record_data[3]}"
                if doctor_display_str in self.doctor_map:
                    self.inputs['doctor_var'].set(doctor_display_str)
                else:
                    self.inputs['doctor_var'].set("")

                self.inputs['date_entry'].insert(0, record_data[4] if record_data[4] else "")
                self.inputs['diagnosis_text'].insert(END, record_data[5] if record_data[5] else "")
                self.inputs['treatment_text'].insert(END, record_data[6] if record_data[6] else "")
                self.inputs['prescription_text'].insert(END, record_data[7] if record_data[7] else "")
                self.inputs['notes_text'].insert(END, record_data[8] if record_data[8] else "")
            else:
                messagebox.showwarning("Record Not Found", "Selected record data could not be retrieved.")
                self.clear_form()

    def add_record(self):
        patient_full_str = self.inputs['patient_var'].get()
        doctor_full_str = self.inputs['doctor_var'].get()

        patient_id = self.patient_map.get(patient_full_str)
        doctor_id = self.doctor_map.get(doctor_full_str)

        if patient_id is None or doctor_id is None:
            messagebox.showerror("Input Error", "Please select both a valid patient and doctor.")
            return

        record_date = self.inputs['date_entry'].get().strip()
        diagnosis = self.inputs['diagnosis_text'].get(1.0, END).strip()
        treatment = self.inputs['treatment_text'].get(1.0, END).strip()
        prescription = self.inputs['prescription_text'].get(1.0, END).strip()
        notes = self.inputs['notes_text'].get(1.0, END).strip()

        if not record_date or not diagnosis:
            messagebox.showerror("Validation Error", "Record Date and Diagnosis are required fields.")
            return

        try:
            datetime.strptime(record_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return

        if len(diagnosis) > 1000:
            messagebox.showerror("Validation Error", "Diagnosis text is too long (max 1000 characters).")
            return

        try:
            self.c.execute('''INSERT INTO medical_records
                          (patient_id, doctor_id, record_date, diagnosis, treatment, prescription, notes)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (patient_id, doctor_id, record_date, diagnosis,
                           treatment, prescription, notes))
            self.conn.commit()
            messagebox.showinfo("Success", "Medical record added successfully.")
            self.load_records()
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add record: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def update_record(self):
        if not hasattr(self, 'current_record_id') or self.current_record_id is None:
            messagebox.showerror("Update Error", "Please select a record to update.")
            return

        patient_full_str = self.inputs['patient_var'].get()
        doctor_full_str = self.inputs['doctor_var'].get()

        patient_id = self.patient_map.get(patient_full_str)
        doctor_id = self.doctor_map.get(doctor_full_str)

        if patient_id is None or doctor_id is None:
            messagebox.showerror("Input Error", "Please select both a valid patient and doctor.")
            return

        record_date = self.inputs['date_entry'].get().strip()
        diagnosis = self.inputs['diagnosis_text'].get(1.0, END).strip()
        treatment = self.inputs['treatment_text'].get(1.0, END).strip()
        prescription = self.inputs['prescription_text'].get(1.0, END).strip()
        notes = self.inputs['notes_text'].get(1.0, END).strip()

        if not record_date or not diagnosis:
            messagebox.showerror("Validation Error", "Record Date and Diagnosis are required fields.")
            return

        try:
            datetime.strptime(record_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return

        if len(diagnosis) > 1000:
            messagebox.showerror("Validation Error", "Diagnosis text is too long (max 1000 characters).")
            return

        if not messagebox.askyesno("Confirm Update", "Are you sure you want to update this record?"):
            return

        try:
            self.c.execute('''UPDATE medical_records SET
                        patient_id=?, doctor_id=?, record_date=?,
                        diagnosis=?, treatment=?, prescription=?, notes=?
                        WHERE record_id=?''',
                        (patient_id, doctor_id, record_date,
                        diagnosis, treatment, prescription, notes,
                        self.current_record_id))

            if self.c.rowcount == 0:
                messagebox.showwarning("Update Warning", "No record was updated. The record might have been deleted by another user or does not exist.")
            else:
                self.conn.commit()
                messagebox.showinfo("Update Success", "Medical record updated successfully.")
                self.load_records()
                self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update record: {str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def delete_record(self):
        if not hasattr(self, 'current_record_id') or self.current_record_id is None:
            messagebox.showerror("Error", "No record selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this medical record? This action cannot be undone and will also delete related records due to cascading deletes."):
            try:
                self.c.execute("DELETE FROM medical_records WHERE record_id=?", (self.current_record_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Medical record deleted successfully.")
                self.load_records()
                self.clear_form()
                self.current_record_id = None
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}")

    def search_records(self):
        search_term = self.inputs['search_entry'].get().strip()
        if not search_term:
            self.load_records()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute('''SELECT mr.record_id, p.name, d.name, mr.record_date, mr.diagnosis
                           FROM medical_records mr
                           JOIN patients p ON mr.patient_id = p.patient_id
                           JOIN doctors d ON mr.doctor_id = d.doctor_id
                           WHERE p.name LIKE ? OR d.name LIKE ? OR mr.diagnosis LIKE ? OR mr.treatment LIKE ?
                           ORDER BY mr.record_date DESC''',
                          (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                messagebox.showinfo("No Results", "No medical records found matching your search criteria.")
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error searching records: {e}")
            print(f"Error searching records: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during search: {str(e)}")
            print(f"An unexpected error occurred during search: {str(e)}")

    def clear_form(self):
        for key in self.inputs:
            widget = self.inputs[key]
            if isinstance(widget, ttk.Entry):
                widget.delete(0, END)
            elif isinstance(widget, Text):
                widget.delete(1.0, END)
            elif isinstance(widget, ttk.Combobox):
                widget.set("") # Clear combobox selection

        self.inputs['date_entry'].insert(0, datetime.now().strftime("%Y-%m-%d")) # Reset date
        self.inputs['search_entry'].delete(0, END)

        if self.tree.focus():
            self.tree.selection_remove(self.tree.focus())

        self.current_record_id = None