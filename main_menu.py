# main_menu.py
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import platform
from datetime import datetime

# Import all your modules
from dashboard import Dashboard
from patient_management import PatientManagement
from doctor_management import DoctorManagement
from appointment import AppointmentManagement
from medical_records import MedicalRecords
from reports import Reports
from settings import Settings
from help import Help
from update_appointments import UpdateAppointments
from display_appointments import DisplayAppointments
from billing_system import BillingSystem

class HospitalManagementSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Hospital Management System")

        # Window setup
        self.setup_window()

        # Configure styles
        self.configure_styles()

        # --- IMPORTANT: Database Connection and Table Creation ---
        self.db_name = 'hospital.db'
        self.conn = None
        self.c = None
        self.connect_db_and_create_tables()
        # --------------------------------------------------------

        # Create main containers
        self.create_main_containers()

        # Create the main menu bar
        self.create_menu_bar()

        # Create toolbar (This is the one the user was referring to as "toolbar")
        self.create_toolbar_buttons() # Renamed to avoid confusion with menu bar

        # Create sidebar
        self.create_sidebar()

        # Create content area
        self.create_content_area()

        # Initialize dashboard (now tables should exist)
        self.show_dashboard()

        # Bind the on_closing method to the window close button
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """Configure main window properties"""
        if platform.system() == 'Windows':
            self.master.state('zoomed')
        else:
            self.master.attributes('-zoomed', True)
        self.master.minsize(1200, 700)

    def configure_styles(self):
        """Configure custom styles for ttk widgets"""
        self.style = ttk.Style()

        # General Button style
        self.style.configure('TButton', font=('Arial', 10), padding=6)
        self.style.map('TButton',
                       foreground=[('pressed', 'white'), ('active', 'white')],
                       background=[('pressed', '!active', '#2980b9'), ('active', '#3498db')])

        # Frame styles
        self.style.configure('Main.TFrame', background='#f5f5f5')
        self.style.configure('Sidebar.TFrame', background='#2c3e50')
        self.style.configure('Toolbar.TFrame', background='#34495e')

        # Sidebar Button styles
        self.style.configure('Sidebar.TButton',
                           font=('Arial', 12, 'bold'),
                           foreground='white',
                           background='#2c3e50',
                           borderwidth=0,
                           padding=10)
        self.style.map('Sidebar.TButton',
                      foreground=[('active', 'white')],
                      background=[('active', '#3498db')])

        # Label styles
        self.style.configure('Header.TLabel',
                           font=('Arial', 20, 'bold'),
                           foreground='white',
                           background='#2c3e50')

        # Danger Button Style (for delete operations)
        self.style.configure('Danger.TButton', background='red', foreground='white')
        self.style.map('Danger.TButton',
                       background=[('active', '#cc0000')],
                       foreground=[('active', 'white')])

    def connect_db_and_create_tables(self):
        """Connects to the database and creates tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.c = self.conn.cursor()
            self.c.execute("PRAGMA foreign_keys = ON;")

            self.c.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date_of_birth TEXT,
                    gender TEXT,
                    address TEXT,
                    phone TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    admission_date TEXT,
                    medical_history TEXT
                )
            ''')

            self.c.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    specialization TEXT,
                    phone TEXT UNIQUE,
                    email TEXT,
                    department TEXT,
                    license_number TEXT UNIQUE NOT NULL
                )
            ''')

            self.c.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL,
                    appointment_time TEXT NOT NULL,
                    purpose TEXT,
                    status TEXT DEFAULT 'Scheduled',
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
                )
            ''')

            self.c.execute('''
                CREATE TABLE IF NOT EXISTS medical_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    record_date TEXT NOT NULL,
                    diagnosis TEXT,
                    treatment TEXT,
                    prescription TEXT,
                    notes TEXT,
                    FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
                )
            ''')

            self.c.execute('''
                CREATE TABLE IF NOT EXISTS billing (
                    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    appointment_id INTEGER,
                    service_description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    bill_date TEXT NOT NULL,
                    due_date TEXT,
                    status TEXT DEFAULT 'Pending',
                    FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                    FOREIGN KEY(appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL
                )
            ''')

            self.conn.commit()
            print("Database tables checked/created successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Connection Error", f"Failed to connect to database or create tables: {e}\nApplication will exit.")
            self.master.destroy()
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred during database setup: {e}\nApplication will exit.")
            self.master.destroy()

    def create_main_containers(self):
        """Create main container frames"""
        self.main_container = ttk.Frame(self.master, style='Main.TFrame')
        self.main_container.pack(fill=BOTH, expand=True)

        # Toolbar container
        self.toolbar_frame = ttk.Frame(self.main_container, style='Toolbar.TFrame', height=50)
        self.toolbar_frame.pack(fill=X)

        # Bottom container (sidebar + content)
        self.bottom_container = ttk.Frame(self.main_container, style='Main.TFrame')
        self.bottom_container.pack(fill=BOTH, expand=True)

    def create_menu_bar(self):
        """Creates a traditional software-style menu bar."""
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        # --- File Menu ---
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=self.print_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # --- Edit Menu ---
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_command(label="Delete", command=self.delete)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all)

        # --- View Menu ---
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        # FIX: Changed ttk.BooleanVar to tk.BooleanVar
        self.show_toolbar_var = tk.BooleanVar(value=True) # Store the variable if you want to control toolbar visibility
        view_menu.add_checkbutton(label="Show Toolbar", variable=self.show_toolbar_var, command=self.toggle_toolbar_visibility)
        view_menu.add_checkbutton(label="Show Status Bar", variable=tk.BooleanVar(value=True)) # Assuming a status bar will be added
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)

        # --- Tools Menu ---
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Options", command=self.show_settings)
        tools_menu.add_command(label="Spell Check", command=self.spell_check)
        tools_menu.add_command(label="Preferences", command=self.show_preferences)

        # --- Window Menu ---
        window_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Window", menu=window_menu)
        window_menu.add_command(label="Minimize", command=self.master.iconify)
        window_menu.add_command(label="Maximize", command=lambda: self.master.state('zoomed'))
        window_menu.add_command(label="Restore", command=lambda: self.master.state('normal'))
        window_menu.add_separator()
        window_menu.add_command(label="Close", command=self.on_closing)

        # --- Help Menu ---
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="View Help", command=self.show_help)
        help_menu.add_command(label="Send Feedback", command=self.send_feedback)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

    def toggle_toolbar_visibility(self):
        """Toggles the visibility of the toolbar."""
        if self.show_toolbar_var.get():
            self.toolbar_frame.pack(fill=X)
        else:
            self.toolbar_frame.pack_forget()

# ... (rest of your HospitalManagementSystem class and main execution block)
    def create_toolbar_buttons(self):
        """Create top toolbar with quick access buttons."""
        toolbar_items = [
            ("Dashboard", self.show_dashboard),
            ("Patients", lambda: self.load_module('patient_management', 'PatientManagement')),
            ("Appointments", lambda: self.load_module('appointment', 'AppointmentManagement')),
            ("Records", lambda: self.load_module('medical_records', 'MedicalRecords')),
            ("Billing", lambda: self.load_module('billing_system', 'BillingSystem')),
            ("Reports", self.show_reports),
            ("Exit", self.master.quit) # This makes exactly 7 buttons
        ]

        for text, command in toolbar_items:
            btn = Button(self.toolbar_frame, text=text, command=command,
                        bg='#34495e', fg='white', font=('Arial', 10),
                        bd=0, padx=12, pady=5, relief=FLAT,
                        activebackground='#2980b9', activeforeground='white')
            btn.pack(side=LEFT, padx=2)

        # Add clock
        self.clock_label = Label(self.toolbar_frame, text="",
                               bg='#34495e', fg='white', font=('Arial', 10))
        self.clock_label.pack(side=RIGHT, padx=10)
        self.update_clock()

    def update_clock(self):
        """Update the clock in toolbar"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.master.after(1000, self.update_clock)

    def create_sidebar(self):
        """Create the sidebar navigation"""
        self.sidebar_frame = ttk.Frame(self.bottom_container, style='Sidebar.TFrame', width=220)
        self.sidebar_frame.pack(side=LEFT, fill=Y)
        self.sidebar_frame.pack_propagate(False)

        # Sidebar header
        header = ttk.Label(self.sidebar_frame, text="Hospital System", style='Header.TLabel')
        header.pack(fill=X, pady=20, ipady=10)

        # Navigation buttons
        self.create_sidebar_buttons()

    def create_sidebar_buttons(self):
        """Create sidebar navigation buttons"""
        nav_items = [
            ("Dashboard", "📊", self.show_dashboard),
            ("Patients", "👨‍⚕️", lambda: self.load_module('patient_management', 'PatientManagement')),
            ("Doctors", "👩‍⚕️", lambda: self.load_module('doctor_management', 'DoctorManagement')),
            ("Appointments", "📅", lambda: self.load_module('appointment', 'AppointmentManagement')),
            ("Medical Records", "📋", lambda: self.load_module('medical_records', 'MedicalRecords')),
            ("Billing", "💰", lambda: self.load_module('billing_system', 'BillingSystem')),
            ("Reports", "📈", self.show_reports),
            ("Settings", "⚙️", self.show_settings),
            ("Exit", "🚪", self.master.quit)
        ]

        for text, icon, command in nav_items:
            btn = ttk.Button(self.sidebar_frame,
                           text=f" {icon}  {text}",
                           style='Sidebar.TButton',
                           command=command)
            btn.pack(fill=X, pady=2, padx=5, ipady=5)

    def create_content_area(self):
        """Create the main content area where modules will be loaded."""
        self.content_frame = ttk.Frame(self.bottom_container, style='Main.TFrame')
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        self.content_frame.grid_propagate(False)

    def clear_content(self):
        """Clears all widgets from the content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def load_module(self, module_name, class_name):
        """Dynamically loads a module into the content area."""
        self.clear_content()

        try:
            module = __import__(module_name)
            module_class = getattr(module, class_name)
            module_class(self.content_frame, self.conn, self.c)

        except ImportError:
            messagebox.showerror("Module Error", f"Module '{module_name}' not found.\nPlease ensure '{module_name}.py' exists in the same directory.")
        except AttributeError:
            messagebox.showerror("Class Error", f"Class '{class_name}' not found in module '{module_name}'.\nPlease check the class name in '{module_name}.py'.")
        except Exception as e:
            messagebox.showerror("Loading Error", f"Failed to load {module_name}:\n{str(e)}")
            print(f"Error loading module {module_name}: {e}")

    def show_dashboard(self):
        """Instantiates and displays the Dashboard content."""
        self.clear_content()
        Dashboard(self.content_frame, self.conn, self.c)

    def show_reports(self):
        self.clear_content()
        Reports(self.content_frame, self.conn, self.c)

    def show_settings(self):
        self.clear_content()
        Settings(self.content_frame, self.conn, self.c)

    def show_help(self):
        self.clear_content()
        Help(self.content_frame, self.conn, self.c)

    def show_about(self):
        """Displays an about message box."""
        messagebox.showinfo("About", "Hospital Management System\nVersion 1.0\nDeveloped by Your Name/Team")

    def on_closing(self):
        """Handles closing the application and database connection cleanly."""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            if self.conn:
                self.conn.close()
                print("Database connection closed.")
            self.master.destroy()

    def new_file(self): pass
    def open_file(self): pass
    def save_file(self): pass
    def save_as(self): pass
    def print_file(self): pass
    def undo(self): pass
    def redo(self): pass
    def cut(self): pass
    def copy(self): pass
    def paste(self): pass
    def delete(self): pass
    def select_all(self): pass
    def zoom_in(self): pass
    def zoom_out(self): pass
    def reset_zoom(self): pass
    def spell_check(self): pass
    def show_preferences(self): pass
    def send_feedback(self): pass

if __name__ == "__main__":
    root = Tk()
    app = HospitalManagementSystem(root)
    root.mainloop()