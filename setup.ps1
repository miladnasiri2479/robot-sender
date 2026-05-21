# 🤖 Robot Sender - Automated Setup Script (Windows)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Welcome to Robot Sender Setup        " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Gather User Input
Write-Host "`n[1/3] Platform Configuration" -ForegroundColor Yellow
$source = Read-Host "Enter SOURCE platform (soroush, telegram, bale, rubika, eitaa)"
$targets_raw = Read-Host "Enter TARGET platforms (comma separated, e.g: telegram,eitaa,bale)"
$targets = $targets_raw.Split(",").Trim()

$credentials = @{}
$target_mapping = @{}

# Function to get credentials
function Get-Creds($p) {
    Write-Host "`n--- Configuration for [$p] ---" -ForegroundColor Green
    if ($p -eq "soroush") {
        $token = Read-Host "Enter Soroush Bot Token"
        return @{ "token" = $token }
    } elseif ($p -eq "telegram") {
        $token = Read-Host "Enter Telegram Bot Token"
        return @{ "token" = $token }
    } elseif ($p -eq "eitaa") {
        $token = Read-Host "Enter Eitaayar API Token"
        return @{ "token" = $token }
    } elseif ($p -eq "rubika") {
        $token = Read-Host "Enter Rubika Bot Token"
        return @{ "token" = $token }
    } elseif ($p -eq "bale") {
        $token = Read-Host "Enter Bale Bot Token"
        return @{ "token" = $token }
    }
}

# Get Source details
$source_id = Read-Host "Enter Source Channel ID"
$credentials[$source] = Get-Creds $source

# Get Target details
foreach ($t in $targets) {
    $t_id = Read-Host "Enter Channel ID for Target [$t]"
    $target_mapping[$t] = $t_id
    if (-not $credentials.ContainsKey($t)) {
        $credentials[$t] = Get-Creds $t
    }
}

# 2. Generate config.json
Write-Host "`n[2/3] Generating Configuration..." -ForegroundColor Yellow
$config = @{
    "source" = $source
    "source_channel_id" = $source_id
    "interval" = 60
    "targets" = $target_mapping
    "credentials" = $credentials
}

$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "config.json" -Encoding utf8

# 3. Finalize
Write-Host "`n[3/3] Setup Complete!" -ForegroundColor Yellow
Write-Host "All files have been generated and configured." -ForegroundColor Green

$run_now = Read-Host "`nDo you want to run the system now via Docker? (y/n)"
if ($run_now -eq "y") {
    Write-Host "Launching Docker Compose..." -ForegroundColor Cyan
    docker-compose up -d --build
    Write-Host "System is running in background!" -ForegroundColor Green
    Write-Host "Use 'docker-compose logs -f app' to see live logs."
} else {
    Write-Host "You can start the system later by running: docker-compose up -d" -ForegroundColor White
}

Write-Host "`nPress any key to exit..."
$null = [Console]::ReadKey()
