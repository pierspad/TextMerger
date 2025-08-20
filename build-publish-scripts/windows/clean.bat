@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo     TextMerger Windows Clean Script
echo ========================================
echo.

:: Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: Get directories
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\.."
set "BUILD_DIR=%SCRIPT_DIR%"

echo %BLUE%Cleaning build artifacts...%NC%

:: Change to windows build directory 
cd /d "%BUILD_DIR%"

:: Remove PyInstaller directories from windows build directory
if exist "dist" (
    echo %YELLOW%Removing dist directory...%NC%
    rmdir /s /q "dist"
)

if exist "build" (
    echo %YELLOW%Removing build directory...%NC%
    rmdir /s /q "build"
)

:: Change to project root for global cleanup
cd /d "%PROJECT_ROOT%"

:: Remove spec build cache
if exist "__pycache__" (
    echo %YELLOW%Removing __pycache__ directories...%NC%
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
)

:: Remove built executables from windows build directory
echo %YELLOW%Removing old executables from windows build directory...%NC%
cd /d "%BUILD_DIR%"
if exist "TextMerger*.exe" (
    del "TextMerger*.exe"
)

:: List remaining files in build directory
echo %BLUE%Remaining files in windows build directory:%NC%
dir "%BUILD_DIR%" /b

echo.
echo %GREEN%Clean completed!%NC%
pause
