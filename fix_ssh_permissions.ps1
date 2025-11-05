# Script to fix SSH file permissions on Windows
# Run this script as Administrator

Write-Host "Fixing SSH file permissions..." -ForegroundColor Green
Write-Host ""

$sshPath = "$env:USERPROFILE\.ssh"
$configPath = "$env:USERPROFILE\.ssh\config"
$keyPath = "$env:USERPROFILE\.ssh\id_ed25519"
$username = $env:USERNAME

# Check if .ssh folder exists
if (Test-Path $sshPath) {
    Write-Host "1. Fixing permissions for .ssh folder..." -ForegroundColor Yellow
    & icacls $sshPath /inheritance:r | Out-Null
    $grantCmd = $username + ':(OI)(CI)F'
    & icacls $sshPath /grant:r $grantCmd | Out-Null
    Write-Host "   .ssh folder fixed" -ForegroundColor Green
} else {
    Write-Host "   .ssh folder not found" -ForegroundColor Yellow
}

# Check if config file exists
if (Test-Path $configPath) {
    Write-Host "2. Fixing permissions for config file..." -ForegroundColor Yellow
    & icacls $configPath /inheritance:r | Out-Null
    $grantCmd = $username + ':(R,W)'
    & icacls $configPath /grant:r $grantCmd | Out-Null
    Write-Host "   config file fixed" -ForegroundColor Green
} else {
    Write-Host "   config file not found" -ForegroundColor Yellow
}

# Check if private key exists
if (Test-Path $keyPath) {
    Write-Host "3. Fixing permissions for private key..." -ForegroundColor Yellow
    & icacls $keyPath /inheritance:r | Out-Null
    $grantCmd = $username + ':(R)'
    & icacls $keyPath /grant:r $grantCmd | Out-Null
    Write-Host "   private key fixed" -ForegroundColor Green
} else {
    Write-Host "   private key not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking permissions:" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $configPath) {
    Write-Host "Config file permissions:" -ForegroundColor Yellow
    icacls $configPath
    Write-Host ""
}

Write-Host "Done! Now try to connect again in Cursor." -ForegroundColor Green
