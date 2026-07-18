import cv2
import time
import threading
from datetime import datetime
from app.config import Config

class AttendanceManager:
    def __init__(self, face_system, db):
        self.face_system = face_system
        self.db = db
        self.camera = None
        self.is_running = False
        self.present_today = set()
        self.callback = None
        self.frame_count = 0
    
    def set_callback(self, callback):
        self.callback = callback
    
    def start_camera(self, camera_id=0):
        try:
            print(f"[INFO] محاولة فتح الكاميرا {camera_id}...")
            
            # جرب طرق مختلفة
            for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
                self.camera = cv2.VideoCapture(camera_id, backend)
                if self.camera.isOpened():
                    print(f"[INFO] ✅ تم فتح الكاميرا مع backend {backend}")
                    break
            
            # إذا ما تفتحاتش، جرب بدون backend
            if not self.camera or not self.camera.isOpened():
                self.camera = cv2.VideoCapture(camera_id)
                if self.camera.isOpened():
                    print(f"[INFO] ✅ تم فتح الكاميرا sans backend")
            
            if not self.camera or not self.camera.isOpened():
                print(f"[ERROR] ❌ ما تفتحاتش الكاميرا {camera_id}")
                return False
            
            # ضبط الدقة
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # اختبار
            ret, frame = self.camera.read()
            if not ret or frame is None:
                print("[ERROR] ❌ الكاميرا ما كتقراش الصور")
                self.camera.release()
                self.camera = None
                return False
            
            print(f"[INFO] ✅ الكاميرا {camera_id} خدامة! ({frame.shape})")
            return True
            
        except Exception as e:
            print(f"[ERROR] ❌ مشكلة: {e}")
            return False
    
    def stop_camera(self):
        self.is_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        try:
            cv2.destroyAllWindows()
        except:
            pass
    
    def start_attendance(self, show_window=True):
        if not self.camera:
            print("[ERROR] ❌ الكاميرا ما خدامتش!")
            return False
        
        students = self.db.get_all_students()
        if not students:
            print("[ERROR] ❌ مافاش طلاب مسجلين!")
            return False
        
        if not self.face_system.initialized:
            print("[ERROR] ❌ مافاش encodages!")
            return False
        
        records = self.db.get_today_attendance()
        self.present_today = {f"{r[0]} {r[1]}" for r in records}
        
        self.is_running = True
        self.frame_count = 0
        
        print(f"[INFO] 🚀 بدينا الحضور - {len(students)} طالب")
        
        thread = threading.Thread(target=self._process_video, args=(show_window,))
        thread.daemon = True
        thread.start()
        return True
    
    def _process_video(self, show_window):
        while self.is_running and self.camera:
            try:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    continue
                
                self.frame_count += 1
                
                face_locations, results = self.face_system.process_frame(frame)
                
                frame = self._annotate_frame(frame, face_locations, results)
                
                info = f"Frame: {self.frame_count} | ✅ Présents: {len(self.present_today)}"
                cv2.putText(frame, info, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                if show_window:
                    cv2.imshow('📸 Présence', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"[ERROR] {e}")
                break
        
        self.stop_camera()
    
    def _annotate_frame(self, frame, face_locations, results):
        scale = 1.0 / Config.IMAGE_SCALE
        
        for (top, right, bottom, left), result in zip(face_locations, results):
            top = int(top * scale)
            right = int(right * scale)
            bottom = int(bottom * scale)
            left = int(left * scale)
            
            if result and result.get('student_id'):
                name = result['name']
                confidence = result['confidence']
                student_id = result['student_id']
                
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"{name} ({confidence*100:.0f}%)",
                           (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                if name not in self.present_today and confidence >= Config.MIN_CONFIDENCE:
                    is_new = self.db.record_attendance(student_id, confidence)
                    if is_new:
                        self.present_today.add(name)
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"[PRÉSENCE] ✅ {name} - {timestamp}")
                        if self.callback:
                            self.callback('present', name, timestamp, confidence)
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "❓ INCONNU", (left, top-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return frame