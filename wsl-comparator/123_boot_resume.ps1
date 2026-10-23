# Extended replay: started by the "siegel-replay-resume" logon task (2026-10-23). Keeps WSL up and resumes the run.
# Remove the task when the replay is done: Unregister-ScheduledTask -TaskName siegel-replay-resume -Confirm:$false
Start-Process -WindowStyle Hidden -FilePath wsl.exe -ArgumentList '-d','Ubuntu-24.04','-u','root','--','sleep','259200'
Start-Sleep 5
wsl.exe -d Ubuntu-24.04 -u root -- bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/123_boot_resume.sh
