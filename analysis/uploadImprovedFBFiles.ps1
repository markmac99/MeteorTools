# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to upload improved fit details of fireballs
#
# args : arg1 date, arg2 stationid
$loc = Get-Location
if ($args.count -lt 2) {
    write-output "usage: uploadImprovedFBFiles.ps1 yyyymmdd UKxxxxx"
    exit 1
}
set-location $PSScriptRoot
    
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']

$awsprofile=$ini['aws']['awsprofile']

$dt = [string]$args[0]
$cam = $args[1]
$tf = $cam + '_' + $dt + '_180000'
$targpth = "$fbfldr\$dt\$cam\$tf"

$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]
$yr=$dt.substring(0,4)
$ym=$dt.substring(0,6)
$ymd=$dt

set-location $fbfldr

if ((test-path $targpth\platepars_all_recalibrated.json) -eq 0)
{
    & $PSScriptRoot\makePPallFromPP.ps1 $args[0] $args[1]
}

aws s3 cp $targpth/platepar_cmn2010.cal s3://ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/ --profile $awsprofile
aws s3 cp $targpth/platepars_all_recalibrated.json s3://ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/ --profile $awsprofile
aws s3 cp $targpth/*.ecsv s3://ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/  --profile $awsprofile
# must upload FTP file last
aws s3 cp $targpth/FTPdetect*manual.txt s3://ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/  --profile $awsprofile
Set-Location $Loc