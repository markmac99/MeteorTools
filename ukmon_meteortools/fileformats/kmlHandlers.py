import xmltodict
from shapely.geometry import Polygon
import csv
import simplekml
import numpy as np
import pandas as pd
import os


def readCameraKML(kmlFilename, return_poly=False):
    """ Load a KML file and return either a list of lats and longs, or a Shapely polygon  
    
    Arguments:  
        kmlFilename:    [string] full path to the KML file to consume   
        return_poly:    [bool] return a Shapely polygon? Default False  

    
    Returns:  
        if return_poly is false, returns a tuple of (cameraname, lats, longs) where lats and longs are lists of the 
        latitudes and longitudes in the KML file.  

        If return_poly is true, returns a tuple of (cameranamem, shapely Polygon)  
    """

    with open(kmlFilename) as fd:
        x = xmltodict.parse(fd.read())
        cname = x['kml']['Folder']['name']
        coords = x['kml']['Folder']['Placemark']['MultiGeometry']['Polygon']['outerBoundaryIs']['LinearRing']['coordinates']
        coords = coords.split('\n')
        if return_poly is False:
            lats = []
            lngs = []
            for lin in coords:
                s = lin.split(',')
                lngs.append(float(s[0]))
                lats.append(float(s[1]))
            return cname, lats, lngs
        else:
            ptsarr=[]
            for lin in coords:
                s = lin.split(',')
                ptsarr.append((float(s[0]), float(s[1])))
            polyg = Polygon(ptsarr)
            return cname, polyg 


def trackCsvtoKML(trackcsvfile, trackdata=None, saveOutput=True, outdir=None):
    """ 
    Either reads a CSV file containing lat, long, height of an event and 
    creates a 3d KML file from it or, if trackdata is populated, converts a Pandas dataframe containing 
    the same data. Output is written to disk unless saveOutput is false.  
    
    Arguments:  
        trackcsvfile:   [string] full path to the file to read from  
        trackdata:      [array] pandas dataframe containing the data. Default None  
        saveOutput:     [bool] write the KML file to disk. Default true  
        outdir:         [string] where to save the file. Default same folder as the source file

    Returns:  
        the KML file as a tuple  
        """
    kml=simplekml.Kml()
    kml.document.name = trackcsvfile
    if trackdata is None:
        inputfile = csv.reader(open(trackcsvfile))
        for row in inputfile:
            #columns are lat, long, height, times
            kml.newpoint(name='', coords=[(row[1], row[0], row[2])])
    else:
        for i,r in trackdata.iterrows():
            kml.newpoint(name=f'{r[3]:.5f}', coords=[(r[1], r[0], r[2])], extrude=1, altitudemode='absolute')
    if 'csv' in trackcsvfile:
        outname = trackcsvfile.replace('.csv','.kml')
    else:
        outname = f'{trackcsvfile}.kml'
    if saveOutput:
        if outdir is None:
            outdir, _ = os.path.split(trackcsvfile)
        os.makedirs(outdir, exist_ok=True)
        outname = os.path.join(outdir, outname)
        kml.save(outname)
    return kml


def trackKMLtoCsv(kmlfile, kmldata = None, saveOutput=True, outdir=None):
    """ convert a track KML retrieved by ukmondb.trajectoryKML to a 3 dimensional CSV file
    containing coordinates of points on the trajectory.   
    
    Arguments:  
        kmlfile     [string] full path to the KML file to read from.  
        kmldata     [kml] the kml data if available.   
        saveOutput  [bool] Default True, save the output to file.  
        outdir      [string] where to save to if saveOutput is True.  

    Note: if kmldata is supplied, then kmlfile is ignored.  
        
    Returns:  
        a Pandas dataframe containing the lat, long, alt and time of each 
        point on the trajectory, sorted by time. 

        """
    with open(kmlfile) as fd:
        x = xmltodict.parse(fd.read())
        placemarks=x['kml']['Document']['Placemark']
        lats = []
        lons = []
        alts = [] 
        tims = []
        for pm in placemarks:
            tims.append(float(pm['name']))
            coords = pm['Point']['coordinates'].split(',')
            lons.append(float(coords[0]))
            lats.append(float(coords[1]))
            alts.append(float(coords[2]))
    df = pd.DataFrame({"lats": lats, "lons": lons, "alts": alts, "times": tims})
    df = df.sort_values(by=['times', 'lats'])
    if saveOutput:
        fname = kmlfile
        if outdir is None:
            outdir, fname = os.path.split(kmlfile)
        outf = os.path.join(outdir, fname).replace('.kml', '.csv').replace('.KML','.csv')
        df.to_csv(outf, index=False)
    return df


def getTrackDetails(traj):
    """ Get track details from a WMPL trajectory object  
    
    Arguments:  
        traj:       a WMPL trajectory object containing observations  

    Returns:  
        a Pandas dataframe containing the lat, long, alt and time of each point on the trajectory, sorted by time. 
    """
    lats = []
    lons = []
    alts = [] 
    lens = []
    # Go through observation from all stations
    for obs in traj.observations:
        # Go through all observed points
        for i in range(obs.kmeas):
            lats.append(np.degrees(obs.model_lat[i]))
            lons.append(np.degrees(obs.model_lon[i]))
            alts.append(obs.model_ht[i])
            lens.append(obs.time_data[i])
    df = pd.DataFrame({"lats": lats, "lons": lons, "alts": alts, "times": lens})
    df = df.sort_values(by=['times', 'lats'])
    return df
