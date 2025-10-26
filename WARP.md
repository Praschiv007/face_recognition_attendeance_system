# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview
Face Recognition Attendance System - An automated employee attendance tracking system using OpenCV face recognition (Haar Cascade + LBPH), Flask backend, and SQLite database.

## Development Commands

### Running the Application
```bash
python main.py
```
The application runs on `http://0.0.0.0:5000` by default.

### Installing Dependencies
This project appears to use `uv` for dependency management. Install required packages:
```bash
pip install flask opencv-contrib-python pillow numpy
```

Note: `opencv-contrib-python` is required (not just `opencv-python`) as it includes the face recognition module (`cv2.face`).

## Architecture

### Core Components
The system follows a three-module architecture:

1. **`main.py`** - Flask application with routes and API endpoints
   - RESTful API endpoints: `/api/register`, `/api/mark_attendance`, `/api/records`, `/api/employees`
   - Server-side rendered pages using Jinja2 templates
   - Coordinates between database and face recognition modules

2. **`database.py`** - Database abstraction layer
   - SQLite connection management with `attendance.db`
   - Two tables: `employees` (with face encodings as BLOB) and `attendance` (check-in/out records)
   - Face encodings stored as pickled binary data

3. **`face_recognition_module.py`** - OpenCV face recognition logic
   - Face detection: Haar Cascade (`haarcascade_frontalface_default.xml`)
   - Face recognition: LBPH (Local Binary Patterns Histograms) Face Recognizer
   - Image validation and quality checks
   - Recognition confidence threshold: < 70 for positive match

### Key Design Patterns

**Face Encoding Storage**: Face images are converted to grayscale, resized to 200x200, and stored as pickled numpy arrays in the database BLOB field. The LBPH recognizer is retrained whenever a new employee is registered.

**Attendance Logic**: First face capture of the day = check-in, second capture = check-out. The system checks for existing attendance records by `emp_id` and `date` to determine the action.

**Frontend Camera Access**: Uses WebRTC `getUserMedia` API to capture images directly in the browser, which are then sent as base64-encoded data to the backend.

### Data Flow

**Registration Flow**:
1. Browser captures face image via WebRTC → base64 encoding
2. POST to `/api/register` with employee details + image
3. Backend validates image quality and detects single face
4. Creates face encoding (200x200 grayscale ROI)
5. Stores in database and retrains LBPH recognizer

**Attendance Flow**:
1. Browser captures face image → base64 encoding
2. POST to `/api/mark_attendance` with image
3. Backend runs LBPH recognition against all stored encodings
4. On match (confidence < 70), records check-in or check-out
5. Returns employee info and attendance status

## Important Technical Details

### Face Recognition Constraints
- Single face required in frame (validation enforced)
- Minimum face size: 100x100 pixels
- Minimum image resolution: 200x200 pixels
- Recognition requires good lighting for accuracy
- LBPH recognizer must be retrained after each new employee registration

### Database Schema
- **employees**: `emp_id` (TEXT, unique), `name`, `email`, `department`, `face_encoding` (BLOB), `registered_date`
- **attendance**: `emp_id` (FK), `check_in_time`, `check_out_time`, `date`, `status`
- Face encodings are pickled numpy arrays (grayscale 200x200 face ROI)

### Security & Authentication
No authentication is implemented. System assumes trusted network environment. All endpoints are publicly accessible.

## File Structure
- `main.py` - Flask app and API routes
- `database.py` - SQLite database operations
- `face_recognition_module.py` - Face detection and recognition
- `templates/` - HTML templates (index, register, attendance, records, employees)
- `static/` - CSS and JavaScript files
- `attendance.db` - SQLite database (auto-created, gitignored)
- `face_data/`, `attendance_data/` - Directories (gitignored)
