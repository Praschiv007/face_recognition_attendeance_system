# Face Recognition Attendance System

## Overview

An automated employee attendance tracking system that uses face recognition technology to track employee check-ins and check-outs. Built with Flask for the backend, OpenCV for face recognition, SQLite for data storage, and a web-based frontend using HTML/CSS/JavaScript with WebRTC for camera access.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework: Flask (Python 3.11)**
- Simple, lightweight web framework chosen for rapid development
- RESTful API endpoints for employee registration, attendance marking, and data retrieval
- Session management using Flask's built-in secret key mechanism

**Face Recognition System: OpenCV with LBPH**
- Uses Haar Cascade for face detection (`haarcascade_frontalface_default.xml`)
- LBPH (Local Binary Patterns Histograms) Face Recognizer for face recognition
- Chosen for its balance between accuracy and performance without requiring heavy ML frameworks
- Face encodings stored as pickled binary data in the database

**Rationale**: OpenCV provides a lightweight, efficient solution for real-time face recognition without requiring cloud services or expensive GPU resources. LBPH is suitable for controlled environments with relatively stable lighting conditions.

### Frontend Architecture

**Web-based Interface**
- Server-side rendered HTML templates using Jinja2
- Vanilla JavaScript for client-side interactions (no heavy frameworks)
- WebRTC getUserMedia API for direct camera access in the browser
- Responsive CSS with gradient-based modern UI design

**Key Design Pattern**: Progressive enhancement with camera controls that gracefully handle permission denials and errors.

### Data Storage

**Database: SQLite**
- File-based relational database (`attendance.db`)
- Two main tables:
  - `employees`: Stores employee information and face encodings as BLOB
  - `attendance`: Tracks check-in/check-out times with foreign key to employees

**Rationale**: SQLite chosen for simplicity, zero-configuration setup, and adequate performance for small-to-medium deployments. No separate database server required.

**Schema Design**:
- Face encodings stored directly in the database as binary blobs (pickled numpy arrays)
- Attendance records use separate check-in and check-out timestamps on the same record
- Date field allows for easy daily attendance queries

### Core Workflows

**Employee Registration Flow**:
1. Capture employee details via web form
2. Access camera via WebRTC
3. Capture face image, encode to base64
4. Send to backend via POST request
5. Backend validates image quality, detects face, creates encoding
6. Store employee data and face encoding in database
7. Retrain face recognizer with new data

**Attendance Marking Flow**:
1. Access camera via WebRTC
2. Capture face image
3. Send to backend for recognition
4. Backend compares against all stored face encodings
5. If match found, record check-in or check-out based on existing records for the day
6. Return employee information and attendance status to frontend

### Authentication & Authorization

**Current State**: No authentication implemented
- System assumes trusted network environment
- All endpoints are publicly accessible
- Suitable for internal company networks or controlled environments

**Future Consideration**: Could be enhanced with employee PIN verification or admin authentication for viewing records.

## External Dependencies

### Python Packages

**OpenCV (cv2)**
- Face detection using Haar Cascades
- LBPH face recognition algorithm
- Image processing and manipulation
- Version: opencv-contrib-python (includes face recognition module)

**Flask**
- Web framework and routing
- Template rendering with Jinja2
- Request/response handling
- JSON API responses

**PIL (Pillow)**
- Image format conversion
- Base64 image decoding
- Used to convert browser-captured images to numpy arrays

**NumPy**
- Array operations for image data
- Required by OpenCV for image representations
- Face encoding storage format

**Standard Library**: sqlite3, pickle, base64, datetime, os

### Browser APIs

**WebRTC getUserMedia**
- Camera access directly in the browser
- Real-time video streaming
- No plugin or third-party service required
- Requires HTTPS in production (or localhost for development)

### Static Assets

**Haar Cascade Classifier**
- Pre-trained XML file from OpenCV (`haarcascade_frontalface_default.xml`)
- Provided by cv2.data.haarcascades
- No external download required

### Database

**SQLite**
- File-based database (attendance.db)
- No separate server process
- Included in Python standard library
- Suitable for single-instance deployments

**Limitation**: SQLite doesn't handle high concurrency well. For production deployments with multiple simultaneous users, consider migrating to PostgreSQL or MySQL.

### No Cloud Services

The system is entirely self-contained with no external API calls or cloud dependencies, making it suitable for air-gapped or privacy-sensitive environments.