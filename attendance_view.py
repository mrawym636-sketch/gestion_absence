import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
from datetime import datetime
import os
from app.config import Config
from app import utils

class AttendanceView:
    def __init__(self, parent, db, manager, callback=None):
        self.parent = parent
        self.db = db
        self.manager = manager
        self.callback = callback
        self.is_running = False
        self.video_loop = None
        self.face_system = None
        self._build_ui()
    
    def set_face_system(self, face_system):
        self.face_system = face_system
    
    def _build_ui(self):
        frame = tk.LabelFrame(self.parent, text="🎥 Prise des Présences",
                             font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame.pack(fill='both', expand=True, pady=5)
        
        # ============================================
        # ✅ Prêt و 📸 Images - فوق الكل
        # ============================================
        status_frame = tk.Frame(frame)
        status_frame.pack(fill='x', pady=(0, 5))
        
        self.status_label = tk.Label(status_frame, text='✅ Prêt', fg='green',
                                    font=('Arial', 10, 'bold'))
        self.status_label.pack(side='left')
        
        self.frame_label = tk.Label(status_frame, text='📸 Images: 0', fg='gray',
                                   font=('Arial', 9))
        self.frame_label.pack(side='right')
        
        # ============================================
        # الأزرار - تحت ✅ Prêt و فوق الكاميرا
        # ============================================
        f_btns = tk.Frame(frame)
        f_btns.pack(fill='x', pady=(0, 5))
        
        # زر Démarrer
        self.start_btn = tk.Button(f_btns, text='▶ Démarrer',
                                  command=self._start,
                                  bg='#27ae60', fg='white', width=12,
                                  font=('Arial', 10, 'bold'))
        self.start_btn.pack(side='left', padx=2)
        
        # زر Arrêter
        self.stop_btn = tk.Button(f_btns, text='⏹ Arrêter',
                                 command=self._stop,
                                 bg='#e74c3c', fg='white', width=12,
                                 state='disabled',
                                 font=('Arial', 10, 'bold'))
        self.stop_btn.pack(side='left', padx=2)
        
        # زر Exporter
        self.export_btn = tk.Button(f_btns, text='📊 Exporter',
                                   command=self._export,
                                   bg='#9b59b6', fg='white', width=12)
        self.export_btn.pack(side='left', padx=2)
        
        # زر Réinitialiser
        self.reset_btn = tk.Button(f_btns, text='🔄 Réinitialiser',
                                  command=self._reset_today,
                                  bg='#f39c12', fg='white', width=12)
        self.reset_btn.pack(side='left', padx=2)
        
        # ============================================
        # Caméra - تحت الأزرار
        # ============================================
        f_cam = tk.Frame(frame)
        f_cam.pack(fill='x', pady=2)
        
        tk.Label(f_cam, text="Caméra:").pack(side='left')
        self.camera_entry = tk.Entry(f_cam, width=10)
        self.camera_entry.insert(0, '0')
        self.camera_entry.pack(side='left', padx=5)
        tk.Label(f_cam, text="(0=webcam)", fg='gray', font=('Arial', 8)).pack(side='left')
        
        # ============================================
        # 🖼️ ICI LA CAMÉRA - الإطار الأسود
        # ============================================
        video_frame = tk.Frame(frame, bg='black', width=400, height=280)
        video_frame.pack(pady=5)
        video_frame.pack_propagate(False)
        
        self.video_label = tk.Label(video_frame, bg='black',
                                   text='🖼️ ICI LA CAMÉRA\n(image en direct)',
                                   fg='white', font=('Arial', 14))
        self.video_label.pack(fill='both', expand=True)
    
    def _start(self):
        camera_id = self.camera_entry.get().strip()
        if not camera_id:
            camera_id = '0'
        
        try:
            camera_id = int(camera_id)
        except:
            camera_id = 0
        
        if not self.face_system:
            messagebox.showerror('Erreur', '❌ Système non initialisé!')
            return
        
        students = self.db.get_all_students()
        if not students:
            messagebox.showerror('Erreur', '❌ مافاش طلاب مسجلين!\nسجل طلاب باش يخدم التعرف.')
            return
        
        if not self.face_system.initialized:
            messagebox.showerror('Erreur', '❌ مافاش encodages!\nدوز على "🔄 Mettre à Jour"')
            return
        
        if not self.manager.start_camera(camera_id):
            messagebox.showerror('Erreur', '❌ الكاميرا ما خدامتش!\nجرب رقم آخر (1, 2, 3...)')
            return
        
        self.manager.set_callback(self._on_event)
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text='🔍 Prise de présence...', fg='blue')
        self.video_label.config(text="📸 Prise de présence...", fg='yellow')
        
        thread = threading.Thread(target=self._run)
        thread.daemon = True
        thread.start()
        
        self._update_video()
    
    def _update_video(self):
        if not self.is_running:
            return
        
        if self.manager.camera and self.manager.camera.isOpened():
            try:
                ret, frame = self.manager.camera.read()
                if ret and frame is not None:
                    display = cv2.resize(frame, (400, 280))
                    rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(rgb)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.imgtk = imgtk
                    self.video_label.config(image=imgtk, text="")
            except Exception as e:
                print(f"[ERROR] {e}")
        
        if self.is_running:
            self.video_loop = self.parent.after(50, self._update_video)
    
    def _run(self):
        try:
            self.manager.start_attendance(show_window=True)
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.parent.after(0, self._on_stop)
    
    def _stop(self):
        if self.is_running:
            self.manager.stop_camera()
            self.status_label.config(text='⏹ Arrêt en cours...', fg='orange')
    
    def _on_stop(self):
        self.is_running = False
        if self.video_loop:
            self.parent.after_cancel(self.video_loop)
            self.video_loop = None
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text='✅ Prêt', fg='green')
        self.video_label.config(image='', text="🖼️ ICI LA CAMÉRA\n(image en direct)", fg='white')
        
        stats = self.db.get_attendance_stats()
        if self.callback:
            self.callback(stats)
    
    def _on_event(self, event_type, name, timestamp, confidence):
        self.parent.after(0, lambda: self.status_label.config(
            text=f'✅ {name} - {timestamp}', fg='green'
        ))
        self.parent.after(0, lambda: self.frame_label.config(
            text=f'📸 Images: {self.manager.frame_count}'
        ))
        if self.callback:
            self.parent.after(0, lambda: self.callback(None))
    
    def _export(self):
        try:
            filename = utils.save_attendance_report(self.db)
            messagebox.showinfo('Export', f'✅ Rapport exporté:\n{filename}')
        except Exception as e:
            messagebox.showerror('Erreur', f'❌ Erreur: {e}')
    
    def _reset_today(self):
        from datetime import datetime
        csv_path = os.path.join('attendance_records', f'attendance_{datetime.now().strftime("%Y-%m-%d")}.csv')
        if os.path.exists(csv_path):
            os.remove(csv_path)
            messagebox.showinfo('Réinitialisé', '✅ Présences du jour réinitialisées')
        else:
            messagebox.showinfo('Info', 'Aucune présence à réinitialiser')