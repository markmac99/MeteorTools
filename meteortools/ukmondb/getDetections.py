# Copyright (C) 2018-2023 Mark McIntyre

# use the API to retrieve single-station data

import datetime 
import requests
import pandas as pd


def getDetections(dtstr, interval='m'):
    """ 
    Returns a list of detections within one interval of the specified time  

    Arguments:  
        dtstr:      [string] Date to search for in the format YYYYMMDD_HHMMSS  
        interval:   [string] window to search around the specified time. Currently only 'm' supported  

    Returns:  
        pandas dataframe containing [ID, Dtstamp, Filename] of any matching detections  

    Note:  
        dtstr must be at least YYYYMMDD_HHMM. If seconds are omitted, the window wil be centred on 
        hh:mm:30.  

    """
    srchapi = 'https://api.ukmeteors.co.uk/detections?'
    if len(dtstr) < 13:
        print('date range too wide. Must contain minutes')
        return False
    if len(dtstr) == 13:
        dtstr = dtstr + '30'
    if len(dtstr) == 14:
        dtstr = dtstr + '0'
    dt = datetime.datetime.strptime(dtstr[:15], '%Y%m%d_%H%M%S')
    if interval == 'm':
        dt1 = (dt + datetime.timedelta(seconds=-30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        dt2 = (dt + datetime.timedelta(seconds=30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    apiurl = f'{srchapi}d1={dt1}&d2={dt2}&opts=t:S'

    res = requests.get(apiurl)
    ids = []
    filenames = []
    dtstamps = []
    if res.status_code == 200:
        rawdata=res.text.strip()
        rawdata = rawdata[8:-2]
        spls = rawdata.split('"')
        for spl in spls:
            if len(spl) > 10:
                thisrow = spl.split(',')
                ids.append(thisrow[4])
                fname = thisrow[5].split('/')[-1].strip()
                filenames.append(fname)
                dtstamps.append(fname[10:25])
        df = pd.DataFrame({'ID':ids, 'Dtstamp':dtstamps, 'Filename':filenames})
        return df
    else:
        return False
