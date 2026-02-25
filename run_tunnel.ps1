Write-Host "Launching SSH Tunnel to localhost.run..."
# Run SSH in background job or direct execution capturing output
$p = Start-Process ssh -ArgumentList "-o StrictHostKeyChecking=no -R 80:localhost:8501 nokey@localhost.run" -NoNewWindow -PassThru -RedirectStandardOutput "deploy_log.txt" -RedirectStandardError "deploy_error.txt"
Write-Host "Process Started with ID: $($p.Id)"
Start-Sleep -Seconds 5
Get-Content deploy_log.txt
Get-Content deploy_error.txt
