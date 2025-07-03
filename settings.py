import tkinter as tk
from tkinter import ttk, messagebox, Frame, Label, Button, BOTH, X, W, E, filedialog
import sqlite3
import shutil
from datetime import datetime

class Settings:
    def __init__(self, master_frame, conn, c):
        self.master_frame = master_frame
        self.conn = conn
        self.c = c

        # Clear any existing widgets in the parent frame
        for widget in self.master_frame.winfo_children():
            widget.destroy()

        # Internal variables for settings - initialized with default values
        self.notifications_enabled = tk.BooleanVar(value=True)
        self.notification_frequency = tk.StringVar(value="Daily")
        self.app_language = tk.StringVar(value="English")
        self.audit_logging_enabled = tk.BooleanVar(value=False)
        self.log_max_size = tk.IntVar(value=100) # In MB
        self.default_startup_module = tk.StringVar(value="Dashboard")
        self.row_highlighting = tk.BooleanVar(value=True)
        self.report_path = tk.StringVar(value="./reports")
        self.auto_save_interval = tk.IntVar(value=5) # In minutes
        self.display_record_limit = tk.IntVar(value=50) # Number of records to display in tables
        self.font_size = tk.IntVar(value=10) # Default font size for most text
        self.notifications_var = tk.BooleanVar(value=True) # Duplicated from above, keeping for consistency with user code
        self.backup_var = tk.BooleanVar(value=False) # For auto backup
        self.language_var = tk.StringVar(value="English") # Duplicated from above, keeping for consistency with user code
        self.startup_page = tk.StringVar(value="Dashboard")
        self.dark_mode = tk.BooleanVar(value=False) # Initial state: Light mode

        self.style = ttk.Style()
        self.setup_themes() # Define custom themes
        self.load_current_settings() # Load saved settings or apply defaults
        self.apply_initial_theme() # Apply the theme based on loaded/default dark_mode setting

        self.create_settings_ui()


    def setup_themes(self):
        """Defines custom light and dark themes based on existing ttk themes."""
        # --- Light Mode Theme ---
        # Based on 'clam' theme, but with specific overrides
        self.style.theme_create("LightMode", parent="clam", settings={
            "TFrame": {"configure": {"background": "#f0f2f5"}},
            "TLabel": {"configure": {"background": "#f0f2f5", "foreground": "#333333"}},
            "TLabelframe": {"configure": {"background": "#f0f2f5", "foreground": "#333333", "relief": "solid", "bordercolor": "#cccccc"}},
            "TLabelframe.Label": {"configure": {"background": "#f0f2f5", "foreground": "#333333"}},
            "TButton": {"configure": {"background": "#007bff", "foreground": "white", "font": ('Arial', 9, 'bold'), "padding": 6}},
            "TButton:hover": {"configure": {"background": "#0056b3"}},
            "TCheckbutton": {"configure": {"background": "#f0f2f5", "foreground": "#333333"}},
            "TRadiobutton": {"configure": {"background": "#f0f2f5", "foreground": "#333333"}},
            "TCombobox": {"configure": {"fieldbackground": "white", "foreground": "#333333", "selectbackground": "#e0e0e0", "selectforeground": "#333333"}},
            "TEntry": {"configure": {"fieldbackground": "white", "foreground": "#333333"}},
            "TSpinbox": {"configure": {"fieldbackground": "white", "foreground": "#333333"}},
            "TScrollbar": {"configure": {"background": "#e0e0e0", "troughcolor": "#f0f0f0"}},
            "Treeview": {"configure": {"background": "white", "foreground": "#333333", "fieldbackground": "white", "rowheight": 25}},
            "Treeview.Heading": {"configure": {"background": "#607D8B", "foreground": "white", "font": ('Arial', 10, 'bold')}}
        })

        # --- Dark Mode Theme ---
        # Based on 'clam' theme for consistent widget appearance, but with dark colors
        self.style.theme_create("DarkMode", parent="clam", settings={
            "TFrame": {"configure": {"background": "#2c2c2c"}},
            "TLabel": {"configure": {"background": "#2c2c2c", "foreground": "#e0e0e0"}},
            "TLabelframe": {"configure": {"background": "#2c2c2c", "foreground": "#e0e0e0", "relief": "solid", "bordercolor": "#444444"}},
            "TLabelframe.Label": {"configure": {"background": "#2c2c2c", "foreground": "#e0e0e0"}},
            "TButton": {"configure": {"background": "#343a40", "foreground": "#e0e0e0", "font": ('Arial', 9, 'bold'), "padding": 6}},
            "TButton:hover": {"configure": {"background": "#495057"}},
            "TCheckbutton": {"configure": {"background": "#2c2c2c", "foreground": "#e0e0e0"}},
            "TRadiobutton": {"configure": {"background": "#2c2c2c", "foreground": "#e0e0e0"}},
            "TCombobox": {"configure": {"fieldbackground": "#444444", "foreground": "#e0e0e0", "selectbackground": "#666666", "selectforeground": "#e0e0e0", "bordercolor": "#555555"}},
            "TEntry": {"configure": {"fieldbackground": "#444444", "foreground": "#e0e0e0", "bordercolor": "#555555"}},
            "TSpinbox": {"configure": {"fieldbackground": "#444444", "foreground": "#e0e0e0", "bordercolor": "#555555"}},
            "TScrollbar": {"configure": {"background": "#555555", "troughcolor": "#3c3c3c"}},
            "Treeview": {"configure": {"background": "#3c3c3c", "foreground": "#e0e0e0", "fieldbackground": "#3c3c3c", "rowheight": 25}},
            "Treeview.Heading": {"configure": {"background": "#4a4a4a", "foreground": "#e0e0e0", "font": ('Arial', 10, 'bold')}}
        })


    def apply_initial_theme(self):
        """Applies the initial theme based on the dark_mode setting."""
        if self.dark_mode.get():
            self.style.theme_use("DarkMode")
        else:
            self.style.theme_use("LightMode")


    def create_settings_ui(self):
        # Main frame will take on the background from the theme
        self.main_frame = ttk.Frame(self.master_frame)
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Header - using ttk.Label for consistent theming
        ttk.Label(self.main_frame, text="Application Settings",
                  font=('Arial', 24, 'bold')).pack(pady=(10, 20))

        # --- General Settings Section ---
        general_settings_frame = ttk.LabelFrame(self.main_frame, text="General Settings", padding=(15, 10))
        general_settings_frame.pack(fill=X, pady=10, padx=10)
        general_settings_frame.grid_columnconfigure(1, weight=1) # Make entry columns expand

        # Database Path Display
        ttk.Label(general_settings_frame, text="Database Path:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        db_path = self.conn.database if self.conn and hasattr(self.conn, 'database') else "Not connected"
        ttk.Label(general_settings_frame, text=db_path, font=('Arial', 10), foreground='blue').grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Application Theme (Dropdown for available system themes + custom theme status)
        ttk.Label(general_settings_frame, text="Current Base Theme:", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        # Display the active theme, but let dark mode control the custom theme.
        ttk.Label(general_settings_frame, text=self.style.theme_use(), font=('Arial', 10, 'italic')).grid(row=1, column=1, padx=5, pady=5, sticky='ew')


        # Feature 1: Default Module on Startup
        ttk.Label(general_settings_frame, text="Default Startup Module:", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(general_settings_frame, textvariable=self.default_startup_module,
                     values=["Dashboard", "Patients", "Doctors", "Appointments", "Medical Records", "Billing", "Reports", "Settings", "Help"], state="readonly").grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Feature 2: Application Language
        ttk.Label(general_settings_frame, text="Application Language:", font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(general_settings_frame, textvariable=self.app_language,
                     values=["English", "Spanish", "French", "German"], state="readonly").grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        # --- Notification Settings Section ---
        notification_frame = ttk.LabelFrame(self.main_frame, text="Notification Settings", padding=(15, 10))
        notification_frame.pack(fill=X, pady=10, padx=10)
        notification_frame.grid_columnconfigure(1, weight=1)

        # Feature 3: Enable Notifications
        ttk.Checkbutton(notification_frame, text="Enable Application Notifications", variable=self.notifications_enabled).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Feature 4: Notification Frequency
        ttk.Label(notification_frame, text="Frequency:", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(notification_frame, textvariable=self.notification_frequency,
                     values=["Daily", "Weekly", "Monthly", "Disabled"], state="readonly").grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # --- Data & Logging Settings Section ---
        data_logging_frame = ttk.LabelFrame(self.main_frame, text="Data & Logging", padding=(15, 10))
        data_logging_frame.pack(fill=X, pady=10, padx=10)
        data_logging_frame.grid_columnconfigure(1, weight=1)

        # Feature 5: Backup Database
        ttk.Button(data_logging_frame, text="Backup Database", command=self.backup_database).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Feature 6: Restore Database
        ttk.Button(data_logging_frame, text="Restore Database", command=self.restore_database).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Feature 7: Enable Audit Logging
        ttk.Checkbutton(data_logging_frame, text="Enable Detailed Audit Logging", variable=self.audit_logging_enabled).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Feature 8: Log File Max Size
        ttk.Label(data_logging_frame, text="Max Log File Size (MB):", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Spinbox(data_logging_frame, from_=10, to=1000, increment=10, textvariable=self.log_max_size).grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # --- Display & Performance Settings Section ---
        display_perf_frame = ttk.LabelFrame(self.main_frame, text="Display & Performance", padding=(15, 10))
        display_perf_frame.pack(fill=X, pady=10, padx=10)
        display_perf_frame.grid_columnconfigure(1, weight=1)

        # Feature 9: Row Highlighting in Tables
        ttk.Checkbutton(display_perf_frame, text="Enable Row Highlighting in Tables", variable=self.row_highlighting).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Feature 10: Auto-save Interval
        ttk.Label(display_perf_frame, text="Auto-save Interval (minutes):", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Spinbox(display_perf_frame, from_=1, to=60, increment=1, textvariable=self.auto_save_interval).grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Default Report Save Path (with browse button)
        ttk.Label(display_perf_frame, text="Default Report Save Path:", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.report_path_entry = ttk.Entry(display_perf_frame, textvariable=self.report_path)
        self.report_path_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(display_perf_frame, text="Browse", command=self.browse_report_path, width=8).grid(row=2, column=2, padx=(5,0), pady=5, sticky='w')


        # --- Advanced Preferences Section ---
        extra_frame = ttk.LabelFrame(self.main_frame, text="Advanced Preferences", padding=(15, 10))
        extra_frame.pack(fill=X, pady=10, padx=10)
        extra_frame.grid_columnconfigure(1, weight=1)

        # 1. Font Size Selector
        ttk.Label(extra_frame, text="Global Font Size:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=W)
        ttk.Spinbox(extra_frame, from_=8, to=30, textvariable=self.font_size).grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # 2. Enable Notifications (re-used from above, assuming this is a master switch or a different type)
        ttk.Checkbutton(extra_frame, text="Enable All Notifications", variable=self.notifications_var).grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        # 3. Auto Backup
        ttk.Checkbutton(extra_frame, text="Enable Automatic Database Backup", variable=self.backup_var).grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        # 4. Language Selector (re-used from above, assuming this is a global language setting)
        ttk.Label(extra_frame, text="Application Language:", font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky=W)
        ttk.Combobox(extra_frame, textvariable=self.language_var, values=["English", "Swahili", "French", "Spanish"], state="readonly").grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        # 5. User Role (Display Only)
        ttk.Label(extra_frame, text="Current User Role:", font=('Arial', 10, 'bold')).grid(row=4, column=0, padx=5, pady=5, sticky=W)
        ttk.Label(extra_frame, text="Administrator", foreground="green").grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # 6. Startup Page
        ttk.Label(extra_frame, text="Default Startup Page:", font=('Arial', 10, 'bold')).grid(row=5, column=0, padx=5, pady=5, sticky=W)
        ttk.Combobox(extra_frame, textvariable=self.startup_page, values=["Dashboard", "Appointments", "Patients", "Doctors", "Medical Records", "Billing", "Reports"], state="readonly").grid(row=5, column=1, padx=5, pady=5, sticky='ew')

        # 7. Dark Mode Switch
        ttk.Checkbutton(extra_frame, text="Enable Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode).grid(row=6, column=0, columnspan=2, sticky='w', padx=5, pady=10)

        # 8. Check for Updates Button
        ttk.Button(extra_frame, text="Check for Updates", command=self.check_updates).grid(row=7, column=0, columnspan=2, pady=10)

        # 9. Version Display
        ttk.Label(extra_frame, text="App Version: v1.0.3", font=('Arial', 9, 'italic'), foreground="gray").grid(row=8, column=0, columnspan=2, sticky='e', padx=5, pady=5)

        # --- Action Buttons ---
        action_buttons_frame = ttk.Frame(self.main_frame, padding=(10, 5))
        action_buttons_frame.pack(fill=X, pady=20, padx=10)
        action_buttons_frame.columnconfigure(0, weight=1)
        action_buttons_frame.columnconfigure(1, weight=1)

        ttk.Button(action_buttons_frame, text="Save Settings", command=self.save_settings).grid(row=0, column=0, padx=5, sticky='ew')
        ttk.Button(action_buttons_frame, text="Reset All Defaults", command=self.reset_all_defaults).grid(row=0, column=1, padx=5, sticky='ew')


    def load_current_settings(self):
        # In a full application, this method would load settings from a configuration file (e.g., JSON, INI)
        # For this demo, values are initialized with defaults.
        # Example of loading from a hypothetical JSON file:
        # import json
        # try:
        #     with open("app_settings.json", "r") as f:
        #         settings_data = json.load(f)
        #     self.notifications_enabled.set(settings_data.get("notifications_enabled", True))
        #     self.notification_frequency.set(settings_data.get("notification_frequency", "Daily"))
        #     self.app_language.set(settings_data.get("app_language", "English"))
        #     self.audit_logging_enabled.set(settings_data.get("audit_logging_enabled", False))
        #     self.log_max_size.set(settings_data.get("log_max_size_mb", 100))
        #     self.default_startup_module.set(settings_data.get("default_startup_module", "Dashboard"))
        #     self.row_highlighting.set(settings_data.get("row_highlighting_enabled", True))
        #     self.report_path.set(settings_data.get("report_save_path", "./reports"))
        #     self.auto_save_interval.set(settings_data.get("auto_save_interval_minutes", 5))
        #     self.display_record_limit.set(settings_data.get("display_record_limit", 50))
        #     self.font_size.set(settings_data.get("global_font_size", 10))
        #     self.notifications_var.set(settings_data.get("notifications_enabled_master", True)) # Master switch
        #     self.backup_var.set(settings_data.get("auto_backup_enabled", False))
        #     self.language_var.set(settings_data.get("app_language_global", "English")) # Global language
        #     self.startup_page.set(settings_data.get("startup_page", "Dashboard"))
        #     self.dark_mode.set(settings_data.get("dark_mode_enabled", False))
        # except FileNotFoundError:
        #     print("Settings file not found, using default settings.")
        # except Exception as e:
        #     print(f"Error loading settings: {e}, using default settings.")
        pass # Placeholder for actual loading logic

    def reset_all_defaults(self):
        """Resets all settings variables to their initial default values and updates the UI."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset ALL settings to their default values? This cannot be undone for unsaved changes."):
            self.notifications_enabled.set(True)
            self.notification_frequency.set("Daily")
            self.app_language.set("English")
            self.audit_logging_enabled.set(False)
            self.log_max_size.set(100)
            self.default_startup_module.set("Dashboard")
            self.row_highlighting.set(True)
            self.report_path.set("./reports")
            self.auto_save_interval.set(5)
            self.display_record_limit.set(50)
            self.font_size.set(10)
            self.notifications_var.set(True)
            self.backup_var.set(False)
            self.language_var.set("English")
            self.startup_page.set("Dashboard")
            self.dark_mode.set(False) # Reset to light mode

            self.apply_initial_theme() # Apply the light theme

            # Manually update entry fields if necessary (as StringVar doesn't always update visual instantly)
            self.report_path_entry.delete(0, tk.END)
            self.report_path_entry.insert(0, self.report_path.get())

            messagebox.showinfo("Settings Reset", "All settings have been reset to default values.")

    def toggle_dark_mode(self):
        """Switches between LightMode and DarkMode themes."""
        if self.dark_mode.get():
            self.style.theme_use("DarkMode")
        else:
            self.style.theme_use("LightMode")

        # Optional: Apply font size changes here if you want them tied to theme
        # self.apply_font_size()

    def check_updates(self):
        # Simulated check
        messagebox.showinfo("Update Check", "Checking for updates...\n\nYou are using the latest version (v1.0.3).")

    def apply_theme_preview(self, event=None):
        # This method is removed as dark mode now controls the theme directly.
        # You can re-add if you want to allow users to pick other base ttk themes,
        # but it would complicate the light/dark mode logic.
        pass

    def backup_database(self):
        # Ensure the database connection is available
        if not self.conn:
            messagebox.showerror("Backup Error", "Database connection not established.")
            return

        # Ask user for save location
        backup_file = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile=f"hospital_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        if not backup_file:
            return # User cancelled

        try:
            # Create a backup connection to the new file
            backup_conn = sqlite3.connect(backup_file)
            with backup_conn:
                # Use the built-in SQLite backup API
                self.conn.backup(backup_conn)
            backup_conn.close()
            messagebox.showinfo("Backup Successful", f"Database backed up to:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup database: {e}")
            print(f"Backup Error: {e}")

    def restore_database(self):
        if not messagebox.askyesno("Confirm Restore", "Restoring will overwrite your current database. All unsaved changes will be lost and the application will restart. Do you want to continue?"):
            return

        restore_file = filedialog.askopenfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if not restore_file:
            return # User cancelled

        try:
            # Close the current database connection first before attempting to overwrite
            if self.conn:
                self.conn.close()
                print("Original database connection closed for restore.")

            # Overwrite the active hospital.db with the selected backup file
            # self.conn.database holds the path 'hospital.db' which is set in main_menu.py
            shutil.copyfile(restore_file, "hospital.db") # Assuming 'hospital.db' is the current database file name
            messagebox.showinfo("Restore Initiated", "Database restored successfully. The application will now close. Please restart it to load the restored database.")
            self.master_frame.winfo_toplevel().destroy() # Close the main Tkinter window
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore database: {e}")
            print(f"Restore Error: {e}")
            # In case of failure, you might want to try to re-establish the connection
            # or inform the user to manually restart/check db file.
            messagebox.showinfo("Restore Failed", "Please check console for error. You might need to restart the application.")


    def browse_report_path(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.report_path.set(folder_selected)

    def clear_temporary_files(self):
        # This method was not called in the UI but was present. Keeping for completeness.
        if messagebox.askyesno("Clear Temporary Files", "This will remove temporary application files. Do you want to proceed?"):
            # Placeholder for actual file deletion logic. In a real app, you'd delete specific temp files.
            messagebox.showinfo("Success", "Temporary files 'cleared'. (No actual files deleted in this demo)")
            print("Action: Clear Temporary Files (Demo)")

    def save_settings(self):
        # Gather all current settings values
        settings_data = {
            "notifications_enabled": self.notifications_enabled.get(),
            "notification_frequency": self.notification_frequency.get(),
            "app_language": self.app_language.get(),
            "audit_logging_enabled": self.audit_logging_enabled.get(),
            "log_max_size_mb": self.log_max_size.get(),
            "default_startup_module": self.default_startup_module.get(),
            "row_highlighting_enabled": self.row_highlighting.get(),
            "report_save_path": self.report_path.get(),
            "auto_save_interval_minutes": self.auto_save_interval.get(),
            "display_record_limit": self.display_record_limit.get(),
            "global_font_size": self.font_size.get(),
            "notifications_enabled_master": self.notifications_var.get(),
            "auto_backup_enabled": self.backup_var.get(),
            "app_language_global": self.language_var.get(),
            "startup_page": self.startup_page.get(),
            "dark_mode_enabled": self.dark_mode.get()
        }

        # In a real application, you would save `settings_data` to a persistent file (e.g., JSON, INI, custom)
        # For this demo, we'll just print them to the console and show a confirmation.
        print("\n--- Current Settings Saved (Demo) ---")
        for key, value in settings_data.items():
            print(f"{key}: {value}")
        print("-------------------------------------\n")

        messagebox.showinfo("Settings Saved", "Current settings have been 'saved' (not permanently for this demo).")