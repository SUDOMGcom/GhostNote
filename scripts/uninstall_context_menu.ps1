$RegistryPath = "HKCU:\Software\Classes\Directory\Background\shell\GhostNote"

Remove-Item -Path $RegistryPath -Recurse -Force

Write-Output "GhostNote context menu removed."