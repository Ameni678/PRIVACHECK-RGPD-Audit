@echo off
chcp 65001 >nul
cd /d "%~dp0"
title PRIVACHECK AI - Professional
color 1F
echo.
echo  ======================================================
echo       PRIVACHECK AI  ^|  Analyse - Conformite - Confiance
echo  ======================================================
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo Python est introuvable.
  echo Installez Python 3 depuis https://www.python.org/downloads/
  echo Cochez "Add Python to PATH" pendant l'installation.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creation de l'environnement virtuel...
  py -3 -m venv .venv
  if errorlevel 1 goto error
)
echo [2/3] Installation des dependances (premier lancement uniquement)...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
if not exist ".env" copy ".env.example" ".env" >nul
echo.
echo [3/3] Demarrage de PRIVACHECK AI...
echo L'application sera disponible sur http://localhost:8501
echo Gardez cette fenetre ouverte pendant l'utilisation.
echo Pour arreter : Ctrl + C.
echo.
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
if errorlevel 1 goto error
exit /b 0
:error
echo.
echo Une erreur est survenue. Verifiez Python et votre connexion Internet.
echo Si besoin, ouvrez le dossier et consultez README.md.
pause
exit /b 1
