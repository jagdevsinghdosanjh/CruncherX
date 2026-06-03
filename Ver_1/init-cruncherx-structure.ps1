# init-cruncherx-structure.ps1
# Clean, safe, error-proof version

param(
    [string]$RootPath = "."
)

$projectRoot = "$RootPath\CruncherX"

function MakeDir($path) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
    }
}

function MakeFile($path, $content = "") {
    if (-not (Test-Path $path)) {
        New-Item -ItemType File -Path $path -Value $content | Out-Null
    }
}

# -------------------------
# ROOT
# -------------------------
MakeDir $projectRoot

# -------------------------
# .streamlit
# -------------------------
$streamlit = "$projectRoot\.streamlit"
MakeDir $streamlit
MakeFile "$streamlit\config.toml" "# CruncherX theme config"
MakeFile "$streamlit\secrets.toml" "# SUPABASE_URL="" ""`n# SUPABASE_KEY="" """
MakeFile "$streamlit\runtime.txt" "3.11"

# -------------------------
# supabase
# -------------------------
$supabase = "$projectRoot\supabase"
MakeDir $supabase
MakeDir "$supabase\migrations"
MakeDir "$supabase\schemas"
MakeDir "$supabase\policies"
MakeDir "$supabase\seed"

MakeFile "$supabase\client.py" @"
from supabase import create_client
import os

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase env vars not set")
    return create_client(url, key)
"@

# -------------------------
# core
# -------------------------
$core = "$projectRoot\core"
MakeDir $core

$coreFolders = @("auth","billing","monitoring","orgs","plans","usage","database","utils")
foreach ($f in $coreFolders) {
    MakeDir "$core\$f"
    MakeFile "$core\$f\__init__.py"
}
MakeFile "$core\__init__.py"

# -------------------------
# services
# -------------------------
$services = "$projectRoot\services"
MakeDir $services

$serviceFolders = @("compression","ocr","analytics","logging","self_heal")
foreach ($f in $serviceFolders) {
    MakeDir "$services\$f"
    MakeFile "$services\$f\__init__.py"
}
MakeFile "$services\__init__.py"

# -------------------------
# engines
# -------------------------
$engines = "$projectRoot\engines"
MakeDir $engines

$engineFolders = @("cloud","local","shared")
foreach ($f in $engineFolders) {
    MakeDir "$engines\$f"
    MakeFile "$engines\$f\__init__.py"
}
MakeFile "$engines\__init__.py"

# -------------------------
# ui
# -------------------------
$ui = "$projectRoot\ui"
MakeDir $ui

$uiFolders = @("components","layouts","themes")
foreach ($f in $uiFolders) {
    MakeDir "$ui\$f"
    MakeFile "$ui\$f\__init__.py"
}
MakeFile "$ui\__init__.py"

# Sidebar + Footer
MakeFile "$ui\components\sidebar.py" "import streamlit as st`n# def render_sidebar(): ..."
MakeFile "$ui\components\footer.py" "import streamlit as st`n# def render_footer(): ..."

# -------------------------
# pages
# -------------------------
$pages = "$projectRoot\pages"
MakeDir $pages

$pageFolders = @("dashboard","admin","compression","ocr","billing","support","about")
foreach ($f in $pageFolders) {
    MakeDir "$pages\$f"
    MakeFile "$pages\$f\__init__.py"
}
MakeFile "$pages\__init__.py"

# -------------------------
# config
# -------------------------
$config = "$projectRoot\config"
MakeDir $config

MakeFile "$config\__init__.py"
MakeFile "$config\settings.py" @"
APP_NAME = "CruncherX"
THEME_PRIMARY = "#39FF14"
THEME_BG = "#000000"
"@
MakeFile "$config\constants.py" "# shared constants"
MakeFile "$config\environment.py" "# env helpers"

# -------------------------
# scripts
# -------------------------
$scripts = "$projectRoot\scripts"
MakeDir $scripts

MakeFile "$scripts\deploy.sh" "#!/bin/bash`n# deploy CruncherX"
MakeFile "$scripts\migrate.py" "# db migration entrypoint"
MakeFile "$scripts\clean_metadata.py" "# self-heal script"

# -------------------------
# tests
# -------------------------
$tests = "$projectRoot\tests"
MakeDir $tests

$testFiles = @("test_engines.py","test_auth.py","test_billing.py","test_monitoring.py")
foreach ($t in $testFiles) {
    MakeFile "$tests\$t" "# pytest skeleton"
}

# -------------------------
# app entry
# -------------------------
$app = "$projectRoot\app"
MakeDir $app
MakeFile "$app\__init__.py"
MakeFile "$app\Home.py" @"
import streamlit as st
st.set_page_config(page_title='CruncherX', layout='wide')
st.title('CruncherX')
st.write('Smaller PDFs. Bigger Productivity.')
"@

# -------------------------
# README
# -------------------------
MakeFile "$projectRoot\README.md" "# CruncherX SaaS Structure"

Write-Host "CruncherX SaaS structure created successfully."
