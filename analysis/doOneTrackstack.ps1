# Copyright (C) Mark McIntyre
# do a trackstack for one camera for one night
# relies on configuration stored in analysis.ini

$loc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "usage: doOneTrackstack.ps1 camid {yyyymmdd}"
    write-output "eg doOneTrackstack.ps1 UK1234 20231105"
    write-output "if the date is omitted, then the current year+month are used"
    exit 1
}
$camid = $args[0].toupper()
if ($args.count -eq 2){
    $ymd = ([string]$args[1]).substring(0,8)
}else {
    $ymd = (get-date -uformat '%Y%m%d')
}

$ini=get-inicontent "analysis.ini"
$hostname=$ini['stations'][$camid]
$localfolder=$ini['localdata']['localfolder']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

$tmpfldr=New-TemporaryFolder # from helperfunctions.ps1

$loc=get-location
#set-location $tmpfldr
scp ${hostname}:RMS_data/ArchivedFiles/${camid}_${ymd}*/FTPdetectinfo_*.txt $tmpfldr

$ftps=(get-childitem $tmpfldr\FTPdetectinfo_${camid}_${ymd}* -exclude *backup*,*unfil*,*cal*).fullname

if ($ftps)
{
    Write-Output "collecting data"
    scp ${hostname}:RMS_data/ArchivedFiles/${camid}_${ymd}*/.config $tmpfldr
    scp ${hostname}:RMS_data/ArchivedFiles/${camid}_${ymd}*/mask.bmp $tmpfldr
    scp ${hostname}:RMS_data/ArchivedFiles/${camid}_${ymd}*/flat.bmp $tmpfldr
    scp ${hostname}:RMS_data/ArchivedFiles/${camid}_${ymd}*/platepars_all_recalibrated.json $tmpfldr
    $fffiles = (Get-Content $ftps | select-string "FF_")
    foreach ($ff in $fffiles) {
        scp ${hostname}:RMS_data/ArchivedFiles/${camid}_${ymd}*/$ff $tmpfldr
    }
    Write-Output "creating image"
    conda activate $rms_env
    set-location $rms_loc
    python -m Utils.TrackStack $tmpfldr -c $tmpfldr\.config -x
    set-location $loc

    $ts=(Get-ChildItem $tmpfldr\*track_stack.jpg).fullname
    if ($ts) {
        $li = (get-content $ftps | select-object -first 1)
        $metcount = [int]$li.split(' ')[3]
        Write-Output "Annotating image, cam is $hostname, date is $ymd, metcount is $metcount"
        $ts=$ts.replace('\','/')
        python -c "from meteortools.utils import annotateImage;annotateImage('$ts', '$hostname', $metcount, '$ymd')"
        Write-Output "copying image"
        $newn="${camid}_${ymd}.jpg"
        copy-item $ts $localfolder\trackstacks\$newn
    }
    else {
        Write-Output "stacking failed"
    }
    conda deactivate
    remove-item $tmpfldr -recurse
}
else 
{
    write-output "No FTPdetect file found in ${camid}_${ymd}, cannot continue"
    exit 1
}


