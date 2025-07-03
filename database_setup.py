import sqlite3

def setup_database():
    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()
    
    # Patients table
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                address TEXT,
                phone TEXT,
                blood_type TEXT,
                allergies TEXT,
                registration_date TEXT)''')
    
    # Doctors table
    c.execute('''CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT,
                phone TEXT,
                email TEXT,
                department TEXT)''')
    
    # Appointments table (enhanced from your original)
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                scheduled_time TEXT,
                status TEXT DEFAULT 'Scheduled',
                purpose TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id))''')
    
    # Medical records table
    c.execute('''CREATE TABLE IF NOT EXISTS medical_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                date TEXT,
                diagnosis TEXT,
                treatment TEXT,
                prescription TEXT,
                notes TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id))''')
    
    # Billing table
    c.execute('''CREATE TABLE IF NOT EXISTS billing (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                amount REAL,
                date_issued TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'Unpaid',
                service_description TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id))''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()