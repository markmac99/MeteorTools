# powershell test script
# source the configuration and update the pythonpath
. f:\videos\MeteorCam\ukmondata\config.ps1
$env:PYTHONPATH="$env:WMPL_LOC;$env:RMS_LOC;.;.."
Push-Location "$PSScriptRoot/.."

# unset this so that we use the internal shared datafiles
$env:datadir=""
if ($args.count -eq 0 ) {
    pytest -v ./tests --cov=. --cov-report term-missing:skip-covered --cov-report html
}else{
    $targ=$args[0]
    pytest -v ./tests/test_$targ.py --cov=$targ --cov-report term-missing:skip-covered 
}
Pop-Location