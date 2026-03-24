@echo off
title VaultPy Builder
color 0A

echo.
echo  ========================================
echo    VaultPy ^| Build Script
echo    Packaging app into a single .exe
echo  ========================================
echo.

:: ── Step 1: Check Python ─────────────────────────────────────────────
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Install it from https://python.org
    pause & exit /b 1
)
echo  OK - Python found
echo.

:: ── Step 2: Check pip ────────────────────────────────────────────────
echo [2/6] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: pip not found.
    pause & exit /b 1
)
echo  OK - pip found
echo.

:: ── Step 3: Install dependencies ─────────────────────────────────────
echo [3/6] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  ERROR: Failed to install dependencies.
    pause & exit /b 1
)
pip install pyinstaller --quiet
if errorlevel 1 (
    echo  ERROR: Failed to install PyInstaller.
    pause & exit /b 1
)
echo  OK - All dependencies installed
echo.

:: ── Step 4: Create static folder if missing ──────────────────────────
echo [4/6] Checking static folder...
if not exist "static" mkdir static
echo  OK - static folder ready
echo.

:: ── Step 5: Patch app.py via external patch.py ───────────────────────
echo [5/6] Preparing build entry point...
python patch.py
if errorlevel 1 (
    echo  ERROR: Patching failed.
    pause & exit /b 1
)
echo  OK - app_build.py ready
echo.

:: ── Step 6: Run PyInstaller ───────────────────────────────────────────
echo [6/6] Building executable with PyInstaller...
echo  This may take 2-3 minutes, please wait...
echo.

pyinstaller --onefile --noconsole --add-data "templates;templates" --add-data "static;static" --hidden-import "webview" --hidden-import "webview.platforms.winforms" --collect-all "webview" --name "VaultPy" app_build.py

if errorlevel 1 (
    echo.
    echo  ERROR: PyInstaller build failed. See above for details.
    pause & exit /b 1
)

:: ── Cleanup ───────────────────────────────────────────────────────────
del app_build.py >nul 2>&1
del VaultPy.spec >nul 2>&1
rmdir /s /q build >nul 2>&1

echo.
echo  ========================================
echo    BUILD SUCCESSFUL!
echo  ========================================
echo.
echo  Your executable is ready at:
echo    dist\VaultPy.exe
echo.
echo  Next step: run the Inno Setup script
echo  to create a proper Windows installer.
echo.
pause