# Скрипт полной остановки сервисов LRE (порты 8000 и 8080)

Write-Host "Остановка сервисов LRE..." -ForegroundColor Yellow

$ports = @(8000, 8080)

# 1. Поиск и остановка процессов по портам 8000 и 8080
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            if ($procId -gt 0) {
                try {
                    taskkill /F /PID $procId /T 2>$null
                    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                    Write-Host "  [OK] Освобожден порт $port (PID $procId)" -ForegroundColor Green
                } catch {}
            }
        }
    } else {
        Write-Host "  [-] Порт $port свободен" -ForegroundColor DarkGray
    }
}

# 2. Остановка всех дочерних процессов Python (включая воркеры uvicorn и python3.13)
$pyProcs = Get-Process | Where-Object { $_.ProcessName -like "python*" }
foreach ($p in $pyProcs) {
    try {
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Завершен процесс $($p.ProcessName) (PID $($p.Id))" -ForegroundColor Green
    } catch {}
}

Write-Host "`nВсе сервисы LRE полностью остановлены, порты 8000 и 8080 свободны." -ForegroundColor Cyan
