$ProjectRoot = Split-Path -Parent $PSScriptRoot
$AddEntry = Join-Path $ProjectRoot "src\add_entry.py"
$IconPath = Join-Path $ProjectRoot "assets\icons\GhostNote.ico"

$MenuName = "Add GhostNote"
$RegistryPath = "HKCU:\Software\Classes\Directory\Background\shell\GhostNote"
$CommandPath = Join-Path $RegistryPath "command"

New-Item -Path $RegistryPath -Force | Out-Null
Set-ItemProperty -Path $RegistryPath -Name "MUIVerb" -Value $MenuName
Set-ItemProperty -Path $RegistryPath -Name "Icon" -Value $IconPath

New-Item -Path $CommandPath -Force | Out-Null

$Command = "pyw.exe `"$AddEntry`""

Set-ItemProperty -Path $CommandPath -Name "(default)" -Value $Command

Write-Output "GhostNote context menu installed."
Write-Output "Command: $Command"
Write-Output "AddEntry exists: $(Test-Path $AddEntry)"