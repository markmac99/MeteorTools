# Copyright (C) 2018-2023 Mark McIntyre
# 
#
import os
import glob
import xmltodict

from shapely.geometry import Polygon
from shapely.geometry import Point


def _munchKML(kmlFilename):
    """ Private function to work around circular dependency 
    """
    with open(kmlFilename) as fd:
        x = xmltodict.parse(fd.read())
        cname = x['kml']['Folder']['name']
        coords = x['kml']['Folder']['Placemark']['MultiGeometry']['Polygon']['outerBoundaryIs']['LinearRing']['coordinates']
        coords = coords.split('\n')
        ptsarr=[]
        for lin in coords:
            s = lin.split(',')
            ptsarr.append((float(s[0]), float(s[1])))
        polyg = Polygon(ptsarr)
        return cname, polyg 


def pointInsideFov(latDegs,lngDegs, kmlFilename):
    """
    Test if a point is inside the field of view of a KML file. Useful for testing which 
    cameras might have seen an event at a known location.  

    Arguments:  
        latDegs:        [degrees] latitude of the point  
        lngDegs:        [degrees] latitude of the point  
        kmlFileName:    [str] full path to the KML file to test  

    Returns:  
        True or False  
    """

    c1, p1 = _munchKML(kmlFilename)
    pt = Point(latDegs, lngDegs)
    return p1.contains(pt)


def checkKMLOverlap(kmfile1, kmfile2):
    """
    Test if two KML files overlap. Useful for finding which other cameras 
    might have seen an event seen by the first camera. 

    Arguments:  
        kmlfile1:       [str] full path to first KML file  
        kmlfile2:       [str] full path to second KML file  

    Returns:  
        True or False
    """
    _,p1 = _munchKML(kmfile1)
    _,p2 = _munchKML(kmfile2)
    return p1.intersects(p2)


def getOverlapWith(srcfolder, kmlpattern='*-25km.kml', refcam='UK0006'):
    """
    Check for overlap between the named camera, and every KML file in a folder, at the pattern altitude  

    Arguments:  
        srcfolder:  [str] path to folder containing KML files to test.   
        kmlpattern: [str] kml pattern to match. Default "*-25km.kml"  
        refcam:     [str] Cameraid to check against. Its KML must be in srcfolder  
     
    Returns:  
        list of camera IDs that overlap with the target  
    """
    kmllist = glob.glob1(srcfolder, kmlpattern)
    currmatches=[]
    refkml = f'{refcam}{kmlpattern[1:]}'
    currmatches.append(refcam[:6])
    print('checking ', refkml)
    for testkml in kmllist:
        if testkml != refkml:
            testcam,_ = os.path.splitext(testkml)
            if checkKMLOverlap(os.path.join(srcfolder, refkml), os.path.join(srcfolder, testkml)) is True:
                currmatches.append(testcam[:6])
    return currmatches



def getOverlappingCameras(srcfolder, kmlpattern='*-25km.kml'):
    """
    Check for all overlaps in the folder at the pattern altitude. Returns a massive 2d array  

    Arguments:  
        srcfolder:  [str] path to folder containing KML files to test.   
        kmlpattern: [str] kml pattern to match. Default "*-25km.kml"  

    Returns:  
        list of lists of groups of overlaping IDs 
     
    """
    kmllist = glob.glob1(srcfolder, kmlpattern)
    kmllist2 = kmllist
    matches = []

    for refkml in kmllist:
        currmatches=[]
        refcam,_ = os.path.splitext(refkml)
        currmatches.append(refcam[:6])
        for testkml in kmllist2:
            if testkml != refkml:
                testcam,_ = os.path.splitext(testkml)
                if checkKMLOverlap(os.path.join(srcfolder, refkml), os.path.join(srcfolder, testkml)) is True:
                    currmatches.append(testcam[:6])
        matches.append(currmatches)
    return matches
