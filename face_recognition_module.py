import cv2
import numpy as np
import pickle
import base64
from io import BytesIO
from PIL import Image
import os

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
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            if len(faces) == 0:
                return None, "No face detected in the image"
            
            if len(faces) > 1:
                return None, "Multiple faces detected. Please ensure only one face is visible"
            
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            
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
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            if len(faces) == 0:
                return None, None, "No face detected"
            
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            
            label, confidence = self.recognizer.predict(face_roi)
            
            if confidence < 70:
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
            
            if width < 200 or height < 200:
                return False, "Image resolution too low. Please use better lighting or camera"
            
            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            if len(faces) == 0:
                return False, "No face detected. Please position your face clearly in front of the camera"
            
            if len(faces) > 1:
                return False, "Multiple faces detected. Please ensure only one person is in frame"
            
            (x, y, w, h) = faces[0]
            
            if w < 100 or h < 100:
                return False, "Face too small. Please move closer to the camera"
            
            return True, "Image quality acceptable"
            
        except Exception as e:
            return False, f"Error validating image: {str(e)}"
