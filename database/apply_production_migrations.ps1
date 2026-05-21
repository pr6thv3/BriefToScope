param(
    [string]$DatabaseUrl = $env:DATABASE_URL
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    $DatabaseUrl = $env:SUPABASE_DB_URL
}
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    $DatabaseUrl = $env:POSTGRES_URL
}
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw "Set DATABASE_URL, SUPABASE_DB_URL, or POSTGRES_URL before running this migration script."
}

$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
    throw "psql is required. Install PostgreSQL client tools before running this migration script."
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$orderedMigrations = @(
    "production_foundation.sql",
    "production_rls_policies.sql"
)

foreach ($migration in $orderedMigrations) {
    $path = Join-Path $root $migration
    if (-not (Test-Path $path)) {
        throw "Migration file not found: $path"
    }
    Write-Host "Applying $migration"
    & psql $DatabaseUrl -v ON_ERROR_STOP=1 -f $path
}

Write-Host "Production migrations applied in order."
