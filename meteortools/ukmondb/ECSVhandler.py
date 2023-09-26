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
                numecsvs = len([e for e in ecsvlines if '# %ECSV' in e]) # find out how many meteors 
                fnamebase = dateStr.replace(':','_').replace('.','_') # create an output filename
                if numecsvs == 1:
                    print('saving to ', fnamebase+ '.ecsv')
                    with open(os.path.join(outdir, fnamebase + '.ecsv'), 'w') as outf:
                        outf.writelines(ecsvlines)
                else:
                    outf = None
                    j=1
                    for i in range(len(ecsvlines)):
                        if '# %ECSV' in ecsvlines[i]:
                            if outf is not None:
                                outf.close()
                                j=j+1
                            outf = open(os.path.join(outdir, fnamebase + f'_M{j:03d}.ecsv'), 'w')
                            print('saving to ', fnamebase + f'_M{j:03d}.ecsv')
                        outf.write(f'{ecsvlines[i]}\n')
        else:
            print('no error, but no data returned')
    else:
        print(res.status_code)
    return ecsvlines
