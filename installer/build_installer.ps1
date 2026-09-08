$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$version = (Select-String -Path "$scriptDir\..\src\config.py" -Pattern 'APP_VERSION\s*=\s*["'']([^"'']+)["'']').Matches.Groups[1].Value
$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"

& $iscc "$scriptDir\GhostNote.iss" "/DAppVersion=$version"