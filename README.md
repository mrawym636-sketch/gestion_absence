# 📸 Système de Gestion des Présences par Reconnaissance Faciale

## Description
Application complète de gestion des présences et des absences utilisant la reconnaissance faciale en temps réel avec OpenCV et `face_recognition`.  
Elle permet d’enregistrer des étudiants, de prendre les présences automatiquement via la webcam, et d’exporter des rapports CSV.

---

## Fonctionnalités
- ✅ **Reconnaissance faciale en temps réel** (via webcam)
- ✅ **Gestion complète des étudiants** (ajout, modification, suppression)
- ✅ **Base de données SQLite** pour stocker les étudiants et les présences
- ✅ **Export de rapports CSV** (présences du jour)
- ✅ **Statistiques en direct** (nombre de présents/absents, taux de présence)
- ✅ **Interface graphique moderne** (Tkinter)
- ✅ **Journal des événements** (logs)
- ✅ **Arrêt automatique** de la caméra après utilisation
- ✅ **Support de la caméra USB et IP** (webcam, IP Webcam sur téléphone)

---

## Technologies utilisées
- **Python 3.11** (ou 3.10)
- **OpenCV** (capture et traitement vidéo)
- **face_recognition** (reconnaissance faciale)
- **dlib-bin** (backend pour face_recognition)
- **Tkinter** (interface graphique)
- **SQLite** (base de données)
- **Pillow** (manipulation d’images)

---

## Installation

### Prérequis
- Windows 10/11 (ou Linux/Mac avec adaptations)
- Python 3.11 (recommandé) – [Télécharger Python](https://www.python.org/downloads/)

### Étapes d’installation

1. **Téléchargez ou clonez le projet** dans un dossier, par exemple `C:\Users\votre_nom\Desktop\gestion_absence`.

2. **Double‑cliquez sur `install.bat`** (ou exécutez‑le dans un terminal).

   Ce script va :
   - Vérifier la présence de Python
   - Créer un environnement virtuel (`venv`)
   - Installer toutes les dépendances (OpenCV, face_recognition, etc.)
   - Télécharger automatiquement le fichier `haarcascade_frontalface_default.xml` (nécessaire pour la détection)
   - Lancer l’application

   > ⚠️ **Si `install.bat` ne fonctionne pas**, ouvrez un terminal (cmd) et exécutez les commandes suivantes :
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
       L’application démarre automatiquement après l’installation.

Utilisation
1. Ajouter un étudiant

    Remplissez les champs Prénom, Nom et Classe.

    Cliquez sur 📷 Sélectionner Photos (3‑5) et choisissez des photos où le visage est bien visible (de face, bonne luminosité).

    Cliquez sur 💾 Enregistrer.

    L’étudiant est ajouté à la base de données et ses encodages faciaux sont générés automatiquement.

2. Mettre à jour les encodages

    Après avoir ajouté ou supprimé des étudiants, cliquez sur 🔄 Mettre à Jour pour recalculer tous les encodages.

    Cette opération est nécessaire pour que la reconnaissance fonctionne correctement.

3. Prendre les présences

    Dans la section 🎥 Prise des Présences, assurez‑vous que le champ Caméra contient 0 (webcam par défaut) ou l’URL d’une caméra IP.

    Cliquez sur ▶ Démarrer.

    La caméra s’ouvre et affiche le flux vidéo.

    Lorsque le système reconnaît un visage, il enregistre automatiquement la présence (une fois par jour et par étudiant).

    Vous pouvez arrêter à tout moment avec ⏹ Arrêter.

4. Exporter les rapports

    Cliquez sur 📊 Exporter pour générer un fichier CSV contenant les présences du jour.

    Le fichier est sauvegardé dans le dossier reports/ avec le nom attendance_AAAA‑MM‑JJ.csv.

5. Réinitialiser les présences du jour

    Cliquez sur 🔄 Réinitialiser pour effacer toutes les présences enregistrées aujourd’hui.

6. Consulter les logs

    Le 📋 Journal affiche toutes les actions (démarrage, reconnaissance, arrêt, erreurs).

    Vous pouvez vider le journal avec le bouton 🗑 Effacer.

Structure du projet
text
```
gestion_absence/
├── app/
│   ├── __init__.py
│   ├── config.py            # Configuration (chemins, paramètres)
│   ├── database.py          # Gestion de la base SQLite
│   ├── face_system.py       # Encodages et reconnaissance faciale
│   ├── attendance_manager.py # Gestion de la caméra et des présences
│   └── utils.py             # Fonctions utilitaires (export CSV)
├── gui/
│   ├── __init__.py
│   ├── main_window.py       # Fenêtre principale
│   ├── student_manager.py   # Gestion des étudiants (ajout/suppression)
│   ├── attendance_view.py   # Interface de prise de présence
│   └── styles.py            # Couleurs et polices
├── data/                    # Dossiers de données
│   ├── faces/               # Photos des étudiants
│   ├── encodings/           # Encodages sauvegardés (.pkl)
│   └── attendance.db        # Base de données SQLite
├── reports/                 # Rapports CSV exportés
├── requirements.txt         # Dépendances Python
├── main.py                  # Point d’entrée
├── install.bat              # Script d’installation (Windows)
├── run.bat                  # Script de lancement
└── README.md                # Ce fichier
```
Dépannage
Problème : « ModuleNotFoundError: No module named 'cv2' »

    Vérifiez que vous êtes bien dans l’environnement virtuel (venv).

    Réinstallez OpenCV : pip install opencv-python==4.8.1.78

Problème : La caméra ne s’ouvre pas

    Assurez‑vous qu’aucune autre application (Teams, Zoom, etc.) n’utilise la caméra.

    Essayez de changer le numéro de la caméra (0, 1, 2, ...) dans le champ Caméra.

    Testez votre caméra avec un autre logiciel (ex: l’application appareil photo de Windows).

Problème : Le visage n’est pas reconnu

    Utilisez des photos de bonne qualité (visage bien éclairé, de face).

    Après avoir ajouté des étudiants, n’oubliez pas de cliquer sur 🔄 Mettre à Jour.

    Si le problème persiste, augmentez le nombre de photos par étudiant (4‑5).

Problème : dlib ne s’installe pas

    Sur Windows, utilisez dlib-bin (inclus dans les dépendances) au lieu de dlib.

    Si vous avez besoin de la version complète, installez Visual Studio Build Tools avec le kit C++.

Crédits

    Développé avec ❤️ en Python.

    Bibliothèques : OpenCV, face_recognition, dlib.

Licence

Ce projet est distribué sous licence MIT.
text


---

**Téléchargez ce fichier et placez‑le à la racine de votre projet sous le nom `README.md`.**  
Il contient toutes les informations nécessaires pour comprendre, installer et utiliser votre application. 🚀

