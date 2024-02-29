# Copyright (C) 2018-2023 Mark McIntyre

import requests
import os


def getECSVs(stationID, dateStr, savefiles=False, outdir='.'):
    """
    Retrieve a detection in ECSV format for the specified date  

    Arguments:  
        stationID:  [str] RMS Station ID code  
        dateStr:    [str] Date/time to retrieve for in ISO1601 format   
                          eg 2021-07-17T02:41:05.05  
    
    Keyword Arguments:  
        saveFiles:  [bool] save to file, or print to screen. Default False  
        outdir:     [str] path to save files into. Default '.'  
    """
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    ecsvlines=''
    if res.status_code == 200:
        rawdata=res.text.strip()
        if len(rawdata) > 10:
            ecsvlines=rawdata.split('\n') # convert the raw data into a python list
            if savefiles is True:
                os.makedirs(outdir, exist_ok=True)
                fnamebase = dateStr.replace(':','_').replace('.','_') # create an output filename
                j=0
                outf = False
                for li in ecsvlines:
                    if 'issue getting data' in li:
                        print(li)
                        return li
                    if '# %ECSV' in li:
                        if outf is not False:
                            outf.close()
                        j=j+1
                        fname = fnamebase + f'_ukmda_{stationID}_M{j:03d}.ecsv'
                        outf = open(os.path.join(outdir, fname), 'w')
                        print('saving to ', os.path.join(outdir,fname))
                    if outf:
                        outf.write(f'{li}\n')
                    else:
                        print('no ECSV marker found in data')
        else:
            print('no error, but no data returned')
    else:
        print(res.status_code)
    return ecsvlines
