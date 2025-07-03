# update_appointments.py (Revised to fit your schema and main_menu structure)
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class UpdateAppointments: # Renamed from Application for clarity
    def __init__(self, master_frame, conn, c): # Accept master_frame, conn, and c
        self.master_frame = master_frame
        self.conn = conn  # Use the shared connection
        self.c = c        # Use the shared cursor

        # Clear any existing widgets in the master_frame (content_frame)
        for widget in self.master_frame.winfo_children():
            widget.destroy()

        # Main Frame within the master_frame
        self.main_frame = Frame(self.master_frame, bg='#f0f0f0')
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Top Frame for Search
        self.search_frame = ttk.LabelFrame(self.main_frame, text="Find Appointment", padding="10 10 10 10")
        self.search_frame.pack(fill=X, pady=10, padx=10)

        ttk.Label(self.search_frame, text="Search by Patient Name or Appointment ID:", font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.search_entry = ttk.Entry(self.search_frame, width=40, font=('Arial', 11))
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self.search_frame, text="Search", command=self.search_appointments).grid(row=0, column=2, padx=10, pady=5)

        self.search_frame.grid_columnconfigure(1, weight=1)


        # Frame for displaying search results (Treeview)
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Search Results", padding="10 10 10 10")
        self.results_frame.pack(fill=BOTH, expand=True, pady=10, padx=10)

        # Treeview for search results
        self.tree = ttk.Treeview(self.results_frame, columns=("ID", "Patient", "Doctor", "Date", "Time", "Status", "Reason"), show="headings")

        self.tree.heading("ID", text="ID", anchor=CENTER)
        self.tree.heading("Patient", text="Patient", anchor=W)
        self.tree.heading("Doctor", text="Doctor", anchor=W)
        self.tree.heading("Date", text="Date", anchor=CENTER)
        self.tree.heading("Time", text="Time", anchor=CENTER)
        self.tree.heading("Status", text="Status", anchor=CENTER)
        self.tree.heading("Reason", text="Reason", anchor=W)

        self.tree.column("ID", width=50, stretch=NO, anchor=CENTER)
        self.tree.column("Patient", width=120, stretch=YES)
        self.tree.column("Doctor", width=120, stretch=YES)
        self.tree.column("Date", width=90, stretch=NO, anchor=CENTER)
        self.tree.column("Time", width=60, stretch=NO, anchor=CENTER)
        self.tree.column("Status", width=90, stretch=NO, anchor=CENTER)
        self.tree.column("Reason", width=200, stretch=YES)

        vsb = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_appointment_select)


        # Frame for Update Form (initially hidden or empty)
        self.update_form_frame = ttk.LabelFrame(self.main_frame, text="Appointment Details", padding="10 10 10 10")
        self.update_form_frame.pack(fill=X, pady=10, padx=10) # Pack it, but keep it empty initially

        # Store entry/combobox widgets
        self.inputs = {}
        self.combo_vars = {}
        self.current_appointment_id = None # To store the ID of the selected appointment

        # Maps for patient/doctor IDs
        self.patient_map = {}
        self.doctor_map = {}
        self.load_patients_and_doctors() # Load these once

    def load_patients_and_doctors(self):
        """Loads patient and doctor data for comboboxes."""
        try:
            self.c.execute("SELECT patient_id, name FROM patients ORDER BY name ASC")
            patients = self.c.fetchall()
            self.patient_map = {f"{pid} - {name}": pid for pid, name in patients}

            self.c.execute("SELECT doctor_id, name, specialization FROM doctors ORDER BY name ASC")
            doctors = self.c.fetchall()
            self.doctor_map = {f"{did} - {name} ({spec})": did for did, name, spec in doctors}
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading patient/doctor data: {e}\nEnsure 'patients' and 'doctors' tables exist.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading patient/doctor data: {e}")

    def search_appointments(self):
        """Searches for appointments based on patient name or appointment ID."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Input Required", "Please enter a patient name or appointment ID to search.")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.clear_update_form() # Clear form when new search is initiated

        try:
            # Try to search by ID first if input is numeric
            try:
                appt_id = int(search_term)
                query = '''SELECT a.appointment_id, p.name, d.name,
                           strftime('%Y-%m-%d', a.scheduled_time), strftime('%H:%M', a.scheduled_time), a.status, a.reason
                           FROM appointments a
                           JOIN patients p ON a.patient_id = p.patient_id
                           JOIN doctors d ON a.doctor_id = d.doctor_id
                           WHERE a.appointment_id = ?
                           ORDER BY a.scheduled_time DESC'''
                self.c.execute(query, (appt_id,))
            except ValueError:
                # If not numeric, search by patient name
                query = '''SELECT a.appointment_id, p.name, d.name,
                           strftime('%Y-%m-%d', a.scheduled_time), strftime('%H:%M', a.scheduled_time), a.status, a.reason
                           FROM appointments a
                           JOIN patients p ON a.patient_id = p.patient_id
                           JOIN doctors d ON a.doctor_id = d.doctor_id
                           WHERE p.name LIKE ?
                           ORDER BY a.scheduled_time DESC'''
                self.c.execute(query, (f"%{search_term}%",))

            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                messagebox.showinfo("No Results", "No appointments found matching your search criteria.")

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error searching appointments: {e}\nEnsure tables exist and columns are correct.")
            print(f"Error searching appointments: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during search: {e}")
            print(f"An unexpected error occurred during search: {e}")

    def on_appointment_select(self, event):
        """Populates the update form when an appointment is selected in the Treeview."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.current_appointment_id = values[0] # The appointment_id

            # Fetch complete appointment data using JOINs to get original IDs
            self.c.execute('''SELECT a.patient_id, p.name, a.doctor_id, d.name, d.specialization,
                           a.scheduled_time, a.status, a.reason
                           FROM appointments a
                           JOIN patients p ON a.patient_id = p.patient_id
                           JOIN doctors d ON a.doctor_id = d.doctor_id
                           WHERE a.appointment_id=?''', (self.current_appointment_id,))
            appt_data = self.c.fetchone()

            if appt_data:
                self.populate_update_form(appt_data)
            else:
                messagebox.showwarning("Not Found", "Appointment data could not be retrieved.")
                self.clear_update_form()

    def populate_update_form(self, appt_data):
        """Creates and populates the update form with selected appointment data."""
        self.clear_update_form() # Clear existing widgets in the form frame

        # Re-create form elements dynamically
        form_elements = [
            ("Patient:", "patient_combo"),
            ("Doctor:", "doctor_combo"),
            ("Date (YYYY-MM-DD):", "date_entry"),
            ("Time (HH:MM):", "time_entry"),
            ("Purpose:", "purpose_entry"),
            ("Status:", "status_combo")
        ]

        for i, (label_text, widget_name) in enumerate(form_elements):
            ttk.Label(self.update_form_frame, text=label_text, font=('Arial', 11)).grid(row=i, column=0, sticky=W, pady=5, padx=5)

            if "combo" in widget_name:
                self.combo_vars[widget_name] = StringVar()
                combo = ttk.Combobox(self.update_form_frame, textvariable=self.combo_vars[widget_name],
                                     width=35, font=('Arial', 10))
                combo.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                self.inputs[widget_name] = combo
                if widget_name == "patient_combo":
                    combo['values'] = list(self.patient_map.keys())
                elif widget_name == "doctor_combo":
                    combo['values'] = list(self.doctor_map.keys())
                elif widget_name == "status_combo":
                    combo['values'] = ["Scheduled", "Completed", "Cancelled"]
            else:
                entry = ttk.Entry(self.update_form_frame, width=37, font=('Arial', 10))
                entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                self.inputs[widget_name] = entry

        # Fill the form with data
        # appt_data indices:
        # 0: a.patient_id, 1: p.name, 2: a.doctor_id, 3: d.name, 4: d.specialization,
        # 5: a.scheduled_time, 6: a.status, 7: a.reason

        patient_display_str = f"{appt_data[0]} - {appt_data[1]}"
        doctor_display_str = f"{appt_data[2]} - {appt_data[3]} ({appt_data[4]})"

        self.combo_vars['patient_combo'].set(patient_display_str)
        self.combo_vars['doctor_combo'].set(doctor_display_str)

        scheduled_dt_obj = datetime.strptime(appt_data[5], "%Y-%m-%d %H:%M:%S")
        self.inputs['date_entry'].insert(0, scheduled_dt_obj.strftime("%Y-%m-%d"))
        self.inputs['time_entry'].insert(0, scheduled_dt_obj.strftime("%H:%M"))
        self.combo_vars['status_combo'].set(appt_data[6] if appt_data[6] else "Scheduled")
        self.inputs['purpose_entry'].insert(0, appt_data[7] if appt_data[7] else "")

        # Buttons for Update and Delete
        ttk.Button(self.update_form_frame, text="Update Appointment", command=self.update_appointment).grid(row=len(form_elements), column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self.update_form_frame, text="Delete Appointment", command=self.delete_appointment, style='Danger.TButton').grid(row=len(form_elements), column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.update_form_frame, text="Clear Form", command=self.clear_update_form).grid(row=len(form_elements) + 1, columnspan=2, pady=5, padx=5, sticky="ew")

        # Style for danger button
        self.master_frame.master.master.style.configure('Danger.TButton', background='red', foreground='white')
        self.master_frame.master.master.style.map('Danger.TButton',
                                                   background=[('active', '#cc0000')],
                                                   foreground=[('active', 'white')])

        self.update_form_frame.grid_columnconfigure(1, weight=1) # Make entry column expand

    def clear_update_form(self):
        """Clears all widgets and resets state of the update form frame."""
        for widget in self.update_form_frame.winfo_children():
            widget.destroy()
        self.inputs.clear()
        self.combo_vars.clear()
        self.current_appointment_id = None
        self.tree.selection_remove(self.tree.focus()) # Deselect in treeview

    def update_appointment(self):
        """Updates the selected appointment in the database."""
        if self.current_appointment_id is None:
            messagebox.showerror("Error", "No appointment selected for update.")
            return

        # Get patient and doctor IDs from the maps
        patient_full_str = self.combo_vars['patient_combo'].get()
        doctor_full_str = self.combo_vars['doctor_combo'].get()

        patient_id = self.patient_map.get(patient_full_str)
        doctor_id = self.doctor_map.get(doctor_full_str)

        if patient_id is None or doctor_id is None:
            messagebox.showerror("Input Error", "Please select a valid patient and doctor from the lists.")
            return

        date_str = self.inputs['date_entry'].get().strip()
        time_str = self.inputs['time_entry'].get().strip()
        purpose = self.inputs['purpose_entry'].get().strip() # Maps to DB 'reason'
        status = self.combo_vars['status_combo'].get()

        # Validate required fields
        if not date_str or not time_str or not purpose:
            messagebox.showerror("Validation Error", "Date, Time, and Purpose are required fields.")
            return

        # Validate date and time format
        try:
            scheduled_datetime_str = f"{date_str} {time_str}:00" # Add seconds
            datetime.strptime(scheduled_datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid Date or Time format. Use YYYY-MM-DD and HH:MM.")
            return

        try:
            self.c.execute('''UPDATE appointments SET
                          patient_id=?, doctor_id=?, scheduled_time=?, status=?, reason=?
                          WHERE appointment_id=?''',
                          (patient_id, doctor_id, scheduled_datetime_str, status, purpose,
                           self.current_appointment_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Appointment updated successfully.")
            self.search_appointments() # Refresh the search results
            self.clear_update_form()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Error", f"Failed to update appointment (Integrity Error): {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while updating appointment: {str(e)}")

    def delete_appointment(self):
        """Deletes the selected appointment from the database."""
        if self.current_appointment_id is None:
            messagebox.showerror("Error", "No appointment selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this appointment? This action cannot be undone."):
            try:
                self.c.execute("DELETE FROM appointments WHERE appointment_id=?", (self.current_appointment_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Appointment deleted successfully.")
                self.search_appointments() # Refresh the search results
                self.clear_update_form()
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred while deleting appointment: {str(e)}")

    # Removed __del__ as the connection is managed by main_menu.py
    # def __del__(self):
    #     self.conn.close()

# Example of how you would test this file individually (for development)
# if __name__ == "__main__":
#     root = Tk()
#     root.title("Update Appointments Test")
#     root.geometry("1000x800")
#
#     # For standalone testing, create a dummy connection
#     test_conn = sqlite3.connect('test_hospital.db') # Use a test DB name
#     test_c = test_conn.cursor()
#
#     # Ensure tables exist for testing (copy from main_menu.py's create_tables)
#     test_c.execute('''
#         CREATE TABLE IF NOT EXISTS patients (
#             patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             date_of_birth TEXT, gender TEXT, address TEXT, phone TEXT UNIQUE, email TEXT,
#             admission_date TEXT, medical_history TEXT
#         )
#     ''')
#     test_c.execute('''
#         CREATE TABLE IF NOT EXISTS doctors (
#             doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL, specialization TEXT, phone TEXT UNIQUE, email TEXT, license_number TEXT UNIQUE
#         )
#     ''')
#     test_c.execute('''
#         CREATE TABLE IF NOT EXISTS appointments (
#             appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             patient_id INTEGER NOT NULL,
#             doctor_id INTEGER NOT NULL,
#             scheduled_time TEXT NOT NULL,
#             reason TEXT,
#             status TEXT,
#             FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
#             FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
#         )
#     ''')
#     # Insert some dummy data for testing if tables are empty
#     test_c.execute("INSERT OR IGNORE INTO patients (patient_id, name, phone) VALUES (1, 'Alice Smith', '1112223333')")
#     test_c.execute("INSERT OR IGNORE INTO patients (patient_id, name, phone) VALUES (2, 'Bob Johnson', '4445556666')")
#     test_c.execute("INSERT OR IGNORE INTO doctors (doctor_id, name, specialization) VALUES (101, 'Dr. Emily White', 'Cardiology')")
#     test_c.execute("INSERT OR IGNORE INTO doctors (doctor_id, name, specialization) VALUES (102, 'Dr. John Davis', 'Pediatrics')")
#     test_c.execute("INSERT OR IGNORE INTO appointments (appointment_id, patient_id, doctor_id, scheduled_time, reason, status) VALUES (1001, 1, 101, '2025-07-10 10:00:00', 'Routine Checkup', 'Scheduled')")
#     test_c.execute("INSERT OR IGNORE INTO appointments (appointment_id, patient_id, doctor_id, scheduled_time, reason, status) VALUES (1002, 2, 102, '2025-07-11 14:30:00', 'Follow-up', 'Completed')")
#     test_conn.commit()
#
#     # Instantiate the class
#     UpdateAppointments(root, test_conn, test_c)
#     root.mainloop()
#     test_conn.close() # Close connection when done with testing