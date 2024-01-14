# Copyright (C) 2018-2023 Mark McIntyre

import datetime
import pandas as pd
import argparse
import os
import matplotlib.pyplot as plt
from meteortools.utils import greatCircleDistance
try:
    from wmpl.Utils.PlotMap_OSM import OSMMap
except:
    print('WMPL not available')

RAD2DEG=57.2958


def multiEventGroundMap(startdt, enddt, statid=None, shwr=None, outdir=None, minmag=999, fireballsonly=False,
                        obslat=None, obslon=None, evtdist=None):
    """
    Plots a ground track diagram of all events between two dates, with filters by station and shower  

    Arguments:  
        start:      [string] start date in YYYYMMDD format  
        end:        [string] end date in YYYYMMDD format  
        statid:     [string] station to filter for. Default all stations.  
        shwr:       [string] Filter by shower eg PER. Default All showers.  
        outdir:     [string] where to save the file to. if this parameter is omitted, the image will be displayed not saved  
        shwr:       [float] Min mag to include.  
        fbonly:     [bool] True if only to plot fireballs.
        obslat:     [float] Observers latitude: if this is set, obslon and evtdist must be set too
        obslon:     [float] Observers longitude
        evtdist:    [float] Event distance from observer

    Output:  
        A jpg map of the detections.   

    Note:  
        This function reads directly from the UKMON public dataset.  
        If obslat is set, then obslon and evtdist must be set, and only events within evtdist of the 
        observer will be plotted. 

    """
    yr = startdt[:4]

    cols=['_lat1', '_lng1','_lat2','_lng2','_stream','dtstamp', 'stations', '_amag', 'isfb']
    matchfile = f'https://archive.ukmeteors.co.uk/browse/parquet/matches-full-{yr}.parquet.snap'

    dta = pd.read_parquet(matchfile, columns=cols)
    dta = dta[dta._amag < minmag]
    if fireballsonly:
        dta = dta[dta.isfb==1]
    # filter the data down to just the cols we want
    sd = datetime.datetime.strptime(startdt, '%Y%m%d')
    sd = sd+datetime.timedelta(hours=12)
    if startdt == enddt:
        ed = sd + datetime.timedelta(days=1)
    else:
        ed = datetime.datetime.strptime(enddt, '%Y%m%d')
        ed = ed+datetime.timedelta(hours=12)
    dta = dta[dta.dtstamp >= sd.timestamp()]
    dta = dta[dta.dtstamp <= ed.timestamp()]
    
    if shwr is not None:
        dta = dta[dta._stream==shwr.upper()]
    if statid is not None:
        dta = dta[dta.stations.str.contains(statid.upper())]
    if obslat:
        obslat = float(obslat)
        obslon = float(obslon)
        evtdist = float(evtdist)
        dta['evtdist'] = [greatCircleDistance(obslat/RAD2DEG, obslon/RAD2DEG, x/RAD2DEG,y/RAD2DEG) for x,y in zip(dta._lat2, dta._lng2)]
        dta = dta[dta.evtdist <= evtdist]

    if len(dta) > 1:
        plt.clf()
        fig = plt.gcf()
        fig.set_size_inches(11.6, 8.26)
        lat_list = [min(min(dta._lat1), min(dta._lat2))/RAD2DEG, max(max(dta._lat1), max(dta._lat2))/RAD2DEG]
        lon_list = [min(min(dta._lng1), min(dta._lng2))/RAD2DEG, max(max(dta._lng1), max(dta._lng2))/RAD2DEG]
        # Init the map
        #print(lat_list, lon_list)
        m = OSMMap(lat_list, lon_list, border_size=50, color_scheme='dark')
        lat1s=list(dta._lat1)
        lat2s=list(dta._lat2)
        lng1s=list(dta._lng1)
        lng2s=list(dta._lng2)
        for l1, l2, g1, g2 in zip(lat1s, lat2s, lng1s, lng2s):
            lats = [l1/RAD2DEG, l2/RAD2DEG]
            lons = [g1/RAD2DEG, g2/RAD2DEG]
            m.plot(lats, lons, c='r')
            m.scatter(l2/RAD2DEG, g2/RAD2DEG, c='k', marker='+', s=50, alpha=0.75)
        if outdir is not None:
            plt.savefig(os.path.join(outdir, f'{startdt}-{enddt}-{shwr}-{statid}.jpg'))
        else:
            plt.show()
        plt.close()
    return 


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="""Plot a ground map of many detections.""",
        formatter_class=argparse.RawTextHelpFormatter)

    arg_parser.add_argument('start_date', type=str, help='start date in yyyymmdd format')
    arg_parser.add_argument('end_date', type=str, help='end date in yyyymmdd format')
    arg_parser.add_argument('-s', '--shower', metavar='SHOWER', type=str,
        help="Map just this single shower given its code (e.g. PER, ORI, ETA).")

    arg_parser.add_argument('-i', '--stationid', metavar='STATID', help='Station id eg UK0006')
    arg_parser.add_argument('-o', '--outdir', metavar='OUTDIR', help='Location to save jpg into')
    arg_parser.add_argument('-m', '--minmag', metavar='MINMAG', type=float, help='Minimum magnitude to filter for')
    arg_parser.add_argument('-f', '--fbonly', action='store_true', help='Plot only fireballs')
    arg_parser.add_argument('-l', '--obs_lat', metavar='OBSLAT', help='Observer latitude (degrees')
    arg_parser.add_argument('-g', '--obs_lon', metavar='OBSLON', help='Observer longitude (degrees)')
    arg_parser.add_argument('-d', '--event_distance', metavar='EVTDIST', help='Distance from observer (km)')

    cml_args = arg_parser.parse_args()
    minmag = cml_args.minmag
    if not minmag:
        minmag = 999
    obslat = cml_args.obs_lat
    if not obslat:
        obslat = None
        obslon = None
        evtdist = None
    else:
        if not cml_args.obs_lon or not cml_args.event_distance:
            print('if providing an observer latitude, must also supply longitude and distance')
            exit(0)
        else:
            obslon = cml_args.obs_lon
            evtdist = cml_args.event_distance
    multiEventGroundMap(cml_args.start_date, cml_args.end_date, 
        cml_args.stationid, cml_args.shower, cml_args.outdir, minmag, cml_args.fbonly, 
        obslat, obslon, evtdist)
