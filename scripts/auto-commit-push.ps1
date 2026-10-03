# PowerShell Auto-Commit & Push Script
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "=== Auto Commit & Push - Claude Skills Marketplace ===" -ForegroundColor Cyan
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "`n[1/3] Running Skill Doctor Linter..." -ForegroundColor Yellow
python skills/skill-doctor/scripts/skill_doctor.py skills
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Skill Doctor detected issues! Push aborted." -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/3] Staging git changes..." -ForegroundColor Yellow
git add -A

$commitMsg = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "feat(skills): update skills definition (" + (Get-Date -Format "yyyy-MM-dd HH:mm") + ")"
}

git commit -m $commitMsg

Write-Host "`n[3/3] Pushing to GitHub origin main..." -ForegroundColor Yellow
git push origin main

Write-Host "`n=== SUCCESS! Pushed to https://github.com/bakaryuu1997-sys/Claude-skills ===" -ForegroundColor Green
Write-Host "Other machines with Auto-Update enabled will sync automatically.`n" -ForegroundColor Green
