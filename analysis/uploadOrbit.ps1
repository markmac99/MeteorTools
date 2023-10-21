# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to create a zip file of a solution and upload it

$loc = get-location
if ($args.count -lt 1) {
    $curdir = get-location
}else {
    $curdir = resolve-path $args[0]
}
Add-Type -AssemblyName System.Windows.Forms

# look for a single pickle file in the target folder
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
$srcdir = (get-item $picklefile).directoryname

# look for jpgs and mp4s in the expected place relative to the pickle file
$jpgdir = resolve-path $srcdir\..\jpgs 
if ((test-path $jpgdir) -eq 0) 
{
    $FileBrowser = New-Object System.Windows.Forms.OpenFileDialog -Property @{ InitialDirectory = $curdir; Filter = 'images (*.jpg)|*.jpg'; Title='Select JPG folder' }
    $null = $FileBrowser.ShowDialog()
    $jpgs = $filebrowser.filename
    $jpgdir = (get-item $jpgs).directoryname    
}
$mp4dir = resolve-path $srcdir\..\mp4s 
if ((test-path $mp4dir) -eq 0){
    $FileBrowser = New-Object System.Windows.Forms.OpenFileDialog -Property @{ InitialDirectory = $curdir; Filter = 'images (*.mp4)|*.mp4'; Title='Select MP4 folder' }
    $null = $FileBrowser.ShowDialog()
    $mp4s = $filebrowser.filename
    $mp4dir = (get-item $mp4s).directoryname
}
$orbname = (get-item ((get-item $picklefile).directoryname)).name

if ((test-path $env:temp\$orbname\mp4s) -eq 0 ) {mkdir $env:temp\$orbname\mp4s | out-null}
if ((test-path $env:temp\$orbname\jpgs) -eq 0 ) {mkdir $env:temp\$orbname\jpgs | out-null}
copy-item $picklefile $env:temp\$orbname
copy-item $jpgdir\*.jpg $env:temp\$orbname\jpgs
copy-item $mp4dir\*.mp4 $env:temp\$orbname\mp4s
if ((test-path $env:temp\$orbname.zip) -eq 1 ) { remove-item $env:temp\$orbname.zip}
compress-archive -destinationpath "$env:temp\$orbname.zip" -path "$env:temp\$orbname\*" 
remove-item $env:temp\$orbname\* -Recurse

curl -X PUT -H "Content-Type:application/zip" --data-binary "@$env:temp\$orbname.zip" "https://api.ukmeteors.co.uk/fireballfiles?orbitfile=$orbname.zip"
move-item $env:temp\$orbname.zip $mp4dir\.. -Force
set-location $loc
