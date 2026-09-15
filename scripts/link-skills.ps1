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

# Guard: refuse to write a link into a git working tree that does not ignore it.
#
# Measured 2026-09-15. `~/.claude/skills/` held 15 links into this repo. `~/.claude` is
# itself a git working tree and ignored none of them. Git does not model a link: it walks
# through and records what it finds as ordinary tracked files. So both repositories
# tracked the same bytes, and both HEAD trees hashed to the same object. A routine
# `git checkout` in that repository then removed one link and its tracked files left that
# index in a single operation, with nothing anywhere reporting it. A second card showed as
# locally modified there while this repo was clean, so a `git restore` would have written
# a stale HEAD through the link and reverted a merged commit in this repo's working tree.
#
# The existing Dest guard above does not catch this. It only fires when Dest is itself a
# link into this repo, which was not the case.
$destForGit = if (Test-Path $Dest) { (Resolve-Path $Dest).Path } else { (Split-Path $Dest -Parent) }
$gitRoot = ''
if ($destForGit -and (Test-Path $destForGit)) {
  $probe = & git -C $destForGit rev-parse --show-toplevel 2>$null
  if ($LASTEXITCODE -eq 0 -and $probe) { $gitRoot = ($probe | Select-Object -First 1).Trim() }
}

if ($gitRoot) {
  $unignored = @()
  foreach ($src in $skillDirs) {
    $candidate = Join-Path $Dest $src.Name
    & git -C $gitRoot check-ignore -q -- $candidate 2>$null
    if ($LASTEXITCODE -ne 0) { $unignored += $candidate }
  }
  if ($unignored.Count -gt 0) {
    Write-Host ''
    Write-Error (
      "REFUSED: the destination lies inside the git working tree at $gitRoot, " +
      "and $($unignored.Count) of the $($skillDirs.Count) link path(s) are not ignored there. " +
      "First: $($unignored[0]). Git records a link as ordinary files, so that tree would " +
      "track this repo's bytes and a routine checkout in either repository could delete " +
      "them from the other's index. Add these paths to that repository's .gitignore, or " +
      "install the collection instead with `claude plugin marketplace add MrBinnacle/skills`."
    )
    exit 1
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
