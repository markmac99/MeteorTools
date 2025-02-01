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

aws s3 sync s3://ukmda-shared/matches/RMSCorrelate/trajectories/${yr}/${ym}/${ymd}/${traj}/ ${pth} --exclude "*" --include "*.pickle"
aws s3 sync s3://ukmda-website/reports/${yr}/orbits/${ym}/${ymd}/${traj}/ ${pth} --exclude "*" --include "extra*.html"

$pref = '<a href="'
$mid = '"><video width="20%"><source src="'
$tail = '" width="20%" type="video/mp4"></video></a>'

Write-Output $pth
Get-ChildItem $pth/*.mov
$fils=(get-childitem $pth/*.mov)
foreach ($fil in $fils){
    $fnam = $fil.name
    $ofnam = $fnam.replace('.mov', '.mp4')
    ffmpeg -i $fil -vcodec h264 $pth/$ofnam
}
$fils=(get-childitem $pth/*.mp4)
foreach ($fil in $fils){
    $fnam = $fil.name
    $imgpth = "/img/mp4/${yr}/${ym}/${fnam}"
    Write-Output ${pref}${imgpth}${mid}${imgpth}${tail} >> $pth\extrampgs.html
    aws s3 cp ${fil} s3://ukmda-website${imgpth}
}

$pref = '<a href="'
$mid = '"><img src="'
$tail = '" width="20%"></a>'
$fils=(get-childitem $pth/*.jpg)
foreach ($fil in $fils){
    $fnam = $fil.name
    $imgpth="/img/single/${yr}/${ym}/$fnam"
    Write-Output ${pref}${imgpth}${mid}${imgpth}${tail} >> $pth\extrajpgs.html
    aws s3 cp ${fil} s3://ukmda-website${imgpth}
}

aws s3 sync ${pth} s3://ukmda-website/reports/${yr}/orbits/${ym}/${ymd}/${traj}/ --exclude "*" --include "extra*.html"
$pickle = (get-childitem $pth/*.pickle).fullname
aws s3 cp ${pickle} s3://ukmda-shared/matches/RMSCorrelate/trajectories/${yr}/${ym}/${ymd}/${traj}/ 
Write-Output "uploaded $pickle at $(get-date)"
set-location $loc
