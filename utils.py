import csv
import os
from datetime import datetime
from app.config import Config

def save_attendance_report(db):
    date = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(Config.REPORTS_DIR, f'attendance_{date}.csv')
    
    records = db.get_today_attendance()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Prénom', 'Nom', 'Classe', 'Heure', 'Confiance'])
        for r in records:
            writer.writerow([r[0], r[1], r[2] or '', r[3], f"{r[4]*100:.1f}%" if r[4] else ''])
    
    return filename