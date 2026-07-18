import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    FACES_DIR = os.path.join(DATA_DIR, 'faces')
    ENCODINGS_DIR = os.path.join(DATA_DIR, 'encodings')
    DATABASE_PATH = os.path.join(DATA_DIR, 'attendance.db')
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    
    FACE_DETECTION_MODEL = 'hog'
    RECOGNITION_THRESHOLD = 0.6
    IMAGE_SCALE = 0.25
    MIN_CONFIDENCE = 0.5
    
    CAMERA_ID = 0
    FRAME_INTERVAL = 0.05
    
    @classmethod
    def ensure_directories(cls):
        for directory in [cls.DATA_DIR, cls.FACES_DIR, cls.ENCODINGS_DIR, cls.REPORTS_DIR]:
            os.makedirs(directory, exist_ok=True)
        return True
    
    @classmethod
    def get_student_folder(cls, first_name, last_name):
        return os.path.join(cls.FACES_DIR, f"{first_name}_{last_name}")
    
    @classmethod
    def get_encoding_path(cls):
        return os.path.join(cls.ENCODINGS_DIR, 'encodings.pkl')