$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillsRoot = Join-Path $Root '.agents\skills'
$Dest = Join-Path $SkillsRoot 'project-harness-codex'
New-Item -ItemType Directory -Force -Path $SkillsRoot | Out-Null
if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
New-Item -ItemType SymbolicLink -Path $Dest -Target (Join-Path $Root 'skills') | Out-Null
Write-Host "Linked repo-local raw skills for development at .agents\skills\project-harness-codex"
