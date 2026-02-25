Write-Host "Diagnosing SSH Setup..."
$sshPath = "C:\Windows\System32\OpenSSH\ssh.exe"
if (Test-Path $sshPath) {
    Write-Host "FOUND: SSH executable exists at $sshPath"
    Write-Host "Try running this command explicitly:"
    Write-Host "& '$sshPath' -R 80:localhost:8501 nokey@localhost.run"
}
else {
    Write-Host "MISSING: SSH client not found in standard paths."
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "FOUND: Git is installed. You might find ssh inside Git Bash."
    }
}
