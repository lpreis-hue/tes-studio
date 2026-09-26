param(
    [string]$EnvironmentName = "tes-studio"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $ProjectRoot

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "Conda não encontrado. Instale Miniforge ou Anaconda e abra um novo terminal."
}

$environmentFile = Join-Path $ProjectRoot "environment.yml"
$environmentList = conda env list --json | ConvertFrom-Json
$environmentExists = $environmentList.envs | Where-Object {
    (Split-Path -Leaf $_) -eq $EnvironmentName
}

if ($environmentExists) {
    Write-Host "Atualizando o ambiente $EnvironmentName..."
    conda env update --name $EnvironmentName --file $environmentFile --prune
} else {
    Write-Host "Criando o ambiente $EnvironmentName..."
    conda env create --name $EnvironmentName --file $environmentFile
}

conda run --no-capture-output --name $EnvironmentName python scripts/check_project.py
conda run --no-capture-output --name $EnvironmentName pyinstaller --noconfirm --clean tes.spec

$executable = Join-Path $ProjectRoot "dist\TeS Studio\TeS Studio.exe"
if (-not (Test-Path -LiteralPath $executable)) {
    throw "O build terminou sem produzir o executável esperado: $executable"
}

Write-Host "Build concluído: $executable"
