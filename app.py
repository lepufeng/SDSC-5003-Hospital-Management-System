from flask_cors import CORS
from flask import Flask, jsonify  # 添加 jsonify 导入
import os  # 添加 os 导入用于路径检查

# 导入蓝图
from backend.blueprints import admin_bp, appointments_bp, doctors_bp, patients_bp
from backend.db import get_db_connection, DB_PATH  # 导入 DB_PATH


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
    print(f"✅ 数据库表创建完成！数据库文件位置: {DB_PATH}")


def create_app():
    app = Flask(__name__)
    CORS(app)

    # 只在应用启动时初始化数据库一次
    with app.app_context():
        init_db()

    # 注册蓝图
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(admin_bp)

    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'service': 'hospital_management',
            'database': 'connected',
            'database_path': DB_PATH
        })

    # 添加调试端点
    @app.route('/debug/db')
    def debug_db():
        import sqlite3

        info = {
            'db_exists': os.path.exists(DB_PATH),
            'db_size': os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0,
            'tables': []
        }

        if info['db_exists']:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()

                # 获取所有表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                info['tables'] = [table[0] for table in tables]

                # 获取每个表的记录数
                for table in info['tables']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    info[f'{table}_count'] = count

                conn.close()
            except Exception as e:
                info['error'] = str(e)

        return jsonify(info)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)