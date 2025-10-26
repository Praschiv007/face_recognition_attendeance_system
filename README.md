# Face Recognition Attendance System

An automated employee attendance tracking system using face recognition technology built with Python, Flask, and OpenCV.

## Features

- **Employee Registration**: Register new employees with their face data
- **Automated Attendance**: Mark attendance using face recognition
- **Check-in/Check-out**: Automatic tracking of entry and exit times
- **Attendance Records**: View and filter attendance history
- **Employee Management**: View all registered employees
- **Real-time Face Detection**: Uses OpenCV's Haar Cascade and LBPH Face Recognizer
- **Web-based Interface**: Easy-to-use browser-based application

## Technology Stack

- **Backend**: Python 3.11, Flask
- **Face Recognition**: OpenCV (Haar Cascade + LBPH Face Recognizer)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Camera Access**: WebRTC getUserMedia API

## How It Works

1. **Registration**: New employees provide their ID, name, and other details, then capture their face photo
2. **Face Encoding**: The system detects and encodes facial features using OpenCV
3. **Attendance Marking**: Employees look at the camera to check in/out
4. **Recognition**: The system compares the captured face with stored encodings
5. **Recording**: Check-in and check-out times are automatically recorded

## Project Structure

```
.
├── main.py                      # Flask application and routes
├── database.py                  # Database operations and schema
├── face_recognition_module.py   # Face recognition logic
├── templates/                   # HTML templates
│   ├── index.html              # Home page
│   ├── register.html           # Employee registration
│   ├── attendance.html         # Mark attendance
│   ├── records.html            # View attendance records
│   └── employees.html          # View employees
├── static/
│   ├── css/
│   │   └── style.css           # Stylesheet
│   └── js/
│       ├── register.js         # Registration page logic
│       ├── attendance.js       # Attendance marking logic
│       └── records.js          # Records filtering logic
└── attendance.db               # SQLite database (auto-created)
```

## Database Schema

### Employees Table
- `id`: Primary key
- `emp_id`: Unique employee ID
- `name`: Employee name
- `email`: Email address
- `department`: Department name
- `face_encoding`: Encoded face data (BLOB)
- `registered_date`: Registration timestamp

### Attendance Table
- `id`: Primary key
- `emp_id`: Employee ID (foreign key)
- `check_in_time`: Check-in timestamp
- `check_out_time`: Check-out timestamp
- `date`: Attendance date
- `status`: Attendance status

## Usage

### Register New Employee
1. Navigate to "Register Employee"
2. Fill in employee details (ID, name, email, department)
3. Click "Start Camera" to activate webcam
4. Click "Capture Photo" when ready
5. Click "Register Employee" to save

### Mark Attendance
1. Navigate to "Mark Attendance"
2. Click "Start Camera"
3. Position your face in the camera view
4. Click "Mark Attendance"
5. System will recognize and record your attendance

### View Records
1. Navigate to "View Records"
2. Use date filter to view specific dates
3. See check-in/check-out times for all employees

## Security Features

- Face encodings are stored securely in the database
- No plain face images are stored
- Session management for web application
- Input validation on all forms

## Browser Requirements

- Modern browser with webcam support (Chrome, Firefox, Safari, Edge)
- HTTPS or localhost (required for camera access)
- JavaScript enabled

## Notes

- First capture of the day = Check-in
- Second capture of the day = Check-out
- Ensure good lighting for better recognition accuracy
- Only one person should be visible during capture
- Face should be clearly visible and unobstructed

## Future Enhancements

- Export attendance reports to CSV/Excel
- Email notifications for check-in/out
- Dashboard with statistics and analytics
- Multi-factor authentication
- Mobile app support
- Cloud storage integration
