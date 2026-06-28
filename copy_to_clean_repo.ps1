<#
.SYNOPSIS
    Copy core project files to a fresh "CareerIntel" repo directory.
    Excludes: thesis files, agent guides, memory-bank, chatbot sub-repo,
              cv_templates_output, llama binaries, test archives, dev docs.
.USAGE
    .\copy_to_clean_repo.ps1
    # Then: cd D:\CareerIntel && git init && git add . && git commit -m "init: CareerIntel clean repo"
#>

$ErrorActionPreference = "Stop"

$SRC  = "D:\Job-Market-Analytics-Platform"
$DEST = "D:\CareerIntel"

# ── 1. Create target directory ──────────────────────────────────────────────
if (Test-Path $DEST) {
    Write-Host "[!] $DEST already exists. Remove it first or choose a different path." -ForegroundColor Red
    exit 1
}
New-Item -ItemType Directory -Path $DEST -Force | Out-Null
Write-Host "[+] Created $DEST" -ForegroundColor Green

# ── 2. Root-level files to copy ─────────────────────────────────────────────
$rootFiles = @(
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "tsconfig.scripts.json",
    "next.config.js",
    "postcss.config.js",
    "tailwind.config.ts",
    ".eslintrc.json",
    "middleware.ts",
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    ".env.local.example",
    "README.md",
    "Modelfile.careerintel-hr-coach",
    "Modelfile.careerintel-structured-gen",
    "Modelfile.careerintel-tool-call",
    "supabase_user_resume_data.sql"
)

Write-Host "`n[*] Copying root files..." -ForegroundColor Cyan
foreach ($f in $rootFiles) {
    $srcPath = Join-Path $SRC $f
    if (Test-Path $srcPath) {
        Copy-Item $srcPath -Destination (Join-Path $DEST $f)
        Write-Host "    $f" -ForegroundColor Gray
    } else {
        Write-Host "    [SKIP] $f (not found)" -ForegroundColor Yellow
    }
}

# ── 3. Directories to copy (with exclusion patterns) ────────────────────────

# Helper: copy directory excluding patterns
function Copy-FilteredDir {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExcludeDirs = @(),
        [string[]]$ExcludeFiles = @()
    )

    if (!(Test-Path $Source)) {
        Write-Host "    [SKIP] $Source (not found)" -ForegroundColor Yellow
        return
    }

    # Get all items recursively
    $items = Get-ChildItem -Path $Source -Recurse -Force

    foreach ($item in $items) {
        $relativePath = $item.FullName.Substring($Source.Length)
        $destPath = Join-Path $Destination $relativePath

        # Check if path contains any excluded directory
        $skip = $false
        foreach ($exDir in $ExcludeDirs) {
            if ($relativePath -match [regex]::Escape($exDir)) {
                $skip = $true
                break
            }
        }
        if ($skip) { continue }

        # Check if file matches excluded file patterns
        if (!$item.PSIsContainer) {
            foreach ($exFile in $ExcludeFiles) {
                if ($item.Name -like $exFile) {
                    $skip = $true
                    break
                }
            }
        }
        if ($skip) { continue }

        if ($item.PSIsContainer) {
            if (!(Test-Path $destPath)) {
                New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            }
        } else {
            $parentDir = Split-Path $destPath -Parent
            if (!(Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            Copy-Item $item.FullName -Destination $destPath -Force
        }
    }
}

# Common exclusion patterns
$commonExcludeDirs  = @("__pycache__", ".git", ".gitnexus", ".claude", "node_modules", ".next")
$commonExcludeFiles = @("*.pyc", "*.pyo")

# -- app/ (Next.js pages & API routes)
Write-Host "`n[*] Copying app/ ..." -ForegroundColor Cyan
Copy-FilteredDir -Source (Join-Path $SRC "app") `
                 -Destination (Join-Path $DEST "app") `
                 -ExcludeDirs $commonExcludeDirs `
                 -ExcludeFiles $commonExcludeFiles

# -- backend/ (server-side logic)
Write-Host "[*] Copying backend/ ..." -ForegroundColor Cyan
$backendExcludeDirs = $commonExcludeDirs + @("\backend\chatbot\data")
Copy-FilteredDir -Source (Join-Path $SRC "backend") `
                 -Destination (Join-Path $DEST "backend") `
                 -ExcludeDirs $backendExcludeDirs `
                 -ExcludeFiles $commonExcludeFiles

# -- frontend/ (shared UI components)
Write-Host "[*] Copying frontend/ ..." -ForegroundColor Cyan
Copy-FilteredDir -Source (Join-Path $SRC "frontend") `
                 -Destination (Join-Path $DEST "frontend") `
                 -ExcludeDirs $commonExcludeDirs `
                 -ExcludeFiles $commonExcludeFiles

# -- public/ (static assets)
Write-Host "[*] Copying public/ ..." -ForegroundColor Cyan
Copy-FilteredDir -Source (Join-Path $SRC "public") `
                 -Destination (Join-Path $DEST "public") `
                 -ExcludeDirs $commonExcludeDirs `
                 -ExcludeFiles $commonExcludeFiles

# -- scripts/ (utilities)
Write-Host "[*] Copying scripts/ ..." -ForegroundColor Cyan
Copy-FilteredDir -Source (Join-Path $SRC "scripts") `
                 -Destination (Join-Path $DEST "scripts") `
                 -ExcludeDirs $commonExcludeDirs `
                 -ExcludeFiles $commonExcludeFiles

# -- python-ml-service/ (FastAPI ML gateway)
Write-Host "[*] Copying python-ml-service/ ..." -ForegroundColor Cyan
Copy-FilteredDir -Source (Join-Path $SRC "python-ml-service") `
                 -Destination (Join-Path $DEST "python-ml-service") `
                 -ExcludeDirs $commonExcludeDirs `
                 -ExcludeFiles $commonExcludeFiles

# -- scraper/ (Celery-based scraper for GitHub Actions)
Write-Host "[*] Copying scraper/ ..." -ForegroundColor Cyan
Copy-FilteredDir -Source (Join-Path $SRC "scraper") `
                 -Destination (Join-Path $DEST "scraper") `
                 -ExcludeDirs $commonExcludeDirs `
                 -ExcludeFiles $commonExcludeFiles

# -- .github/workflows/ (GitHub Actions)
Write-Host "[*] Copying .github/workflows/ ..." -ForegroundColor Cyan
$ghWorkflowDest = Join-Path $DEST ".github\workflows"
New-Item -ItemType Directory -Path $ghWorkflowDest -Force | Out-Null
$scrapeYml = Join-Path $SRC ".github\workflows\scrape.yml"
if (Test-Path $scrapeYml) {
    Copy-Item $scrapeYml -Destination (Join-Path $ghWorkflowDest "scrape.yml")
    Write-Host "    scrape.yml" -ForegroundColor Gray
}

# ── 4. Generate clean .gitignore ────────────────────────────────────────────
Write-Host "`n[*] Generating clean .gitignore ..." -ForegroundColor Cyan
$gitignoreContent = @"
# Dependencies
/node_modules
/.pnp
.pnp.js

# Testing
/coverage

# Next.js
/.next/
/out/

# Production
/build

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment files
.env*.local
.env.docker
.env

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts

# Scraped output
scraped_data.json
cv_templates_output/

# Python
.venv/
__pycache__/
*.py[cod]
*$py.class

# Model artifacts
adapter_model.safetensors
adapter_config.json

# Local LLM binaries
/llama.cpp*/
/llama.zip

# Backend chatbot data (local runtime)
backend/chatbot/data/
"@

Set-Content -Path (Join-Path $DEST ".gitignore") -Value $gitignoreContent -Encoding UTF8
Write-Host "    .gitignore" -ForegroundColor Gray

# ── 5. Summary ──────────────────────────────────────────────────────────────
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  CareerIntel clean repo ready at:" -ForegroundColor Green
Write-Host "  $DEST" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green

# Count files
$fileCount = (Get-ChildItem -Path $DEST -Recurse -File).Count
$dirCount  = (Get-ChildItem -Path $DEST -Recurse -Directory).Count
Write-Host "`n  Files: $fileCount | Directories: $dirCount" -ForegroundColor Cyan

Write-Host "`n[*] Next steps:" -ForegroundColor Yellow
Write-Host "    cd $DEST" -ForegroundColor White
Write-Host "    git init" -ForegroundColor White
Write-Host "    git add ." -ForegroundColor White
Write-Host '    git commit -m "init: CareerIntel - Job Market Analytics Platform"' -ForegroundColor White
Write-Host "    git remote add origin https://github.com/<your-username>/CareerIntel.git" -ForegroundColor White
Write-Host "    git push -u origin main" -ForegroundColor White
