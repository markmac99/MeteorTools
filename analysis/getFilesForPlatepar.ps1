#
# powershell script to grab supporting files for fireball analysis
#
# args : arg1 date, arg2 stationid
$loc = Get-Location
if ($args.count -lt 2) {
    write-output "usage: getFilesForPlatepar.ps1 UKxxxxx reqdate"
    exit 1
}
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$fbfldr=$ini['localdata']['fbfolder']
$ppfldr=$fbfldr+'/../platepars'

# camera ID from commandline
$cam = $args[0]
if($args.Count -gt 1){
    $dt = [string]$args[1]
}
else {
    $dt=(get-date -uformat '+%Y%m%d')    
}

# create target path
$targpth = "$ppfldr/$cam/$dt"
if ((test-path $targpth) -eq 0) {mkdir $targpth}

set-location $targpth

# copy the required files
python -c "from meteortools.ukmondb import getFBfiles; getFBfiles('${cam}_${dt}_210000', '${targpth}');"

(Get-Content -path $targpth/.config) -replace 'gaia_dr2_mag_11.5.npy','BSC5' > $targpth/.config.new
copy-item $targpth/.config.new $targpth/.config

# job done
Set-Location $Loc