$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Dest = Join-Path $HOME '.agents\skills\project-harness-codex'
New-Item -ItemType Directory -Force -Path (Join-Path $HOME '.agents\skills') | Out-Null
if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
New-Item -ItemType SymbolicLink -Path $Dest -Target (Join-Path $Root 'skills') | Out-Null
Write-Host "Linked raw skills to $Dest"
Write-Host "This mode is developer-only. Plugin installation remains the recommended distribution path."
