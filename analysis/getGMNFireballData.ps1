# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to grab supporting files from GMN for fireball analysis
#
# args : arg1 date, arg2 stationid

if ($args.count -lt 2) {
    write-output 'usage: getGMNData.ps1 yyyymmdd_HHMMSS.000000 "cam1,cam2,cam3..."'
    exit 1
}
push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$fbfldr=$ini['localdata']['fbfolder']
$IDFILE=$ini['gmn']['idfile']

set-Location $fbfldr

$DT = $args[0]
$CAMS = $args[1]
$STATLIST=[system.string]::join(',',$CAMS)
Write-Output $DT $STATLIST
pause
#$DT = "20220102_031505.000000"
#$STATLIST = "UK000P,UK0052,UK0057"
ssh -i $IDFILE analysis@gmn.uwo.ca "source ~/anaconda3/etc/profile.d/conda.sh && conda activate wmpl && python scripts/extract_fireball.py $DT $STATLIST"
scp -i $IDFILE -pr analysis@gmn.uwo.ca:event_extract/$DT ./$DT
ssh -i $IDFILE analysis@gmn.uwo.ca "rm -Rf event_extract/$DT"

$rms_env=$ini['rms']['rms_env']
conda activate $rms_env
$rms_loc=$ini['rms']['rms_loc']
set-location $rms_loc

# $yr=$dt.substring(0,4)
# $dtpth = $fbfldr + "/" + $yr + "/" + $dt
$dtpth = $fbfldr + "/" + $dt
foreach ($cam in $cams) {
	$frpth=$dtpth + "/" + $cam
	if (test-path $frpth){
		python -m Utils.FRbinViewer -x -f mp4 $frpth -c $frpth/.config
		Move-Item $frpth/*.mp4 $dtpth -Force
		python -m Utils.BatchFFtoImage $frpth jpg
		Move-Item $frpth/*.jpg $dtpth -Force
	}
}

Pop-Location