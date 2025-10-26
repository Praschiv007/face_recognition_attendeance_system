import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration from environment variables"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database Configuration
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'attendance.db')
    
    # Face Recognition Configuration
    RECOGNITION_CONFIDENCE_THRESHOLD = int(os.getenv('RECOGNITION_CONFIDENCE_THRESHOLD', 70))
    MIN_FACE_SIZE = int(os.getenv('MIN_FACE_SIZE', 100))
    MIN_IMAGE_WIDTH = int(os.getenv('MIN_IMAGE_WIDTH', 200))
    MIN_IMAGE_HEIGHT = int(os.getenv('MIN_IMAGE_HEIGHT', 200))
    FACE_ENCODING_WIDTH = int(os.getenv('FACE_ENCODING_WIDTH', 200))
    FACE_ENCODING_HEIGHT = int(os.getenv('FACE_ENCODING_HEIGHT', 200))
    
    # Haar Cascade Configuration
    FACE_DETECTION_SCALE_FACTOR = float(os.getenv('FACE_DETECTION_SCALE_FACTOR', 1.1))
    FACE_DETECTION_MIN_NEIGHBORS = int(os.getenv('FACE_DETECTION_MIN_NEIGHBORS', 5))
    
    # Attendance Records
    MAX_RECORDS_LIMIT = int(os.getenv('MAX_RECORDS_LIMIT', 50))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def validate():
        """Validate critical configuration values"""
        if Config.RECOGNITION_CONFIDENCE_THRESHOLD < 0 or Config.RECOGNITION_CONFIDENCE_THRESHOLD > 100:
            raise ValueError("RECOGNITION_CONFIDENCE_THRESHOLD must be between 0 and 100")
        
        if Config.MIN_FACE_SIZE < 50:
            raise ValueError("MIN_FACE_SIZE must be at least 50 pixels")
        
        if Config.FACE_DETECTION_SCALE_FACTOR <= 1.0:
            raise ValueError("FACE_DETECTION_SCALE_FACTOR must be greater than 1.0")
        
        if Config.FACE_DETECTION_MIN_NEIGHBORS < 1:
            raise ValueError("FACE_DETECTION_MIN_NEIGHBORS must be at least 1")
