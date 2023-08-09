# Copyright (C) 2018-2023 Mark McIntyre

""" This folder contains some data files used by the library:  
    IMO_Working_Meteor_Shower_List.xml, the IMO's official working list  
    streamfulldata.npy  - a numpy dataset containing the Jenniskens full meteor list, including unconfirmed and disputed showers  

These files are updated whenever the library version is bumped, but if you want to override the files, define an 
environment variable DATADIR, and place your own copies of the files at $DATADIR/share. 
"""