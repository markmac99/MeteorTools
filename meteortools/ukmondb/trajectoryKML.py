# Copyright (C) 2018-2023 Mark McIntyre
import numpy as np
import requests
import json
import os 
import pandas as pd

try:
    from ..fileformats import trackCsvtoKML
except Exception:
    from meteortools.fileformats import trackCsvtoKML


def trajectoryKML(trajname, outdir=None):
    """
    Create a 3-d KML file showing the trajectory of a meteor which can be 
    loaded into Google Maps. 
    
    Arguments:  
        trajname:   [string] trajectory name eg 20230213_025913.678_UK
        outdir:     [string] where to save the file. Defaults to current location  

    Returns:  
        kmlfile:    name of the saved KML file  
    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
    fmt = 'json'
    apicall = f'{apiurl}?reqval={trajname}&format={fmt}'
    res = requests.get(apicall, stream=True)
    if res.status_code == 200:
        data=b''
        for chunk in res.iter_content(chunk_size=4096):
            data = data + chunk
        jsd = json.loads(data)
        lats = []
        lons = []
        hts = [] 
        times = []
        for js in jsd['observations']:
            k = list(js.keys())[0]
            thisstat = js[k]
            lats += thisstat['model_lat']
            lons += thisstat['model_lon']
            hts += thisstat['model_ht']
            times += thisstat['time_data']
        df = pd.DataFrame({"lats": np.degrees(lats), "lons": np.degrees(lons), "alts": hts, "times": times})
        df = df.sort_values(by=['times', 'lats'])
        outfname = os.path.join(outdir, f'{trajname}.kml')
        if outdir is None:
            outdir = '.'
            os.makedirs(outdir, exist_ok=True)
        trackCsvtoKML(trajname, df, saveOutput=True, outdir=outdir)
        return outfname
    else:
        print('no match')
        return None
