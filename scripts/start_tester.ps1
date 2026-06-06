$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PreferredPort = 8000
$CandidatePorts = @($PreferredPort, 8010, 8011, 8012)

function Test-BotServer {
    param([int]$Port)

    try {
        $health = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 2
        $tester = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/tester" -UseBasicParsing -TimeoutSec 2
        return $health.StatusCode -eq 200 -and $tester.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Test-PortAvailable {
    param([int]$Port)

    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $connection = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        $connected = $connection.AsyncWaitHandle.WaitOne(250, $false)
        $client.Close()
        return -not $connected
    }
    catch {
        return $true
    }
}

if (-not (Test-Path -LiteralPath $PythonPath)) {
    throw "Virtual environment Python was not found at $PythonPath. Run the setup commands from docs\README.md first."
}

$SelectedPort = $null
foreach ($port in $CandidatePorts) {
    if (Test-BotServer -Port $port) {
        $SelectedPort = $port
        break
    }
}

if ($SelectedPort -eq $null) {
    foreach ($port in $CandidatePorts) {
        if (Test-PortAvailable -Port $port) {
            $SelectedPort = $port
            break
        }
    }
}

if ($SelectedPort -eq $null) {
    throw "Could not find a free local port for the BOT V1 tester."
}

if (-not (Test-BotServer -Port $SelectedPort)) {
    Start-Process `
        -FilePath $PythonPath `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$SelectedPort" `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden

    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Milliseconds 500
        if (Test-BotServer -Port $SelectedPort) {
            break
        }
    }
}

$TesterUrl = "http://127.0.0.1:$SelectedPort/tester"
Start-Process $TesterUrl

