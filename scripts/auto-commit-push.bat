@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

rem Usage: auto-commit-push.bat "commit message" [new-file-or-folder ...]
rem Lints the skill set, stages tracked changes (git add -u) plus the listed paths, commits, pull --rebase, push. Never force-pushes.

if "%~1"=="" (
    echo Usage: %~nx0 "commit message" [new-file-or-folder ...]
    echo   Staged: tracked files that changed + the paths you list. "git add -A" is never used.
    exit /b 2
)

set "MSG=%~1"
shift
set "EXTRA="
:collect
if "%~1"=="" goto run
set EXTRA=!EXTRA! "%~1"
shift
goto collect

:run
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto-commit-push.ps1" -Message "!MSG!" !EXTRA!
exit /b %errorlevel%
