import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.config import Config
from app.database import Database
from app.face_system import FaceSystem
from app.attendance_manager import AttendanceManager
from gui.student_manager import StudentManager
from gui.attendance_view import AttendanceView

class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('📸 Gestion des Présences')
        self.window.geometry('1100x750')
        self.window.configure(bg='#f0f0f0')
        
        Config.ensure_directories()
        self.db = Database(Config.DATABASE_PATH)
        self.face_system = FaceSystem(self.db)
        self.manager = AttendanceManager(self.face_system, self.db)
        
        self._build_ui()
        self._update_stats()
    
    def _build_ui(self):
        # Header
        header = tk.Frame(self.window, bg='#2c3e50', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text='📸 Gestion des Présences',
                font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white').pack(pady=10)
        
        # Main
        main = tk.Frame(self.window, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel
        left = tk.Frame(main, bg='#f0f0f0')
        left.pack(side='left', fill='both', expand=True)
        
        # Right panel
        right = tk.Frame(main, bg='#f0f0f0', width=400)
        right.pack(side='right', fill='both')
        right.pack_propagate(False)
        
        # Sections
        self.student_manager = StudentManager(left, self.db, self.face_system, self._update_stats)
        
        self.attendance_view = AttendanceView(left, self.db, self.manager, self._update_stats)
        self.attendance_view.set_face_system(self.face_system)
        
        self._build_stats(right)
        self._build_log(right)
        
        # Footer
        footer = tk.Frame(self.window, bg='#34495e', height=25)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        tk.Label(footer, text='Système de Présence v3.0', bg='#34495e', fg='white').pack(pady=3)
    
    def _build_stats(self, parent):
        frame = tk.LabelFrame(parent, text='📊 Statistiques',
                             font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame.pack(fill='x', pady=(0, 5))
        
        self.stats_text = tk.Text(frame, height=5, width=40,
                                 font=('Consolas', 10), state='disabled')
        self.stats_text.pack(fill='both')
        
        self.progress = ttk.Progressbar(frame, length=350, mode='determinate')
        self.progress.pack(pady=5)
    
    def _build_log(self, parent):
        frame = tk.LabelFrame(parent, text='📋 Journal',
                             font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(frame, height=15, width=40,
                               font=('Consolas', 9), state='disabled')
        self.log_text.pack(side='left', fill='both', expand=True)
        
        scroll = tk.Scrollbar(frame, command=self.log_text.yview)
        scroll.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scroll.set)
        
        tk.Button(frame, text='🗑 Effacer', command=self._clear_log,
                 bg='#e74c3c', fg='white').pack(side='bottom', pady=2)
    
    def _update_stats(self, stats=None):
        if stats is None:
            stats = self.db.get_attendance_stats()
        
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0,
            f'👥 Total: {stats["total"]}\n'
            f'✅ Présents: {stats["present"]}\n'
            f'❌ Absents: {stats["absent"]}\n'
            f'📊 Taux: {stats["rate"]:.1f}%\n'
        )
        self.stats_text.config(state='disabled')
        self.progress['value'] = stats['rate']
        
        self._log(f'📊 Stats: {stats["present"]}/{stats["total"]} présents')
    
    def _log(self, message):
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f'[{timestamp}] {message}\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.db.add_log(message)
    
    def _clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.db.clear_logs()
    
    def run(self):
        self.window.mainloop()