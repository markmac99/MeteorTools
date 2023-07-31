# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to grab supporting files for fireball analysis
#
# args : arg1 date, arg2 stationid
$loc = Get-Location
if ($args.count -lt 2) {
    write-output "usage: getFireballFiles.ps1 yyyymmdd HHMM"
    exit 1
}
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$fbfldr=$ini['fireballs']['localfolder']

conda activate $ini['wmpl']['wmpl_env']
$wmplloc=$ini['wmpl']['wmpl_loc']
$env:PYLIB=$ini['pylib']['pylib']
$env:pythonpath="$wmplloc;$env:pylib"

set-location $fbfldr

# read date and camera ID from commandline
$dt = [string]$args[0]
$hm = [string]$args[1]
#$cam = $args[2]

$fbdate=$dt + '_' + $hm

python -m analysis.gatherDetectionData $fbdate

Set-Location $Loc
Write-Output "press Ctrl-C to stop now, or to gather ftp and platepar data"
pause 
set-location $fbfldr

$ids = get-content ${fbdate}\ids.txt
$uniqueids = (Write-Output $ids | sort-object | get-unique)

foreach ($id in $uniqueids)
{
    python -c "from analysis.gatherDetectionData import getFtpAndPlate; getFtpAndPlate('${id}', '${dt}', '${hm}', '${fbdate}')"
}

# job done
Set-Location $Loc