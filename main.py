from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
from face_recognition_module import FaceRecognitionSystem
from config import Config
from datetime import datetime, date
import os

# Validate configuration
Config.validate()

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

db = Database(Config.DATABASE_NAME)
face_system = FaceRecognitionSystem()
face_system.load_encodings_from_db(db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/attendance')
def attendance_page():
    return render_template('attendance.html')

@app.route('/records')
def records_page():
    records = db.get_attendance_records()
    return render_template('records.html', records=records)

@app.route('/employees')
def employees_page():
    employees = db.get_all_employees()
    return render_template('employees.html', employees=employees)

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        emp_id = data.get('emp_id')
        name = data.get('name')
        email = data.get('email', '')
        department = data.get('department', '')
        image_data = data.get('image')
        
        if not emp_id or not name or not image_data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        is_valid, validation_msg = face_system.validate_image_quality(image_data)
        if not is_valid:
            return jsonify({'success': False, 'message': validation_msg}), 400
        
        face_encoding, encode_msg = face_system.encode_face_from_image(image_data)
        
        if face_encoding is None:
            return jsonify({'success': False, 'message': encode_msg}), 400
        
        success, message = db.register_employee(emp_id, name, email, department, face_encoding)
        
        if success:
            face_system.load_encodings_from_db(db)
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mark_attendance', methods=['POST'])
def api_mark_attendance():
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image provided'}), 400
        
        emp_id, name, recognition_msg = face_system.recognize_face(image_data)
        
        if emp_id is None:
            return jsonify({'success': False, 'message': recognition_msg}), 400
        
        success, message = db.mark_attendance(emp_id)
        
        if success:
            employee = db.get_employee_by_id(emp_id)
            return jsonify({
                'success': True, 
                'message': message,
                'employee': {
                    'emp_id': employee[0],
                    'name': employee[1],
                    'department': employee[3] if len(employee) > 3 else ''
                }
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/records')
def api_records():
    try:
        date_param = request.args.get('date')
        if date_param:
            records = db.get_attendance_records(date_param)
        else:
            records = db.get_attendance_records()
        
        records_list = []
        for record in records:
            records_list.append({
                'emp_id': record[0],
                'name': record[1],
                'check_in_time': record[2],
                'check_out_time': record[3],
                'date': record[4],
                'status': record[5]
            })
        
        return jsonify({'success': True, 'records': records_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/employees')
def api_employees():
    try:
        employees = db.get_all_employees()
        employees_list = []
        for emp in employees:
            employees_list.append({
                'emp_id': emp[0],
                'name': emp[1],
                'email': emp[2],
                'department': emp[3],
                'registered_date': emp[4]
            })
        
        return jsonify({'success': True, 'employees': employees_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.FLASK_DEBUG)
