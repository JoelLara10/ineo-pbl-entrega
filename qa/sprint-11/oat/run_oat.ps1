
# Run from the repository root, no Bash installation required on Windows.

param(
    [Parameter(Mandatory=$true)]
    [ValidateRange(0,86400)]
    [int]$RpoTargetSeconds,

    [ValidateSet('all','health','backup','corrupt')]
    [string]$Case = 'all'
)

$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path

Push-Location $root

try {

    $compose = @(
        'compose',
        '-p', 'ineo-oat-s11',
        '-f', 'compose.test.yml',
        '-f', 'compose.oat-s11.yml'
    )

    $sha = (git rev-parse HEAD).Trim()

    if ($LASTEXITCODE -ne 0) {
        throw 'No se pudo obtener SHA.'
    }

    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $evidence = Join-Path $root "evidence/sprint-11/oat-$stamp"

    New-Item -ItemType Directory -Force $evidence | Out-Null

    "SHA=$sha`nFecha=$(Get-Date -Format o)`nRPO_TARGET_SECONDS=$RpoTargetSeconds`nCase=$Case" |
        Set-Content (Join-Path $evidence 'metadata.txt')

    git status --short |
        Add-Content (Join-Path $evidence 'metadata.txt')

    docker @compose ps |
        Tee-Object -FilePath (Join-Path $evidence 'compose-ps.txt')

    if ($LASTEXITCODE -ne 0) {
        throw 'Docker QA no disponible.'
    }

    # HEALTH CHECK
    if ($Case -in @('all','health')) {

        $results = foreach ($route in @('health','ready')) {

            $http = & curl.exe `
                --silent `
                --show-error `
                --max-time 35 `
                --output NUL `
                --write-out '%{http_code}' `
                "http://localhost:5002/$route"

            $code = $LASTEXITCODE

            [pscustomobject]@{
                endpoint = "/$route"
                http = $http
                curlExit = $code
            }
        }

        $results |
            Format-Table |
            Out-String |
            Tee-Object -FilePath (Join-Path $evidence 'health.txt')

        if (@($results | Where-Object {
            $_.http -ne '200' -or $_.curlExit -ne 0
        }).Count -gt 0) {
            throw 'Health/readiness no aprobaron.'
        }
    }

    # BACKUP AND CORRUPT BACKUP TESTS
    if ($Case -ne 'health') {

        $container = docker @compose ps -q mongo-test

        if ($LASTEXITCODE -ne 0 -or -not $container) {
            throw 'No existe mongo-test activo.'
        }

        $container = $container.Trim()

        Write-Host "Contenedor MongoDB encontrado: $container"

        # Verify QA fixture without double-quote parsing issues.
        $mongoCheck = "if(db.getSiblingDB('ineo_test_s11').pacientes.countDocuments()===0) quit(1); print('Fixture QA disponible');"

        docker @compose exec -T mongo-test mongosh --quiet --eval $mongoCheck

        if ($LASTEXITCODE -ne 0) {
            throw 'No se pudo validar la fixture QA.'
        }

        $remote = "/tmp/oat-$stamp"

        docker @compose exec -T mongo-test mkdir -p $remote

        if ($LASTEXITCODE -ne 0) {
            throw 'No se pudo crear directorio QA.'
        }

        # Copy test files.
        foreach ($file in @(
            'backup_restore.sh',
            'detect_corrupt_backup.sh',
            'fixture_snapshot.js'
        )) {

            docker cp (Join-Path $PSScriptRoot $file) "${container}:$remote/$file"

            if ($LASTEXITCODE -ne 0) {
                throw "No se pudo copiar $file"
            }

            # Normalize CRLF directly without bash -c.
            docker @compose exec -T mongo-test sed -i 's/\r$//' "$remote/$file"

            if ($LASTEXITCODE -ne 0) {
                throw "No se pudo normalizar $file"
            }
        }

        # Execute selected OAT test.
        foreach ($script in @(
            'backup_restore.sh',
            'detect_corrupt_backup.sh'
        )) {

            if (
                ($Case -eq 'backup' -and $script -ne 'backup_restore.sh') -or
                ($Case -eq 'corrupt' -and $script -ne 'detect_corrupt_backup.sh')
            ) {
                continue
            }

            Write-Host "Ejecutando prueba: $script"

            docker @compose exec -T `
                -e "RPO_TARGET_SECONDS=$RpoTargetSeconds" `
                -e "OAT_GIT_SHA=$sha" `
                mongo-test bash "$remote/$script" |
                Tee-Object -FilePath (Join-Path $evidence "$script.txt")

            $testExit = $LASTEXITCODE

            docker cp "${container}:$remote/reports/." $evidence

            if ($LASTEXITCODE -ne 0) {
                throw 'No se pudieron recuperar reportes.'
            }

            if ($testExit -ne 0) {
                throw "Prueba fallida: $script. Revisar $evidence"
            }

            Write-Host "Prueba aprobada: $script" -ForegroundColor Green
        }
    }

    Write-Host "Evidencias: $evidence" -ForegroundColor Green

} finally {

    Pop-Location

}
