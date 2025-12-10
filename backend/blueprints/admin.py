from flask import Blueprint, jsonify, request

from backend.db import get_db_connection
from backend.utils import row_to_dict

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    totals = {}
    for table in ["patients", "doctors", "appointments", "treatments", "billing"]:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        totals[table] = count
    conn.close()
    return jsonify(totals)


# Patient management
@admin_bp.route("/admin/patients", methods=["GET"])
def admin_list_patients():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])


@admin_bp.route("/admin/patients/<int:patient_id>", methods=["GET"])
def admin_get_patient(patient_id: int):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(row_to_dict(row))


@admin_bp.route("/admin/patients", methods=["POST"])
def admin_create_patient():
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO patients (first_name, last_name, gender, date_of_birth, contact_number, address, insurance_provider, insurance_number, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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


@admin_bp.route("/admin/patients/<int:patient_id>", methods=["PUT"])
def admin_update_patient(patient_id: int):
    data = request.get_json() or {}
    fields = [
        "first_name",
        "last_name",
        "gender",
        "date_of_birth",
        "contact_number",
        "address",
        "insurance_provider",
        "insurance_number",
        "email",
    ]
    updates = {field: data.get(field) for field in fields if field in data}
    if not updates:
        return jsonify({"error": "No update fields provided"}), 400

    set_clause = ", ".join(f"{field} = ?" for field in updates)
    values = list(updates.values())
    values.append(patient_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE patients SET {set_clause} WHERE patient_id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({"message": "Patient updated"})


@admin_bp.route("/admin/patients/<int:patient_id>", methods=["DELETE"])
def admin_delete_patient(patient_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Patient deleted"})


# Doctor management
@admin_bp.route("/admin/doctors", methods=["GET"])
def admin_list_doctors():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])


@admin_bp.route("/admin/doctors/<int:doctor_id>", methods=["GET"])
def admin_get_doctor(doctor_id: int):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Doctor not found"}), 404
    return jsonify(row_to_dict(row))


@admin_bp.route("/admin/doctors", methods=["POST"])
def admin_create_doctor():
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO doctors (first_name, last_name, specialization, phone_number, years_experience, hospital_branch, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("first_name"),
            data.get("last_name"),
            data.get("specialization"),
            data.get("phone_number"),
            data.get("years_experience"),
            data.get("hospital_branch"),
            data.get("email"),
        ),
    )
    conn.commit()
    doctor_id = cursor.lastrowid
    conn.close()
    return jsonify({"doctor_id": doctor_id}), 201


@admin_bp.route("/admin/doctors/<int:doctor_id>", methods=["PUT"])
def admin_update_doctor(doctor_id: int):
    data = request.get_json() or {}
    fields = [
        "first_name",
        "last_name",
        "specialization",
        "phone_number",
        "years_experience",
        "hospital_branch",
        "email",
    ]
    updates = {field: data.get(field) for field in fields if field in data}
    if not updates:
        return jsonify({"error": "No update fields provided"}), 400

    set_clause = ", ".join(f"{field} = ?" for field in updates)
    values = list(updates.values())
    values.append(doctor_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE doctors SET {set_clause} WHERE doctor_id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({"message": "Doctor updated"})


@admin_bp.route("/admin/doctors/<int:doctor_id>", methods=["DELETE"])
def admin_delete_doctor(doctor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Doctor deleted"})


# Appointment management
@admin_bp.route("/admin/appointments", methods=["GET"])
def admin_list_appointments():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT a.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name,
               d.first_name AS doctor_first_name, d.last_name AS doctor_last_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])


@admin_bp.route("/admin/appointments/<int:appointment_id>", methods=["GET"])
def admin_get_appointment(appointment_id: int):
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT a.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name,
               d.first_name AS doctor_first_name, d.last_name AS doctor_last_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = ?
        """,
        (appointment_id,),
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify(row_to_dict(row))


@admin_bp.route("/admin/appointments/<int:appointment_id>", methods=["PUT"])
def admin_update_appointment(appointment_id: int):
    data = request.get_json() or {}
    fields = [
        "appointment_date",
        "appointment_time",
        "reason_for_visit",
        "status",
        "doctor_id",
        "patient_id",
    ]
    updates = {field: data.get(field) for field in fields if field in data}
    if not updates:
        return jsonify({"error": "No update fields provided"}), 400

    set_clause = ", ".join(f"{field} = ?" for field in updates)
    values = list(updates.values())
    values.append(appointment_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE appointments SET {set_clause} WHERE appointment_id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({"message": "Appointment updated"})


# Billing management
@admin_bp.route("/admin/billing", methods=["GET"])
def admin_list_billing():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT b.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name
        FROM billing b
        JOIN patients p ON b.patient_id = p.patient_id
        ORDER BY b.bill_date DESC
        """
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(row) for row in rows])


@admin_bp.route("/admin/billing/<int:bill_id>", methods=["GET"])
def admin_get_bill(bill_id: int):
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT b.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name
        FROM billing b
        JOIN patients p ON b.patient_id = p.patient_id
        WHERE b.bill_id = ?
        """,
        (bill_id,),
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Bill not found"}), 404
    return jsonify(row_to_dict(row))


@admin_bp.route("/admin/billing/<int:bill_id>", methods=["PUT"])
def admin_update_bill(bill_id: int):
    data = request.get_json() or {}
    fields = ["amount", "payment_method", "payment_status", "treatment_id", "patient_id"]
    updates = {field: data.get(field) for field in fields if field in data}
    if not updates:
        return jsonify({"error": "No update fields provided"}), 400

    set_clause = ", ".join(f"{field} = ?" for field in updates)
    values = list(updates.values())
    values.append(bill_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE billing SET {set_clause} WHERE bill_id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({"message": "Bill updated"})
