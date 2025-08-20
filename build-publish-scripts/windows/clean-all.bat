@echo off
echo Cleaning build artifacts and temporary files...

cd /d "%~dp0..\.."

:: Remove egg-info directories
if exist "textmerger.egg-info" (
    echo Removing textmerger.egg-info...
    rmdir /s /q "textmerger.egg-info"
)

:: Remove build directory
if exist "build" (
    echo Removing build directory...
    rmdir /s /q "build"
)

:: Remove dist directory
if exist "dist" (
    echo Removing dist directory...
    rmdir /s /q "dist"
)

:: Remove __pycache__ directories
echo Removing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

:: Remove .pyc files
echo Removing .pyc files...
del /s /q *.pyc

echo Clean complete!
