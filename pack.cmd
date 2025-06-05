@echo off
setlocal enabledelayedexpansion

REM Advanced Build Script for Starbucks Survey Automation
REM Supports multiple build configurations and options

echo ========================================
echo Starbucks Survey Automation Builder v2
echo ========================================
echo.

REM Parse command line arguments
set BUILD_TYPE=gui
set CLEAN_BUILD=false
set INCLUDE_CONSOLE=false
set OPTIMIZE=false
set DEBUG_MODE=false

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="--console" (
    set INCLUDE_CONSOLE=true
    shift
    goto :parse_args
)
if /i "%~1"=="--clean" (
    set CLEAN_BUILD=true
    shift
    goto :parse_args
)
if /i "%~1"=="--debug" (
    set DEBUG_MODE=true
    shift
    goto :parse_args
)
if /i "%~1"=="--optimize" (
    set OPTIMIZE=true
    shift
    goto :parse_args
)
if /i "%~1"=="--help" goto :show_help
shift
goto :parse_args

:args_done

REM Show build configuration
echo Build Configuration:
echo - Console mode: !INCLUDE_CONSOLE!
echo - Clean build: !CLEAN_BUILD!
echo - Debug mode: !DEBUG_MODE!
echo - Optimize: !OPTIMIZE!
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    goto :error_exit
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: !PYTHON_VERSION!

REM Check Python version (should be 3.7+)
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if !MAJOR! LSS 3 (
    echo ERROR: Python 3.7+ is required
    goto :error_exit
)
if !MAJOR! EQU 3 if !MINOR! LSS 7 (
    echo ERROR: Python 3.7+ is required
    goto :error_exit
)
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        goto :error_exit
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    goto :error_exit
)
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install/check PyInstaller
echo Checking PyInstaller installation...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        goto :error_exit
    )
) else (
    echo PyInstaller is already installed
    if "!OPTIMIZE!"=="true" (
        echo Upgrading PyInstaller...
        pip install --upgrade pyinstaller
    )
)
echo.

REM Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo WARNING: Some dependencies failed to install
        echo This may cause the build to fail
        set /p continue="Continue anyway? (y/n): "
        if /i "!continue!" neq "y" goto :error_exit
    )
    echo.
)

REM Clean previous builds if requested
if "!CLEAN_BUILD!"=="true" (
    echo Cleaning previous builds...
    if exist "dist" rmdir /s /q "dist"
    if exist "build" rmdir /s /q "build"
    if exist "*.spec" del "*.spec"
    echo.
)

REM Create output directories
if not exist "dist" mkdir "dist"
if not exist "build" mkdir "build"

REM Build PyInstaller command
set PYINSTALLER_CMD=pyinstaller
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --onefile
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --name "starbucks_survey"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --distpath "dist"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --workpath "build"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --specpath "build"

REM Add console option
if "!INCLUDE_CONSOLE!"=="false" (
    set PYINSTALLER_CMD=!PYINSTALLER_CMD! --noconsole
) else (
    set PYINSTALLER_CMD=!PYINSTALLER_CMD! --console
)

REM Add data files
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --add-data "gui;gui"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --add-data "core;core"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --add-data "utils;utils"

REM Add hidden imports
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --hidden-import "tkinter"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --hidden-import "tkinter.ttk"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --hidden-import "tkinter.messagebox"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --hidden-import "tkinter.filedialog"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --hidden-import "openpyxl"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --hidden-import "selenium"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --hidden-import "selenium.webdriver"
set PYINSTALLER_CMD=!PYINSTALLER_CMD! --collect-all "selenium"

REM Add optimization flags
if "!OPTIMIZE!"=="true" (
    set PYINSTALLER_CMD=!PYINSTALLER_CMD! --optimize 2
    set PYINSTALLER_CMD=!PYINSTALLER_CMD! --strip
)

REM Add debug options
if "!DEBUG_MODE!"=="true" (
    set PYINSTALLER_CMD=!PYINSTALLER_CMD! --debug all
    set PYINSTALLER_CMD=!PYINSTALLER_CMD! --log-level DEBUG
)

REM Add main file
set PYINSTALLER_CMD=!PYINSTALLER_CMD! main.py

echo Building executable...
echo Command: !PYINSTALLER_CMD!
echo.
echo This may take several minutes...
echo.

REM Execute build command
!PYINSTALLER_CMD!

if errorlevel 1 (
    echo.
    echo ================================
    echo BUILD FAILED!
    echo ================================
    echo Check the error messages above for details.
    echo.
    echo Common solutions:
    echo - Make sure all dependencies are installed
    echo - Check that all source files exist
    echo - Try running with --debug flag for more info
    goto :error_exit
)

echo.
echo ================================
echo BUILD SUCCESSFUL!
echo ================================
echo.

REM Check output file
if exist "dist\starbucks_survey.exe" (
    echo Executable created: dist\starbucks_survey.exe
    for %%I in ("dist\starbucks_survey.exe") do (
        set /a size_mb=%%~zI/1024/1024
        echo File size: %%~zI bytes (~!size_mb! MB)
    )
    echo.
    
    REM Test the executable
    echo Testing executable...
    "dist\starbucks_survey.exe" --help >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Executable test failed
        echo The exe file was created but may not work correctly
    ) else (
        echo Executable test passed!
    )
    echo.
    
    echo Build artifacts:
    echo - Executable: dist\starbucks_survey.exe
    echo - Build logs: build\
    echo.
    
    set /p run_exe="Run the executable now? (y/n): "
    if /i "!run_exe!"=="y" (
        echo.
        echo Starting application...
        start "" "dist\starbucks_survey.exe"
    )
) else (
    echo ERROR: Executable was not created!
    echo Check build logs in the build\ directory
    goto :error_exit
)

echo.
echo Build completed successfully!
goto :end

:show_help
echo Usage: build_advanced.cmd [options]
echo.
echo Options:
echo   --console    Include console window (for debugging)
echo   --clean      Clean previous builds before building
echo   --debug      Enable debug mode with verbose logging
echo   --optimize   Enable optimization (smaller file size)
echo   --help       Show this help message
echo.
echo Examples:
echo   build_advanced.cmd
echo   build_advanced.cmd --clean --optimize
echo   build_advanced.cmd --console --debug
goto :end

:error_exit
echo.
echo Build failed! Check the errors above.
echo.
pause
exit /b 1

:end
echo.
echo Press any key to exit...
pause >nul
exit /b 0