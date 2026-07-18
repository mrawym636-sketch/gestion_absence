@echo off
title Système de Présence
echo =============================================
echo  📸 SYSTÈME DE PRÉSENCE
echo =============================================
echo.

if exist venv (
    call venv\Scripts\activate
) else (
    echo ❌ Environnement non trouvé!
    echo Lancez install.bat d'abord
    pause
    exit
)

python main.py
pause