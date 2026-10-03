@echo off
chcp 65001 >nul
echo ========================================================
echo   Auto Commit & Push - Claude Skills Marketplace
echo ========================================================

cd /d "%~dp0\.."

echo [1/3] Running Skill Doctor Linter...
python skills\skill-doctor\scripts\skill_doctor.py skills
if %errorlevel% neq 0 (
    echo [ERROR] Skill Doctor failed! Please fix issues before pushing.
    pause
    exit /b %errorlevel%
)

echo [2/3] Staging git changes...
git add -A

set /p MSG="Enter commit message (Leave empty for default): "
if "%MSG%"=="" (
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set CDATE=%%c-%%a-%%b
    set MSG=feat(skills): auto-update skills collection
)

git commit -m "%MSG%"

echo [3/3] Pushing to GitHub (origin main)...
git push origin main

echo ========================================================
echo   Push completed! Other machines with Auto-Update
echo   will receive changes automatically.
echo ========================================================
pause
