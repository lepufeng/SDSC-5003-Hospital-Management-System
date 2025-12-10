# API Guide

This file gives a quick tour of the hospital backend APIs. Everything returns JSON and is grouped by Blueprint so you know which module owns which routes:
- `/patients` — patient signup plus their appointments, treatments, and bills
- `/doctors` — doctor directory and doctor-centric views
- `/appointments` — create, update, cancel, or change status
- `/admin` — dashboard stats plus CRUD for patients, doctors, appointments, and billing

Dates and times are plain strings like `YYYY-MM-DD` and `HH:MM`.

## Patient-side

### Sign up a patient
- **URL**: `/patients/register`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "first_name": "Emily",
    "last_name": "Smith",
    "gender": "female",
    "date_of_birth": "1984-10-12",
    "contact_number": "8228188767",
    "address": "321 Maple Dr",
    "insurance_provider": "PulseSecure",
    "insurance_number": "INS354079",
    "email": "emily.smith@mail.com"
  }
  ```
  `first_name` and `last_name` are required.
- **Response** (`201 Created`):
  ```json
  { "patient_id": 1 }
  ```
> Served by the `patients` Blueprint.

### Get doctors
- **URL**: `/doctors`
- **Method**: `GET`
- **Response** (`200 OK`): Array of doctors.
> Served by the `doctors` Blueprint.

### Book an appointment
- **URL**: `/appointments`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "patient_id": 1,
    "doctor_id": 2,
    "appointment_date": "2024-06-01",
    "appointment_time": "09:30",
    "reason_for_visit": "Annual physical"
  }
  ```
- **Response** (`201 Created`):
  ```json
  { "appointment_id": 10 }
  ```
> Served by the `appointments` Blueprint.

### Update an appointment
- **URL**: `/appointments/{appointment_id}`
- **Method**: `PUT`
- **Request Body (example)**:
  ```json
  {
    "appointment_date": "2024-06-02",
    "appointment_time": "10:00",
    "reason_for_visit": "Need to reschedule",
    "status": "rescheduled",
    "doctor_id": 3
  }
  ```
  You can change any field that makes sense for your case.
- **Response** (`200 OK`): `{ "message": "Appointment updated" }`
> Served by the `appointments` Blueprint.

### Cancel an appointment
- **URL**: `/appointments/{appointment_id}`
- **Method**: `DELETE`
- **Response** (`200 OK`): `{ "message": "Appointment cancelled" }`
> Served by the `appointments` Blueprint.

### See my appointments
- **URL**: `/patients/{patient_id}/appointments`
- **Method**: `GET`
- **Response** (`200 OK`): Array of appointments with doctor info and status.
> Served by the `patients` Blueprint.

### See my treatments
- **URL**: `/patients/{patient_id}/treatments`
- **Method**: `GET`
- **Response** (`200 OK`): Array of treatment records.
> Served by the `patients` Blueprint.

### See my bills
- **URL**: `/patients/{patient_id}/billing`
- **Method**: `GET`
- **Response** (`200 OK`): Array of billing items.
> Served by the `patients` Blueprint.

## Doctor-side

### See my patients (with history)
- **URL**: `/doctors/{doctor_id}/patients`
- **Method**: `GET`
- **Response** (`200 OK`):
  ```json
  [
    {
      "patient": { "patient_id": 1, "first_name": "Emily", "last_name": "Smith", ... },
      "appointments": [
        {
          "appointment_id": 10,
          "appointment_date": "2024-06-01",
          "appointment_time": "09:30",
          "status": "scheduled",
          "treatments": [
            {
              "treatment_id": 5,
              "treatment_type": "Checkup",
              "description": "Blood pressure test",
              "cost": 50.0,
              "treatment_date": "2024-06-01 10:00:00"
            }
          ]
        }
      ]
    }
  ]
  ```
> Served by the `doctors` Blueprint.

### Update appointment status
- **URL**: `/appointments/{appointment_id}/status`
- **Method**: `PUT`
- **Request Body**:
  ```json
  { "status": "completed" }
  ```
- **Response** (`200 OK`): `{ "message": "Status updated" }`
> Served by the `appointments` Blueprint.

## Admin-side

### Dashboard snapshot
- **URL**: `/admin/dashboard`
- **Method**: `GET`
- **Response** (`200 OK`):
  ```json
  { "patients": 30, "doctors": 10, "appointments": 50, "treatments": 20, "billing": 18 }
  ```
> Served by the `admin` Blueprint.

### Patient management
- List: `GET /admin/patients`
- Detail: `GET /admin/patients/{patient_id}`
- Create: `POST /admin/patients` (same fields as patient signup)
- Update: `PUT /admin/patients/{patient_id}` (send only the fields you want to change)
- Delete: `DELETE /admin/patients/{patient_id}`

### Doctor management
- List: `GET /admin/doctors`
- Detail: `GET /admin/doctors/{doctor_id}`
- Create: `POST /admin/doctors`
  ```json
  {
    "first_name": "Michael",
    "last_name": "Johnson",
    "specialization": "Internal Medicine",
    "phone_number": "9019443432",
    "years_experience": 8,
    "hospital_branch": "Downtown Campus",
    "email": "michael.johnson@mail.com"
  }
  ```
- Update: `PUT /admin/doctors/{doctor_id}` (send only fields to edit)
- Delete: `DELETE /admin/doctors/{doctor_id}`

### Appointment management
- List: `GET /admin/appointments`
- Detail: `GET /admin/appointments/{appointment_id}`
- Update: `PUT /admin/appointments/{appointment_id}` (you can change `appointment_date`, `appointment_time`, `reason_for_visit`, `status`, `doctor_id`, `patient_id`)

### Billing management
- List: `GET /admin/billing`
- Detail: `GET /admin/billing/{bill_id}`
- Update: `PUT /admin/billing/{bill_id}` (you can change `amount`, `payment_method`, `payment_status`, `treatment_id`, `patient_id`)
