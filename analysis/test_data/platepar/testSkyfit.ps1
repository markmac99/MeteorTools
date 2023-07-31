# powershell script to run the test
$basfn='M20200514_012042_TACKLEY_NE.avi'
$bascf='.config_NE'

#$basfn='FF_UK000F_20200614_221945_413_0031232.fits'
#$bascf='.config_SE'

$fn='C:\Users\mark\Documents\Projects\meteorhunting\UKmon-shared\NewAnalysis\test_data\platepar\'+$basfn
$cf='C:\Users\mark\Documents\Projects\meteorhunting\UKmon-shared\NewAnalysis\test_data\platepar\'+$bascf

set-location C:\Users\mark\Documents\Projects\meteorhunting\RMS
conda activate RMS
python -m RMS.Astrometry.SkyFit -c $cf $fn

set-location $PSScriptRoot
