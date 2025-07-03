# doctor_management.py
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3

class DoctorManagement:
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
        ttk.Label(self.left_frame, text="Doctor Management",
                  font=('Arial', 18, 'bold'), background='#eaf7f7', foreground='#2c3e50').grid(row=0, columnspan=2, pady=15)

        fields = [
            ("Name", "name"), ("Specialization", "specialization"),
            ("Phone", "phone"), ("Email", "email"), ("Department", "department"), ("License Number", "license_number")
        ]

        self.entries = {}
        for i, (label_text, key) in enumerate(fields, start=1):
            ttk.Label(self.left_frame, text=f"{label_text}:", background='#eaf7f7').grid(row=i, column=0, sticky=W, pady=5, padx=5)
            entry = ttk.Entry(self.left_frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.entries[key] = entry

        # Configure left_frame columns to expand
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=3)

        # Buttons
        ttk.Button(self.left_frame, text="Add Doctor", command=self.add_doctor).grid(row=7, column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Update Doctor", command=self.update_doctor).grid(row=7, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Clear Form", command=self.clear_form).grid(row=8, column=0, pady=5, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Delete Doctor", command=self.delete_doctor, style='Danger.TButton').grid(row=8, column=1, pady=5, padx=5, sticky="ew")

        # Search
        ttk.Label(self.left_frame, text="Search Doctors:", background='#eaf7f7').grid(row=9, column=0, sticky=W, pady=10, padx=5)
        self.search_entry = ttk.Entry(self.left_frame, width=30)
        self.search_entry.grid(row=9, column=1, pady=10, padx=5, sticky="ew")
        ttk.Button(self.left_frame, text="Search", command=self.search_doctor).grid(row=10, columnspan=2, pady=5, padx=5, sticky="ew")

        # Doctor List (Treeview)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#4a69bd', foreground='white')
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

        self.tree = ttk.Treeview(self.right_frame, columns=("ID", "Name", "Specialization", "Department", "Phone", "Email", "License"), show="headings")

        self.tree.heading("ID", text="ID", anchor=CENTER)
        self.tree.heading("Name", text="Name", anchor=W)
        self.tree.heading("Specialization", text="Specialization", anchor=W)
        self.tree.heading("Department", text="Department", anchor=W)
        self.tree.heading("Phone", text="Phone", anchor=W)
        self.tree.heading("Email", text="Email", anchor=W)
        self.tree.heading("License", text="License No.", anchor=W)

        self.tree.column("ID", width=40, stretch=NO, anchor=CENTER)
        self.tree.column("Name", width=120, stretch=YES)
        self.tree.column("Specialization", width=120, stretch=YES)
        self.tree.column("Department", width=90, stretch=YES)
        self.tree.column("Phone", width=90, stretch=NO)
        self.tree.column("Email", width=120, stretch=YES)
        self.tree.column("License", width=80, stretch=NO)

        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill=BOTH, expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_doctor_select)

        self.current_doctor_id = None

        self.load_doctors()

    def load_doctors(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute("SELECT doctor_id, name, specialization, department, phone, email, license_number FROM doctors ORDER BY name ASC")
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                self.tree.insert("", END, values=("", "", "No doctors found.", "", "", "", ""))
                self.tree.item(self.tree.get_children()[0], tags=('no_data',))
                self.tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading doctors: {e}\nEnsure 'doctors' table exists with correct columns.")
            print(f"Error loading doctors: {e}")
            self.tree.insert("", END, values=("", "", "Error loading doctors.", "", "", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading doctors: {e}")
            print(f"An unexpected error occurred while loading doctors: {e}")
            self.tree.insert("", END, values=("", "", "Unexpected error loading doctors.", "", "", "", ""))
            self.tree.item(self.tree.get_children()[0], tags=('error_data',))
            self.tree.tag_configure('error_data', foreground='red', font=('Arial', 10, 'bold'))

    def on_doctor_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.current_doctor_id = values[0]

            self.c.execute("SELECT name, specialization, phone, email, department, license_number FROM doctors WHERE doctor_id=?", (self.current_doctor_id,))
            doctor_data = self.c.fetchone()

            if doctor_data:
                self.clear_form()

                self.entries['name'].insert(0, doctor_data[0] if doctor_data[0] else "")
                self.entries['specialization'].insert(0, doctor_data[1] if doctor_data[1] else "")
                self.entries['phone'].insert(0, doctor_data[2] if doctor_data[2] else "")
                self.entries['email'].insert(0, doctor_data[3] if doctor_data[3] else "")
                self.entries['department'].insert(0, doctor_data[4] if doctor_data[4] else "")
                self.entries['license_number'].insert(0, doctor_data[5] if doctor_data[5] else "")
            else:
                messagebox.showwarning("Record Not Found", "Selected doctor data could not be retrieved.")
                self.clear_form()

    def add_doctor(self):
        data = {key: self.entries[key].get().strip() for key in self.entries}

        if not data['name'] or not data['specialization'] or not data['license_number']:
            messagebox.showerror("Validation Error", "Name, Specialization, and License Number are required fields.")
            return

        if data['phone'] and not data['phone'].isdigit():
             messagebox.showerror("Validation Error", "Phone number should contain only digits.")
             return
        if data['email'] and "@" not in data['email']:
            messagebox.showerror("Validation Error", "Invalid email format.")
            return

        try:
            self.c.execute('''INSERT INTO doctors
                          (name, specialization, phone, email, department, license_number)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                          (data['name'], data['specialization'], data['phone'],
                           data['email'], data['department'], data['license_number']))
            self.conn.commit()
            messagebox.showinfo("Success", "Doctor added successfully.")
            self.load_doctors()
            self.clear_form()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: doctors.phone" in str(e):
                messagebox.showerror("Database Error", "A doctor with this phone number already exists.")
            elif "UNIQUE constraint failed: doctors.license_number" in str(e):
                messagebox.showerror("Database Error", "A doctor with this license number already exists.")
            else:
                messagebox.showerror("Database Error", f"Failed to add doctor: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while adding doctor: {str(e)}")

    def update_doctor(self):
        if not hasattr(self, 'current_doctor_id') or self.current_doctor_id is None:
            messagebox.showerror("Error", "No doctor selected for update.")
            return

        data = {key: self.entries[key].get().strip() for key in self.entries}

        if not data['name'] or not data['specialization'] or not data['license_number']:
            messagebox.showerror("Validation Error", "Name, Specialization, and License Number are required fields.")
            return

        if data['phone'] and not data['phone'].isdigit():
             messagebox.showerror("Validation Error", "Phone number should contain only digits.")
             return
        if data['email'] and "@" not in data['email']:
            messagebox.showerror("Validation Error", "Invalid email format.")
            return

        if not messagebox.askyesno("Confirm Update", "Are you sure you want to update this doctor's record?"):
            return

        try:
            self.c.execute('''UPDATE doctors SET
                          name=?, specialization=?, phone=?, email=?, department=?, license_number=?
                          WHERE doctor_id=?''',
                          (data['name'], data['specialization'], data['phone'],
                           data['email'], data['department'], data['license_number'], self.current_doctor_id))

            if self.c.rowcount == 0:
                messagebox.showwarning("Update Warning", "No doctor record was updated. The record might have been deleted by another user or does not exist.")
            else:
                self.conn.commit()
                messagebox.showinfo("Update Success", "Doctor updated successfully.")
                self.load_doctors()
                self.clear_form()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: doctors.phone" in str(e):
                messagebox.showerror("Database Error", "A doctor with this phone number already exists.")
            elif "UNIQUE constraint failed: doctors.license_number" in str(e):
                messagebox.showerror("Database Error", "A doctor with this license number already exists.")
            else:
                messagebox.showerror("Database Error", f"Failed to update doctor: {str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred while updating doctor: {str(e)}")

    def delete_doctor(self):
        if not hasattr(self, 'current_doctor_id') or self.current_doctor_id is None:
            messagebox.showerror("Error", "No doctor selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this doctor? This action cannot be undone and will also delete related appointments or records due to cascading deletes."):
            try:
                self.c.execute("DELETE FROM doctors WHERE doctor_id=?", (self.current_doctor_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Doctor deleted successfully.")
                self.load_doctors()
                self.clear_form()
                self.current_doctor_id = None
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete doctor: {str(e)}")

    def search_doctor(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_doctors()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.c.execute('''SELECT doctor_id, name, specialization, department, phone, email, license_number
                           FROM doctors
                           WHERE name LIKE ? OR specialization LIKE ? OR department LIKE ? OR license_number LIKE ?
                           ORDER BY name ASC''',
                          (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            rows = self.c.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", END, values=row)
            else:
                messagebox.showinfo("No Results", "No doctors found matching your search criteria.")
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error searching doctors: {e}")
            print(f"Error searching doctors: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during search: {str(e)}")
            print(f"An unexpected error occurred during search: {str(e)}")

    def clear_form(self):
        for key in self.entries:
            self.entries[key].delete(0, END)

        self.search_entry.delete(0, END)

        if self.tree.focus():
            self.tree.selection_remove(self.tree.focus())

        self.current_doctor_id = None