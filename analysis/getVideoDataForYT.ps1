# Copyright (C) 2018-2023 Mark McIntyre 

# powershell script to grab new fireball videos, could be adapted for any user

set-location $psscriptroot

. ./mp4retrConfig.ps1

$keys=((Get-Content $AWSKEYFILE)[1]).split(',')

$Env:AWS_ACCESS_KEY_ID = $keys[2]
$env:AWS_SECRET_ACCESS_KEY = $keys[3]

#	$Env:AWS_ACCESS_KEY_ID = $keys[0]#
	$env:AWS_SECRET_ACCESS_KEY = $keys[1]

set-location $targloc
$mthtoget=read-host -prompt 'Enter month to retrieve eg 202007'
$yr=([string]$mthtoget).substring(0,4)
$mth=([string]$mthtoget).substring(4,2)

if ((test-path $targloc\$yr\$yr$mth) -eq 0 ){
	mkdir $targloc\$yr\$yr$mth
}

aws s3 sync s3://ukmon-shared/videos/$yr/$yr$mth/ $targloc\$yr\$yr$mth --exclude "*" --include "*.mp4"

Write-Output "Done"
explorer $yr\$yr$mth

set-location $psscriptroot

