@echo off
echo =======================================================
echo Starting Web Based Electronic Store System React Client
echo =======================================================

cd /d "%~dp0"
cd code\frontend\client

IF NOT EXIST "node_modules" (
    echo Installing npm dependencies...
    cmd /c npm install
)

echo Starting React Development Server...
cmd /c npm run dev
