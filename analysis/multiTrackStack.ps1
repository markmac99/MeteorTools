param ($dt1, $dt2, $shwrs="ALL", $outdir="c:/temp", $scalefactor=3, $constellations=1)

# Copyright (C) 2018-2023 Mark McIntyre 

# multi night multi camera trackstack

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$RMSLOC=$ini['rms']['rms_loc']
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH="$RMSLOC"
Pop-Location

$conflag=""
if ($constellations -eq 1){
    $conflag="--constellations"
}
$camlist = @('uk0006','uk000f','uk001l','uk002f')
$fldrlist=@()
$startdt = [datetime]::parseexact($dt1,'yyyyMMdd', $null)
$enddt = [datetime]::parseexact($dt2,'yyyyMMdd', $null)
$srcfolder = $ini['localdata']['localfolder']

while ($startdt -le $enddt){
    $dtv=$startdt.tostring('yyyyMMdd')
    for ($i=0;$i -lt $camlist.count ; $i++) { 
        $srcpath = $srcfolder + '\' + $camlist[$i] + '\ArchivedFiles'
        $datedir = $srcpath + '\*_' + $dtv + "_*" 
        $dname = (Get-ChildItem  -directory "$datedir" ).fullname
        $fldrlist =  $fldrlist + $dname 
    }
    $startdt = $startdt.adddays(1)
}
$fbfolder = $ini['localdata']['fbfolder']
$cfg = $fbfolder + '\..\config\uk002f\.config'
push-Location $ini['rms']['rms_loc']
if ($shwrs -eq "ALL") {
    python -m Utils.TrackStack --freecore -x -c $cfg -o $outdir -f $scalefactor $conflag $fldrlist
    $oname = (Get-ChildItem "$outdir\UK002F_$dtv_*track_stack.jpg" ).fullname
    $nname = $oname.replace('UK002F','4CAMS')
}
else {
    python -m Utils.TrackStack --freecore -x -c $cfg -s $shwrs -o $outdir -f $scalefactor $conflag $fldrlist
    $oname = (Get-ChildItem "$outdir\UK002F_$dtv_*track_stack.jpg" ).fullname
    $nname = $oname.replace('UK002F','4CAMS_'+$shwrs+'_')
}
copy-Item $oname $nname -force
Remove-Item $oname
Write-Output "renamed to $nname"
pop-location
