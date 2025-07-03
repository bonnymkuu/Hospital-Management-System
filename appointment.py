# appointment.py
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class AppointmentManagement:
    def __init__(self, master_frame, conn, c):
        self.master_frame = master_frame
        self.conn = conn
        self.c = c

        for widget in self.master_frame.winfo_children():
            widget.destroy()

        self.main_frame = Frame(self.master_frame, bg='#f0f0f0')
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.left_frame = Frame(self.main_frame, padx=10, pady=10, bg='#e0f7fa', relief=GROOVE, bd=2)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        self.right_frame = Frame(self.main_frame, padx=10, pady=10, bg='#e3f2fd', relief=GROOVE, bd=2)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Form Elements
        ttk.Label(self.left_frame, text="Appointment Management", # Changed to ttk.Label
                  font=('Arial', 18, 'bold'), foreground='#2c3e50', background='#e0f7fa').grid(row=0, columnspan=2, pady=15) # Changed fg to foreground, bg to background

        ttk.Label(self.left_frame, text="Patient:", background='#e0f7fa').grid(row=1, column=0, sticky=W, pady=5, padx=5)
        self.patient_var = StringVar()
        self.patient_combo = ttk.Combobox(self.left_frame, textvariable=self.patient_var, width=27, state="readonly")
        self.patient_combo.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.patient_map = {}
        self.load_patients()

        ttk.Label(self.left_frame, text="Doctor:", background='#e0f7fa').grid(row=2, column=0, sticky=W, pady=5, padx=5)
        self.doctor_var = StringVar()
        self.doctor_combo = ttk.Combobox(self.left_frame, textvariable=self.doctor_var, width=27, state="readonly")
        self.doctor_combo.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        self.doctor_map = {}
        self.load_doctors()

        self.inputs = {
            'date_entry': ttk.Entry(self.left_frame, width=30),
            'time_entry': ttk.Entry(self.left_frame, width=30),
            'purpose_entry': ttk.Entry(self.left_frame, width=30)
        }
        self.combo_vars = {
            'patient_combo': self.patient_var,
            'doctor_combo': self.doctor_var,
            'status_combo': StringVar()
        }

        ttk.Label(self.left_frame, text="Date (YYYY-MM-DD):", background='#e0f7fa').grid(row=3, column=0, sticky=W, pady=5, padx=5)
        self.inputs['date_entry'].grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        self.inputs['date_entry'].insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(self.left_frame, text="Time (HH:MM):", background='#e0f7fa').grid(row=4, column=0, sticky=W, pady=5, padx=5)
        self.inputs['time_entry'].grid(row=4, column=1, pady=5, padx=5, sticky="ew")
        self.inputs['time_entry'].insert(0, "10:00")

        ttk.Label(self.left_frame, text="Purpose:", background='#e0f7fa').grid(row=5, column=0, sticky=W, pady=5, padx=5)
        self.inputs['purpose_entry'].grid(row=5, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(self.left_frame, text="Status:", background='#e0f7fa').grid(row=6, column=0, sticky=W, pady=5, padx=5)
        self.status_combo = ttk.Combobox(self.left_frame, textvariable=self.combo_vars['status_combo'],
                                          values=["Scheduled", "Completed", "Cancelled"], width=27, state="readonly")
        self.status_combo.grid(row=6, column=1, pady=5, padx=5, sticky="ew")
        self.status_combo.current(0)

        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=3)

        ttk.Button(self.left_frame, text="Add Appointment", command=self.add_appointment).grid(row=7, column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Update Appointment", command=self.update_appointment).grid(row=7, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Clear Form", command=self.clear_form).grid(row=8, column=0, pady=5, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Delete Appointment", command=self.delete_appointment, style='Danger.TButton').grid(row=8, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(self.left_frame, text="Search Appointments:", background='#e0f7fa').grid(row=9, column=0, sticky=W, pady=10, padx=5)
        self.search_entry = ttk.Entry(self.left_frame, width=30)
        self.search_entry.grid(row=9, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Search", command=self.search_appointments).grid(row=10, columnspan=2, pady=5, padx=5, sticky="ew")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#4a69bd', foreground='white')
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

        self.tree = ttk.Treeview(self.right_frame, columns=("ID", "Patient", "Doctor", "Date", "Time", "Purpose", "Status"), show="headings")

        self.tree.heading("ID", text="ID", anchor=CENTER)
        self.tree.heading("Patient", text="Patient", anchor=W)
        self.tree.heading("Doctor", text="Doctor", anchor=W)
        self.tree.heading("Date", text="Date", anchor=CENTER)
        self.tree.heading("Time", text="Time", anchor=CENTER)
        self.tree.heading("Purpose", text="Purpose", anchor=W)
        self.tree.heading("Status", text="Status", anchor=CENTER)

        self.tree.column("ID", width=50, stretch=NO, anchor=CENTER)
        self.tree.column("Patient", width=120, stretch=YES)
        self.tree.column("Doctor", width=120, stretch=YES)
        self.tree.column("Date", width=90, stretch=NO, anchor=CENTER)
        self.tree.column("Time", width=70, stretch=NO, anchor=CENTER)
        self.tree.column("Purpose", width=150, stretch=YES)
        self.tree.column("Status", width=90, stretch=NO, anchor=CENTER)

        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill=BOTH, expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_appointment_select)

        self.current_appointment_id = None
        self.load_appointments()

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

    def load_doctors(self):
        try:
            self.c.execute("SELECT doctor_id, name FROM doctors ORDER BY name ASC")
            doctors = self.c.fetchall()
            self.doctor_map = {f"{did} - {name}": did for did, name in doctors}
            self.doctor_combo['values'] = list(self.doctor_map.keys())
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading doctors: {e}\nEnsure 'doctors' table exists.")
            print(f"Error loading doctors: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading doctors: {e}")
            print(f"An unexpected error occurred while loading doctors: {e}")

    def load_appointments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute('''SELECT a.appointment_id, p.name, d.name, a.appointment_date,
                               a.appointment_time, a.purpose, a.status
                               FROM appointments a
                               JOIN patients p ON a.patient_id = p.patient_id
                               JOIN doctors d ON a.doctor_id = d.doctor_id
                               ORDER BY a.appointment_date DESC, a.appointment_time DESC''')
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                self.tree.insert("", END, values=("", "", "", "No appointments found.", "", "", ""))
                self.tree.item(self.tree.get_children()[0], tags=('no_data',))
                self.tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading appointments: {e}\nEnsure 'appointments', 'patients', and 'doctors' tables exist with correct columns.")
            print(f"Error loading appointments: {e}")
            self.tree.insert("", END, values=("", "", "", "Error loading appointments.", "", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading appointments: {e}")
            print(f"An unexpected error occurred while loading appointments: {e}")
            self.tree.insert("", END, values=("", "", "", "Unexpected error loading appointments.", "", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))


    def on_appointment_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.current_appointment_id = values[0]

            try:
                self.c.execute('''SELECT a.patient_id, p.name, a.doctor_id, d.name, a.appointment_date,
                               a.appointment_time, a.purpose, a.status
                               FROM appointments a
                               JOIN patients p ON a.patient_id = p.patient_id
                               JOIN doctors d ON a.doctor_id = d.doctor_id
                               WHERE a.appointment_id=?''', (self.current_appointment_id,))
                app_data = self.c.fetchone()

                if app_data:
                    self.clear_form()

                    patient_display_str = f"{app_data[0]} - {app_data[1]}"
                    if patient_display_str in self.patient_map:
                        self.combo_vars['patient_combo'].set(patient_display_str)
                    else:
                        self.combo_vars['patient_combo'].set("")

                    doctor_display_str = f"{app_data[2]} - {app_data[3]}"
                    if doctor_display_str in self.doctor_map:
                        self.combo_vars['doctor_combo'].set(doctor_display_str)
                    else:
                        self.combo_vars['doctor_combo'].set("")

                    self.inputs['date_entry'].insert(0, app_data[4] if app_data[4] else "")
                    self.inputs['time_entry'].insert(0, app_data[5] if app_data[5] else "")
                    self.inputs['purpose_entry'].insert(0, app_data[6] if app_data[6] else "")
                    self.combo_vars['status_combo'].set(app_data[7] if app_data[7] else "Scheduled")
                else:
                    messagebox.showwarning("Appointment Not Found", "Selected appointment data could not be retrieved.")
                    self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to retrieve appointment details: {str(e)}")
                self.clear_form()


    def add_appointment(self):
        patient_full_str = self.combo_vars['patient_combo'].get()
        patient_id = self.patient_map.get(patient_full_str)

        doctor_full_str = self.combo_vars['doctor_combo'].get()
        doctor_id = self.doctor_map.get(doctor_full_str)

        if patient_id is None:
            messagebox.showerror("Input Error", "Please select a valid patient.")
            return
        if doctor_id is None:
            messagebox.showerror("Input Error", "Please select a valid doctor.")
            return

        date_str = self.inputs['date_entry'].get().strip()
        time_str = self.inputs['time_entry'].get().strip()
        purpose = self.inputs['purpose_entry'].get().strip()
        status = self.combo_vars['status_combo'].get()

        if not date_str:
            messagebox.showerror("Validation Error", "Date is required.")
            return
        if not time_str:
            messagebox.showerror("Validation Error", "Time is required.")
            return
        if not purpose:
            messagebox.showerror("Validation Error", "Purpose is required.")
            return

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return

        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Validation Error", "Time must be in HH:MM format.")
            return

        try:
            self.c.execute('''INSERT INTO appointments
                          (patient_id, doctor_id, appointment_date, appointment_time, purpose, status)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                          (patient_id, doctor_id, date_str, time_str, purpose, status))
            self.conn.commit()
            messagebox.showinfo("Success", "Appointment added successfully.")
            self.load_appointments()
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add appointment: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def update_appointment(self):
        if not hasattr(self, 'current_appointment_id') or self.current_appointment_id is None:
            messagebox.showerror("Update Error", "Please select an appointment to update.")
            return

        patient_full_str = self.combo_vars['patient_combo'].get()
        patient_id = self.patient_map.get(patient_full_str)

        doctor_full_str = self.combo_vars['doctor_combo'].get()
        doctor_id = self.doctor_map.get(doctor_full_str)

        if patient_id is None:
            messagebox.showerror("Input Error", "Please select a valid patient.")
            return
        if doctor_id is None:
            messagebox.showerror("Input Error", "Please select a valid doctor.")
            return

        date_str = self.inputs['date_entry'].get().strip()
        time_str = self.inputs['time_entry'].get().strip()
        purpose = self.inputs['purpose_entry'].get().strip()
        status = self.combo_vars['status_combo'].get()

        if not date_str:
            messagebox.showerror("Validation Error", "Date is required.")
            return
        if not time_str:
            messagebox.showerror("Validation Error", "Time is required.")
            return
        if not purpose:
            messagebox.showerror("Validation Error", "Purpose is required.")
            return

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return

        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Validation Error", "Time must be in HH:MM format.")
            return

        if not messagebox.askyesno("Confirm Update", "Are you sure you want to update this appointment?"):
            return

        try:
            self.c.execute('''UPDATE appointments SET
                          patient_id=?, doctor_id=?, appointment_date=?, appointment_time=?, purpose=?, status=?
                          WHERE appointment_id=?''',
                          (patient_id, doctor_id, date_str, time_str, purpose, status, self.current_appointment_id))

            if self.c.rowcount == 0:
                messagebox.showwarning("Update Warning", "No appointment was updated. The appointment might have been deleted by another user or does not exist.")
            else:
                self.conn.commit()
                messagebox.showinfo("Update Success", "Appointment updated successfully.")
                self.load_appointments()
                self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update appointment: {str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def delete_appointment(self):
        if not hasattr(self, 'current_appointment_id') or self.current_appointment_id is None:
            messagebox.showerror("Error", "No appointment selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this appointment? This action cannot be undone."):
            try:
                self.c.execute("DELETE FROM appointments WHERE appointment_id=?", (self.current_appointment_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Appointment deleted successfully.")
                self.load_appointments()
                self.clear_form()
                self.current_appointment_id = None
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred while deleting appointment: {str(e)}")

    def search_appointments(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_appointments()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute('''SELECT a.appointment_id, p.name, d.name, a.appointment_date,
                               a.appointment_time, a.purpose, a.status
                               FROM appointments a
                               JOIN patients p ON a.patient_id = p.patient_id
                               JOIN doctors d ON a.doctor_id = d.doctor_id
                               WHERE p.name LIKE ? OR d.name LIKE ? OR a.purpose LIKE ? OR a.status LIKE ?
                               ORDER BY a.appointment_date DESC, a.appointment_time DESC''',
                          (f"%{search_term}%", f"R%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                messagebox.showinfo("No Results", "No appointments found matching your search criteria.")
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error searching appointments: {e}")
            print(f"Error searching appointments: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during search: {str(e)}")
            print(f"An unexpected error occurred during search: {str(e)}")

    def clear_form(self):
        self.combo_vars['patient_combo'].set("")
        self.combo_vars['doctor_combo'].set("")
        self.inputs['date_entry'].delete(0, END)
        self.inputs['date_entry'].insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.inputs['time_entry'].delete(0, END)
        self.inputs['time_entry'].insert(0, "10:00")
        self.inputs['purpose_entry'].delete(0, END)
        self.combo_vars['status_combo'].set("Scheduled")

        if self.tree.focus():
            self.tree.selection_remove(self.tree.focus())

        self.current_appointment_id = None