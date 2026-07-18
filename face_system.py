import cv2
import numpy as np
import pickle
import os
import warnings
warnings.filterwarnings("ignore")

try:
    import face_recognition
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'face-recognition', '--no-deps'])
    import face_recognition

from app.config import Config

class FaceSystem:
    def __init__(self, db):
        self.db = db
        self.encodings_file = Config.get_encoding_path()
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        self.initialized = False
        self.load_encodings()
    
    def load_encodings(self):
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_encodings = data['encodings']
                    self.known_names = data['names']
                    self.known_ids = data['ids']
                self.initialized = True
                print(f"[INFO] {len(self.known_encodings)} encodages chargés")
                return True
            except:
                return False
        return False
    
    def save_encodings(self):
        data = {
            'encodings': self.known_encodings,
            'names': self.known_names,
            'ids': self.known_ids
        }
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(data, f)
    
    def generate_encodings(self):
        students = self.db.get_all_students()
        if not students:
            return False
        
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        
        for student in students:
            student_id, first_name, last_name = student[0], student[1], student[2]
            full_name = f"{first_name} {last_name}"
            
            folder = Config.get_student_folder(first_name, last_name)
            if not os.path.exists(folder):
                continue
            
            photos = [f for f in os.listdir(folder) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            self.db.update_student_photo_count(student_id, len(photos))
            
            for photo in photos:
                try:
                    img = face_recognition.load_image_file(os.path.join(folder, photo))
                    encodings = face_recognition.face_encodings(img)
                    if encodings:
                        self.known_encodings.append(encodings[0])
                        self.known_names.append(full_name)
                        self.known_ids.append(student_id)
                        break
                except:
                    continue
        
        self.save_encodings()
        self.initialized = True
        return True
    
    def add_student_encoding(self, student_id, first_name, last_name, image_paths):
        full_name = f"{first_name} {last_name}"
        
        for img_path in image_paths:
            try:
                img = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(full_name)
                    self.known_ids.append(student_id)
                    self.save_encodings()
                    return True
            except:
                continue
        return False
    
    def remove_student_encoding(self, student_id):
        indices = [i for i, sid in enumerate(self.known_ids) if sid == student_id]
        for i in sorted(indices, reverse=True):
            del self.known_encodings[i]
            del self.known_names[i]
            del self.known_ids[i]
        self.save_encodings()
    
    def recognize_face(self, face_encoding):
        if not self.known_encodings:
            return None
        
        distances = face_recognition.face_distance(self.known_encodings, face_encoding)
        min_distance = np.min(distances)
        min_index = np.argmin(distances)
        
        if min_distance < Config.RECOGNITION_THRESHOLD:
            return {
                'student_id': self.known_ids[min_index],
                'name': self.known_names[min_index],
                'confidence': 1 - min_distance
            }
        return None
    
    def process_frame(self, frame):
        if not self.initialized:
            return [], []
        
        if frame is None:
            return [], []
        
        try:
            small = cv2.resize(frame, (0, 0), fx=Config.IMAGE_SCALE, fy=Config.IMAGE_SCALE)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb, model='hog')
            if not face_locations:
                return [], []
            
            face_encodings = face_recognition.face_encodings(rgb, face_locations)
            
            results = []
            for face_encoding in face_encodings:
                result = self.recognize_face(face_encoding)
                results.append(result)
            
            return face_locations, results
        except Exception as e:
            print(f"[ERROR] {e}")
            return [], []