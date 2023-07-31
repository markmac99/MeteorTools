This folder contains files for use in daily checks of the data from the pi

camera1.ini
===========
config file used by the other scripts

dailyReview.ps1
==============
reads the config file then copies the data from the Pi to a local folder
before starting the BinViewer so you can review the data.
optionally, if you have RMS installed and configured locally, the script
will run some postprocessing on the local ConfirmedFiles folder

reorgByYMD.ps1
==============
Copies the Pi data into a more structured layout similar to that used
by the UFO suite, ie YYYY\YYYYmm\YYYYmmDD\. 

manualReduction.ps1
===================
Simplifies the process of manually identifying a meteor. Run this script from
the commandline with two arguments: the date and time you want to process eg 20200514 033412
to manually review an FF file from 03:34:12 from the night of 2020-05-14. 
Note that data from after midnight will be in the folder for the previous evening!

Once the ManualReduction window opens, press Ctrl-P to load the platepar file
Then use the arrow keys to find the start of the meteor. Use left-click to mark the position of 
the meteor in each frame, and shift-left-click to paint the trail. Repeat for each frame
containing the meteor. 
Then press Ctrl-S to save the FTP file. 
When you exit the programme, two notepad windows will pop up, one containing your new FTP file
and one containing the old one. You can then copy the relevant details from the new into the old file. 

