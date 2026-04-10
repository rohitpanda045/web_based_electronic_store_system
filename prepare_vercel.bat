@echo off
echo =======================================================
echo Preparing Project for Vercel Deployment
echo =======================================================

cd /d "%~dp0"

echo Moving Python files to root...
xcopy /E /Y "code\backend\*" .\

echo Moving frontend static files to root...
mkdir static 2>nul
xcopy /E /Y "code\frontend\static\*" .\static\

echo Moving frontend templates to root...
mkdir templates 2>nul
xcopy /E /Y "code\frontend\templates\*" .\templates\

echo Deleting obsolete directories...
rmdir /S /Q code

echo Removing old scripts...
del /F /Q run_react.bat
del /F /Q run_local.bat
del /F /Q cleanup_and_run.bat

echo Creating a new running script for testing...
echo python app.py > run_server.bat

echo.
echo =======================================================
echo SUCCESS! Your project is now flattened and ready for Vercel.
echo You can test it locally by running "run_server.bat".
echo =======================================================
pause
