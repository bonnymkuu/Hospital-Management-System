import tkinter as tk
from tkinter import ttk, messagebox, Frame, Label, Button, BOTH, X, W, E, filedialog # Import filedialog
import sqlite3
import shutil # For file copying in restore
from datetime import datetime # For timestamping backups

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

        self.create_settings_ui()
        self.load_current_settings() # In a real app, this would load saved settings

    def create_settings_ui(self):
        self.main_frame = Frame(self.master_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Header
        ttk.Label(self.main_frame, text="Application Settings",
                  font=('Arial', 24, 'bold'), foreground='#333333', background='#f8f8f8').pack(pady=(10, 20))

        # --- General Settings Section ---
        general_settings_frame = ttk.LabelFrame(self.main_frame, text="General Settings", padding=(10, 10))
        general_settings_frame.pack(fill=X, pady=10, padx=10)

        # Database Path Display (existing)
        ttk.Label(general_settings_frame, text="Database Path:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        db_path = self.conn.database if self.conn and hasattr(self.conn, 'database') else "Not connected"
        ttk.Label(general_settings_frame, text=db_path, font=('Arial', 10), foreground='blue').grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Application Theme (existing, updated to list all available themes)
        ttk.Label(general_settings_frame, text="Application Theme:", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.theme_var = tk.StringVar(value="Default (Clam)") # Retain for UI, but populate from actual themes
        self.theme_combo = ttk.Combobox(general_settings_frame, textvariable=self.theme_var,
                                         values=ttk.Style().theme_names()) # Populate with all available ttk themes
        self.theme_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.theme_combo.set(ttk.Style().theme_use()) # Set current theme as default selection
        self.theme_combo.bind("<<ComboboxSelected>>", self.apply_theme_preview)

        # Feature 1: Default Module on Startup
        ttk.Label(general_settings_frame, text="Default Startup Module:", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(general_settings_frame, textvariable=self.default_startup_module,
                     values=["Dashboard", "Patients", "Doctors", "Appointments", "Medical Records", "Billing", "Reports", "Settings", "Help"]).grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Feature 2: Application Language
        ttk.Label(general_settings_frame, text="Application Language:", font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(general_settings_frame, textvariable=self.app_language,
                     values=["English", "Spanish", "French", "German"]).grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        general_settings_frame.grid_columnconfigure(1, weight=1) # Make entry columns expand

        # --- Notification Settings Section ---
        notification_frame = ttk.LabelFrame(self.main_frame, text="Notification Settings", padding=(10, 10))
        notification_frame.pack(fill=X, pady=10, padx=10)

        # Feature 3: Enable Notifications
        ttk.Checkbutton(notification_frame, text="Enable Application Notifications", variable=self.notifications_enabled).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Feature 4: Notification Frequency
        ttk.Label(notification_frame, text="Frequency:", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(notification_frame, textvariable=self.notification_frequency,
                     values=["Daily", "Weekly", "Monthly", "Disabled"]).grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        notification_frame.grid_columnconfigure(1, weight=1)

        # --- Data & Logging Settings Section ---
        data_logging_frame = ttk.LabelFrame(self.main_frame, text="Data & Logging", padding=(10, 10))
        data_logging_frame.pack(fill=X, pady=10, padx=10)

        # Feature 5: Backup Database
        ttk.Button(data_logging_frame, text="Backup Database", command=self.backup_database).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Feature 6: Restore Database
        ttk.Button(data_logging_frame, text="Restore Database", command=self.restore_database).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Feature 7: Enable Audit Logging
        ttk.Checkbutton(data_logging_frame, text="Enable Detailed Audit Logging", variable=self.audit_logging_enabled).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Feature 8: Log File Max Size
        ttk.Label(data_logging_frame, text="Max Log File Size (MB):", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Spinbox(data_logging_frame, from_=10, to=1000, increment=10, textvariable=self.log_max_size).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        data_logging_frame.grid_columnconfigure(1, weight=1)

        # --- Display & Performance Settings Section ---
        display_perf_frame = ttk.LabelFrame(self.main_frame, text="Display & Performance", padding=(10, 10))
        display_perf_frame.pack(fill=X, pady=10, padx=10)

        # Feature 9: Row Highlighting in Tables
        ttk.Checkbutton(display_perf_frame, text="Enable Row Highlighting in Tables", variable=self.row_highlighting).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Feature 10: Auto-save Interval
        ttk.Label(display_perf_frame, text="Auto-save Interval (minutes):", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Spinbox(display_perf_frame, from_=1, to=60, increment=1, textvariable=self.auto_save_interval).grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        display_perf_frame.grid_columnconfigure(1, weight=1)

        # Default Report Save Path (existing, now with browse button)
        ttk.Label(display_perf_frame, text="Default Report Save Path:", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.report_path_entry = ttk.Entry(display_perf_frame, textvariable=self.report_path)
        self.report_path_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(display_perf_frame, text="Browse", command=self.browse_report_path).grid(row=2, column=2, padx=5, pady=5, sticky='w')


        # --- Action Buttons ---
        action_buttons_frame = Frame(self.main_frame, bg='#f8f8f8')
        action_buttons_frame.pack(fill=X, pady=20, padx=10)
        action_buttons_frame.columnconfigure(0, weight=1)
        action_buttons_frame.columnconfigure(1, weight=1)

        # Extra Settings
        extra_frame = ttk.LabelFrame(self.main_frame, text="Advanced Preferences", padding=(10, 10))
        extra_frame.pack(fill=X, pady=10, padx=10)

        # 1. Font Size Selector
        ttk.Label(extra_frame, text="Font Size:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.font_size = tk.IntVar(value=12)
        ttk.Spinbox(extra_frame, from_=8, to=30, textvariable=self.font_size).grid(row=0, column=1, padx=5, pady=5, sticky=E)

        # 2. Enable Notifications
        self.notifications_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(extra_frame, text="Enable Notifications", variable=self.notifications_var).grid(row=1, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        # 3. Auto Backup
        self.backup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(extra_frame, text="Enable Auto Backup", variable=self.backup_var).grid(row=2, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        # 4. Language Selector
        ttk.Label(extra_frame, text="Language:", font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.language_var = tk.StringVar(value="English")
        ttk.Combobox(extra_frame, textvariable=self.language_var, values=["English", "Swahili", "French", "Spanish"]).grid(row=3, column=1, padx=5, pady=5, sticky=E)

        # 5. User Role (Display Only)
        ttk.Label(extra_frame, text="User Role:", font=('Arial', 10, 'bold')).grid(row=4, column=0, padx=5, pady=5, sticky=W)
        ttk.Label(extra_frame, text="Administrator", foreground="green").grid(row=4, column=1, padx=5, pady=5, sticky=E)

        # 6. Reset to Default Button
        ttk.Button(extra_frame, text="Reset to Default", command=self.reset_defaults).grid(row=5, column=0, columnspan=2, pady=10)

        # 7. Startup Page
        ttk.Label(extra_frame, text="Startup Page:", font=('Arial', 10, 'bold')).grid(row=6, column=0, padx=5, pady=5, sticky=W)
        self.startup_page = tk.StringVar(value="Dashboard")
        ttk.Combobox(extra_frame, textvariable=self.startup_page, values=["Dashboard", "Appointments", "Reports", "Settings"]).grid(row=6, column=1, padx=5, pady=5, sticky=E)

        # 8. Dark Mode
        self.dark_mode = tk.BooleanVar()
        ttk.Checkbutton(extra_frame, text="Enable Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode).grid(row=7, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        # 9. Check for Updates Button
        ttk.Button(extra_frame, text="Check for Updates", command=self.check_updates).grid(row=8, column=0, columnspan=2, pady=10)

        # 10. Version Display
        ttk.Label(extra_frame, text="App Version: v1.0.3", font=('Arial', 9, 'italic'), foreground="gray").grid(row=9, column=0, columnspan=2, sticky=E, padx=5, pady=5)

        ttk.Button(action_buttons_frame, text="Save Settings", command=self.save_settings).grid(row=0, column=0, padx=5, sticky='ew')
        ttk.Button(action_buttons_frame, text="Reset to Defaults", command=self.reset_to_defaults).grid(row=0, column=1, padx=5, sticky='ew')


    def load_current_settings(self):
        # In a full application, this method would load settings from a configuration file (e.g., JSON, INI)
        # For this demo, values are initialized with defaults, so this method serves as a placeholder.
        # Example of loading:
        # try:
        #     with open("app_settings.json", "r") as f:
        #         settings_data = json.load(f)
        #     self.notifications_enabled.set(settings_data.get("notifications_enabled", True))
        #     self.notification_frequency.set(settings_data.get("notification_frequency", "Daily"))
        #     # ... load other settings
        # except FileNotFoundError:
        #     print("Settings file not found, using default settings.")
        pass

    def reset_defaults(self):
        self.report_path_entry.delete(0, tk.END)
        self.report_path_entry.insert(0, "./reports")
        self.theme_var.set("Default (Clam)")
        self.font_size.set(12)
        self.notifications_var.set(True)
        self.backup_var.set(False)
        self.language_var.set("English")
        self.startup_page.set("Dashboard")
        self.dark_mode.set(False)
        messagebox.showinfo("Defaults Restored", "All settings have been reset to default.")

    def toggle_dark_mode(self):
        if self.dark_mode.get():
            self.main_frame.configure(bg="#2c2c2c")
        else:
            self.main_frame.configure(bg="#f8f8f8")

    def check_updates(self):
        # Simulated check
        messagebox.showinfo("Update Check", "You are using the latest version.")

    def apply_theme_preview(self, event=None):
        selected_theme = self.theme_var.get()
        style = ttk.Style()
        try:
            style.theme_use(selected_theme)
            # messagebox.showinfo("Theme Preview", f"Theme set to: {selected_theme}") # Optional: show a small info box
        except Exception as e:
            messagebox.showerror("Theme Error", f"Could not apply theme: {e}")
            print(f"Error applying theme: {e}")

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
        if messagebox.askyesno("Clear Temporary Files", "This will remove temporary application files. Do you want to proceed?"):
            # Placeholder for actual file deletion logic. In a real app, you'd delete specific temp files.
            messagebox.showinfo("Success", "Temporary files 'cleared'. (No actual files deleted in this demo)")
            print("Action: Clear Temporary Files (Demo)")

    def reset_to_defaults(self):
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to their default values?"):
            # Reset all internal variables to their initial values
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

            # Update UI elements to reflect new values
            self.theme_var.set("Default (Clam)") # Reset theme dropdown
            ttk.Style().theme_use('clam') # Apply default theme visually

            # Update entry widgets manually if not directly linked to StringVar (like self.report_path_entry)
            self.report_path_entry.delete(0, tk.END)
            self.report_path_entry.insert(0, self.report_path.get())

            messagebox.showinfo("Settings Reset", "All settings have been reset to their default values.")
            print("Action: Settings Reset to Defaults (Demo)")


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
            "application_theme": self.theme_var.get()
        }

        # In a real application, you would save `settings_data` to a persistent file (e.g., JSON, INI, custom)
        # For this demo, we'll just print them to the console and show a confirmation.
        print("\n--- Current Settings Saved (Demo) ---")
        for key, value in settings_data.items():
            print(f"{key}: {value}")
        print("-------------------------------------\n")

        messagebox.showinfo("Settings Saved", "Current settings have been 'saved' (not permanently for this demo).")