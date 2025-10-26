import cv2
import numpy as np
import pickle
import base64
from io import BytesIO
from PIL import Image
import os
from config import Config

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_trained = False
        
        # Load configuration
        self.confidence_threshold = Config.RECOGNITION_CONFIDENCE_THRESHOLD
        self.min_face_size = Config.MIN_FACE_SIZE
        self.min_image_width = Config.MIN_IMAGE_WIDTH
        self.min_image_height = Config.MIN_IMAGE_HEIGHT
        self.face_encoding_width = Config.FACE_ENCODING_WIDTH
        self.face_encoding_height = Config.FACE_ENCODING_HEIGHT
        self.scale_factor = Config.FACE_DETECTION_SCALE_FACTOR
        self.min_neighbors = Config.FACE_DETECTION_MIN_NEIGHBORS
    
    def load_encodings_from_db(self, db):
        employees = db.get_employee_encodings()
        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        
        faces = []
        labels = []
        
        for idx, (emp_id, name, encoding_blob) in enumerate(employees):
            encoding = pickle.loads(encoding_blob)
            self.known_face_encodings.append(encoding)
            self.known_face_ids.append(emp_id)
            self.known_face_names.append(name)
            
            faces.append(encoding)
            labels.append(idx)
        
        if len(faces) > 0:
            self.recognizer.train(faces, np.array(labels))
            self.is_trained = True
    
    def _decode_image(self, image_data):
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image = np.array(image)
        else:
            image = np.array(image_data)
        
        if len(image.shape) == 2:
            gray = image
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        return image, gray
    
    def encode_face_from_image(self, image_data):
        try:
            image, gray = self._decode_image(image_data)
            
            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(self.min_face_size, self.min_face_size)
            )
            
            if len(faces) == 0:
                return None, "No face detected in the image"
            
            if len(faces) > 1:
                return None, "Multiple faces detected. Please ensure only one face is visible"
            
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (self.face_encoding_width, self.face_encoding_height))
            
            encoding_blob = pickle.dumps(face_roi)
            return encoding_blob, "Face encoded successfully"
                
        except Exception as e:
            return None, f"Error encoding face: {str(e)}"
    
    def recognize_face(self, image_data):
        try:
            if not self.is_trained or len(self.known_face_encodings) == 0:
                return None, None, "No registered employees found"
            
            image, gray = self._decode_image(image_data)
            
            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(self.min_face_size, self.min_face_size)
            )
            
            if len(faces) == 0:
                return None, None, "No face detected"
            
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (self.face_encoding_width, self.face_encoding_height))
            
            label, confidence = self.recognizer.predict(face_roi)
            
            if confidence < self.confidence_threshold:
                emp_id = self.known_face_ids[label]
                name = self.known_face_names[label]
                match_confidence = 100 - confidence
                return emp_id, name, f"Recognized with {match_confidence:.2f}% confidence"
            else:
                return None, None, "Face not recognized"
            
        except Exception as e:
            return None, None, f"Error recognizing face: {str(e)}"
    
    def validate_image_quality(self, image_data):
        try:
            image, gray = self._decode_image(image_data)
            
            height, width = gray.shape[:2]
            
            if width < self.min_image_width or height < self.min_image_height:
                return False, f"Image resolution too low (min: {self.min_image_width}x{self.min_image_height}). Please use better lighting or camera"
            
            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(self.min_face_size, self.min_face_size)
            )
            
            if len(faces) == 0:
                return False, "No face detected. Please position your face clearly in front of the camera"
            
            if len(faces) > 1:
                return False, "Multiple faces detected. Please ensure only one person is in frame"
            
            (x, y, w, h) = faces[0]
            
            if w < self.min_face_size or h < self.min_face_size:
                return False, f"Face too small (min: {self.min_face_size}x{self.min_face_size}). Please move closer to the camera"
            
            return True, "Image quality acceptable"
            
        except Exception as e:
            return False, f"Error validating image: {str(e)}"
