@echo off
chcp 65001 >nul
echo ========================================================
echo   Auto Commit ^& Push - Claude Skills Marketplace
echo ========================================================

cd /d "%~dp0\.."

echo [1/3] Running Skill Doctor Linter...
python skills\x6-skill-doctor\scripts\skill_doctor.py skills
if %errorlevel% neq 0 (
    echo [ERROR] Skill Doctor failed! Please fix issues before pushing.
    pause
    exit /b %errorlevel%
)

if not exist ".git" (
    echo [INIT] Khoi tao Git repository va gan remote origin...
    git init
    git branch -M main
    git remote add origin https://github.com/bakaryuu1997-sys/Claude-skills.git
)

echo [2/3] Staging git changes...
git add -A

set /p MSG="Enter commit message (Leave empty for default): "
if "%MSG%"=="" (
    set MSG=feat(skills): auto-update skills collection
)

git commit -m "%MSG%"

echo [3/3] Pushing to GitHub (origin main)...
git push origin main
if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo [CANH BAO PUSH THAT BAI]:
    echo Neu gap loi 'Repository not found' hoac 'Permission denied':
    echo 1. Chuyen repo 'Claude-skills' tren GitHub sang PUBLIC (Khuyen nghi)
    echo    hoac:
    echo 2. Vao GitHub repo Settings -^> Collaborators -^> Add 'bakaryuu1997-sys'
    echo ========================================================
) else (
    echo ========================================================
    echo   Push completed! Other machines with Auto-Update
    echo   will receive changes automatically.
    echo ========================================================
)
pause
