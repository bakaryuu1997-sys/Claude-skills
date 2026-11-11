<#
.SYNOPSIS
  Lint the skill set (x6-skill-doctor), commit and push to origin/main. Non-interactive, never force-pushes.

.DESCRIPTION
  1. Runs skills/x6-skill-doctor/scripts/skill_doctor.py; any FAIL aborts before anything is staged.
  2. Stages ONLY already-tracked files that changed (git add -u) plus the paths you pass explicitly
     (new files must be listed). It never runs "git add -A", so stray files are not committed.
  3. Commits with -Message, then "git pull --rebase origin main" and "git push origin main" (no --force).
     If rebase or push fails the commit stays local and the script exits non-zero.

.PARAMETER Message
  Commit message (Conventional Commits recommended, e.g. "fix(skills): ..."). Required, no prompt.

.PARAMETER Paths
  Extra (new/untracked) files or folders to stage, relative to the repo root.

.PARAMETER NoPush
  Commit but do not pull/push.

.PARAMETER DryRun
  Run the linter and print what would be staged; change nothing.

.EXAMPLE
  powershell -File scripts\auto-commit-push.ps1 -Message "fix(skills): sync counts" skills\d2-uat-acceptance\scripts\punch_list_to_backlog.py
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Message,
    [switch]$NoPush,
    [switch]$DryRun,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Paths
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONDONTWRITEBYTECODE = "1"

function Fail([string]$Text, [int]$Code = 1) {
    Write-Host "[ERROR] $Text" -ForegroundColor Red
    exit $Code
}

function Invoke-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) { Fail ("git " + ($args -join " ") + " failed (exit code $LASTEXITCODE)") }
}

if ([string]::IsNullOrWhiteSpace($Message)) { Fail "Message must not be empty." 2 }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail "git not found in PATH." 2 }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Fail "python not found in PATH." 2 }

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "=== Auto Commit & Push ($root) ===" -ForegroundColor Cyan

$branch = (& git rev-parse --abbrev-ref HEAD).Trim()
if ($branch -ne "main") { Fail "Current branch is '$branch'; this script only publishes from 'main'." 2 }

Write-Host "`n[1/3] Skill Doctor linter..." -ForegroundColor Yellow
& python -B skills/x6-skill-doctor/scripts/skill_doctor.py skills
if ($LASTEXITCODE -ne 0) { Fail "Skill Doctor reported FAIL. Nothing was staged, committed or pushed." 3 }

# Validate explicit paths: inside the repo, not secrets/runtime state.
$blocked = '(^|[\\/])(project-context\.json|\.env[^\\/]*|\.context-history|[^\\/]*\.archive\.jsonl|[^\\/]*\.pem|[^\\/]*\.key)$'
$resolved = @()
foreach ($p in $Paths) {
    if ([string]::IsNullOrWhiteSpace($p)) { continue }
    $full = [System.IO.Path]::GetFullPath((Join-Path $root $p))
    if (-not $full.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) { Fail "Path is outside the repository: $p" 2 }
    if (-not (Test-Path -LiteralPath $full)) { Fail "Path does not exist: $p" 2 }
    if ($full -match $blocked) { Fail "Refusing to stage a secret/runtime file: $p" 2 }
    $resolved += $p
}

Write-Host "`n[2/3] Staging..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "DryRun: would run 'git add -u' (tracked files changed below) and add: $($resolved -join ', ')" -ForegroundColor Magenta
    & git diff --name-only
    exit 0
}
Invoke-Git add -u
foreach ($p in $resolved) { Invoke-Git add -- $p }

& git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Write-Host "Nothing staged - no commit created." -ForegroundColor Yellow; exit 0 }
& git diff --cached --stat

Invoke-Git commit -m $Message

if ($NoPush) { Write-Host "`nCommitted locally (-NoPush)." -ForegroundColor Green; exit 0 }

Write-Host "`n[3/3] Pull --rebase and push (no force)..." -ForegroundColor Yellow
& git pull --rebase origin main
if ($LASTEXITCODE -ne 0) { Fail "Rebase failed. The commit is kept locally; resolve conflicts, then push manually." 4 }
& git push origin main
if ($LASTEXITCODE -ne 0) { Fail "Push failed. The commit is kept locally. Check access to the remote (repository must be reachable and you need write permission)." 5 }

Write-Host "`n=== Pushed to origin/main. Machines with Auto-Update enabled will sync. ===" -ForegroundColor Green
