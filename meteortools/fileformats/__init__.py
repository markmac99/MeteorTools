# Copyright (C) 2018-2023 Mark McIntyre
# flake8: noqa
"""
Functions to load and manage various meteor file formats
- RMS FTPdetectInfo files
- RMS Platepar fiels
- The IMO Working shower list and full stream data list
- UFO Capture XML files
- UFO Analyser XML files

"""

from .ftpDetectInfo import filterFTPforSpecificTime, writeNewFTPFile, loadFTPDetectInfo, MeteorObservation
from .imoWorkingShowerList import IMOshowerList, majorlist, minorlist
from .platepar import loadPlatepars, platepar
from .UFOAnalyzerXML import UAXml
from .UFOCapXML import UCXml
from .kmlHandlers import trackCsvtoKML, trackKMLtoCsv, getTrackDetails, readCameraKML
