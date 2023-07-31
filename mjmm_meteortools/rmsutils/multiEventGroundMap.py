# Copyright (C) 2018-2023 Mark McIntyre

import datetime
import pandas as pd
import argparse
import os
import matplotlib.pyplot as plt
try:
    from wmpl.Utils.PlotMap_OSM import OSMMap
except:
    print('WMPL not available')

RAD2DEG=57.2958


def multiEventGroundMap(startdt, enddt, statid=None, shwr=None, outdir=None):
    """
    Plots a ground track diagram of all events between two dates, with filters by station and shower  

    Arguments:  
        start:      [string] start date in YYYYMMDD format  
        end:        [string] end date in YYYYMMDD format  
        statid:     [string] station to filter for. Default all stations.  
        shwr:       [string] Filter by shower eg PER. Default All showers.  
        outdir:     [string] where to save the file to. if this parameter is omitted, the image will be displayed not saved  

    Output:  
        A jpg map of the detections.   

    Note:  
        This function reads directly from the UKMON public dataset.  

    """
    yr = startdt[:4]

    cols=['_lat1', '_lng1','_lat2','_lng2','_stream','dtstamp', 'stations']
    matchfile = f'https://archive.ukmeteornetwork.co.uk/browse/parquet/matches-full-{yr}.parquet.snap'

    dta = pd.read_parquet(matchfile, columns=cols)

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

    if len(dta) > 1:
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

    cml_args = arg_parser.parse_args()

    multiEventGroundMap(cml_args.start_date, cml_args.end_date, 
        cml_args.stationid, cml_args.shower, cml_args.outdir)
