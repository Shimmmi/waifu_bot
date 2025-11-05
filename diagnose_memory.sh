#!/bin/bash
# Скрипт для диагностики использования памяти на сервере
# Запуск: bash diagnose_memory.sh

echo "=========================================="
echo "   Memory Usage Diagnostic Report"
echo "=========================================="
echo ""

echo "1. SYSTEM MEMORY STATUS:"
echo "------------------------"
free -h
echo ""

echo "2. MEMORY DETAILS (from /proc/meminfo):"
echo "----------------------------------------"
cat /proc/meminfo | grep -E 'MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree|Shmem|Slab|SReclaimable|SUnreclaim'
echo ""

echo "3. TOP 15 PROCESSES BY MEMORY USAGE:"
echo "-------------------------------------"
ps aux --sort=-%mem --width=200 | head -16
echo ""

echo "4. MEMORY USAGE BY USER:"
echo "------------------------"
ps aux | awk 'NR>1 {arr[$1]+=$4} END {for (i in arr) print i, arr[i]"%"}'
echo ""

echo "5. PROCESSES WITH HIGH MEMORY (>100MB RSS):"
echo "--------------------------------------------"
ps aux --sort=-%mem | awk 'NR==1 || $6 > 102400 {printf "%-10s %6s %5s%% %10s %s\n", $1, $6/1024"M", $4, $2, $11}'
echo ""

echo "6. SYSTEM LOAD AND UPTIME:"
echo "---------------------------"
uptime
echo ""

echo "7. DISK USAGE:"
echo "--------------"
df -h
echo ""

echo "8. SWAP STATUS:"
echo "---------------"
swapon --show
if [ $(swapon --show | wc -l) -eq 0 ]; then
    echo "⚠️  WARNING: No swap configured!"
fi
echo ""

echo "9. RUNNING SERVICES:"
echo "--------------------"
systemctl list-units --type=service --state=running --no-pager | head -20
echo ""

echo "10. DOCKER CONTAINERS (if Docker is installed):"
echo "-----------------------------------------------"
if command -v docker &> /dev/null; then
    docker stats --no-stream 2>/dev/null || echo "Docker is not running or requires sudo"
else
    echo "Docker is not installed"
fi
echo ""

echo "11. LARGE FILES IN MEMORY (if lsof is available):"
echo "-------------------------------------------------"
if command -v lsof &> /dev/null; then
    lsof 2>/dev/null | awk '{print $2}' | sort -u | xargs -I {} sh -c 'ps -p {} -o pid=,rss=,comm= 2>/dev/null' | awk '$2 > 100000 {printf "PID: %-6s RSS: %8s KB %s\n", $1, $2, $3}' | head -10
else
    echo "lsof is not installed (install with: apt install lsof)"
fi
echo ""

echo "=========================================="
echo "   Recommendations:"
echo "=========================================="
AVAILABLE=$(free | awk '/^Mem:/ {print $7}')
TOTAL=$(free | awk '/^Mem:/ {print $2}')
AVAILABLE_MB=$((AVAILABLE / 1024))
TOTAL_MB=$((TOTAL / 1024))

if [ $AVAILABLE_MB -lt 200 ]; then
    echo "❌ CRITICAL: Only ${AVAILABLE_MB} MB available (${TOTAL_MB} MB total)"
    echo "   Action required: Create swap file and free memory"
elif [ $AVAILABLE_MB -lt 512 ]; then
    echo "⚠️  WARNING: Only ${AVAILABLE_MB} MB available (${TOTAL_MB} MB total)"
    echo "   Recommendation: Create swap file for better stability"
else
    echo "✅ OK: ${AVAILABLE_MB} MB available (${TOTAL_MB} MB total)"
fi

if [ $(swapon --show | wc -l) -eq 0 ]; then
    echo "⚠️  WARNING: No swap configured"
    echo "   Recommendation: Create 2GB swap file"
fi

echo ""
echo "=========================================="

