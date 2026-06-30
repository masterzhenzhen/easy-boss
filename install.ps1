$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "skills\easy-boss"
$target = Join-Path $env:USERPROFILE ".codex\skills\easy-boss"

if (-not (Test-Path -LiteralPath $source)) {
  throw "Skill source not found: $source"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
if (Test-Path -LiteralPath $target) {
  Remove-Item -LiteralPath $target -Recurse -Force
}
Copy-Item -LiteralPath $source -Destination $target -Recurse -Force

Write-Host "Installed Easy Boss to: $target"
Write-Host "Restart Codex or open a new conversation, then use: `$easy-boss"
