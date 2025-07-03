import tkinter as tk
from tkinter import ttk, messagebox, Frame, Label, Button, Scrollbar, VERTICAL, CENTER, RIGHT, Y, BOTH, END, LEFT, X
import sqlite3
from datetime import datetime, timedelta # Import timedelta
import calendar # Import calendar for month names

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Dashboard:
    def __init__(self, parent_frame, conn, c):
        self.parent_frame = parent_frame
        self.conn = conn
        self.c = c

        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.create_dashboard_ui()

    def create_dashboard_ui(self):
        """Builds the UI for the dashboard."""
        # Main container for the dashboard content
        container = Frame(self.parent_frame, bg='#f0f2f5') # Lighter background
        container.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Header
        Label(container, text="Hospital Dashboard",
              font=('Arial', 24, 'bold'), bg='#f0f2f5', fg='#333333').pack(pady=20)

        # Top section for statistics cards
        stats_frame = Frame(container, bg='#f0f2f5')
        stats_frame.pack(fill=X, pady=10)
        self.display_statistics(stats_frame)

        # Middle section for graphs (using a grid for better layout)
        graphs_frame = Frame(container, bg='#f0f2f5')
        graphs_frame.pack(fill=BOTH, expand=True, pady=10)
        graphs_frame.grid_columnconfigure(0, weight=1)
        graphs_frame.grid_columnconfigure(1, weight=1)
        graphs_frame.grid_rowconfigure(0, weight=1)
        graphs_frame.grid_rowconfigure(1, weight=1)

        self.display_graphs(graphs_frame)

        # Bottom section for tables (also using a grid)
        tables_frame = Frame(container, bg='#f0f2f5')
        tables_frame.pack(fill=BOTH, expand=True, pady=10)
        tables_frame.grid_columnconfigure(0, weight=1)
        tables_frame.grid_columnconfigure(1, weight=1)
        tables_frame.grid_rowconfigure(0, weight=1) # Only one row for tables in this example

        self.display_tables(tables_frame)

    def display_statistics(self, parent_frame):
        """Displays the key statistics cards with rounded borders."""
        stats = [
            ("Total Patients", "SELECT COUNT(*) FROM patients", "#4CAF50"), # Green
            ("Total Doctors", "SELECT COUNT(*) FROM doctors", "#2196F3"), # Blue
            ("Today's Appointments", "SELECT COUNT(*) FROM appointments WHERE appointment_date = date('now') AND status = 'Scheduled'", "#FF9800"), # Orange
            ("Pending Bills", "SELECT COUNT(*) FROM billing WHERE status != 'Paid'", "#F44336") # Red
        ]

        for i in range(len(stats)):
            parent_frame.columnconfigure(i, weight=1)

        for i, (title, query, color) in enumerate(stats):
            count = "N/A"
            try:
                self.c.execute(query)
                count = self.c.fetchone()[0]
            except sqlite3.OperationalError as e:
                print(f"Warning: Could not fetch stat for '{title}' due to missing table or column: {e}")
                count = "Error"
            except Exception as e:
                print(f"An unexpected error occurred for '{title}': {e}")
                count = "Error"

            card_canvas = tk.Canvas(parent_frame, bg=parent_frame['bg'], highlightthickness=0)
            card_canvas.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Draw a rounded rectangle on the canvas initially
            rect = card_canvas.create_rectangle(5, 5, 1, 1, outline=color, fill=color, width=2)

            # Bind to the canvas's <Configure> event to resize the rectangle
            card_canvas.bind("<Configure>",
                             lambda event, c=card_canvas, r=rect:
                             c.coords(r, 5, 5, event.width-5, event.height-5))


            # Content frame for labels, placed on top of the canvas
            stat_card_content = Frame(card_canvas, bg=color, padx=15, pady=15)
            stat_card_content.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.95, relheight=0.95)

            Label(stat_card_content, text=title, font=('Arial', 12, 'bold'),
                  bg=color, fg='white').pack()
            Label(stat_card_content, text=str(count), font=('Arial', 28, 'bold'),
                  bg=color, fg='white').pack(pady=5)

            # Bind click event to the content frame (which covers most of the card)
            stat_card_content.bind("<Button-1>", lambda e, q=query: self.show_card_details(title, q))
            # Also bind to the canvas itself for clicks outside the content frame
            card_canvas.bind("<Button-1>", lambda e, q=query: self.show_card_details(title, q))

    def show_card_details(self, title, query):
        """Displays a message box with details for a clicked card."""
        details = ""
        try:
            if "COUNT" in query.upper(): # Simple check for count queries
                self.c.execute(query)
                count = self.c.fetchone()[0]
                details = f"Total {title.lower()}: {count}"
            else:
                details = f"Details for {title} (query: {query})" # Fallback
        except Exception as e:
            details = f"Could not fetch details: {e}"
        messagebox.showinfo(f"{title} Details", details)


    def display_graphs(self, parent_frame):
        """Displays different types of graphs with data from the database."""
        # Graph 1: Patients by Gender (Pie Chart)
        gender_labels, gender_sizes = self.get_patients_by_gender()
        self.create_pie_chart(parent_frame, row=0, column=0,
                              title="Patients by Gender",
                              labels=gender_labels,
                              sizes=gender_sizes)

        # Graph 2: Monthly Appointments (Bar Chart)
        appt_months, appt_counts = self.get_monthly_appointments()
        self.create_bar_chart(parent_frame, row=0, column=1,
                              title="Last 6 Months Appointments",
                              x_labels=appt_months,
                              values=appt_counts)

        # Graph 3: Doctor Specialization Distribution (Bar Chart)
        spec_labels, spec_counts = self.get_doctor_specializations()
        self.create_bar_chart(parent_frame, row=1, column=0,
                              title="Doctor Specializations",
                              x_labels=spec_labels,
                              values=spec_counts,
                              color='#9C27B0') # Purple

        # Graph 4: Revenue Trend (Line Chart)
        revenue_months, revenue_amounts = self.get_monthly_revenue()
        self.create_line_chart(parent_frame, row=1, column=1,
                               title="Last 6 Months Revenue (Ksh)",
                               x_labels=revenue_months,
                               values=revenue_amounts)


    def get_patients_by_gender(self):
        """Fetches patient count by gender from the database."""
        labels = []
        sizes = []
        try:
            self.c.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
            rows = self.c.fetchall()
            if rows:
                for gender, count in rows:
                    if gender: # Ensure gender is not None or empty
                        labels.append(gender)
                        sizes.append(count)
                # Handle cases where some genders might be missing from the data
                # For example, if only Male and Female are present, but 'Other' is a desired label.
                # This simple approach only includes existing genders.
            else:
                labels = ['No Data']
                sizes = [1] # A small placeholder to make the chart render
        except sqlite3.OperationalError as e:
            print(f"DB Error (get_patients_by_gender): {e}")
            labels = ['DB Error']
            sizes = [1]
        except Exception as e:
            print(f"Error (get_patients_by_gender): {e}")
            labels = ['Error']
            sizes = [1]
        return labels, sizes

    def get_monthly_appointments(self):
        """Fetches appointment counts per month for the last 6 months."""
        months = []
        counts = []
        try:
            today = datetime.now()
            for i in range(6): # Last 6 months including current
                target_month = today - timedelta(days=30 * (5 - i)) # Approx. 30 days per month
                month_start = target_month.replace(day=1)
                # Find the last day of the month
                if target_month.month == 12:
                    month_end = target_month.replace(month=1, year=target_month.year + 1, day=1) - timedelta(days=1)
                else:
                    month_end = target_month.replace(month=target_month.month + 1, day=1) - timedelta(days=1)

                month_name = calendar.month_abbr[target_month.month]
                year_abbr = str(target_month.year)[-2:] # '24' for 2024

                self.c.execute(
                    "SELECT COUNT(*) FROM appointments WHERE appointment_date BETWEEN ? AND ?",
                    (month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d"))
                )
                count = self.c.fetchone()[0]
                months.append(f"{month_name}'{year_abbr}")
                counts.append(count)
        except sqlite3.OperationalError as e:
            print(f"DB Error (get_monthly_appointments): {e}")
            months = ['Error'] * 6
            counts = [0] * 6
        except Exception as e:
            print(f"Error (get_monthly_appointments): {e}")
            months = ['Error'] * 6
            counts = [0] * 6
        return months, counts

    def get_doctor_specializations(self):
        """Fetches doctor counts by specialization from the database."""
        labels = []
        counts = []
        try:
            self.c.execute("SELECT specialization, COUNT(*) FROM doctors GROUP BY specialization")
            rows = self.c.fetchall()
            if rows:
                for spec, count in rows:
                    if spec: # Ensure specialization is not None or empty
                        labels.append(spec)
                        counts.append(count)
            else:
                labels = ['No Data']
                counts = [1]
        except sqlite3.OperationalError as e:
            print(f"DB Error (get_doctor_specializations): {e}")
            labels = ['DB Error']
            counts = [1]
        except Exception as e:
            print(f"Error (get_doctor_specializations): {e}")
            labels = ['Error']
            counts = [1]
        return labels, counts

    def get_monthly_revenue(self):
        """Fetches total paid revenue per month for the last 6 months."""
        months = []
        amounts = []
        try:
            today = datetime.now()
            for i in range(6): # Last 6 months including current
                target_month = today - timedelta(days=30 * (5 - i)) # Approx. 30 days per month
                month_start = target_month.replace(day=1)
                # Find the last day of the month
                if target_month.month == 12:
                    month_end = target_month.replace(month=1, year=target_month.year + 1, day=1) - timedelta(days=1)
                else:
                    month_end = target_month.replace(month=target_month.month + 1, day=1) - timedelta(days=1)

                month_name = calendar.month_abbr[target_month.month]
                year_abbr = str(target_month.year)[-2:] # '24' for 2024

                self.c.execute(
                    "SELECT SUM(amount) FROM billing WHERE status = 'Paid' AND bill_date BETWEEN ? AND ?",
                    (month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d"))
                )
                total_amount = self.c.fetchone()[0]
                months.append(f"{month_name}'{year_abbr}")
                amounts.append(total_amount if total_amount is not None else 0) # Handle None for SUM

        except sqlite3.OperationalError as e:
            print(f"DB Error (get_monthly_revenue): {e}")
            months = ['Error'] * 6
            amounts = [0] * 6
        except Exception as e:
            print(f"Error (get_monthly_revenue): {e}")
            months = ['Error'] * 6
            amounts = [0] * 6
        return months, amounts

    def create_pie_chart(self, parent, row, column, title, labels, sizes):
        """Creates a pie chart and embeds it in the Tkinter frame."""
        fig, ax = plt.subplots(figsize=(4, 3), dpi=80) # Smaller figure size
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(title, fontsize=12)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        canvas.draw()

    def create_bar_chart(self, parent, row, column, title, x_labels, values, color='#1ABC9C'):
        """Creates a bar chart and embeds it in the Tkinter frame."""
        fig, ax = plt.subplots(figsize=(4, 3), dpi=80)
        ax.bar(x_labels, values, color=color)
        ax.set_title(title, fontsize=12)
        ax.tick_params(axis='x', rotation=45) # Rotate labels if needed
        plt.tight_layout() # Adjust layout to prevent labels from overlapping

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        canvas.draw()

    def create_line_chart(self, parent, row, column, title, x_labels, values, color='#3498db'):
        """Creates a line chart and embeds it in the Tkinter frame."""
        fig, ax = plt.subplots(figsize=(4, 3), dpi=80)
        ax.plot(x_labels, values, marker='o', linestyle='-', color=color)
        ax.set_title(title, fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        canvas.draw()

    def display_tables(self, parent_frame):
        """Displays multiple small tables."""
        # Table 1: Recent Appointments
        recent_appt_frame = Frame(parent_frame, bg='white', bd=1, relief="solid")
        recent_appt_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.display_recent_appointments(recent_appt_frame)

        # Table 2: Patients with Pending Bills (Dummy/Simplified)
        pending_bills_frame = Frame(parent_frame, bg='white', bd=1, relief="solid")
        pending_bills_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.display_patients_with_pending_bills(pending_bills_frame)

    def display_recent_appointments(self, parent_frame):
        """Displays a table of recent appointments."""
        Label(parent_frame, text="Recent Appointments",
              font=('Arial', 14, 'bold'), bg='white', fg='#333333').pack(pady=5)

        style = ttk.Style()
        style.configure("Dashboard.Treeview.Heading", font=('Arial', 9, 'bold'), background='#607D8B', foreground='white') # Darker header
        style.configure("Dashboard.Treeview", font=('Arial', 9), rowheight=20)


        columns = ("Patient", "Doctor", "Date", "Status")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=6, style="Dashboard.Treeview")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER)
            if col == "Patient" or col == "Doctor":
                tree.column(col, width=100)
            else:
                tree.column(col, width=70)


        scrollbar = ttk.Scrollbar(parent_frame, orient=VERTICAL, command=tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill=BOTH, expand=True, padx=5, pady=5)

        try:
            self.c.execute('''
                SELECT p.name, d.name, a.appointment_date, a.status
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                ORDER BY a.appointment_date DESC, a.appointment_time DESC LIMIT 8
            ''')
            rows = self.c.fetchall()
            if rows:
                for row in rows:
                    tree.insert("", END, values=row)
            else:
                tree.insert("", END, values=("", "No recent appointments", "", ""))

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Could not fetch recent appointments: {e}")
            tree.insert("", END, values=("", "Error loading", "", ""))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            tree.insert("", END, values=("", "Unexpected Error", "", ""))


    def display_patients_with_pending_bills(self, parent_frame):
        """Displays a table of patients with pending bills."""
        Label(parent_frame, text="Patients with Pending Bills",
              font=('Arial', 14, 'bold'), bg='white', fg='#333333').pack(pady=5)

        style = ttk.Style()
        style.configure("Dashboard.Treeview.Heading", font=('Arial', 9, 'bold'), background='#607D8B', foreground='white')
        style.configure("Dashboard.Treeview", font=('Arial', 9), rowheight=20)

        columns = ("Patient", "Amount", "Status")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=6, style="Dashboard.Treeview")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER)
            if col == "Patient":
                tree.column(col, width=120)
            else:
                tree.column(col, width=80)

        scrollbar = ttk.Scrollbar(parent_frame, orient=VERTICAL, command=tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill=BOTH, expand=True, padx=5, pady=5)

        try:
            self.c.execute('''
                SELECT p.name, b.amount, b.status
                FROM billing b
                JOIN patients p ON b.patient_id = p.patient_id
                WHERE b.status = 'Pending' OR b.status = 'Partially Paid'
                ORDER BY b.bill_date DESC LIMIT 8
            ''')
            rows = self.c.fetchall()
            if rows:
                for row in rows:
                    tree.insert("", END, values=row)
            else:
                tree.insert("", END, values=("", "No pending bills", ""))
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Could not fetch pending bills: {e}")
            tree.insert("", END, values=("", "Error loading", ""))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            tree.insert("", END, values=("", "Unexpected Error", ""))