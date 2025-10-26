import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_name='attendance.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                department TEXT,
                face_encoding BLOB NOT NULL,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT NOT NULL,
                check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_out_time TIMESTAMP,
                date DATE NOT NULL,
                status TEXT DEFAULT 'present',
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_employee(self, emp_id, name, email, department, face_encoding):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO employees (emp_id, name, email, department, face_encoding)
                VALUES (?, ?, ?, ?, ?)
            ''', (emp_id, name, email, department, face_encoding))
            conn.commit()
            return True, "Employee registered successfully"
        except sqlite3.IntegrityError:
            return False, "Employee ID already exists"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    def get_all_employees(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT emp_id, name, email, department, registered_date FROM employees')
        employees = cursor.fetchall()
        conn.close()
        return employees
    
    def get_employee_encodings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT emp_id, name, face_encoding FROM employees')
        employees = cursor.fetchall()
        conn.close()
        return employees
    
    def mark_attendance(self, emp_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT * FROM attendance 
            WHERE emp_id = ? AND date = ?
        ''', (emp_id, today))
        
        existing_record = cursor.fetchone()
        
        if existing_record:
            if existing_record[3] is None:
                cursor.execute('''
                    UPDATE attendance 
                    SET check_out_time = CURRENT_TIMESTAMP 
                    WHERE emp_id = ? AND date = ?
                ''', (emp_id, today))
                conn.commit()
                conn.close()
                return True, "Check-out recorded successfully"
            else:
                conn.close()
                return False, "Attendance already marked for today"
        else:
            cursor.execute('''
                INSERT INTO attendance (emp_id, date)
                VALUES (?, ?)
            ''', (emp_id, today))
            conn.commit()
            conn.close()
            return True, "Check-in recorded successfully"
    
    def get_attendance_records(self, date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if date:
            cursor.execute('''
                SELECT a.emp_id, e.name, a.check_in_time, a.check_out_time, a.date, a.status
                FROM attendance a
                JOIN employees e ON a.emp_id = e.emp_id
                WHERE a.date = ?
                ORDER BY a.check_in_time DESC
            ''', (date,))
        else:
            cursor.execute('''
                SELECT a.emp_id, e.name, a.check_in_time, a.check_out_time, a.date, a.status
                FROM attendance a
                JOIN employees e ON a.emp_id = e.emp_id
                ORDER BY a.date DESC, a.check_in_time DESC
            ''')
        
        records = cursor.fetchall()
        conn.close()
        return records
    
    def get_employee_by_id(self, emp_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT emp_id, name, email, department FROM employees WHERE emp_id = ?', (emp_id,))
        employee = cursor.fetchone()
        conn.close()
        return employee
