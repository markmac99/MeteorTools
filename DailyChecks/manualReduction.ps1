# script to run manual meteor reduction for the Pi
# Copyright (C) 2018-2023 Mark McIntyre

if($args.count -lt 2) {
    Write-Output "usage: manuaReduction inifile datestr"
    Write-Output "eg manuaReduction UK0006.ini 20200703"
    exit
}

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$inifname = $args[0]
$ini=get-inicontent $inifname

$datadir=$ini['camera']['localfolder']
$cam=$ini['camera']['camera_name']
$RMSloc=$ini['rms']['rms_loc']
$rmsenv=$ini['rms']['rms_env']

$localdir=$datadir +'\Interesting\'+ $args[1]


$ffpath=$localdir+'\FF*.fits'
$ff=(Get-ChildItem $ffpath).fullname

# run the manual reduction process
set-location $RMSloc 
conda activate $rmsenv
python -m Utils.ManualReduction $ff

# find the new FTPfile and the original
$ftppath=$localdir+'\FTPdetectinfo*manual.txt'
$ftp=(Get-ChildItem $ftppath).fullname

$arcpath=$datadir + '\ConfirmedFiles\'+$cam+'_'+$args[1]+'*'
if (-not (test-path $arcpath) )
{
    $arcpath=$datadir + '\ArchivedFiles\'+$cam+'_'+$args[1]+'*'
}

$oldftppath=$arcpath+'\FTPdetectinfo*.txt'
$oldftp=((Get-ChildItem $oldftppath -exclude *backup*,*uncal*,*pre-con*).fullname)
$fuloldpth=(Get-ChildItem $arcpath).fullname

msg  /w $env:username "opening windows for you to edit the FTPdetect files - don't forget to change the meteor count!"

notepad $ftp
notepad $oldftp | out-null

$jppath=$localdir+'\FF*.jpg'
copy-item $jppath $fuloldpth
copy-item $ff $fuloldpth

python $PSScriptRoot\ufoShowerAssoc.py $oldftp
$platepar=$localdir+'\platepar_cmn2010.cal'
python -m Utils.RMS2UFO $oldftp $platepar

Set-Location $PSScriptRoot
.\reorgByYMD.ps1 $args[0]
.\UploadToUkMon.ps1 $args[0]
