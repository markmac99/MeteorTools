# Copyright (C) 2018-2023 Mark McIntyre 

if ($args.count -lt 1) {
    write-output "usage: getStationDets.ps1 searchpattern {refresh}"
    exit 1
}


push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

$ini=get-inicontent analysis.ini
$localfolder=$ini['ukmondata']['localfolder']
$shrbucket=$ini['aws']['shrbucket']

$patt = $args[0].toupper()
$refresh = $args[1]
if ("$refresh" -ne "" )
{
    aws s3 cp $shrbucket/admin/stationdetails.csv $localfolder/admin
    #aws s3 cp $shrbucket/admin/cameraLocs.json $localfolder/admin
    aws s3 cp $shrbucket/consolidated/camera-details.csv $localfolder/consolidated
}

Set-Location $localfolder
$camerafile = "consolidated/camera-details.csv"
$locationjson = "admin/cameraLocs.json"
$stationdets = "admin/stationdetails.csv"

bash -c "grep $patt $stationdets"
bash -c "grep $patt $camerafile"

pop-location
