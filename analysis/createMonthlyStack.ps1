# Copyright (C)Mark McIntyre
#
# This script creates a monthly stack for a given camera, copying the data from the Pi.
# After obtaining the images, the script pauses to allow you to clean the data in another window by 
# deleting the bad JPG versions. Once you press enter to resume, the script will delete the corresponding
# fits files and stack whats left. 
# After processing, the cleaned data are pushed back to ~/RMS_data/tmpstack on the Pi so that subsequent
# runs can work from a pre-cleaned dataset. 
# optionally, the scipt then uploads the stack to a specified location on a server and/or AWS s3. 
# To disable this, set webserver  and/or cambucket a blank string in the ini file
#
$loc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "usage: createMonthlyStack.ps1 camid {yyyymm}"
    write-output "eg createMonthlyStack.ps1 UK1234 202311"
    write-output "if the date is omitted, then the current year+month are used"
    exit 1
}
$camid = $args[0].toupper()
if ($args.count -eq 2){
    $ym = ([string]$args[1]).substring(0,6)
}else {
    $ym = (get-date -uformat '%Y%m')
}

$ini=get-inicontent "analysis.ini"
$hostname=$ini['stations'][$camid]
$localfolder=$ini['localdata']['localfolder'] + '/' + $camid
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']
$webserver=$ini['upload']['webserver']
$awsprofile=$ini['upload']['awsprofile']
$awsbuck=$ini['upload']['cambucket']

$srcpath=$localfolder + '\ArchivedFiles'
$destpath=$localfolder+'\..\mthlystacks\'+$camid

Write-Output "processing $camid for $ym"

if ((test-path $destpath) -eq 0) { mkdir $destpath}

Write-output "removing existing files from folder $destpath"
Get-ChildItem $destpath\*.fits -exclude "FF_${camid}_${ym}*" | Remove-Item
remove-item $destpath\*.jpg

Write-output "copying new data"
# for the current month we can fetch from the camera
$currmth = (get-date -uformat '%Y%m')
if ($ym -eq $currmth -or ((get-date).day -lt 3)) {
    $destpath_l ="/mnt/" +$destpath.replace(':','').tolower().replace('\','/')
    $upstreampath_l = "${hostname}:RMS_data/tmpstack/*_${ym}*.fits"
    bash -c "rsync -avz --delete $upstreampath_l $destpath_l"
    $upstreampath_l = "${hostname}:RMS_data/tmpstack/*.bmp"
    bash -c "rsync -avz --delete $upstreampath_l $destpath_l"
}
else {
    $dlist = (Get-ChildItem  -directory "$srcpath\*_$ym*" ).name
    foreach ($path in $dlist) {
        robocopy $srcpath\$path $destpath FF*.fits mask.bmp flat.bmp /NFL /NDL /NJH /NJS /nc /xc /ns /np /v
    }
}

Write-output "creating jpgs"
conda activate $RMS_ENV
set-location $RMS_LOC
python -m Utils.BatchFFtoImage $destpath jpg

$fitsfiles=(Get-ChildItem  $destpath\*.fits).fullname
& explorer $destpath.replace('/','\')
write-output "now examine the JPGs and delete any bad ones"
pause

Write-output "removing bad images and stacking"
foreach ($fits in $fitsfiles) {
    $jpg = $fits.replace('.fits','.jpg')
    if ((test-path $jpg) -eq 0) { remove-item "$fits" }
}
Remove-Item $destpath\*stack*.jpg
python -m Utils.StackFFs $destpath -x -s -b jpg -f $destpath/flat.bmp -m $destpath/mask.bmp

Write-output "annotating and optionally uploading the stack"
$stackfile = (Get-ChildItem  $destpath\*stack*.jpg ).name
if ((test-path $destpath\$stackfile) -eq 1)
{
    $metcount = $stackfile.split('_')[2]
    $imgfile=("$destpath\$stackfile").replace('\','/')
    python -c "from meteortools.utils import annotateImage; annotateImage('$imgfile', '$hostname', $metcount, '$ym')"
    $newname=$hostname.toupper() + '_' + $ym + '.jpg'
    Move-Item $destpath\*.jpg $destpath\..\$newname -force

    set-location "$destpath\.."
    if ($webserver) {
        if ($ym -eq $currmth ) {
            $latf=$hostname.toupper() + '_latest.jpg'
            $webtarg=$webserver+":data/meteors"
            scp $newname $webtarg/$latf
        }
    }
    if ($awsbuck) {
        $awstarg = $awsbuck + '/' + $hostname.toupper() + "/stacks/" 
        aws s3 cp $newname $awstarg --profile $awsprofile
    }
}
else {
    Write-Output 'no stack to upload'
}
#if processing the current month sync the local cleaned folder back to the tempdir on the target
if ($ym -eq $currmth ) {
  write-output "Syncing back to remote folder"
  Write-Output "$upstreampath_l"
  bash -c "rsync -avz --delete --include *.bmp --include *.fits $destpath_l/ $upstreampath_l"
}

set-location $loc
#pause