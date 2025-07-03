import tkinter as tk
from tkinter import ttk, messagebox, Frame, Label, Button, Scrollbar, VERTICAL, CENTER, RIGHT, Y, BOTH, END, LEFT, X
from tkinter import filedialog # Import filedialog for saving file
import sqlite3
from datetime import datetime

# Import for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch # For setting widths if needed

class Reports:
    def __init__(self, master_frame, conn, c):
        self.master_frame = master_frame
        self.conn = conn
        self.c = c

        # Store the currently displayed report data and columns for PDF generation
        self.current_report_data = []
        self.current_report_columns = []
        self.current_report_title = ""

        # Clear any existing widgets in the parent frame
        for widget in self.master_frame.winfo_children():
            widget.destroy()

        self.create_reports_ui()

    def create_reports_ui(self):
        self.main_frame = Frame(self.master_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Header
        ttk.Label(self.main_frame, text="Reporting and Analytics",
                  font=('Arial', 24, 'bold'), foreground='#333333', background='#f8f8f8').pack(pady=(10, 20))

        # Control Frame for Report Selection and Filters
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Report Options", padding=(10, 10))
        self.control_frame.pack(fill=X, pady=10, padx=10)

        # Report Type Selection
        ttk.Label(self.control_frame, text="Select Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.report_type_var = tk.StringVar()
        self.report_type_combo = ttk.Combobox(self.control_frame, textvariable=self.report_type_var,
                                              values=["Appointments Report", "Patient List", "Doctor List", "Billing Summary"])
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.report_type_combo.set("Appointments Report") # Default selection
        self.report_type_combo.bind("<<ComboboxSelected>>", self.on_report_type_change)

        # Filters for Appointments Report (initially visible)
        self.appointment_filters_frame = ttk.Frame(self.control_frame)
        self.appointment_filters_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.create_appointment_filters(self.appointment_filters_frame)

        # Button Frame for Generate and Download
        button_frame = ttk.Frame(self.control_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Generate Report", command=self.generate_selected_report).pack(side=LEFT, padx=5)

        # --- Add the Download PDF button ---
        self.download_pdf_button = ttk.Button(button_frame, text="Download PDF", command=self.download_report_pdf, state=tk.DISABLED)
        self.download_pdf_button.pack(side=LEFT, padx=5)
        # --- End of Download PDF button ---

        # Display Frame for Reports
        self.report_display_frame = ttk.Frame(self.main_frame, relief=tk.GROOVE, borderwidth=1)
        self.report_display_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Initial load of default report
        self.generate_selected_report()

    def create_appointment_filters(self, parent_frame):
        # Start Date
        ttk.Label(parent_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.start_date_entry = ttk.Entry(parent_frame, width=20)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-01")) # Default to start of month

        # End Date
        ttk.Label(parent_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.end_date_entry = ttk.Entry(parent_frame, width=20)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Default to today

        # Status
        ttk.Label(parent_frame, text="Status:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(parent_frame, textvariable=self.status_var,
                                         values=["All", "Scheduled", "Completed", "Cancelled"])
        self.status_combo.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        self.status_combo.set("All")

        parent_frame.columnconfigure(1, weight=1) # Make entry columns expand

    def on_report_type_change(self, event=None):
        # Hide/show filter frames based on selection
        selected_type = self.report_type_var.get()
        if selected_type == "Appointments Report":
            self.appointment_filters_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        else:
            self.appointment_filters_frame.grid_forget() # Hide filters

        # Clear display area when report type changes
        self.clear_report_display()
        # Disable PDF button when report type changes (until new report is generated)
        self.download_pdf_button.config(state=tk.DISABLED)

    def generate_selected_report(self):
        self.clear_report_display()
        report_type = self.report_type_var.get()

        # Clear previous report data
        self.current_report_data = []
        self.current_report_columns = []
        self.current_report_title = ""
        self.download_pdf_button.config(state=tk.DISABLED) # Disable until data is loaded

        if report_type == "Appointments Report":
            self.current_report_title = "Appointments Report"
            self.current_report_columns = ("ID", "Patient Name", "Doctor Name", "Date", "Time", "Purpose", "Status")
            self.load_appointments_report()
        elif report_type == "Patient List":
            self.current_report_title = "Patient List"
            self.current_report_columns = ("ID", "Name", "DoB", "Gender", "Phone", "Email", "Address", "Admission Date")
            self.load_patients_report()
        elif report_type == "Doctor List":
            self.current_report_title = "Doctor List"
            self.current_report_columns = ("ID", "Name", "Specialization", "Department", "Phone", "Email", "License No.")
            self.load_doctors_report()
        elif report_type == "Billing Summary":
            self.current_report_title = "Billing Summary"
            self.current_report_columns = ("Bill ID", "Patient Name", "Service", "Amount", "Bill Date", "Due Date", "Status")
            self.load_billing_summary()
        else:
            ttk.Label(self.report_display_frame, text="Please select a report type.", font=('Arial', 14)).pack(pady=50)

        # Enable PDF button if data was successfully loaded
        if self.current_report_data:
            self.download_pdf_button.config(state=tk.NORMAL)


    def clear_report_display(self):
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()

    def load_appointments_report(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        status = self.status_var.get()

        if not start_date or not end_date:
            messagebox.showerror("Input Error", "Please enter both Start Date and End Date.")
            return

        # Basic date validation (can be enhanced)
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Date format must be YYYY-MM-DD.")
            return

        columns = self.current_report_columns # Use class attribute for consistency
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER, width=100) # Default width
            if col in ["Patient Name", "Doctor Name", "Purpose"]:
                tree.column(col, width=150)
            if col in ["Date", "Time"]:
                tree.column(col, width=90)


        scrollbar = ttk.Scrollbar(self.report_display_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True)

        query = '''
            SELECT a.appointment_id, p.name, d.name, a.appointment_date, a.appointment_time, a.purpose, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date BETWEEN ? AND ?
        '''
        params = [start_date, end_date]

        if status != "All":
            query += " AND a.status = ?"
            params.append(status)

        query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC"

        try:
            self.c.execute(query, tuple(params))
            rows = self.c.fetchall()

            if rows:
                self.current_report_data = rows # Store data
                for row in rows:
                    tree.insert("", END, values=row)
            else:
                self.current_report_data = [] # No data
                tree.insert("", END, values=("", "", "No appointments found for the selected criteria.", "", "", "", ""))
                tree.item(tree.get_children()[0], tags=('no_data',))
                tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching appointments report: {e}")
            print(f"Error fetching appointments report: {e}")
            self.current_report_data = [] # Clear on error
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            self.current_report_data = [] # Clear on error


    def load_patients_report(self):
        columns = self.current_report_columns # Use class attribute for consistency
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER, width=100)
            if col == "Name" or col == "Address":
                tree.column(col, width=150)
            if col in ["Phone", "Email"]:
                tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.report_display_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True)

        try:
            self.c.execute("SELECT patient_id, name, date_of_birth, gender, phone, email, address, admission_date FROM patients ORDER BY name ASC")
            rows = self.c.fetchall()

            if rows:
                self.current_report_data = rows # Store data
                for row in rows:
                    tree.insert("", END, values=row)
            else:
                self.current_report_data = [] # No data
                tree.insert("", END, values=("", "", "No patients found.", "", "", "", "", ""))
                tree.item(tree.get_children()[0], tags=('no_data',))
                tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching patient report: {e}")
            print(f"Error fetching patient report: {e}")
            self.current_report_data = [] # Clear on error
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            self.current_report_data = [] # Clear on error

    def load_doctors_report(self):
        columns = self.current_report_columns # Use class attribute for consistency
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER, width=100)
            if col in ["Name", "Specialization", "Department"]:
                tree.column(col, width=120)
            if col in ["Phone", "Email", "License No."]:
                tree.column(col, width=110)

        scrollbar = ttk.Scrollbar(self.report_display_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True)

        try:
            self.c.execute("SELECT doctor_id, name, specialization, department, phone, email, license_number FROM doctors ORDER BY name ASC")
            rows = self.c.fetchall()

            if rows:
                self.current_report_data = rows # Store data
                for row in rows:
                    tree.insert("", END, values=row)
            else:
                self.current_report_data = [] # No data
                tree.insert("", END, values=("", "", "No doctors found.", "", "", "", ""))
                tree.item(tree.get_children()[0], tags=('no_data',))
                tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching doctor report: {e}")
            print(f"Error fetching doctor report: {e}")
            self.current_report_data = [] # Clear on error
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            self.current_report_data = [] # Clear on error

    def load_billing_summary(self):
        columns = self.current_report_columns # Use class attribute for consistency
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER, width=100)
            if col in ["Patient Name", "Service"]:
                tree.column(col, width=150)
            if col in ["Amount", "Bill Date", "Due Date", "Status"]:
                tree.column(col, width=90)

        scrollbar = ttk.Scrollbar(self.report_display_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True)

        try:
            self.c.execute('''
                SELECT b.bill_id, p.name, b.service_description, b.amount, b.bill_date, b.due_date, b.status
                FROM billing b
                JOIN patients p ON b.patient_id = p.patient_id
                ORDER BY b.bill_date DESC
            ''')
            rows = self.c.fetchall()

            if rows:
                self.current_report_data = rows # Store data
                for row in rows:
                    tree.insert("", END, values=row)
            else:
                self.current_report_data = [] # No data
                tree.insert("", END, values=("", "", "No billing records found.", "", "", "", ""))
                tree.item(tree.get_children()[0], tags=('no_data',))
                tree.tag_configure('no_data', foreground='gray', font=('Arial', 10, 'italic'))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching billing summary: {e}")
            print(f"Error fetching billing summary: {e}")
            self.current_report_data = [] # Clear on error
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            self.current_report_data = [] # Clear on error

    def download_report_pdf(self):
        if not self.current_report_data or not self.current_report_columns:
            messagebox.showwarning("No Report Data", "Please generate a report first before trying to download.")
            return

        # Ask user where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title=f"Save {self.current_report_title} as PDF"
        )

        if not file_path:
            return # User cancelled

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Add title
            story.append(Paragraph(f"<b>{self.current_report_title}</b>", styles['h1']))
            story.append(Spacer(1, 0.2 * inch))

            # Add current date and time
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))

            # Prepare data for the table
            data = [list(self.current_report_columns)] # Headers
            for row in self.current_report_data:
                data.append([str(item) for item in row]) # Ensure all items are strings

            # Create the table
            table = Table(data)

            # Add style to the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')), # Header background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')), # Alternating row colors
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]))

            story.append(table)

            doc.build(story)
            messagebox.showinfo("PDF Generated", f"Report saved successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to generate PDF: {e}")
            print(f"Error generating PDF: {e}")