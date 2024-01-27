# Copyright (C) 2018-2023 Mark McIntyre 
#
# manually reduce one camera folder 
#
# args : arg1 date, arg2 stationid

if ($args.count -lt 1) {
    write-output "usage: manualReduction.ps1 yyyymmdd_hhmm\UKxxxxx"
    exit 1
}

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$fbfldr=$ini['localdata']['fbfolder']
set-location $fbfldr

# locate target path
$argstr = [string]$args[0]
$targpth = "$fbfldr\$argstr"
$jpgpth = "$targpth\..\jpgs"
$mp4pth = "$targpth\..\mp4s"

if ((test-path $targpth) -eq 0) { 
    Write-Output "path not found" 
}
else {
    if ((test-path $jpgpth) -eq 0) { mkdir $jpgpth }
    if ((test-path $mp4pth) -eq 0) { mkdir $mp4pth }
    write-output "processing $targpth"
    conda activate $ini['rms']['rms_env']
    $env:PYTHONPATH=$ini['rms']['rms_loc']
    push-Location $ini['rms']['rms_loc']
    if (test-path "$targpth\FF*.fits") {
        if ((test-path "$targpth\FF*.jpg") -eq 0) {
            python -m Utils.BatchFFtoImage $targpth jpg
        }
        foreach ($jpg in $jpgs) { 
            if ((test-path "$jpgpth\$jpg") -eq 0) {
                copy-item $targpth\$jpg $jpgpth\ -Force
            }
        }
        if ((test-path $targpth\*.mp4) -eq 0 ) {
            if (test-path "$targpth\FR*.bin") {
                python -m Utils.FRbinViewer -x -f mp4 $targpth
            }
            $mp4s = (Get-ChildItem $targpath\FF*.mp4)
            foreach ($mp4 in $mp4s) { 
                if ((test-path "$mp4pth\$mp4") -eq 0) {
                    move-item $targpth\$jpg $mp4pth\ -Force                
                }
            }
        }
    }
    # run SkyFit to refine the platepar and reduce the path
    python -m Utils.SkyFit2 $targpth -c $targpth\.config
    $usefrs = read-host -prompt "rename FFs and rerun?"
    if ($usefrs -eq 'Y') {
        $fitsfiles=(Get-ChildItem $targpth\FF*.fits).FullName
        $frfiles=(Get-ChildItem $targpth\FR*.bin).FullName
        if ($frfiles -ne "" ) {
            foreach ($fits in $fitsfiles) { $newn = ${fits} + ".calibonly" ; Rename-Item $fits $newn }
        }
        else {
            Write-Output "no FR files, not renaming the FFs"
        }
        python -m Utils.SkyFit2 $targpth -c $targpth\.config

        foreach ($fits in $fitsfiles) { $newn = ${fits} + ".calibonly" ; Rename-Item  $newn $fits}
}
}
pop-location

