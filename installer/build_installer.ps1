$version = (Select-String -Path "..\src\config.py" -Pattern 'APP_VERSION\s*=\s*["'']([^"'']+)["'']').Matches.Groups[1].Value
$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"

& $iscc ".\GhostNote.iss" "/DAppVersion=$version"