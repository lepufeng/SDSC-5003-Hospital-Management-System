from flask_cors import CORS
from flask import Flask

from backend.blueprints import admin_bp, appointments_bp, doctors_bp, patients_bp
from backend.db import get_db_connection


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            specialization TEXT,
            phone_number TEXT,
            years_experience INTEGER,
            hospital_branch TEXT,
            email TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            gender TEXT,
            date_of_birth TEXT,
            contact_number TEXT,
            address TEXT,
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            insurance_provider TEXT,
            insurance_number TEXT,
            email TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason_for_visit TEXT,
            status TEXT DEFAULT 'scheduled',
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
            FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS treatments (
            treatment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            treatment_type TEXT,
            description TEXT,
            cost REAL,
            treatment_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS billing (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            treatment_id INTEGER,
            bill_date TEXT DEFAULT CURRENT_TIMESTAMP,
            amount REAL NOT NULL,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'unpaid',
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
            FOREIGN KEY(treatment_id) REFERENCES treatments(treatment_id) ON DELETE SET NULL
        );
        """
    )

    conn.commit()
    conn.close()


def create_app():
    app = Flask(__name__)
    CORS(app)
    @app.before_request
    def ensure_db_initialized():
        init_db()

    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000) 
