<#
.SYNOPSIS
  Link this repo's published skills into a local Agent Skills directory as symlinks,
  so `git pull` keeps the installed copy current and drift is structurally impossible.

.DESCRIPTION
  Windows PowerShell symlink installer. For every skill in this repo (each directory
  containing a SKILL.md), it replaces the local install directory with a symlink pointing
  back into the repo.

  IMPORTANT — scope. This links ONLY the skills that live in THIS repo. The repo is the
  curated, de-personalized *published* subset; any private, unpublished skills in the
  local directory are never touched, never symlinked, and never enumerated here. (This is
  the one safe difference from a whole-tree "link everything" script: a superset local
  library must not be collapsed into the published subset.)

  Symlinks on Windows require either Developer Mode (Settings > For developers) or an
  elevated (Administrator) shell. If neither is available, New-Item -ItemType SymbolicLink
  fails; the script reports that and makes no changes.

.PARAMETER Dest
  The local skills directory to link into. Defaults to ~/.claude/skills (Claude Code).
  Pass another path (e.g. ~/.agents/skills) to link into a second harness.

.PARAMETER Apply
  Actually make changes. WITHOUT this flag the script runs DRY (prints the plan only).
  Because this replaces directories in your live skills folder, dry-run is the default.

.PARAMETER BackupRoot
  Where replaced real directories are moved before being symlinked over. Defaults to a
  timestamped folder under the Dest's parent. A replaced dir is never deleted outright.

.EXAMPLE
  pwsh ./scripts/link-skills.ps1              # dry run — show what would happen
  pwsh ./scripts/link-skills.ps1 -Apply       # do it (needs Dev Mode or elevation)
#>

[CmdletBinding()]
param(
  [string]$Dest = (Join-Path $HOME '.claude/skills'),
  [switch]$Apply,
  [string]$BackupRoot
)

$ErrorActionPreference = 'Stop'

# Repo root = parent of this script's directory.
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SkillsRoot = Join-Path $RepoRoot 'skills'

if (-not (Test-Path $SkillsRoot)) {
  Write-Error "No skills/ directory found at $SkillsRoot — is this the repo root?"
  exit 1
}

# Enumerate the repo's published skills: one entry per directory holding a SKILL.md.
$skillDirs = Get-ChildItem -Path $SkillsRoot -Recurse -Filter 'SKILL.md' -File |
  Where-Object { $_.FullName -notmatch '[\\/]node_modules[\\/]' -and $_.FullName -notmatch '[\\/]deprecated[\\/]' } |
  ForEach-Object { $_.Directory }

if (-not $skillDirs) {
  Write-Error "Found no SKILL.md files under $SkillsRoot."
  exit 1
}

Write-Host "Repo:  $RepoRoot"
Write-Host "Dest:  $Dest"
Write-Host ("Mode:  {0}" -f ($(if ($Apply) { 'APPLY (will modify the destination)' } else { 'DRY RUN (no changes) — pass -Apply to execute' })))
Write-Host ("Skills: {0} published" -f $skillDirs.Count)
Write-Host ''

# Guard: if Dest itself is a symlink resolving into this repo, per-skill links would be
# written back into the repo's own tree. Bail rather than pollute the working copy.
if (Test-Path $Dest) {
  $destItem = Get-Item $Dest -Force
  if ($destItem.LinkType -eq 'SymbolicLink') {
    $resolved = (Resolve-Path $Dest).Path
    if ($resolved -eq $RepoRoot -or $resolved.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar)) {
      Write-Error "Dest $Dest is a symlink into this repo ($resolved). Remove it and re-run."
      exit 1
    }
  }
}

if (-not $Apply) {
  # Nothing is created in dry run, including the backup root.
} else {
  if (-not $BackupRoot) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $BackupRoot = Join-Path (Split-Path $Dest -Parent) ("skills-backup-$stamp")
  }
  New-Item -ItemType Directory -Force -Path $Dest        | Out-Null
}

$linked = 0; $skipped = 0; $backedUp = 0; $failed = 0

foreach ($src in $skillDirs) {
  $name   = $src.Name
  $target = Join-Path $Dest $name
  $srcPath = $src.FullName

  $existing = if (Test-Path $target) { Get-Item $target -Force } else { $null }

  # Already correctly linked? Skip (idempotent).
  if ($existing -and $existing.LinkType -eq 'SymbolicLink') {
    $curTarget = try { (Resolve-Path $target).Path } catch { '' }
    if ($curTarget -eq $srcPath) {
      Write-Host "  skip   $name (already linked)"
      $skipped++
      continue
    }
  }

  if (-not $Apply) {
    if ($null -eq $existing) {
      Write-Host "  link   $name  (new symlink -> $srcPath)"
    } elseif ($existing.LinkType -eq 'SymbolicLink') {
      Write-Host "  relink $name  (repoint symlink -> $srcPath)"
    } else {
      Write-Host "  BACKUP+link $name  (real dir -> backup, then symlink -> $srcPath)"
    }
    $linked++
    continue
  }

  try {
    if ($existing) {
      if ($existing.LinkType -eq 'SymbolicLink') {
        # Wrong-target symlink: drop it (removing a link never touches the repo contents).
        Remove-Item $target -Force
      } else {
        # Real directory: back it up before replacing. Never delete outright.
        New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
        Move-Item -Path $target -Destination (Join-Path $BackupRoot $name)
        Write-Host "  backup $name -> $(Join-Path $BackupRoot $name)"
        $backedUp++
      }
    }
    New-Item -ItemType SymbolicLink -Path $target -Target $srcPath | Out-Null
    Write-Host "  linked $name -> $srcPath"
    $linked++
  } catch {
    Write-Warning "  FAILED $name : $($_.Exception.Message)"
    Write-Warning "  (Windows symlinks need Developer Mode or an elevated shell.)"
    $failed++
  }
}

Write-Host ''
Write-Host ("Done. linked/would-link=$linked  skipped=$skipped  backed-up=$backedUp  failed=$failed")
if ($Apply -and $backedUp -gt 0) { Write-Host "Backups: $BackupRoot" }
if (-not $Apply) { Write-Host "This was a DRY RUN. Re-run with -Apply to make changes." }
if ($failed -gt 0) { exit 1 }
