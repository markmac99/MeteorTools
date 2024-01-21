# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to create a zip file of a solution and upload it

$loc = get-location
if ($args.count -lt 1) {
    $curdir = get-location
}else {
    $curdir = resolve-path $args[0]
}
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini
Set-Location $Loc

Add-Type -AssemblyName System.Windows.Forms

conda activate $ini['wmpl']['wmpl_env']
$wmplloc = $ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc;$env:pythonpath"

write-output "Find the pickle"
$picklefile= (Get-ChildItem $curdir\*.pickle -r).fullname
if ($picklefile -is [Array] -or $picklefile.length -eq 0) {
    $FileBrowser = New-Object System.Windows.Forms.OpenFileDialog -Property @{ InitialDirectory = $curdir; Filter = 'pickles (*.pickle)|*.pickle'; Title='Select orbit pickle' }
    $null = $FileBrowser.ShowDialog()
    $picklefile = $filebrowser.filename
    if ( $picklefile -eq "" ) {
        Write-Output "Cancelled"
        set-location $loc
        exit
    }
}
write-output "find the orbit full name"
$srcdir = ((get-item $picklefile).directoryname).replace('\','/')
$pickname = (get-item $picklefile).name
$origdir = (python -c "from wmpl.Utils.Pickling import loadPickle;pick = loadPickle('${srcdir}','${pickname}');print(pick.output_dir)")
$orbname = split-path $origdir -leaf
if ((test-path $curdir\$orbname) -eq 0 )
{
    mkdir -force $curdir\$orbname
    move-item $picklefile $curdir\$orbname\
}
$picklefile = (Get-ChildItem $picklefile -r).fullname

write-output "look for jpgs and mp4s"
mkdir -force $curdir\jpgs
$jpgdir = resolve-path $curdir\jpgs 
Move-Item $curdir\*.jpg $jpgdir
mkdir -force $curdir\mp4s
$mp4dir = resolve-path $curdir\mp4s 
Move-Item $curdir\*.mp4 $mp4dir

write-output "Creating zip file"
if ((test-path $env:temp\$orbname\mp4s) -eq 0 ) {mkdir $env:temp\$orbname\mp4s | out-null}
if ((test-path $env:temp\$orbname\jpgs) -eq 0 ) {mkdir $env:temp\$orbname\jpgs | out-null}
copy-item $picklefile $env:temp\$orbname
copy-item $jpgdir\*.jpg $env:temp\$orbname\jpgs
copy-item $mp4dir\*.mp4 $env:temp\$orbname\mp4s
if ((test-path $env:temp\$orbname.zip) -eq 1 ) { remove-item $env:temp\$orbname.zip}
compress-archive -destinationpath "$env:temp\$orbname.zip" -path "$env:temp\$orbname\*" 
remove-item $env:temp\$orbname\* -Recurse

write-output "Uploading $orbname.zip"
curl -X PUT -H "Content-Type:application/zip" --data-binary "@$env:temp\$orbname.zip" "https://api.ukmeteors.co.uk/fireballfiles?orbitfile=$orbname.zip"
move-item $env:temp\$orbname.zip $curdir -Force
Write-Output "uploaded at $(get-date)"
set-location $loc
conda deactivate
