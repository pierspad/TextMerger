@echo off
setlocal enabledelayedexpansion

:: Windows Build Script
echo ========================================
echo.

:: Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: Get script directory and project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\.."
set "BUILD_DIR=%SCRIPT_DIR%"
set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "PIP_EXE=%PROJECT_ROOT%\.venv\Scripts\pip.exe"

:: Create build directory if it doesn't exist
if not exist "%BUILD_DIR%" (
    mkdir "%BUILD_DIR%"
)

:: Check if virtual environment exists, if not use system Python
if not exist "%PYTHON_EXE%" (
    echo %YELLOW%Virtual environment not found, using system Python...%NC%
    set "PYTHON_EXE=python"
    set "PIP_EXE=pip"
) else (
    echo %GREEN%Using virtual environment Python%NC%
)

:: Check if Python is installed
echo %BLUE%Checking Python installation...%NC%
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Python is not installed or not in PATH%NC%
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Show Python version and location
echo %BLUE%Python version:%NC%
"%PYTHON_EXE%" --version
echo %BLUE%Python executable:%NC%
echo %PYTHON_EXE%
if "%PYTHON_EXE%"=="python" (
    echo %BLUE%Python location:%NC%
    where python 2>nul || echo System Python not found in PATH
)

:: Check if PyInstaller is installed
echo %BLUE%Checking PyInstaller...%NC%
"%PYTHON_EXE%" -c "import PyInstaller; print('PyInstaller version:', PyInstaller.__version__)" 2>nul
if errorlevel 1 (
    echo %YELLOW%PyInstaller not found. Installing...%NC%
    "%PIP_EXE%" install pyinstaller
    if errorlevel 1 (
        echo %RED%Error: Failed to install PyInstaller%NC%
        pause
        exit /b 1
    )
)

:: Install dependencies
echo %BLUE%Installing dependencies...%NC%
cd /d "%PROJECT_ROOT%"
if exist requirements.txt (
    echo %BLUE%Installing from requirements.txt...%NC%
    "%PIP_EXE%" install -r requirements.txt
    if errorlevel 1 (
        echo %RED%Error: Failed to install dependencies from requirements.txt%NC%
        pause
        exit /b 1
    )
) else (
    echo %YELLOW%No requirements.txt found. Installing manually...%NC%
    "%PIP_EXE%" install "PyQt5>=5.15.11" "Flask>=3.1.1" "Werkzeug>=3.1.3"
    if errorlevel 1 (
        echo %RED%Error: Failed to install dependencies%NC%
        pause
        exit /b 1
    )
)

:: Clean previous builds
echo %BLUE%Cleaning previous builds...%NC%
cd /d "%BUILD_DIR%"
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "TextMerger*.exe" del "TextMerger*.exe"

:: Back to project root for version extraction
cd /d "%PROJECT_ROOT%"

:: Extract version from pyproject.toml
echo %BLUE%Extracting version...%NC%
for /f "tokens=2 delims== " %%a in ('findstr "version" pyproject.toml') do (
    set "VERSION=%%a"
    set "VERSION=!VERSION:"=!"
    set "VERSION=!VERSION: =!"
)

if "!VERSION!"=="" (
    echo %RED%Error: Could not extract version from pyproject.toml%NC%
    pause
    exit /b 1
)

echo %GREEN%Found version: !VERSION!%NC%

:: Verify spec file exists
if not exist "%SCRIPT_DIR%textmerger.spec" (
    echo %RED%Error: textmerger.spec not found in windows build directory%NC%
    echo %YELLOW%Looking for: %SCRIPT_DIR%textmerger.spec%NC%
    pause
    exit /b 1
)

:: Build executable from windows directory
echo %BLUE%Building Windows executable...%NC%
echo This may take a few minutes...
echo %BLUE%Command: "%PYTHON_EXE%" -m PyInstaller "%SCRIPT_DIR%textmerger.spec" --clean --noconfirm --workpath "%BUILD_DIR%build" --distpath "%BUILD_DIR%dist"%NC%

cd /d "%BUILD_DIR%"
"%PYTHON_EXE%" -m PyInstaller "textmerger.spec" --clean --noconfirm --workpath "build" --distpath "dist"

if errorlevel 1 (
    echo %RED%Error: PyInstaller build failed%NC%
    echo %YELLOW%Check the output above for details%NC%
    pause
    exit /b 1
)

:: Check if executable was created
echo %BLUE%Checking if executable was created...%NC%
if not exist "dist\TextMerger.exe" (
    echo %RED%Error: TextMerger.exe was not created in dist folder%NC%
    echo %YELLOW%Contents of dist folder:%NC%
    if exist "dist" (
        dir "dist"
    ) else (
        echo No dist folder found
    )
    pause
    exit /b 1
)

:: Get info about the created executable
echo %GREEN%Executable found!%NC%
for %%F in ("dist\TextMerger.exe") do (
    echo File: %%~nxF
    echo Size: %%~zF bytes
    echo Modified: %%~tF
)

:: Test the executable briefly
echo %BLUE%Testing executable...%NC%
echo Starting TextMerger for 3 seconds to verify it works...
start "TextMerger Test" "dist\TextMerger.exe"
timeout /t 3 /nobreak >nul
taskkill /f /im TextMerger.exe >nul 2>&1

:: Copy to build directory with version
set "EXE_NAME=TextMerger-!VERSION!-windows.exe"
echo %BLUE%Copying executable to: %BUILD_DIR%!EXE_NAME!%NC%

copy "dist\TextMerger.exe" "!EXE_NAME!"

if errorlevel 1 (
    echo %RED%Error: Failed to copy executable to build directory%NC%
    pause
    exit /b 1
)

:: Verify the final file exists and get its info
if not exist "!EXE_NAME!" (
    echo %RED%Error: Final executable not found at expected location%NC%
    pause
    exit /b 1
)

:: Get file size in MB
for %%F in ("!EXE_NAME!") do set "FILE_SIZE=%%~zF"
set /a "FILE_SIZE_MB=!FILE_SIZE! / 1048576"

:: Final verification
echo %BLUE%Final verification...%NC%
if exist "!EXE_NAME!" (
    echo %GREEN%✓ Executable exists at: %BUILD_DIR%!EXE_NAME!%NC%
    echo %GREEN%✓ File size: !FILE_SIZE_MB! MB%NC%
) else (
    echo %RED%✗ Final executable not found%NC%
    exit /b 1
)

echo.
echo %GREEN%========================================%NC%
echo %GREEN%     Build completed successfully!%NC%
echo %GREEN%========================================%NC%
echo.
echo %GREEN%Executable created: %BUILD_DIR%!EXE_NAME!%NC%
echo %GREEN%File size: !FILE_SIZE_MB! MB%NC%
echo.
echo %YELLOW%To test the executable manually:%NC%
echo "%BUILD_DIR%!EXE_NAME!"
echo.

:: Ask if user wants to test now
set /p "test_now=Do you want to test the executable now? (y/n): "
if /i "%test_now%"=="y" (
    echo %BLUE%Starting TextMerger...%NC%
    start "" "!EXE_NAME!"
)

echo %GREEN%Build script completed successfully!%NC%
pause
