param ($cams, $dates, $shwrs="ALL", $outdir="c:/temp", $scalefactor=3, $constellations=1)

# Copyright (C) 2018-2023 Mark McIntyre 

# multi night multi camera trackstack

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$PYLIB=$ini['pylib']['pylib']
$RMSLOC=$ini['rms']['rms_loc']
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH="$PYLIB;$RMSLOC"
Pop-Location

$conflag=""
if ($constellations -eq 1){
    $conflag="--constellations"
}

push-Location $ini['rms']['rms_loc']
Write-Output "$cams $dates $shwrs $outdir $scalefactor $conflag"
python -m usertools.multiTrackStack $cams $dates -s $shwrs -o $outdir -f $scalefactor $conflag
pop-location
