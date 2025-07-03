from tkinter import *
from tkinter import messagebox
import sqlite3, pyttsx3
from datetime import datetime

class Application:
    def __init__(self, master):
        self.master = master
        self.main_frame = Frame(master)
        self.main_frame.pack(fill=BOTH, expand=True)
        self.master.title("Appointment Display")
        
        # Database connection
        self.conn = sqlite3.connect('hospital.db')
        self.c = self.conn.cursor()
        
        # Get today's appointments
        today = datetime.now().strftime("%Y-%m-%d")
        self.c.execute('''SELECT a.appointment_id, p.name, d.name, time(a.scheduled_time)
                       FROM appointments a
                       JOIN patients p ON a.patient_id = p.patient_id
                       JOIN doctors d ON a.doctor_id = d.doctor_id
                       WHERE date(a.scheduled_time) = ? AND a.status = 'Scheduled'
                       ORDER BY a.scheduled_time''', (today,))
        self.appointments = self.c.fetchall()
        self.current_index = 0
        
        # UI Elements
        self.main_frame = Frame(self.master, bg='white')
        self.main_frame.pack(fill=BOTH, expand=True)
        
        Label(self.main_frame, text="Today's Appointments",
              font=('arial', 50, 'bold'), fg='green', bg='white').pack(pady=20)
        
        # Current appointment display
        self.appointment_frame = Frame(self.main_frame, bg='white')
        self.appointment_frame.pack(pady=50)
        
        self.num_label = Label(self.appointment_frame, font=('arial', 100, 'bold'), bg='white')
        self.num_label.pack()
        
        self.patient_label = Label(self.appointment_frame, font=('arial', 40, 'bold'), bg='white')
        self.patient_label.pack()
        
        self.doctor_label = Label(self.appointment_frame, font=('arial', 30), bg='white')
        self.doctor_label.pack()
        
        self.time_label = Label(self.appointment_frame, font=('arial', 30), bg='white')
        self.time_label.pack()
        
        # Navigation buttons
        self.button_frame = Frame(self.main_frame, bg='white')
        self.button_frame.pack(pady=30)
        
        self.prev_btn = Button(self.button_frame, text="Previous", width=15, height=2,
                             command=self.prev_appointment, state=DISABLED)
        self.prev_btn.pack(side=LEFT, padx=20)
        
        self.next_btn = Button(self.button_frame, text="Next", width=15, height=2,
                             command=self.next_appointment)
        self.next_btn.pack(side=LEFT, padx=20)
        
        self.complete_btn = Button(self.button_frame, text="Mark Completed", width=15, height=2,
                                 command=self.mark_completed, bg='green', fg='white')
        self.complete_btn.pack(side=LEFT, padx=20)
        
        # Show first appointment
        if self.appointments:
            self.show_appointment()
        else:
            self.num_label.config(text="No")
            self.patient_label.config(text="Appointments")
            self.doctor_label.config(text="Today")
            self.next_btn.config(state=DISABLED)
            self.complete_btn.config(state=DISABLED)
    
    def show_appointment(self):
        if not self.appointments:
            return
        
        appt_id, patient, doctor, time = self.appointments[self.current_index]
        self.num_label.config(text=f"#{appt_id}")
        self.patient_label.config(text=patient)
        self.doctor_label.config(text=f"With Dr. {doctor}")
        self.time_label.config(text=f"At {time}")
        
        # Update button states
        self.prev_btn.config(state=NORMAL if self.current_index > 0 else DISABLED)
        self.next_btn.config(state=NORMAL if self.current_index < len(self.appointments)-1 else DISABLED)
        
        # Announce the appointment
        self.speak(f"Appointment number {appt_id}, {patient}, with Doctor {doctor}, at {time}")
    
    def next_appointment(self):
        if self.current_index < len(self.appointments)-1:
            self.current_index += 1
            self.show_appointment()
    
    def prev_appointment(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_appointment()
    
    def mark_completed(self):
        if not self.appointments:
            return
        
        appt_id = self.appointments[self.current_index][0]
        try:
            self.c.execute("UPDATE appointments SET status='Completed' WHERE appointment_id=?", (appt_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Appointment marked as completed")
            
            # Remove from display list
            del self.appointments[self.current_index]
            
            # Adjust index if needed
            if self.current_index >= len(self.appointments):
                self.current_index = max(0, len(self.appointments)-1)
            
            # Show next or update display
            if self.appointments:
                self.show_appointment()
            else:
                self.num_label.config(text="No")
                self.patient_label.config(text="Appointments")
                self.doctor_label.config(text="Remaining")
                self.next_btn.config(state=DISABLED)
                self.prev_btn.config(state=DISABLED)
                self.complete_btn.config(state=DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update appointment: {str(e)}")
    
    def speak(self, text):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', engine.getProperty('rate') - 50)
            engine.say(text)
            engine.runAndWait()
        except:
            pass  # Text-to-speech not essential
    
    def __del__(self):
        self.conn.close()