# Copyright (C) 2018-2023 Mark McIntyre 
#
# manually reduce one camera folder 
#
# args : arg1 date, arg2 stationid

if ($args.count -lt 1) {
    write-output "usage: densityPlots.ps1 yyyymm"
    exit 1
}
$ym = [string]$args[0]
$yr = $ym.substring(0,4)
push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

#$stationdetails=$ini['fireballs']['stationdets']
$datafldr=$ini['ukmondata']['localfolder']
set-location ${datafldr}/orbits/${yr}

conda activate $ini['wmpl']['wmpl_env']
$env:PYTHONPATH=$ini['wmpl']['wmpl_loc']

if ($dtstr.length -eq 4){

    $yms=(Get-ChildItem $yr).name
    foreach ($ym in $yms){
        if ($ym.substring(0,2) -eq "20") 
        {
            $fldrs=(Get-ChildItem $ym).name

            foreach ($fldr in $fldrs) {
                python -m wmpl.Trajectory.AggregateAndPlot  ./${ym}/${fldr} -p -s 30
                Move-Item ./${ym}/${fldr}/scecliptic_density.png plots/density/${fldr}_density.png -force
                Move-Item ./${ym}/${fldr}/scecliptic_vg.png plots/vg/${fldr}_vg.png -force
                Move-Item ./${ym}/${fldr}/scecliptic_sol.png plots/sol/${fldr}_sol.png -force
            }
        }
    }
}else{
    $fldrs=(Get-ChildItem $ym).name

    foreach ($fldr in $fldrs) {
        python -m wmpl.Trajectory.AggregateAndPlot  ./${ym}/${fldr} -p -s 30
        Move-Item ./${ym}/${fldr}/scecliptic_density.png plots/density/${fldr}_density.png -force
        Move-Item ./${ym}/${fldr}/scecliptic_vg.png plots/vg/${fldr}_vg.png -force
        Move-Item ./${ym}/${fldr}/scecliptic_sol.png plots/sol/${fldr}_sol.png -force
    }

}


pop-location

