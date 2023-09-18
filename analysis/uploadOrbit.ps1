# Copyright (C) 2018-2023 Mark McIntyre 
#
# Powershell script to upload revised fireball data to the website
#

# args : arg1 fbdate arg2 target orbit

$loc = Get-Location
if ($args.count -lt 2) {
    write-output "usage: uploadOrbit.ps1 fbdate orbitname"
    write-output "eg 20220107 20220107-212952.143_UK"
    write-output "eg 20220107  20220107-212952.143488"
    Write-Output "note that the latter format will be renamed with an underscore"
    exit 1
}

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini
set-location $loc

$fbfldr=$ini['fireballs']['localfolder']
$fbdate=$args[0]
set-location $fbfldr\$fbdate

$awsprofile=$ini['aws']['awsprofile']

$env:PYLIB=$ini['pylib']['pylib']
conda activate $ini['wmpl']['wmpl_env']
$wmplloc=$ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc;$env:pylib"


if ((test-path $args[1]) -eq "True" )
{
    $newname=$args[1].replace('-','_') 
    $newname = $newname.substring(0, $newname.length-3)+"_UK"
    Rename-Item $args[1] $newname
    $yr=$newname.substring(0,4)
    $ym=$newname.substring(0,6)
    $yd=$newname.substring(0,8)
    mkdir "$fbfldr/$fbdate/trajectories/$yr/$ym/$yd"
    Move-Item "$fbfldr/$fbdate/$newname" "$fbfldr/$fbdate/trajectories/$yr/$ym/$yd"
}else{
    $newname=$args[1]
    $yr=$newname.substring(0,4)
    $ym=$newname.substring(0,6)
    $yd=$newname.substring(0,8)
}
$srcpath="$fbfldr/$fbdate/trajectories/$yr/$ym/$yd/$newname"

# sort out the jpegs
out-file -filepath $srcpath/extrajpgs.html
$jpgs=(get-item $fbfldr/$fbdate/*.jpg).name
if ($jpgs -is [array]) {
    foreach ($jpg in $jpgs){
        $li = "<a href=""/img/single/${yr}/${ym}/${jpg}""><img src=""/img/single/${yr}/${ym}/${jpg}"" width=""20%""></a>"
        write-output $li  | out-file $srcpath/extrajpgs.html -append
    }
} else {
    $li = "<a href=""/img/single/${yr}/${ym}/${jpgs}""><img src=""/img/single/${yr}/${ym}/${jpgs}"" width=""20%""></a>"
    write-output $li  | out-file $srcpath/extrajpgs.html -append
}
out-file -filepath $srcpath/extrampgs.html
$jpgs=(get-item $fbfldr/$fbdate/*.mp4).name
if ($jpgs -is [array]) {
    foreach ($jpg in $jpgs){
        $li = "<a href=""/img/mp4/${yr}/${ym}/${jpg}""><video width=""20%""><source src=""/img/mp4/${yr}/${ym}/${jpg}"" width=""20%"" type=""video/mp4""></video></a>"
        write-output $li  | out-file $srcpath/extrampgs.html -append
    }
} else {
    $li = "<a href=""/img/mp4/${yr}/${ym}/${jpgs}""><video width=""20%""><source src=""/img/mp4/${yr}/${ym}/${jpgs}"" width=""20%"" type=""video/mp4""></video></a>"
    write-output $li  | out-file $srcpath/extrampgs.html -append
}

# copy the trajectory solution over
$targ="ukmeteornetworkarchive/reports/$yr/orbits/$ym/$yd/$newname"
aws s3 sync "$srcpath" "s3://$targ" --include "*" --exclude "*.jpg" --exclude "*.mp4" --profile $awsprofile
$targ="ukmda-website/reports/$yr/orbits/$ym/$yd/$newname"
aws s3 sync "$srcpath" "s3://$targ" --include "*" --exclude "*.jpg" --exclude "*.mp4" --profile ukmda_admin

# push the jpgs and mp4s to the website
# don't need to push to ukmonshared as the bucket triggers will do that 
#$targ="ukmeteornetworkarchive/img/single/$yr/$ym/"
#aws s3 sync "$fbfldr/$fbdate" "s3://$targ" --exclude "*" --include "*.jpg" --profile $awsprofile
#$targ="ukmeteornetworkarchive/img/mp4/$yr/$ym/"
#aws s3 sync "$fbfldr/$fbdate" "s3://$targ" --exclude "*" --include "*.mp4" --profile $awsprofile
$targ="ukmda-website/img/single/$yr/$ym/"
aws s3 sync "$fbfldr/$fbdate" "s3://$targ" --exclude "*" --include "*.jpg" --profile ukmda_admin
$targ="ukmda-website/img/mp4/$yr/$ym/"
aws s3 sync "$fbfldr/$fbdate" "s3://$targ" --exclude "*" --include "*.mp4" --profile ukmda_admin

# push the pickle and report to ukmon-shared
$targ="ukmda-shared/matches/RMSCorrelate/trajectories/$yr/$ym/$yd/$newname"
$pickle=(get-item "$srcpath/*.pickle").name
aws s3 cp "$srcpath/$pickle" "s3://$targ/" --profile ukmda_admin
$repfile=(get-item "$srcpath/*report.txt").name
aws s3 cp "$srcpath/$repfile" "s3://$targ/" --profile ukmda_admin

$targ="ukmon-shared/matches/RMSCorrelate/trajectories/$yr/$ym/$yd/$newname"
$pickle=(get-item "$srcpath/*.pickle").name
aws s3 cp "$srcpath/$pickle" "s3://$targ/" --profile $awsprofile
$repfile=(get-item "$srcpath/*report.txt").name
aws s3 cp "$srcpath/$repfile" "s3://$targ/" --profile $awsprofile


# add row to dailyreport file
$pf=(Get-ChildItem "$srcpath/*.pickle").fullname
$pf=$pf.replace('\','/')
$env:DATADIR="f:/videos/meteorcam/ukmondata"
aws s3 cp s3://ukmda-shared/consolidated/camera-details.csv $env:DATADIR/consolidated/  --profile ukmda_admin
$newl=(python -c "import reports.reportOfLatestMatches as rml ; print(rml.processLocalFolder('$pf','/home/ec2-user/ukmda-shared/matches/RMSCorrelate'))")

$dlyfile="$yd.txt"
scp "ukmonhelper2:prod/data/dailyreports/$dlyfile" .
$x=(select-string $newl $dlyfile)
if ($x.length -eq 0)
{
    add-content $dlyfile $newl
    scp "$dlyfile" "ukmonhelper2:prod/data/dailyreports/" 
}

# now invoke the script to build the index page and update the daily index.
$cmd="/home/ec2-user/prod/website/updateIndexPages.sh /home/ec2-user/prod/data/dailyreports/$dlyfile"
ssh ukmonhelper2 "$cmd"
$cmd="/home/ec2-user/prod/analysis/consolidateOutput.sh ${yr}"
ssh ukmonhelper2 "$cmd"
$cmd="/home/ec2-user/prod/website/createFireballPage.sh ${yr}"
ssh ukmonhelper2 "$cmd"
set-location $loc
