#
# powershell script to launch the fireball data collector tool
# Copyright (C) 2018-2023 Mark McIntyre
#
push-location $PSScriptRoot

. ..\helperfunctions.ps1
$ini=get-inicontent ..\analysis.ini

$env:PYLIB=$ini['pylib']['pylib']

conda activate ukmon-shared
$wmplloc=$ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc;$env:pylib"

if ($args.count -lt 1) {
    python fireballCollector.py
}else {
    python fireballCollector.py -d $args[0]
}

Pop-Location


