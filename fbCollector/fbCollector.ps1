#
# powershell script to launch the fireball data collector tool
# Copyright (C) 2018-2023 Mark McIntyre
#
push-location $PSScriptRoot

. .\helperfunctions.ps1
$ini=get-inicontent .\config.ini


conda activate ukmon-shared
$wmplloc=$ini['fireballs']['wmpl_loc']
$env:pythonpath="$wmplloc"

if ($args.count -lt 1) {
    python fireballCollector.py
}else {
    python fireballCollector.py -d $args[0]
}

Pop-Location


