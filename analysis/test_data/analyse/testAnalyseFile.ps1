# powershell script to run test

$srcdir='c:/users/mark/documents/projects/meteorhunting/ukmda-shared/newanalysis/'
$ff_directory=$srcdir+'test_data/analyse/'
$ff_name='M20200514_232502_TACKLEY_NE.avi'
$config = '.config_NE'

$fname=$ff_directory+'/'+$ff_name

$modname=$srcdir+'AnalyseUFOwithRMS.py'

conda activate RMS
set-location C:\Users\mark\Documents\Projects\meteorhunting\RMS

python $modname -c $config $fname 

set-location $PSScriptRoot