from flask import Blueprint, jsonify, request

from backend.db import get_db_connection
from backend.utils import row_to_dict

patients_bp = Blueprint("patients", __name__)


@patients_bp.route("/patients/register", methods=["POST"])
def register_patient():
    data = request.get_json() or {}
    required_fields = ["first_name", "last_name"]
    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "first_name and last_name are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO patients (
            first_name, last_name, gender, date_of_birth, contact_number, address,
            insurance_provider, insurance_number, email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("first_name"),
            data.get("last_name"),
            data.get("gender"),
            data.get("date_of_birth"),
            data.get("contact_number"),
            data.get("address"),
            data.get("insurance_provider"),
            data.get("insurance_number"),
            data.get("email"),
        ),
    )
    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return jsonify({"patient_id": patient_id}), 201


@patients_bp.route("/patients/<int:patient_id>/appointments", methods=["GET"])
def patient_appointments(patient_id: int):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT a.*, d.first_name AS doctor_first_name, d.last_name AS doctor_last_name, d.specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """,
        (patient_id,),
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])


@patients_bp.route("/patients/<int:patient_id>/treatments", methods=["GET"])
def patient_treatments(patient_id: int):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT t.*
        FROM treatments t
        JOIN appointments a ON t.appointment_id = a.appointment_id
        WHERE a.patient_id = ?
        ORDER BY t.treatment_date DESC
        """,
        (patient_id,),
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])


@patients_bp.route("/patients/<int:patient_id>/billing", methods=["GET"])
def patient_billing(patient_id: int):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT b.*
        FROM billing b
        WHERE b.patient_id = ?
        ORDER BY b.bill_date DESC
        """,
        (patient_id,),
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])
 # 在 patient_billing 函数后面添加以下代码：

@patients_bp.route("/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id: int):
    """获取单个患者信息"""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?",
        (patient_id,)
    ).fetchone()
    conn.close()
    
    if row is None:
        return jsonify({"error": "Patient not found"}), 404
    
    return jsonify(row_to_dict(row))
