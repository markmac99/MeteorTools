# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to upload an extra video or image of an event, given a trajectory ID 

$loc = get-location
if ($args.count -lt 1) {
    write-output "Usage: addVideoorImg.ps1 trajpath"
    write-output "  First create a folder for the trajectory eg 20241113_192754.345_UK"
    write-output "  Copy any additional mp4, mov or jpgs into it, then run this script"
    exit
}else {
    $pth = $args[0]
}
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini
$fbfolder = $ini['localdata']['fbfolder']
set-location $fbfolder
$traj = (split-path -leaf $pth)

$yr=$traj.Substring(0,4)
$ym=$traj.Substring(0,6)
$ymd=$traj.Substring(0,8)
$pick=$traj.substring(0,15) + '_trajectory.pickle'
$zipf=$traj.substring(0,15) + '.zip'

wget https://archive.ukmeteors.co.uk/reports/${yr}/orbits/${ym}/${ymd}/${traj}/${pick} -O ${pth}\${pick}

if ((test-path $pth\jpgs) -eq $false) { mkdir $pth\jpgs }
if ((test-path $pth\mp4s) -eq $false) { mkdir $pth\mp4s }

move-item $pth\*.jpg $pth\jpgs
move-item $pth\*.mp4 $pth\mp4s

compress-archive -path $pth\* -DestinationPath $pth\$zipf -force

$apikey=(Get-Content ~/.ssh/fbuploadkey.txt)
$headers = @{
    'Content-type' = 'application/zip'
    'Slug' = ${zipf}
    'apikey'= ${apikey}
}
$url = "https://api.ukmeteors.co.uk/fireballfiles?orbitfile=${zipf}"

invoke-webrequest -uri $url -infile $pth\$zipf -Method PUT -Headers $headers

Write-Output "uploaded $zipf at $(get-date)"
set-location $loc
