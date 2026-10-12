# Move the Ubuntu-24.04 WSL distro from C: to D: (Seagate FreeAgent USB drive).
# Plan and rollback notes: docs/wsl-move-plan.md. Run in an ELEVATED Windows PowerShell terminal, one section at a time.
# Nothing here runs automatically: each step asks for confirmation. Close VS Code/terminals that use WSL first.

$ErrorActionPreference = 'Stop'
$env:WSL_UTF8 = '1'                         # make wsl.exe print UTF-8 so its output can be searched
$Distro    = 'Ubuntu-24.04'
$Date      = Get-Date -Format 'yyyy-MM-dd'
$BackupDir = 'C:\wsl-backup'                # recommended: C: (59 GB free). Use 'D:\wsl-backup' only if D: margin allows.
$Target    = "D:\WSL\$Distro"
$OldImage  = 'C:\Users\Work\AppData\Local\wsl\{beda3264-2b75-4d2c-b8d2-931eeb830b69}\ext4.vhdx'
$Tar       = Join-Path $BackupDir "$Distro-$Date.tar"

function Confirm-Step($msg) { $a = Read-Host "$msg  Type YES to continue"; if ($a -ne 'YES') { throw "Stopped by user before: $msg" } }

# --- a. WSL version and --move support --------------------------------------------------------------------
wsl --version
$help = (wsl --help) -join "`n"
$HasMove = $help -match '--move'
"--manage --move available: $HasMove"     # success: True on WSL 2.4.11. If False: update with 'wsl --update', or use fallback f.

# --- b. shut down WSL ---------------------------------------------------------------------------------------
Confirm-Step 'b. wsl --shutdown (stops ALL WSL distros, including docker-desktop)'
wsl --shutdown
Start-Sleep -Seconds 10
wsl -l -v                                   # success: Ubuntu-24.04 shows Stopped

# --- c. export a backup tar ---------------------------------------------------------------------------------
Confirm-Step "c. wsl --export $Distro $Tar  (about 41 GB; takes a while)"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
wsl --export $Distro $Tar

# --- d. verify the tar ----------------------------------------------------------------------------------------
$t = Get-Item $Tar
"{0}  {1:N1} GB" -f $t.FullName, ($t.Length / 1GB)   # success: roughly 35-45 GB (WSL uses ~41 GB inside the image)
if ($t.Length -lt 20GB) { throw 'Backup tar is implausibly small; do not continue.' }

# --- e. move the distro ------------------------------------------------------------------------------------
if ($HasMove) {
  Confirm-Step "e. wsl --manage $Distro --move $Target"
  New-Item -ItemType Directory -Force -Path (Split-Path $Target) | Out-Null
  wsl --manage $Distro --move $Target
  Get-ChildItem $Target | Format-Table Name, @{n='GB'; e={[math]::Round($_.Length/1GB,1)}}   # success: ext4.vhdx ~43 GB on D:
  "Old image still present: $(Test-Path $OldImage)"                                          # success: False (the move removes it)
} else {
  # --- f. FALLBACK, only if --move is unavailable ----------------------------------------------------------
  $NewName = "$Distro-D"
  Confirm-Step "f1. wsl --import $NewName $Target $Tar  (creates a second distro from the backup)"
  wsl --import $NewName $Target $Tar
  # Default user: the current distro's default is root (DefaultUid 0) and /etc/wsl.conf has only [boot] systemd=true,
  # so the imported distro (default root) already matches. No [user] section is needed.
  wsl -d $NewName -u root -- bash -c 'cat /etc/wsl.conf; ps -p 1 -o comm=; id checker'   # success: systemd, checker exists
  "Check the imported distro fully (docs/wsl-move-plan.md, verification checklist) BEFORE the next step."
  Confirm-Step "f2. DESTRUCTIVE AND IRREVERSIBLE: wsl --unregister $Distro deletes the C: distro and its disk image. Only after $NewName is confirmed working"
  wsl --unregister $Distro
  # Then, if you want the original name back: export $NewName, unregister it, import as $Distro (or keep $NewName and tell Claude).
}

# --- g. start the distro and confirm -------------------------------------------------------------------------
wsl -d $Distro -u root -- bash -c 'ps -p 1 -o comm=; df -h / | tail -1; ls /home/checker'   # (use $NewName after fallback)
wsl -l -v
"C: image still present: $(Test-Path $OldImage)   (expected False; if True after a successful move, it can be removed only after the checklist passes)"
"Backup tar kept at $Tar. Delete it only after the post-move checklist passes and you no longer want the backup."
