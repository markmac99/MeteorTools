# Copyright (C) 2018-2023 Mark McIntyre
import numpy as np
import json
import os 
import pandas as pd
import matplotlib.pyplot as plt

from ukmon_meteortools.fileformats import trackCsvtoKML
try:
    from wmpl.Utils.Pickling import loadPickle
except:
    print('WMPL not available')


def pickleToKml(picklename, outdir=None):
    """Create a KML file of the trajectory in a solution pickle
     
    Arguments:  
        picklename: [string] full path to the solution pickle file  

    Keyword Args:  
        outdir: [string] where to save the KML. Default same place as pickle. 
    
    Returns:   
        the KML file as a tuple  
    """
    pickpath, trajname = os.path.split(picklename)
    data = loadPickle(pickpath, trajname).toJson()
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
    os.makedirs(outdir, exist_ok=True)
    return trackCsvtoKML(trajname.replace('.pickle', 'csv'), df, saveOutput=True, outdir=outdir)


def pickleTo2dTrack(picklename, outdir=None):
    """Create a 2d graph of the trajectory in a solution pickle
     
    Arguments:  
        picklename: [string] full path to the solution pickle file  

    Keyword Args:  
        outdir: [string] where to save the plot. Default same place as pickle. 
    
    Returns:   
        none
    """
    pickpath, trajname = os.path.split(picklename)
    data = loadPickle(pickpath, trajname).toJson()
    jsd = json.loads(data)
    alts = [] 
    times = []
    rngs = []
    for js in jsd['observations']:
        k = list(js.keys())[0]
        thisstat = js[k]
        alts += thisstat['model_ht']
        times += thisstat['time_data']
        rngs += thisstat['model_range']

    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    plt.plot(times, alts, linewidth=2)
    ax = plt.gca()
    ax.set(xlabel="Time(s)", ylabel="Altitude (m)")
    #print(min(alts), max(alts))
    ax.set_ylim(bottom = min(min(alts), 25000), top=max(max(alts), 120000))
    orig, fname = os.path.split(picklename)
    if outdir is None:
        outdir = orig
    fname = fname.replace('.pickle', '_2dtrack.png')
    f3dname = os.path.join(outdir, fname)

    plt.title('Trajectory of {}'.format(fname[:15]))
    plt.tight_layout()
    plt.savefig(f3dname, dpi=200)
    plt.close()

    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    plt.plot(rngs, alts, linewidth=2)
    ax = plt.gca()
    ax.set(xlabel="Range (m)", ylabel="Altitude (m)")
    #print(min(alts), max(alts))
    ax.set_ylim(bottom = min(min(alts), 25000), top=max(max(alts), 120000))
    orig, fname = os.path.split(picklename)
    if outdir is None:
        outdir = orig
    fname = fname.replace('.pickle', '_2drange.png')
    f3dname = os.path.join(outdir, fname)

    plt.title('Trajectory of {}'.format(fname[:15]))
    plt.tight_layout()
    plt.savefig(f3dname, dpi=200)
    plt.close()
    return 
