#!/bin/bash
# Скрипт для исправления проблем с ресурсами на сервере
# Запустите на сервере: bash fix_server_resources.sh

echo "=== Fixing Server Resources ==="
echo ""

# 1. Проверка текущего состояния
echo "1. Current memory usage:"
free -h
echo ""

echo "2. Current disk usage:"
df -h
echo ""

# 2. Очистка кэша пакетов
echo "3. Cleaning package cache..."
apt clean 2>/dev/null || yum clean all 2>/dev/null
echo "Done"
echo ""

# 3. Очистка старых логов
echo "4. Cleaning old logs..."
journalctl --vacuum-time=1d 2>/dev/null || echo "Journalctl not available"
echo "Done"
echo ""

# 4. Очистка временных файлов
echo "5. Cleaning temporary files..."
rm -rf /tmp/cursor-* 2>/dev/null
rm -rf /tmp/*.sh 2>/dev/null
rm -rf ~/.cursor-server-* 2>/dev/null
find /tmp -type f -mtime +7 -delete 2>/dev/null
echo "Done"
echo ""

# 5. Создание swap файла (если нет swap)
if [ $(swapon --show | wc -l) -eq 0 ]; then
    echo "6. Creating swap file (2GB)..."
    
    # Проверка свободного места
    available_space=$(df / | tail -1 | awk '{print $4}')
    if [ "$available_space" -gt 2097152 ]; then  # 2GB в KB
        # Создание swap файла
        fallocate -l 2G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=2048
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        
        # Добавление в fstab для постоянства
        if ! grep -q "/swapfile" /etc/fstab; then
            echo "/swapfile none swap sw 0 0" >> /etc/fstab
        fi
        
        echo "Swap file created successfully"
    else
        echo "Not enough disk space for swap file"
    fi
else
    echo "6. Swap already exists"
    swapon --show
fi
echo ""

# 6. Настройка swappiness (оптимизация использования swap)
echo "7. Configuring swappiness..."
if [ -f /proc/sys/vm/swappiness ]; then
    echo 10 > /proc/sys/vm/swappiness
    if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
        echo "vm.swappiness=10" >> /etc/sysctl.conf
    fi
    echo "Swappiness set to 10"
fi
echo ""

# 7. Очистка памяти (освобождение кэша)
echo "8. Freeing memory cache..."
sync
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || echo "Cannot drop caches (requires root)"
echo "Done"
echo ""

# 8. Проверка процессов, потребляющих память
echo "9. Top memory-consuming processes:"
ps aux --sort=-%mem | head -10
echo ""

# 9. Финальное состояние
echo "=== Final State ==="
echo "Memory:"
free -h
echo ""
echo "Disk:"
df -h
echo ""
echo "Swap:"
swapon --show
echo ""

echo "=== Done ==="
echo ""
echo "Recommendations:"
echo "1. If memory usage is still high, consider stopping unnecessary services"
echo "2. Check running processes with: ps aux --sort=-%mem"
echo "3. Consider upgrading server plan if issues persist"
echo ""
echo "Now try connecting with Cursor again."

