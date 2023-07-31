#
# powershell script to launch the fireball data collector tool
# Copyright (C) 2018-2023 Mark McIntyre
#
push-location $PSScriptRoot

. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$fbfldr=$ini['fireballs']['localfolder']
$env:PYLIB=$ini['pylib']['pylib']

conda activate ukmon-shared
$wmplloc=$ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc;$env:pylib"

set-location python
if ($args.count -lt 1) {
    python fireballCollector.py
}else {
    python fireballCollector.py -d $args[0]
}

$pth = $fbfldr.replace('/','\')
explorer "$pth"

Pop-Location
#pause


