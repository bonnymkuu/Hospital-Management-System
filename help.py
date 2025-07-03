import tkinter as tk
from tkinter import ttk, Frame, Label, BOTH

class Help:
    def __init__(self, master_frame, conn, c): # conn and c are passed for consistency, though not used here
        self.master_frame = master_frame
        self.conn = conn
        self.c = c

        # Clear any existing widgets in the parent frame
        for widget in self.master_frame.winfo_children():
            widget.destroy()

        self.create_help_ui()

    def create_help_ui(self):
        self.main_frame = Frame(self.master_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Header
        ttk.Label(self.main_frame, text="Help & About",
                  font=('Arial', 24, 'bold'), foreground='#333333', background='#f8f8f8').pack(pady=(10, 20))

        # Application Info
        info_frame = ttk.LabelFrame(self.main_frame, text="Application Information", padding=(10, 10))
        info_frame.pack(fill=BOTH, pady=10, padx=10)

        ttk.Label(info_frame, text="Application Name:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text="Hospital Management System", font=('Arial', 10)).grid(row=0, column=1, padx=5, pady=2, sticky='w')

        ttk.Label(info_frame, text="Version:", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text="1.0.0", font=('Arial', 10)).grid(row=1, column=1, padx=5, pady=2, sticky='w')

        ttk.Label(info_frame, text="Developed by:", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text="Bonny Boy Mkuu", font=('Arial', 10)).grid(row=2, column=1, padx=5, pady=2, sticky='w')

        ttk.Label(info_frame, text="Release Date:", font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text="July 2025", font=('Arial', 10)).grid(row=3, column=1, padx=5, pady=2, sticky='w')

        info_frame.grid_columnconfigure(1, weight=1) # Make second column expand

        # Usage Instructions / Support
        help_text_frame = ttk.LabelFrame(self.main_frame, text="Usage & Support", padding=(10, 10))
        help_text_frame.pack(fill=BOTH, expand=True, pady=10, padx=10)

        help_message = """
Welcome to the Hospital Management System!

This application allows you to manage patient records, doctor information, appointments, medical records, and billing.

Key Features:
- Dashboard: Overview of key statistics.
- Patient Management: Add, view, update, delete patient details.
- Doctor Management: Manage doctor profiles.
- Appointment Scheduling: Schedule, track, and update appointments.
- Medical Records: Keep detailed medical histories for patients.
- Billing: Generate and manage patient bills.
- Reports: Generate various reports (Appointments, Patients, Doctors, Billing).

For support or bug reports, please contact: bonnymkuu3939@gmail.com
(Note: This is a demo application. Features are for illustrative purposes.)
        """
        help_label = ttk.Label(help_text_frame, text=help_message, font=('Arial', 10), wraplength=700, justify='left', background='white', relief='flat', anchor='nw')
        help_label.pack(fill=BOTH, expand=True, padx=5, pady=5)