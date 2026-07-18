import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from app.config import Config

class StudentManager:
    def __init__(self, parent, db, face_system, callback=None):
        self.parent = parent
        self.db = db
        self.face_system = face_system
        self.callback = callback
        self.selected_images = []
        self._build_ui()
        self._update_list()
    
    def _build_ui(self):
        frame = tk.LabelFrame(self.parent, text="👤 Gestion des Étudiants",
                             font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame.pack(fill='x', pady=(0, 5))
        
        f = tk.Frame(frame)
        f.pack(fill='x', pady=5)
        
        tk.Label(f, text="Prénom:").pack(side='left')
        self.firstname = tk.Entry(f, width=12)
        self.firstname.pack(side='left', padx=5)
        
        tk.Label(f, text="Nom:").pack(side='left', padx=(10,0))
        self.lastname = tk.Entry(f, width=12)
        self.lastname.pack(side='left', padx=5)
        
        tk.Label(f, text="Classe:").pack(side='left', padx=(10,0))
        self.class_name = tk.Entry(f, width=12)
        self.class_name.pack(side='left', padx=5)
        
        f2 = tk.Frame(frame)
        f2.pack(fill='x', pady=5)
        
        tk.Button(f2, text="📷 Sélectionner Photos (3-5)",
                 command=self._select_photos,
                 bg='#3498db', fg='white').pack(side='left')
        
        self.photo_label = tk.Label(f2, text="Aucune photo", fg='gray')
        self.photo_label.pack(side='left', padx=10)
        
        self.listbox = tk.Listbox(frame, height=6)
        self.listbox.pack(fill='x', pady=5)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        
        f3 = tk.Frame(frame)
        f3.pack(fill='x', pady=5)
        
        tk.Button(f3, text="💾 Enregistrer",
                 command=self._register,
                 bg='#27ae60', fg='white', width=12).pack(side='left', padx=2)
        
        tk.Button(f3, text="🗑 Supprimer",
                 command=self._delete,
                 bg='#e74c3c', fg='white', width=12).pack(side='left', padx=2)
        
        tk.Button(f3, text="🔄 Mettre à Jour",
                 command=self._update_encodings,
                 bg='#2980b9', fg='white', width=12).pack(side='left', padx=2)
    
    def _select_photos(self):
        files = filedialog.askopenfilenames(
            title='Sélectionnez 3-5 photos',
            filetypes=[('Images', '*.jpg *.jpeg *.png')]
        )
        if files:
            self.selected_images = list(files)[:5]
            self.photo_label.config(
                text=f'{len(self.selected_images)} photo(s)',
                fg='green' if len(self.selected_images) >= 3 else 'orange'
            )
    
    def _register(self):
        first = self.firstname.get().strip()
        last = self.lastname.get().strip()
        class_name = self.class_name.get().strip()
        
        if not first or not last:
            messagebox.showerror('Erreur', 'Entrez prénom et nom')
            return
        
        if len(self.selected_images) < 3:
            messagebox.showerror('Erreur', 'Sélectionnez 3-5 photos')
            return
        
        if self.db.get_student_by_name(first, last):
            messagebox.showerror('Erreur', 'Cet étudiant existe déjà')
            return
        
        student_id = self.db.add_student(first, last, class_name)
        
        folder = Config.get_student_folder(first, last)
        os.makedirs(folder, exist_ok=True)
        for img in self.selected_images:
            shutil.copy(img, folder)
        
        self.db.update_student_photo_count(student_id, len(self.selected_images))
        
        success = self.face_system.add_student_encoding(
            student_id, first, last, self.selected_images
        )
        
        if success:
            messagebox.showinfo('Succès', f'✅ {first} {last} enregistré')
        else:
            messagebox.showwarning('Attention', 'Étudiant enregistré mais échec encodage')
        
        self._reset_form()
        self._update_list()
        if self.callback:
            self.callback()
    
    def _delete(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning('Avertissement', 'Sélectionnez un étudiant')
            return
        
        name = self.listbox.get(selection[0])
        if not messagebox.askyesno('Confirmation', f'Supprimer {name} ?'):
            return
        
        students = self.db.get_all_students()
        for s in students:
            if f"{s[1]} {s[2]}" == name:
                student_id = s[0]
                break
        else:
            return
        
        self.db.delete_student(student_id)
        self.face_system.remove_student_encoding(student_id)
        
        folder = Config.get_student_folder(s[1], s[2])
        if os.path.exists(folder):
            shutil.rmtree(folder)
        
        self._update_list()
        if self.callback:
            self.callback()
    
    def _update_encodings(self):
        self.face_system.generate_encodings()
        messagebox.showinfo('Succès', '✅ Encodages mis à jour')
        if self.callback:
            self.callback()
    
    def _on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            name = self.listbox.get(selection[0])
            parts = name.split(' ')
            self.firstname.delete(0, tk.END)
            self.firstname.insert(0, parts[0])
            self.lastname.delete(0, tk.END)
            self.lastname.insert(0, parts[1] if len(parts) > 1 else '')
    
    def _reset_form(self):
        self.firstname.delete(0, tk.END)
        self.lastname.delete(0, tk.END)
        self.class_name.delete(0, tk.END)
        self.selected_images = []
        self.photo_label.config(text='Aucune photo', fg='gray')
    
    def _update_list(self):
        self.listbox.delete(0, tk.END)
        for s in self.db.get_all_students():
            self.listbox.insert(tk.END, f"{s[1]} {s[2]}")