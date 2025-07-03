# display_appointments.py
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import threading

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not found. Text-to-speech functionality will be disabled.")
except Exception as e:
    TTS_AVAILABLE = False
    print(f"Warning: Error initializing pyttsx3: {e}. Text-to-speech functionality will be disabled.")

class DisplayAppointments:
    def __init__(self, master_frame, conn, c):
        self.master_frame = master_frame
        self.conn = conn
        self.c = c

        for widget in self.master_frame.winfo_children():
            widget.destroy()

        self.main_frame = Frame(self.master_frame, bg='#e0f0f0')
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        Label(self.main_frame, text="Today's Scheduled Appointments",
              font=('Arial', 36, 'bold'), fg='#004d40', bg='#e0f0f0').pack(pady=(20, 40))

        self.appointment_display_frame = Frame(self.main_frame, bg='#ffffff', relief=RAISED, bd=2, padx=30, pady=30)
        self.appointment_display_frame.pack(pady=30, padx=50, fill=X, expand=False)

        self.num_label = Label(self.appointment_display_frame, text="Loading...", font=('Arial', 70, 'bold'), fg='#00796b', bg='#ffffff')
        self.num_label.pack(pady=(0,10))

        self.patient_label = Label(self.appointment_display_frame, text="", font=('Arial', 30, 'bold'), fg='#333333', bg='#ffffff')
        self.patient_label.pack(pady=(0,5))

        self.doctor_label = Label(self.appointment_display_frame, text="", font=('Arial', 24), fg='#555555', bg='#ffffff')
        self.doctor_label.pack(pady=(0,5))

        self.time_label = Label(self.appointment_display_frame, text="", font=('Arial', 24), fg='#555555', bg='#ffffff')
        self.time_label.pack(pady=(0,20))

        self.button_frame = Frame(self.main_frame, bg='#e0f0f0')
        self.button_frame.pack(pady=40)

        self.prev_btn = ttk.Button(self.button_frame, text="⬅️ Previous", command=self.prev_appointment, state=DISABLED, width=18)
        self.prev_btn.pack(side=LEFT, padx=15)

        self.next_btn = ttk.Button(self.button_frame, text="Next ➡️", command=self.next_appointment, width=18)
        self.next_btn.pack(side=LEFT, padx=15)

        self.complete_btn = ttk.Button(self.button_frame, text="✅ Mark Completed", command=self.mark_completed, width=22)
        self.complete_btn.pack(side=LEFT, padx=15)

        self.engine = None
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.engine.getProperty('rate') - 50)
            except Exception as e:
                print(f"Error initializing pyttsx3 engine: {e}")
                self.engine = None
                TTS_AVAILABLE = False

        self.load_appointments()
        self.current_index = 0

        self.update_display()

    def load_appointments(self):
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            self.c.execute('''SELECT a.appointment_id, p.name, d.name, strftime('%H:%M', a.scheduled_time)
                           FROM appointments a
                           JOIN patients p ON a.patient_id = p.patient_id
                           JOIN doctors d ON a.doctor_id = d.doctor_id
                           WHERE date(a.scheduled_time) = ? AND a.status = 'Scheduled'
                           ORDER BY a.scheduled_time ASC''', (today,))
            self.appointments = self.c.fetchall()
            if not self.appointments:
                self.current_index = 0
            elif self.current_index >= len(self.appointments):
                 self.current_index = len(self.appointments) - 1 if self.appointments else 0

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Error loading appointments: {e}\nEnsure 'appointments', 'patients', and 'doctors' tables exist.")
            print(f"Error loading appointments: {e}")
            self.appointments = []
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading appointments: {e}")
            print(f"An unexpected error occurred while loading appointments: {e}")
            self.appointments = []

    def update_display(self):
        if not self.appointments:
            self.num_label.config(text="No")
            self.patient_label.config(text="Appointments")
            self.doctor_label.config(text="Scheduled for Today")
            self.time_label.config(text="")
            self.prev_btn.config(state=DISABLED)
            self.next_btn.config(state=DISABLED)
            self.complete_btn.config(state=DISABLED)
            self.speak("No appointments scheduled for today.")
            return

        if self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(self.appointments):
            self.current_index = len(self.appointments) - 1

        appt_id, patient, doctor, time = self.appointments[self.current_index]

        self.num_label.config(text=f"#{appt_id}")
        self.patient_label.config(text=patient)
        self.doctor_label.config(text=f"With Dr. {doctor}")
        self.time_label.config(text=f"At {time}")

        self.prev_btn.config(state=NORMAL if self.current_index > 0 else DISABLED)
        self.next_btn.config(state=NORMAL if self.current_index < len(self.appointments) - 1 else DISABLED)
        self.complete_btn.config(state=NORMAL)

        self.speak(f"Next: Appointment number {appt_id}, {patient}, with Doctor {doctor}, at {time}")

    def next_appointment(self):
        if self.current_index < len(self.appointments) - 1:
            self.current_index += 1
            self.update_display()
        else:
            messagebox.showinfo("End of List", "You are at the last appointment for today.")

    def prev_appointment(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
        else:
            messagebox.showinfo("Start of List", "You are at the first appointment for today.")

    def mark_completed(self):
        if not self.appointments:
            messagebox.showwarning("No Appointment", "There is no appointment to mark as completed.")
            return

        appt_id = self.appointments[self.current_index][0]

        if not messagebox.askyesno("Confirm Completion", f"Are you sure you want to mark Appointment #{appt_id} as completed?"):
            return

        try:
            self.c.execute("UPDATE appointments SET status='Completed' WHERE appointment_id=?", (appt_id,))
            self.conn.commit()
            messagebox.showinfo("Success", f"Appointment #{appt_id} marked as completed.")

            del self.appointments[self.current_index]

            if self.current_index >= len(self.appointments) and self.appointments:
                self.current_index = len(self.appointments) - 1
            elif not self.appointments:
                self.current_index = 0

            self.update_display()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update appointment status: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def speak(self, text):
        if TTS_AVAILABLE and self.engine:
            def run_speak():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Error during text-to-speech: {e}")
            threading.Thread(target=run_speak, daemon=True).start()
        else:
            print(f"TTS (Text-to-Speech) unavailable or failed to initialize. Could not speak: '{text}'")