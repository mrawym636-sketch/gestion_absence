import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                class_name TEXT,
                photo_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_out TIMESTAMP,
                confidence REAL,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def add_student(self, first_name, last_name, class_name=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (first_name, last_name, class_name)
            VALUES (?, ?, ?)
        ''', (first_name, last_name, class_name))
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return student_id
    
    def get_all_students(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, first_name, last_name, class_name
            FROM students WHERE is_active = 1
            ORDER BY last_name, first_name
        ''')
        students = cursor.fetchall()
        conn.close()
        return students
    
    def get_student_names(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT first_name || ' ' || last_name as full_name
            FROM students WHERE is_active = 1
            ORDER BY last_name
        ''')
        return [row[0] for row in cursor.fetchall()]
    
    def get_student_by_name(self, first_name, last_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM students
            WHERE first_name = ? AND last_name = ? AND is_active = 1
        ''', (first_name, last_name))
        student = cursor.fetchone()
        conn.close()
        return student
    
    def delete_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET is_active = 0 WHERE id = ?', (student_id,))
        conn.commit()
        conn.close()
    
    def update_student_photo_count(self, student_id, count):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE students SET photo_count = ? WHERE id = ?', (count, student_id))
            conn.commit()
        except:
            cursor.execute('ALTER TABLE students ADD COLUMN photo_count INTEGER DEFAULT 0')
            cursor.execute('UPDATE students SET photo_count = ? WHERE id = ?', (count, student_id))
            conn.commit()
        conn.close()
    
    def record_attendance(self, student_id, confidence):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT id FROM attendance
            WHERE student_id = ? AND DATE(check_in) = ?
        ''', (student_id, today))
        
        if cursor.fetchone():
            conn.close()
            return False
        
        cursor.execute('''
            INSERT INTO attendance (student_id, confidence)
            VALUES (?, ?)
        ''', (student_id, confidence))
        conn.commit()
        conn.close()
        return True
    
    def get_today_attendance(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT s.first_name, s.last_name, s.class_name,
                   a.check_in, a.confidence
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE DATE(a.check_in) = ?
            ORDER BY a.check_in DESC
        ''', (today,))
        records = cursor.fetchall()
        conn.close()
        return records
    
    def get_attendance_stats(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM students WHERE is_active = 1')
        total = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(DISTINCT student_id)
            FROM attendance
            WHERE DATE(check_in) = ?
        ''', (date,))
        present = cursor.fetchone()[0] or 0
        
        conn.close()
        return {
            'total': total,
            'present': present,
            'absent': total - present,
            'rate': (present / total * 100) if total > 0 else 0
        }
    
    def add_log(self, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO logs (message) VALUES (?)', (message,))
        conn.commit()
        conn.close()
    
    def clear_logs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM logs')
        conn.commit()
        conn.close()