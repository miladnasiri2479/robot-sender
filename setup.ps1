# 🤖 Robot Sender - Automated Setup Script (Windows)

# Set Output Encoding to UTF8 for better compatibility
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Show-Header {
    Clear-Host
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "   Welcome to Robot Sender Setup        " -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
}

$platforms = @("telegram", "bale", "eitaa", "rubika", "soroush")
$examples = @{
    "telegram" = "@channelname (Public) or -100xxxx (Private)"
    "bale"     = "cxxxx (Example: c0221345678)"
    "eitaa"    = "@channelname"
    "rubika"   = "@channelname or cxxxx"
    "soroush"  = "channel_id"
}

$token_names = @{
    "telegram" = "Bot Token (from @BotFather)"
    "bale"     = "Bot Token (from @BotFather)"
    "eitaa"    = "Eitaayar API Token (from eitaayar.ir)"
    "rubika"   = "Bot Token (from @BotFather)"
    "soroush"  = "Bot Token (from @mrbot)"
}

function Get-PlatformSelection($title) {
    Write-Host "`n$title" -ForegroundColor Gray
    for ($i = 0; $i -lt $platforms.Count; $i++) {
        Write-Host "  $($i + 1). $($platforms[$i])"
    }
    
    $choice = -1
    while ($choice -lt 1 -or $choice -gt $platforms.Count) {
        $input = Read-Host "Select a platform (1-$($platforms.Count))"
        if ([int]::TryParse($input, [ref]$choice)) {
            if ($choice -lt 1 -or $choice -gt $platforms.Count) {
                Write-Host "Invalid choice." -ForegroundColor Red
            }
        } else {
            Write-Host "Please enter a number." -ForegroundColor Red
            $choice = -1
        }
    }
    return $platforms[$choice - 1]
}

$credentials = @{}
$target_mapping = @{}

Show-Header

# 1. Source Configuration
Write-Host "`n[1/3] Source Configuration (Where to read from)" -ForegroundColor Yellow
$source = Get-PlatformSelection "Select the SOURCE platform:"

Write-Host "`nConfiguring $source as source..." -ForegroundColor Green
$source_example = $examples[$source]
$source_id = Read-Host "Enter Source Channel ID (Example: $source_example)"

Write-Host "`n--- Why is a token needed? ---" -ForegroundColor Gray
Write-Host "To read messages from $source, the bot must be an administrator in the channel." -ForegroundColor Gray
$source_token_name = $token_names[$source]
$source_token = Read-Host "Enter $source_token_name"

$credentials[$source] = @{ "token" = $source_token }

# 2. Target Configuration
Write-Host "`n[2/3] Target Configuration (Where to send to)" -ForegroundColor Yellow
$add_more = "y"
while ($add_more -eq "y") {
    $target_platform = Get-PlatformSelection "Select a TARGET platform:"

    $target_example = $examples[$target_platform]
    $target_id = Read-Host "Enter Channel ID for Target [$target_platform] (Example: $target_example)"
    $target_mapping[$target_platform] = $target_id

    # Get credentials if not already provided
    if (-not $credentials.ContainsKey($target_platform)) {
        $target_token_name = $token_names[$target_platform]
        $target_token = Read-Host "Enter $target_token_name"
        $credentials[$target_platform] = @{ "token" = $target_token }
    }

    $add_more = (Read-Host "`nDo you want to add another target platform? (y/n)").ToLower()
}

# 3. Global Settings
Write-Host "`n[3/3] Global Settings" -ForegroundColor Yellow
$interval = Read-Host "Enter sync interval in seconds (Default: 60)"
if ([string]::IsNullOrWhiteSpace($interval)) { $interval = 60 }

# 4. Generate config.json
Write-Host "`nGenerating Configuration..." -ForegroundColor Yellow
$config = @{
    "source" = $source
    "source_channel_id" = $source_id
    "interval" = [int]$interval
    "targets" = $target_mapping
    "credentials" = $credentials
}

$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "config.json" -Encoding utf8

# 5. Finalize
Write-Host "`nSetup Complete!" -ForegroundColor Green
Write-Host "The 'config.json' file has been created successfully." -ForegroundColor Green

$run_now = (Read-Host "`nDo you want to run the system now via Docker? (y/n)").ToLower()
if ($run_now -eq "y") {
    Write-Host "`nLaunching Docker Compose..." -ForegroundColor Cyan
    docker-compose up -d --build
    Write-Host "`nSystem is running in background!" -ForegroundColor Green
    Write-Host "Use 'docker-compose logs -f app' to see live logs."
} else {
    Write-Host "`nYou can start the system later by running: docker-compose up -d" -ForegroundColor White
}

Write-Host "`nPress any key to exit..."
$null = [Console]::ReadKey()
