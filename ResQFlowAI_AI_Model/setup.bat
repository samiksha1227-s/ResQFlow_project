@echo off
:: ============================================================
:: ResQFlowAI – AI Model Setup Script
:: ⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
:: ============================================================

echo ============================================================
echo   SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE
echo ============================================================
echo.
echo  ResQFlowAI_AI_Model Setup
echo  This script will:
echo    1. Create a Python virtual environment
echo    2. Install required packages
echo    3. Generate synthetic training data
echo    4. Train the severity classification model
echo    5. Run the test suite
echo.
echo ============================================================
pause

:: ── Step 1: Create virtual environment ──────────────────────
echo.
echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure Python 3.8+ is installed and on PATH.
    pause
    exit /b 1
)
echo       Done.

:: ── Step 2: Activate and install packages ───────────────────
echo.
echo [2/5] Installing packages from requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Package installation failed.
    echo Try running manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo       Done.

:: ── Step 3: Generate synthetic data ─────────────────────────
echo.
echo [3/5] Generating synthetic emergency training data...
python data\generate_synthetic_data.py
if errorlevel 1 (
    echo ERROR: Data generation failed.
    pause
    exit /b 1
)
echo       Done.

:: ── Step 4: Train the model ──────────────────────────────────
echo.
echo [4/5] Training RandomForest severity model...
python src\train.py
if errorlevel 1 (
    echo ERROR: Training failed.
    pause
    exit /b 1
)
echo       Done.

:: ── Step 5: Run tests ────────────────────────────────────────
echo.
echo [5/5] Running test suite...
python tests\test_inference.py
echo       Done.

:: ── Summary ──────────────────────────────────────────────────
echo.
echo ============================================================
echo   Setup complete!
echo.
echo   To use the model:
echo     venv\Scripts\activate
echo     python src\predict.py --victims 3 --unconscious 1 --bleeding 1
echo.
echo   SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE
echo ============================================================
pause
