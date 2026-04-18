$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PluginName = 'project-harness-codex'
$PluginDir = Join-Path $HOME '.codex\plugins\project-harness-codex'
$Marketplace = Join-Path $HOME '.agents\plugins\marketplace.json'

New-Item -ItemType Directory -Force -Path (Join-Path $HOME '.codex\plugins') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $HOME '.agents\plugins') | Out-Null
if (Test-Path $PluginDir) { Remove-Item -Recurse -Force $PluginDir }
Copy-Item -Recurse -Force $Root $PluginDir

if (Test-Path $Marketplace) {
  $data = Get-Content $Marketplace -Raw | ConvertFrom-Json
} else {
  $data = [ordered]@{ name = 'personal-local-plugins'; interface = [ordered]@{ displayName = 'Personal Local Plugins' }; plugins = @() }
}
$plugins = @()
foreach ($p in $data.plugins) { if ($p.name -ne $PluginName) { $plugins += $p } }
$plugins += [ordered]@{ name = $PluginName; source = [ordered]@{ source = 'local'; path = './.codex/plugins/project-harness-codex' }; policy = [ordered]@{ installation = 'AVAILABLE'; authentication = 'ON_INSTALL' }; category = 'Productivity' }
$data.plugins = $plugins
$data | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $Marketplace
Write-Host "Installed $PluginName into $PluginDir"
Write-Host "Updated $Marketplace"
Write-Host "Restart Codex, then use /plugins to enable project-harness-codex."
