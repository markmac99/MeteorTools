# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to upload improved FTP file sent over by camera owner
#
# args : arg1 full path to ftpdetect file
$loc = Get-Location
if ($args.count -lt 1) {
    write-output "usage: uploadImprovedFTP.ps1 full\path\to-ftpfile"
    exit 1
}
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini
Set-Location $Loc

$awsprofile=$ini['aws']['awsprofile']

$stationdetails=$ini['fireballs']['stationdets'] 
$fullftpfile = [string]$args[0]
$targpth = (split-path $fullftpfile).replace('\','/')
$ftpname = (split-path $fullftpfile -leaf)
$cam = $ftpname.substring(14,6)
$dt = $ftpname.substring(21,8)

$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]
$yr=$dt.substring(0,4)
$ym=$dt.substring(0,6)
$ymd=$dt

Write-Output "Target location is $stn/$cam/$yr/$ym/$ymd/"
if ((test-path $targpth/processed) -eq 0) { mkdir $targpth/processed}

aws s3 cp $targpth/$ftpname s3://ukmda-shared/archive/$stn/$cam/$yr/$ym/$ymd/ --profile $awsprofile
Move-Item $targpth/$ftpname $targpth/processed/ -Force

if ((test-path $targpth/platepars_all_recalibrated.json) -eq 1){
    $x=(select-string -pattern UK005P -path .\platepars_all_recalibrated.json)
    if ($x.length -gt 0) 
    {
        aws s3 cp $targpth/platepars_all_recalibrated.json s3://ukmda-shared/archive/$stn/$cam/$yr/$ym/$ymd/ --profile $awsprofile
        Move-Item $targpth/platepars_all_recalibrated.json $targpth/processed/platepars_all_recalibrated.json.$cam.$dt
    }
}

