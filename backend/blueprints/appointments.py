from flask import Blueprint, jsonify, request

from backend.db import get_db_connection

appointments_bp = Blueprint("appointments", __name__)


@appointments_bp.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json() or {}
    required_fields = ["patient_id", "doctor_id", "appointment_date", "appointment_time"]
    if not all(data.get(field) for field in required_fields):
        return (
            jsonify(
                {"error": "patient_id, doctor_id, appointment_date, appointment_time are required"}
            ),
            400,
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason_for_visit, status)
        VALUES (?, ?, ?, ?, ?, COALESCE(?, 'scheduled'))
        """,
        (
            data.get("patient_id"),
            data.get("doctor_id"),
            data.get("appointment_date"),
            data.get("appointment_time"),
            data.get("reason_for_visit"),
            data.get("status"),
        ),
    )
    conn.commit()
    appointment_id = cursor.lastrowid
    conn.close()
    return jsonify({"appointment_id": appointment_id}), 201


@appointments_bp.route("/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id: int):
    data = request.get_json() or {}
    fields = [
        "appointment_date",
        "appointment_time",
        "reason_for_visit",
        "status",
        "doctor_id",
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


@appointments_bp.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def cancel_appointment(appointment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appointments SET status = 'cancelled' WHERE appointment_id = ?",
        (appointment_id,),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Appointment cancelled"})


@appointments_bp.route("/appointments/<int:appointment_id>/status", methods=["PUT"])
def update_appointment_status(appointment_id: int):
    data = request.get_json() or {}
    status = data.get("status")
    if not status:
        return jsonify({"error": "status is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appointments SET status = ? WHERE appointment_id = ?",
        (status, appointment_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated"})
