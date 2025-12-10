import sqlite3
import pandas as pd
import os

# ================= 配置路径 =================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(CURRENT_DIR), 'hospital.db')
RAW_DATA_DIR = os.path.join(CURRENT_DIR, 'raw_data')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ================= 1. 清理旧表 =================
    print("清理旧数据表")
    cursor.execute("DROP TABLE IF EXISTS billing")
    cursor.execute("DROP TABLE IF EXISTS treatments")
    cursor.execute("DROP TABLE IF EXISTS appointments")
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS doctors")

    # ================= 2. 创建表结构 =================
    print("创建新表结构")

    # Doctors
    cursor.execute("""
                   CREATE TABLE doctors
                   (
                       doctor_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                       first_name       TEXT        NOT NULL,
                       last_name        TEXT        NOT NULL,
                       specialization   TEXT,
                       phone_number     TEXT,
                       years_experience INTEGER,
                       hospital_branch  TEXT,
                       email            TEXT UNIQUE NOT NULL
                   );
                   """)

    # Patients (注意：已移除 email 的 UNIQUE 约束)
    cursor.execute("""
                   CREATE TABLE patients
                   (
                       patient_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                       first_name         TEXT NOT NULL,
                       last_name          TEXT NOT NULL,
                       gender             TEXT,
                       date_of_birth      DATE,
                       contact_number     TEXT,
                       address            TEXT,
                       registration_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       insurance_provider TEXT,
                       insurance_number   TEXT,
                       email              TEXT NOT NULL
                   );
                   """)

    # Appointments
    cursor.execute("""
                   CREATE TABLE appointments
                   (
                       appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                       patient_id       INTEGER NOT NULL,
                       doctor_id        INTEGER NOT NULL,
                       appointment_date DATE    NOT NULL,
                       appointment_time TIME    NOT NULL,
                       reason_for_visit TEXT,
                       status           TEXT DEFAULT 'Scheduled',
                       FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE,
                       FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id) ON DELETE SET NULL
                   );
                   """)

    # Treatments
    cursor.execute("""
                   CREATE TABLE treatments
                   (
                       treatment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                       appointment_id INTEGER NOT NULL,
                       treatment_type TEXT,
                       description    TEXT,
                       cost           REAL    NOT NULL,
                       treatment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id) ON DELETE CASCADE
                   );
                   """)

    # Billing
    cursor.execute("""
                   CREATE TABLE billing
                   (
                       bill_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                       patient_id     INTEGER NOT NULL,
                       treatment_id   INTEGER NOT NULL,
                       bill_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       amount         REAL    NOT NULL,
                       payment_method TEXT,
                       payment_status TEXT      DEFAULT 'Unpaid',
                       FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                       FOREIGN KEY (treatment_id) REFERENCES treatments (treatment_id)
                   );
                   """)

    # ================= 3. 创建索引 (优化部分) =================
    print("创建索引以优化查询速度")

    # 场景：医生查看某一天的排班 (WHERE appointment_date = ?)
    cursor.execute("CREATE INDEX idx_appointment_date ON appointments(appointment_date);")

    # 场景：查询某个病人的所有历史预约 (WHERE patient_id = ?)
    cursor.execute("CREATE INDEX idx_appointment_patient ON appointments(patient_id);")

    # 场景：财务查看所有未支付的账单 (WHERE payment_status = 'Unpaid')
    cursor.execute("CREATE INDEX idx_billing_status ON billing(payment_status);")

    # 场景：根据名字搜索医生 (WHERE last_name = ?)
    cursor.execute("CREATE INDEX idx_doctor_name ON doctors(last_name, first_name);")

    # ================= 4. 导入数据 =================
    print("导入初始数据")

    def import_csv(file_name, table_name):
        file_path = os.path.join(RAW_DATA_DIR, file_name)
        if not os.path.exists(file_path):
            print(f"警告: 找不到文件 {file_name}")
            return

        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()

            # 智能去字母处理 (D001 -> 1)
            id_cols = ['doctor_id', 'patient_id', 'appointment_id', 'treatment_id', 'bill_id']
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
                if col in id_cols and df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.extract(r'(\d+)').astype(float).astype('Int64')

            # 金额处理
            float_cols = ['cost', 'amount']
            for col in float_cols:
                if col in df.columns and df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace('$', '', regex=False)

            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f" {table_name} 导入成功")

        except Exception as e:
            print(f" {table_name} 导入失败: {e}")

    # 按顺序导入
    import_csv('doctors.csv', 'doctors')
    import_csv('patients.csv', 'patients')
    import_csv('appointments.csv', 'appointments')
    import_csv('treatments.csv', 'treatments')
    import_csv('billing.csv', 'billing')

    conn.commit()
    conn.close()
    print("数据库初始化完成！(包含索引优化)")


if __name__ == '__main__':
    init_db()