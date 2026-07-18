@echo off
title Installation Système de Présence
echo =============================================
echo  📸 INSTALLATION DU SYSTÈME DE PRÉSENCE
echo =============================================
echo.

echo [1/6] Vérification de Python...
python --version
if errorlevel 1 (
    echo ❌ Python non trouvé!
    echo Téléchargez Python 3.11 depuis python.org
    pause
    exit
)

echo.
echo [2/6] Création de l'environnement virtuel...
python -m venv venv

echo.
echo [3/6] Activation...
call venv\Scripts\activate.bat

echo.
echo [4/6] Installation des dépendances...
python -m pip install --upgrade pip
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pillow==10.1.0
pip install dlib-bin==20.0.1
pip install face-recognition==1.3.0 --no-deps
pip install face-recognition-models==0.3.0

echo.
echo [5/6] Téléchargement de haarcascade...
python -c "import cv2, os; import shutil; src=cv2.data.haarcascades+'haarcascade_frontalface_default.xml'; shutil.copy(src, '.')" 2>nul
if errorlevel 1 (
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml' -OutFile 'haarcascade_frontalface_default.xml'"
)

echo.
echo [6/6] Lancement de l'application...
python main.py

pause