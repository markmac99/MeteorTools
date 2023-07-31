# powershell script to run the test

$fn='C:\Users\mark\Documents\Projects\meteorhunting\UKmon-shared\NewAnalysis\test_data\man_red\M20200514_012042_TACKLEY_NE.avi'
$cf='C:\Users\mark\Documents\Projects\meteorhunting\UKmon-shared\NewAnalysis\test_data\man_red\.config_NE'

set-location C:\Users\mark\Documents\Projects\meteorhunting\RMS
conda activate RMS
python -m Utils.ManualReduction -c $cf $fn

set-location $PSScriptRoot