@echo off
echo Setting up ResQFlow AI Backend...
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo Setup complete. Run start.bat to launch.
