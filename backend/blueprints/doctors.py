from flask import Blueprint, jsonify
from datetime import datetime

from backend.db import get_db_connection
from backend.utils import row_to_dict

doctors_bp = Blueprint("doctors", __name__)


@doctors_bp.route("/doctors", methods=["GET"])
def list_doctors():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])


# 获取单个医生信息
@doctors_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id: int):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,)
    ).fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Doctor not found"}), 404
    
    return jsonify(row_to_dict(row))


# 获取医生今日排班
@doctors_bp.route("/doctors/<int:doctor_id>/schedule", methods=["GET"])
def doctor_schedule(doctor_id: int):
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT a.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name,
               p.contact_number AS patient_contact
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.doctor_id = ? AND a.appointment_date = ?
        ORDER BY a.appointment_time ASC
        """,
        (doctor_id, today),
    ).fetchall()
    conn.close()
    
    return jsonify([row_to_dict(row) for row in rows])


# 添加：获取医生的所有预约（用于统计）
@doctors_bp.route("/doctors/<int:doctor_id>/appointments", methods=["GET"])
def doctor_all_appointments(doctor_id: int):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT a.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """,
        (doctor_id,),
    ).fetchall()
    conn.close()
    
    return jsonify([row_to_dict(row) for row in rows])


# 获取医生的所有患者
@doctors_bp.route("/doctors/<int:doctor_id>/patients", methods=["GET"])
def doctor_patients(doctor_id: int):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT p.*, a.appointment_id, a.appointment_date, a.appointment_time, a.status,
               t.treatment_id, t.treatment_type, t.description, t.cost, t.treatment_date
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN treatments t ON a.appointment_id = t.appointment_id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """,
        (doctor_id,),
    ).fetchall()
    conn.close()

    patients = {}
    for row in rows:
        patient_id = row["patient_id"]
        if patient_id not in patients:
            patients[patient_id] = {
                "patient": {
                    "patient_id": row["patient_id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "gender": row["gender"],
                    "date_of_birth": row["date_of_birth"],
                    "contact_number": row["contact_number"],
                    "address": row["address"],
                    "insurance_provider": row["insurance_provider"],
                    "insurance_number": row["insurance_number"],
                    "email": row["email"],
                },
                "appointments": [],
            }

        appointment_entry = {
            "appointment_id": row["appointment_id"],
            "appointment_date": row["appointment_date"],
            "appointment_time": row["appointment_time"],
            "status": row["status"],
            "treatments": [],
        }
        if row["treatment_id"]:
            appointment_entry["treatments"].append(
                {
                    "treatment_id": row["treatment_id"],
                    "treatment_type": row["treatment_type"],
                    "description": row["description"],
                    "cost": row["cost"],
                    "treatment_date": row["treatment_date"],
                }
            )

        existing = patients[patient_id]["appointments"]
        merged = next((a for a in existing if a["appointment_id"] == row["appointment_id"]), None)
        if merged:
            merged["treatments"].extend(appointment_entry["treatments"])
        else:
            patients[patient_id]["appointments"].append(appointment_entry)

    return jsonify(list(patients.values()))