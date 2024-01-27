# Copyright (C) 2018-2023 Mark McIntyre 

# fireball analyser

# NB NB NB
# this script expects the data to already be available 
$loc = Get-Location
if ($args.count -lt 1) {
    write-output "usage: fireballAnalyser.ps1 yyyymmdd"
    exit 1
}

if ($args.count -eq 2) { $mcrun = [int]$args[1] } else { $mcrun = 20 }

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$fbfldr=$ini['localdata']['fbfolder']

# set up paths
$targpth = $fbfldr + '\' + $args[0]
set-location $targpth

conda activate $ini['wmpl']['wmpl_env']
# set PROJ_DIR
$pdd=(python -c "import pyproj ; print(pyproj.datadir.get_data_dir())")
$env:proj_dir="${pdd}"

$wmplloc=$ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc"

#Write-Output $env:pythonpath

#$solver = read-host -prompt "ECSV or RMS solver? (E/R)"
$solver = 'E'
if ($solver -eq 'E') {
    python -m wmpl.Formats.ECSV . -l -x -r $mcrun -w -t 5
}
else {
    python -m wmpl.Trajectory.CorrelateRMS . -l 
}
$pickfile=(Get-ChildItem *.pickle -r  -exclude *_mc_*).fullname 
python -m wmpl.Utils.DynamicMassFit $pickfile -4 -1 --ga 0.65 > .\DynamicMassFit.txt
set-location $loc
conda deactivate
