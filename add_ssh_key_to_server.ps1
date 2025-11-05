# Скрипт для добавления SSH ключа на сервер RocketCloud
# Использование: .\add_ssh_key_to_server.ps1

$publicKey = Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub"
$serverIP = "45.156.21.149"

Write-Host "Ваш публичный SSH ключ:" -ForegroundColor Green
Write-Host $publicKey -ForegroundColor Yellow
Write-Host ""

Write-Host "Инструкция по добавлению ключа:" -ForegroundColor Cyan
Write-Host "1. Подключитесь к серверу через аварийную консоль RocketCloud" -ForegroundColor White
Write-Host "2. Или подключитесь с паролем: ssh root@$serverIP" -ForegroundColor White
Write-Host "3. Выполните следующие команды на сервере:" -ForegroundColor White
Write-Host ""

Write-Host "mkdir -p ~/.ssh" -ForegroundColor Green
Write-Host "chmod 700 ~/.ssh" -ForegroundColor Green
Write-Host "echo `"$publicKey`" >> ~/.ssh/authorized_keys" -ForegroundColor Green
Write-Host "chmod 600 ~/.ssh/authorized_keys" -ForegroundColor Green
Write-Host ""

Write-Host "После выполнения этих команд, попробуйте подключиться:" -ForegroundColor Cyan
Write-Host "ssh rocketcloud-vps" -ForegroundColor Yellow

