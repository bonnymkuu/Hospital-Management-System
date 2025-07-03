# update_appointments.py
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class UpdateAppointments:
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
        self.update_form_frame.pack(fill=X, pady=10, padx=10)

        self.inputs = {}
        self.combo_vars = {}
        self.current_appointment_id = None

        self.patient_map = {}
        self.doctor_map = {}
        self.load_patients_and_doctors()

    def load_patients_and_doctors(self):
        try:
            self.c.execute("SELECT patient_id, name FROM patients ORDER BY name ASC")
            patients = self.c.fetchall()
            self.patient_map = {f"{pid} - {name}": pid for pid, name in patients}

            self.c.execute("SELECT doctor_id, name, specialization FROM doctors ORDER BY name ASC")
            doctors = self.c.fetchall()
            self.doctor_map = {f"{did} - {name} ({spec})": did for did, name, spec in doctors}
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading patient/doctor data: {e}\nEnsure 'patients' and 'doctors' tables exist.")
            print(f"Error loading patient/doctor data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading patient/doctor data: {e}")
            print(f"An unexpected error occurred while loading patient/doctor data: {e}")

    def search_appointments(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Input Required", "Please enter a patient name or appointment ID to search.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.clear_update_form()

        try:
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
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.current_appointment_id = values[0]

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
        self.clear_update_form()

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
                                     width=35, font=('Arial', 10), state="readonly")
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

        patient_display_str = f"{appt_data[0]} - {appt_data[1]}"
        doctor_display_str = f"{appt_data[2]} - {appt_data[3]} ({appt_data[4]})"

        self.combo_vars['patient_combo'].set(patient_display_str)
        self.combo_vars['doctor_combo'].set(doctor_display_str)

        scheduled_dt_obj = datetime.strptime(appt_data[5], "%Y-%m-%d %H:%M:%S")
        self.inputs['date_entry'].insert(0, scheduled_dt_obj.strftime("%Y-%m-%d"))
        self.inputs['time_entry'].insert(0, scheduled_dt_obj.strftime("%H:%M"))
        self.combo_vars['status_combo'].set(appt_data[6] if appt_data[6] else "Scheduled")
        self.inputs['purpose_entry'].insert(0, appt_data[7] if appt_data[7] else "")

        ttk.Button(self.update_form_frame, text="Update Appointment", command=self.update_appointment).grid(row=len(form_elements), column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self.update_form_frame, text="Delete Appointment", command=self.delete_appointment, style='Danger.TButton').grid(row=len(form_elements), column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.update_form_frame, text="Clear Form", command=self.clear_update_form).grid(row=len(form_elements) + 1, columnspan=2, pady=5, padx=5, sticky="ew")

        self.update_form_frame.grid_columnconfigure(1, weight=1)

    def clear_update_form(self):
        for widget in self.update_form_frame.winfo_children():
            widget.destroy()
        self.inputs.clear()
        self.combo_vars.clear()
        self.current_appointment_id = None
        if self.tree.focus(): # Check if there's a focused item before trying to deselect
            self.tree.selection_remove(self.tree.focus())

    def update_appointment(self):
        if self.current_appointment_id is None:
            messagebox.showerror("Error", "No appointment selected for update.")
            return

        patient_full_str = self.combo_vars['patient_combo'].get()
        doctor_full_str = self.combo_vars['doctor_combo'].get()

        patient_id = self.patient_map.get(patient_full_str)
        doctor_id = self.doctor_map.get(doctor_full_str)

        if patient_id is None or doctor_id is None:
            messagebox.showerror("Input Error", "Please select a valid patient and doctor from the lists.")
            return

        date_str = self.inputs['date_entry'].get().strip()
        time_str = self.inputs['time_entry'].get().strip()
        purpose = self.inputs['purpose_entry'].get().strip()
        status = self.combo_vars['status_combo'].get()

        if not date_str or not time_str or not purpose:
            messagebox.showerror("Validation Error", "Date, Time, and Purpose are required fields.")
            return

        try:
            scheduled_datetime_str = f"{date_str} {time_str}:00"
            datetime.strptime(scheduled_datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid Date or Time format. Use YYYY-MM-DD and HH:MM.")
            return

        if not messagebox.askyesno("Confirm Update", "Are you sure you want to update this appointment?"):
            return

        try:
            self.c.execute('''UPDATE appointments SET
                          patient_id=?, doctor_id=?, scheduled_time=?, status=?, reason=?
                          WHERE appointment_id=?''',
                          (patient_id, doctor_id, scheduled_datetime_str, status, purpose,
                           self.current_appointment_id))
            if self.c.rowcount == 0:
                messagebox.showwarning("Update Warning", "No appointment record was updated. The record might have been deleted by another user or does not exist.")
            else:
                self.conn.commit()
                messagebox.showinfo("Success", "Appointment updated successfully.")
                self.search_appointments()
                self.clear_update_form()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Error", f"Failed to update appointment (Integrity Error): {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while updating appointment: {str(e)}")

    def delete_appointment(self):
        if self.current_appointment_id is None:
            messagebox.showerror("Error", "No appointment selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this appointment? This action cannot be undone."):
            try:
                self.c.execute("DELETE FROM appointments WHERE appointment_id=?", (self.current_appointment_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Appointment deleted successfully.")
                self.search_appointments()
                self.clear_update_form()
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred while deleting appointment: {str(e)}")