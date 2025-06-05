@echo off
setlocal enabledelayedexpansion

REM Debug Build Script - Diagnoses and fixes common PyInstaller issues

echo =============================================
echo PyInstaller Debug and Diagnostic Tool
echo =============================================
echo.

echo Step 1: Project Structure Analysis
echo -----------------------------------
echo Current directory: %CD%
echo.

REM Check main file
if exist "main.py" (
    echo ✓ main.py found
) else (
    echo ✗ main.py NOT found
    echo Please ensure you're in the correct directory
    goto :end
)

REM Analyze directory structure
echo.
echo Directory structure:
for /d %%d in (*) do (
    if exist "%%d\*.py" (
        echo ✓ %%d\ (contains Python files)
    ) else (
        echo ? %%d\ (no Python files found)
    )
)

echo.
echo Step 2: Python Environment Check
echo --------------------------------
python --version
echo Python executable: 
where python
echo.

REM Check if in virtual environment
if defined VIRTUAL_ENV (
    echo ✓ Virtual environment active: %VIRTUAL_ENV%
) else (
    echo ! No virtual environment detected
)

echo.
echo Step 3: Dependency Analysis
echo ---------------------------
echo Analyzing main.py imports...

REM Extract imports from main.py
if exist "main.py" (
    echo.
    echo Imports found in main.py:
    findstr /r /c:"^import\|^from.*import" main.py
    echo.
)

echo Checking installed packages...
pip list --format=columns

echo.
echo Step 4: Creating Minimal Test Build
echo -----------------------------------

REM Create a minimal spec file first
echo Creating test spec file...

echo # Minimal test spec file > test_build.spec
echo import sys >> test_build.spec
echo from PyInstaller.building.build_main import Analysis, PYZ, EXE >> test_build.spec
echo. >> test_build.spec
echo a = Analysis( >> test_build.spec
echo     ['main.py'], >> test_build.spec
echo     pathex=[], >> test_build.spec
echo     binaries=[], >> test_build.spec
echo     datas=[], >> test_build.spec
echo     hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox'], >> test_build.spec
echo     hookspath=[], >> test_build.spec
echo     hooksconfig={}, >> test_build.spec
echo     runtime_hooks=[], >> test_build.spec
echo     excludes=[], >> test_build.spec
echo     noarchive=False, >> test_build.spec
echo ) >> test_build.spec
echo. >> test_build.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=None) >> test_build.spec
echo. >> test_build.spec
echo exe = EXE( >> test_build.spec
echo     pyz, >> test_build.spec
echo     a.scripts, >> test_build.spec
echo     a.binaries, >> test_build.spec
echo     a.zipfiles, >> test_build.spec
echo     a.datas, >> test_build.spec
echo     [], >> test_build.spec
echo     name='starbucks_survey_test', >> test_build.spec
echo     debug=False, >> test_build.spec
echo     bootloader_ignore_signals=False, >> test_build.spec
echo     strip=False, >> test_build.spec
echo     upx=True, >> test_build.spec
echo     upx_exclude=[], >> test_build.spec
echo     runtime_tmpdir=None, >> test_build.spec
echo     console=True, >> test_build.spec
echo     disable_windowed_traceback=False, >> test_build.spec
echo     argv_emulation=False, >> test_build.spec
echo     target_arch=None, >> test_build.spec
echo     codesign_identity=None, >> test_build.spec
echo     entitlements_file=None, >> test_build.spec
echo ) >> test_build.spec

echo.
echo Running minimal test build...
pyinstaller test_build.spec --clean

if errorlevel 1 (
    echo.
    echo Test build failed. Let's try even simpler approach...
    echo.
    
    echo Step 5: Ultra-minimal build attempt
    echo -----------------------------------
    pyinstaller --onefile --console --name "test_simple" main.py
    
    if errorlevel 1 (
        echo.
        echo Even minimal build failed. Checking for syntax errors...
        python -m py_compile main.py
        if errorlevel 1 (
            echo ✗ Syntax error in main.py
        ) else (
            echo ✓ main.py syntax is correct
            echo.
            echo The issue might be with dependencies or imports.
            echo Let's check what happens when we run the script directly:
            echo.
            python main.py --help
        )
    ) else (
        echo ✓ Ultra-minimal build succeeded!
        echo You can find the executable in dist\test_simple.exe
    )
) else (
    echo ✓ Test build succeeded!
    echo You can find the executable in dist\starbucks_survey_test.exe
)

echo.
echo Step 6: Recommendations
echo ----------------------

if exist "dist\*.exe" (
    echo ✓ At least one executable was created successfully.
    echo.
    echo Next steps:
    echo 1. Test the created executable
    echo 2. If it works, you can use the working configuration
    echo 3. If you need to add data files, add them one by one and test
    echo.
    echo Created executables:
    dir /b dist\*.exe 2>nul
) else (
    echo ✗ No executables were created.
    echo.
    echo Troubleshooting suggestions:
    echo 1. Check that main.py runs correctly: python main.py
    echo 2. Install missing dependencies: pip install selenium openpyxl
    echo 3. Make sure you have write permissions in this directory
    echo 4. Try running as administrator
    echo 5. Check Python and PyInstaller versions compatibility
    echo.
    echo Current PyInstaller version:
    pyinstaller --version
    echo.
    echo If problems persist, try creating a new virtual environment:
    echo   python -m venv new_venv
    echo   new_venv\Scripts\activate
    echo   pip install pyinstaller selenium openpyxl
    echo   then run this script again
)

echo.
echo Step 7: Cleanup
echo ---------------
if exist "test_build.spec" del "test_build.spec"
echo Temporary files cleaned up.

:end
echo.
echo =============================================
echo Diagnostic complete!
echo =============================================
echo.
pause