Write-Host "=== CruncherX Environment Reset ===" -ForegroundColor Cyan

# Step 1 — Remove old virtual environment
if (Test-Path ".venv") {
    Write-Host "Removing old .venv..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

# Step 2 — Create new virtual environment
Write-Host "Creating new virtual environment..." -ForegroundColor Cyan
python -m venv .venv

# Step 3 — Activate environment
Write-Host "Activating environment..." -ForegroundColor Cyan
.\.venv\Scripts\activate

# Step 4 — Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Step 5 — Install requirements
Write-Host "Installing requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt

# Step 6 — Run CruncherX
Write-Host "Launching CruncherX..." -ForegroundColor Green
streamlit run app/Home.py
