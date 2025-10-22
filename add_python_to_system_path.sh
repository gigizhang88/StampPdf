#!/usr/bin/env bash

# Adds Python and Scripts directories to Windows SYSTEM PATH (Machine scope)
# Usage: run this script in Git Bash as Administrator
# Path to add (edit if your version differs)
PY_DIR='C:\\Users\\gigiz\\AppData\\Local\\Programs\\Python\\Python312'
SCRIPTS_DIR="$PY_DIR\\Scripts"

set -euo pipefail

# Ensure running on Windows (MSYS/Cygwin/Git Bash)
case "${OS:-}" in
  MINGW*|MSYS*|CYGWIN*) : ;; 
  *) echo "This script is intended for Git Bash on Windows." >&2; exit 1;;
esac

# PowerShell command to append to Machine PATH if missing
read -r -d '' PS_CMD <<'PS'
param($py, $scripts)

$regPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
$path = (Get-ItemProperty -Path $regPath -Name Path).Path

$updated = $false
if ($path -notlike "*${py}*") { $path = "$path;${py}"; $updated = $true }
if ($path -notlike "*${scripts}*") { $path = "$path;${scripts}"; $updated = $true }

if ($updated) {
  Set-ItemProperty -Path $regPath -Name Path -Value $path
  # Broadcast environment change
  $signature = '[DllImport("user32.dll", SetLastError=true, CharSet=CharSet.Auto)] public static extern IntPtr SendMessageTimeout(IntPtr hWnd, int Msg, IntPtr wParam, string lParam, int fuFlags, int uTimeout, out IntPtr lpdwResult);'
  $type = Add-Type -MemberDefinition $signature -Name 'Win32SendMessageTimeout' -Namespace Win32 -PassThru
  $HWND_BROADCAST = [IntPtr]0xffff
  $WM_SETTINGCHANGE = 0x1A
  $result = [IntPtr]::Zero
  [void]$type::SendMessageTimeout($HWND_BROADCAST, $WM_SETTINGCHANGE, [IntPtr]::Zero, 'Environment', 2, 5000, [ref]$result)
  Write-Output 'UPDATED'
} else {
  Write-Output 'NOCHANGE'
}
PS

# Run elevated PowerShell via Git Bash
PSH="powershell.exe -NoProfile -ExecutionPolicy Bypass"

# Require admin: test write to HKLM
ADMIN_TEST='try { New-Item -Path "HKLM:\\SOFTWARE\\_permtest_" -Force ^| Out-Null; Remove-Item "HKLM:\\SOFTWARE\\_permtest_" -Force; "OK" } catch { "NO" }'
if [[ "$($PSH -Command "$ADMIN_TEST")" != "OK" ]]; then
  echo "This action requires Administrator privileges. Please run Git Bash as Administrator." >&2
  exit 1
fi

# Execute update
RES=$($PSH -Command "$PS_CMD -py '$PY_DIR' -scripts '$SCRIPTS_DIR'")
case "$RES" in
  UPDATED)
    echo "System PATH updated. Open a NEW terminal, then run: python --version && pip --version";;
  NOCHANGE)
    echo "System PATH already contains the Python paths. Open a NEW terminal to use them.";;
  *)
    echo "Unexpected result: $RES" >&2; exit 1;;
esac
