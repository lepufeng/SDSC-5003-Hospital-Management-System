# SDSC5003-Hostpital-Management-System
This project is a group project assignment of Cityu University of Hong Kong (Dongguan) SDSC5003

```mermaid
erDiagram
    Doctors ||--o{ Appointments : "has"
    Patients ||--o{ Appointments : "makes"
    Patients ||--o{ Billing : "receives"
    Appointments ||--o{ Treatments : "contains"
    Treatments ||--o{ Billing : "generates"

    Doctors {
        int doctor_id PK
        string first_name
        string last_name
        string specialization
        string phone_number
        int years_experience
        string hospital_branch
        string email
    }

    Patients {
        int patient_id PK
        string first_name
        string last_name
        string gender
        date date_of_birth
        string contact_number
        string address
        timestamp registration_date
        string insurance_provider
        string insurance_number
        string email
    }

    Appointments {
        int appointment_id PK
        int patient_id FK
        int doctor_id FK
        date appointment_date
        time appointment_time
        string reason_for_visit
        string status
    }

    Treatments {
        int treatment_id PK
        int appointment_id FK
        string treatment_type
        string description
        float cost
        timestamp treatment_date
    }

    Billing {
        int bill_id PK
        int patient_id FK
        int treatment_id FK
        timestamp bill_date
        float amount
        string payment_method
        string payment_status
    }