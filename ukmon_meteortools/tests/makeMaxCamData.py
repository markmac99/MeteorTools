# powershell script to get test data for the Max Cam process

import os
import datetime
import json
import boto3
from fileformats.ftpDetectInfo import filterFTPforSpecificTime


def gatherData(camlist, ymd, outdir, patt):
    s3bucket='ukmon-shared'
    s3 = boto3.resource('s3')

    for camid in camlist:
        pref = f'matches/RMSCorrelate/{camid}/{camid}_{ymd}'
        for _, obj in enumerate(s3.Bucket(s3bucket).objects.filter(Prefix=pref)):
            fldr = obj.key.split('/')[3].strip()
            os.makedirs(os.path.join(outdir, camid, fldr), exist_ok=True)
            localf = os.path.basename(obj.key)
            if f'FTPdetectinfo_{fldr}.txt' in obj.key:
                localftpname = os.path.join(outdir, camid, fldr, localf)
                s3.meta.client.download_file(s3bucket, obj.key, localftpname)
            elif 'platepars_all_recalibrated.json' in obj.key:
                ppname = os.path.join(outdir, camid, fldr, localf)
                s3.meta.client.download_file(s3bucket, obj.key, ppname)
            elif '.config' in obj.key:
                cfgname = os.path.join(outdir, camid, fldr, localf)
                s3.meta.client.download_file(s3bucket, obj.key, cfgname)

    if patt is not None:
        for camid in camlist:
            if os.path.isdir(os.path.join(outdir, camid)):
                dirs = os.listdir(os.path.join(outdir, camid))
                if 'txt' not in dirs[0]:
                    fils = os.listdir(os.path.join(outdir, camid, dirs[0]))
                    ftpfile = [f for f in fils if 'FTP' in f and 'old' not in f and 'new' not in f]
                    localftpfile = os.path.join(outdir, camid, dirs[0], ftpfile[0])
                    filterFTPforSpecificTime(localftpfile, patt)


if __name__ == '__main__':
    # get datafile with
    # curl "https://api.ukmeteornetwork.co.uk/matches?reqtyp=detail&reqval=20230219_040224.504_UK" > .\MaxCams\19stationmatch.txt

    js = json.load(open('MaxCams/19stationmatch.txt', 'r'))
    camlist=js['stations'].split(';')
    patt = js['_localtime'][1:]
    if int(js['_h_ut']) < 12:
        adjdate = datetime.datetime.strptime(patt[:8], '%Y%m%d') +datetime.timedelta(days =-1)
        dtstr = adjdate.strftime('%Y%m%d')
    else:
        dtstr = patt[:8]

    patt = None
    gatherData(camlist, dtstr, 'MaxCams', patt)
