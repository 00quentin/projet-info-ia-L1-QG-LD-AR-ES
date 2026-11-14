# scripts/changer_cle_openai.ps1
# ==============================
# Remplace la cle OpenAI dans le(s) fichier(s) .env sans l'afficher nulle part :
# saisie masquee, rien dans l'historique ni dans la conversation avec Claude.
# Usage : clic droit > Executer avec PowerShell, ou : & .\scripts\changer_cle_openai.ps1

$ErrorActionPreference = "Stop"
$racine = Split-Path -Parent $PSScriptRoot

# .env de ce dossier + celui du depot principal (si on est dans un worktree)
$cibles = @(Join-Path $racine ".env")
try {
    $commun = git -C $racine rev-parse --path-format=absolute --git-common-dir 2>$null
    if ($commun) {
        $principal = Join-Path (Split-Path -Parent $commun) ".env"
        if ($cibles -notcontains $principal) { $cibles += $principal }
    }
} catch {}

$secret = Read-Host "Colle ta nouvelle cle OpenAI (rien ne s'affiche), puis Entree" -AsSecureString
$cle = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret))
if (-not $cle.StartsWith("sk-")) { Write-Host "Ca ne ressemble pas a une cle OpenAI (sk-...). Rien n'est modifie."; exit 1 }

foreach ($f in $cibles) {
    $lignes = @()
    if (Test-Path $f) { $lignes = @(Get-Content $f | Where-Object { $_ -notmatch '^OPENAI_API_KEY=' }) }
    $lignes += "OPENAI_API_KEY=$cle"
    [IO.File]::WriteAllLines($f, $lignes)
    Write-Host "Cle enregistree dans $f"
}
$cle = $null
Write-Host "C'est fait. Tu peux fermer cet onglet."
