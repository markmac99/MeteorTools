# Copyright (C) 2018-2023 Mark McIntyre 
#
# powershell script to plot intersections on map
#
# load the helper functions
$here=$psscriptroot

. $here\helperfunctions.ps1
# read the inifile
$inifname = $here + '\orbitsolver.ini'
$ini = get-inicontent $inifname

$wmpl_loc = $ini['wmpl']['wmpl_loc']
$wmpl_env = $ini['wmpl']['wmpl_env']
$env:PROJ_LIB = $ini['wmpl']['proj_lib']

$here=$psscriptroot

conda activate $wmpl_env

$env:pythonpath="$wmpl_loc;..\"

python plotStationsOnMap.py $args[0]