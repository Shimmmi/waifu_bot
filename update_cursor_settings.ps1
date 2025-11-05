# Script to update Cursor settings for Remote SSH timeouts
# Run this script to automatically add timeout settings to Cursor

Write-Host "Updating Cursor settings for Remote SSH..." -ForegroundColor Green
Write-Host ""

$settingsPath = "$env:APPDATA\Cursor\User\settings.json"
$settingsDir = "$env:APPDATA\Cursor\User"

# Create directory if it doesn't exist
if (-not (Test-Path $settingsDir)) {
    Write-Host "Creating settings directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
}

# Read existing settings or create new
$settings = @{}
if (Test-Path $settingsPath) {
    Write-Host "Reading existing settings..." -ForegroundColor Yellow
    try {
        $content = Get-Content $settingsPath -Raw -Encoding UTF8
        $settings = $content | ConvertFrom-Json -AsHashtable
        if (-not $settings) {
            $settings = @{}
        }
    } catch {
        Write-Host "Warning: Could not parse existing settings. Creating new file." -ForegroundColor Yellow
        $settings = @{}
    }
}

# Add or update Remote SSH timeout settings
Write-Host "Adding Remote SSH timeout settings..." -ForegroundColor Yellow

$settings["remote.SSH.connectTimeout"] = 120
$settings["remote.SSH.serverInstallTimeout"] = 300
$settings["remote.SSH.remoteServerListenOnSocket"] = $true
$settings["remote.SSH.useLocalServer"] = $false

# Convert to JSON with proper formatting
$jsonContent = $settings | ConvertTo-Json -Depth 10

# Write to file
try {
    $jsonContent | Set-Content -Path $settingsPath -Encoding UTF8 -Force
    Write-Host "Settings updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Settings file: $settingsPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Added settings:" -ForegroundColor Yellow
    Write-Host "  - remote.SSH.connectTimeout: 120" -ForegroundColor White
    Write-Host "  - remote.SSH.serverInstallTimeout: 300" -ForegroundColor White
    Write-Host "  - remote.SSH.remoteServerListenOnSocket: true" -ForegroundColor White
    Write-Host "  - remote.SSH.useLocalServer: false" -ForegroundColor White
    Write-Host ""
    Write-Host "Now restart Cursor and try connecting again." -ForegroundColor Green
} catch {
    Write-Host "Error writing settings: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please manually edit: $settingsPath" -ForegroundColor Yellow
    Write-Host "Add these settings:" -ForegroundColor Yellow
    Write-Host '{' -ForegroundColor White
    Write-Host '    "remote.SSH.connectTimeout": 120,' -ForegroundColor White
    Write-Host '    "remote.SSH.serverInstallTimeout": 300,' -ForegroundColor White
    Write-Host '    "remote.SSH.remoteServerListenOnSocket": true,' -ForegroundColor White
    Write-Host '    "remote.SSH.useLocalServer": false' -ForegroundColor White
    Write-Host '}' -ForegroundColor White
}

