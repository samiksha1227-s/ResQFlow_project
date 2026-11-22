cd .@echo title ResQFlow AI - Backend API (FastAPI)
echo ========================================================
echo Starting ResQFlow AI Backend Server on http://localhost:8000
echo Interactive API Docs: http://localhost:8000/docs
echo ========================================================
cd /d "%~dp0backend"
venv\Scripts\python.exe run.py
pause
