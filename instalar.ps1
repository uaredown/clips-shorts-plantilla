# Instala todo lo necesario (Windows). Uso: powershell -ExecutionPolicy Bypass -File instalar.ps1
$ErrorActionPreference = "Continue"
Write-Host "1/4 Librerias de Python..."
python -m pip install --upgrade -r requirements.txt

Write-Host "2/4 ffmpeg (winget)..."
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements }

Write-Host "3/4 TwitchDownloaderCLI (chat de VODs)..."
$bin = Join-Path $PSScriptRoot "stages\01-fuentes-clips\bin"
New-Item -ItemType Directory -Force $bin | Out-Null
if (-not (Test-Path (Join-Path $bin "TwitchDownloaderCLI.exe"))) {
    $rel = Invoke-RestMethod "https://api.github.com/repos/lay295/TwitchDownloader/releases/latest"
    $asset = $rel.assets | Where-Object { $_.name -match "CLI.*Windows-x64\.zip$" } | Select-Object -First 1
    $zip = Join-Path $env:TEMP $asset.name
    Invoke-WebRequest $asset.browser_download_url -OutFile $zip
    Expand-Archive $zip -DestinationPath $bin -Force
}

Write-Host "4/4 Comprobacion..."
python -c "import faster_whisper, googleapiclient, PIL; print('python ok')"
ffmpeg -version | Select-Object -First 1
yt-dlp --version
python -m streamlink --version
Write-Host "Listo. Siguiente paso: README.md -> 'Crear el canal' y 'Conectar la API'."
