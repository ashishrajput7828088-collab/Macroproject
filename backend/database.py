import sqlite3
from datetime import datetime, timezone
from config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def init_tables():
    conn = get_db()
    cur = conn.cursor()

    # 1. Hospitals Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        category TEXT DEFAULT 'Multispeciality',
        address TEXT NOT NULL,
        locality TEXT DEFAULT 'Gwalior',
        phone TEXT NOT NULL,
        emergency_phone TEXT NOT NULL,
        ambulance_phone TEXT DEFAULT '108',
        email TEXT DEFAULT '',
        website TEXT DEFAULT '',
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        emergency_24x7 INTEGER NOT NULL DEFAULT 1,
        trauma_center INTEGER NOT NULL DEFAULT 0,
        rating REAL NOT NULL DEFAULT 4.5,
        reviews_count INTEGER NOT NULL DEFAULT 120,
        opd_timings TEXT DEFAULT '09:00 AM - 05:00 PM',
        consultation_fee INTEGER NOT NULL DEFAULT 500,
        description TEXT DEFAULT '',
        verified INTEGER NOT NULL DEFAULT 1,
        active INTEGER NOT NULL DEFAULT 1,
        source TEXT NOT NULL DEFAULT 'real',
        osm_id TEXT,
        updated_at TEXT
    )""")

    hospital_columns = {row["name"] for row in cur.execute("PRAGMA table_info(hospitals)")}
    if "photo_url" not in hospital_columns:
        cur.execute("ALTER TABLE hospitals ADD COLUMN photo_url TEXT DEFAULT ''")
    if "photo_credit" not in hospital_columns:
        cur.execute("ALTER TABLE hospitals ADD COLUMN photo_credit TEXT DEFAULT ''")

    # 2. Services / Departments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE CASCADE,
        service TEXT NOT NULL
    )""")

    # 3. Beds Breakdown
    cur.execute("""
    CREATE TABLE IF NOT EXISTS beds (
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE CASCADE,
        bed_type TEXT NOT NULL,
        total INTEGER NOT NULL DEFAULT 0,
        occupied INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(hospital_id, bed_type)
    )""")

    # 4. Doctors Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        qualification TEXT NOT NULL,
        specialty TEXT NOT NULL,
        category TEXT NOT NULL,
        experience_years INTEGER NOT NULL DEFAULT 10,
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE SET NULL,
        hospital_name TEXT NOT NULL,
        clinic_address TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT DEFAULT '',
        opd_timings TEXT NOT NULL,
        days_available TEXT DEFAULT 'Mon - Sat',
        fee INTEGER NOT NULL DEFAULT 500,
        rating REAL NOT NULL DEFAULT 4.8,
        reviews_count INTEGER NOT NULL DEFAULT 150,
        badge TEXT DEFAULT 'Verified Specialist',
        about TEXT DEFAULT '',
        avatar TEXT DEFAULT '👨‍⚕️'
    )""")
    doctor_columns = {row["name"] for row in cur.execute("PRAGMA table_info(doctors)")}
    if "verified" not in doctor_columns:
        cur.execute("ALTER TABLE doctors ADD COLUMN verified INTEGER NOT NULL DEFAULT 1")

    # 5. Blood Banks Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_banks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE SET NULL,
        address TEXT NOT NULL,
        contact_person TEXT DEFAULT 'Blood Bank Officer',
        phone TEXT NOT NULL,
        emergency_24x7 INTEGER NOT NULL DEFAULT 1,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        verified INTEGER NOT NULL DEFAULT 1
    )""")

    # 6. Blood Units Inventory
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_inventory (
        blood_bank_id INTEGER REFERENCES blood_banks(id) ON DELETE CASCADE,
        blood_group TEXT NOT NULL,
        units_available INTEGER NOT NULL DEFAULT 10,
        last_updated TEXT,
        PRIMARY KEY(blood_bank_id, blood_group)
    )""")

    # 7. Ambulances Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ambulances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        vehicle_type TEXT NOT NULL, -- 'ALS (Advanced Life Support)', 'BLS', 'Patient Transport', 'Mobile ICU'
        operator_type TEXT NOT NULL, -- 'Government', 'Hospital', 'Private'
        phone TEXT NOT NULL,
        base_location TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        available INTEGER NOT NULL DEFAULT 1,
        features TEXT DEFAULT 'Oxygen Cylinder, Cardiac Monitor, Defibrillator, Ventilator'
    )""")

    # 8. Appointments Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_id TEXT UNIQUE NOT NULL,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        patient_name TEXT NOT NULL,
        patient_phone TEXT NOT NULL,
        patient_age INTEGER NOT NULL DEFAULT 30,
        patient_gender TEXT NOT NULL DEFAULT 'Not specified',
        problem_description TEXT DEFAULT '',
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE SET NULL,
        hospital_name TEXT NOT NULL,
        doctor_id INTEGER REFERENCES doctors(id) ON DELETE SET NULL,
        doctor_name TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        consultation_type TEXT NOT NULL DEFAULT 'In-Clinic OPD',
        status TEXT NOT NULL DEFAULT 'Confirmed',
        fee INTEGER NOT NULL DEFAULT 500,
        payment_status TEXT NOT NULL DEFAULT 'Pay at Hospital',
        created_at TEXT NOT NULL
    )""")

    # 9. Patient Users Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        gender TEXT DEFAULT '',
        blood_group TEXT DEFAULT '',
        emergency_contact TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )""")

    # 10. Emergency SOS Dispatches
    cur.execute("""
    CREATE TABLE IF NOT EXISTS emergency_sos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sos_code TEXT UNIQUE NOT NULL,
        caller_name TEXT DEFAULT 'Emergency Caller',
        caller_phone TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        location_address TEXT DEFAULT 'Gwalior',
        emergency_type TEXT NOT NULL DEFAULT 'General Medical Emergency',
        status TEXT NOT NULL DEFAULT 'Dispatched',
        assigned_ambulance TEXT DEFAULT '108 Gwalior Rapid Response',
        created_at TEXT NOT NULL
    )""")

    # 11. Reviews Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER REFERENCES hospitals(id) ON DELETE CASCADE,
        doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
        patient_name TEXT NOT NULL,
        rating INTEGER NOT NULL DEFAULT 5,
        review_text TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")

    # 12. Admin Users Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL
    )""")

    # 13. Blood Donors Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_name TEXT NOT NULL,
        donor_phone TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        city TEXT DEFAULT 'Gwalior',
        age INTEGER DEFAULT 25,
        last_donated TEXT,
        registered_at TEXT NOT NULL
    )""")

    # 14. Blood Requests Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        units_needed INTEGER NOT NULL DEFAULT 1,
        hospital_name TEXT NOT NULL,
        contact_phone TEXT NOT NULL,
        urgency TEXT DEFAULT 'Urgent',
        status TEXT DEFAULT 'Open',
        created_at TEXT NOT NULL
    )""")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_tables()
    print("All enterprise database tables verified and ready!")
