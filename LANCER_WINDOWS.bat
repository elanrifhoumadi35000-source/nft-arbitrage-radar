@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py
) else (
  set PY=python
)

if not exist ".venv\Scripts\python.exe" (
  echo Creation de l'environnement Python...
  %PY% -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Installation / mise a jour des dependances...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo ==========================================================
  echo Fichier .env cree.
  echo Ouvre .env, colle ta cle OpenSea puis relance ce fichier.
  echo ==========================================================
  notepad ".env"
  pause
  exit /b
)

python main.py
echo.
pause
