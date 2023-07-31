# powershell script to grab interesting files from Pi Camera analysis
# and reorganize them into UFO-style yyyy\yyyymm\yyyymmdd folders
# for easier searching
# Copyright (C) 2018-2023 Mark McIntyre

$curloc=get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    $inifname='../TACKLEY_TC.ini'
}
else {
    $inifname = $args[0]
}
$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$maxage=$ini['camera']['maxage']
$localfolder=$ini['camera']['localfolder']

$srcpath=$localfolder+'\'
$age=[int]$maxage

$arcpath=$srcpath + '\ConfirmedFiles\'
#$numfiles= (dir $arcpath).count
if (-not (test-path $arcpath) ) #-or $numfiles -eq 0)
{
    $arcpath=$srcpath + '\ArchivedFiles\'
}
$mindt = (get-date).AddDays(-$age)
$dlist = (get-childitem -directory $arcpath | where-object {$_.creationtime -gt $mindt }).Name
foreach ($dname in $dlist)
{
    $msg = 'processing '+$dname
    Write-Output $msg
    $yr=$dname.substring(7,4)
    $mt=$dname.substring(11,2)
    $dy=$dname.substring(13,2)

    # powershell can recursively create a folder
    $pth= $srcpath+$yr+'\'+$yr+$mt+'\'+$yr+$mt+$dy
    $exists = test-path $pth
    if ($exists -ne $true) { mkdir $pth | Out-Null}

    write-output 'copying radiant data'
    $src=$arcpath+$dname +'\*radiants.*'
    copy-item $src $pth
    $src=$arcpath+$dname +'\*assocs.*'
    copy-item $src $pth
    write-output 'copying meteors data'
    $src=$arcpath+$dname +'\*meteors.*'
    copy-item $src $pth
    write-output 'copying thumbs'
    $src=$arcpath+$dname +'\*thumbs.jpg'
    copy-item $src $pth
    write-output 'copying FTPdetect file and platepar'
    $src=$arcpath+$dname +'\FTP*.txt'
    copy-item $src $pth
    $src=$arcpath+$dname +'\platepar*'
    copy-item $src $pth
    $precs=$pth +'\FTP*pre-confirmation.txt'
    remove-item $precs
    write-output 'copying UFO file'
    $src=$arcpath+$dname +'\*.csv'
    copy-item $src $pth
    write-output 'copying JPGs, gifs and MP4s'
    $src=$arcpath+$dname +'\FF_*.jpg'
    copy-item $src $pth
    $src=$arcpath+$dname +'\FF_*.gif'
    copy-item $src $pth
    $src=$arcpath+$dname +'\*.mp4'
    copy-item $src $pth

    # if an all-night timelapse exists on the Pi, copy that too
    $remotepath='\\'+$hostname+'\RMS_data\ArchivedFiles\'
    $src = $remotepath+$dname+'\UK*.mp4'
    $exists = test-path $src
    $dest = $pth+'\UK*.mp4'
    $exists2 = test-path $dest
    if($exists -ne 0 -and $exists2 -eq 0){
        write-output 'copying allnight timelapse'
        copy-item $src $pth
    }
}
set-location $curloc