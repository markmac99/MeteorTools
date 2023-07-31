# Copyright (C) 2018-2023 Mark McIntyre 
#
# manually reduce one camera folder 
#
# args : arg1 date, arg2 stationid

if ($args.count -lt 2) {
    write-output "usage: manualReduction.ps1 yyyymmdd UKxxxxx"
    exit 1
}

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

#$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']
set-location $fbfldr

# read date and camera ID from commandline
$dt = [string]$args[0]
$cam = $args[1]

# locate target path
$targpth = "$fbfldr\$dt\$cam"
write-output "processing $targpth"

# run SkyFit to refine the platepar and reduce the path
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH=$ini['rms']['rms_loc']
push-Location $ini['rms']['rms_loc']
python -m Utils.BatchFFtoImage $targpth jpg
move-item $targpth\*.jpg $fbfldr\$dt -Force
if (test-path "$targpth\*.fits") {
    python -m Utils.FRbinViewer -x -f mp4 $targpth
    move-item $targpth\*.mp4 $fbfldr\$dt -Force
}
python -m Utils.SkyFit2 $targpth -c $targpth\.config

pop-location

