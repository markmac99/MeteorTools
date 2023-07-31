# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd


def _findNearDuplicates():
    """ not yet implemented """
    cols=['_mjd','_localtime','_lat1','_lng1','_lat2','_lng2','numstats','stations']
    df = pd.read_parquet('matched/matches-full-2022.parquet.snap', columns=cols)
    df['l1diff']=df._lat1.diff()*60
    df['l2diff']=df._lat2.diff()*60
    df['g1diff']=df._lng1.diff()*60
    df['g2diff']=df._lng2.diff()*60
    df['dtdiff']=df._mjd.diff()*86400
    df['stdiff']=df.numstats.diff()
    df['bl1diff']=df._lat1.diff(periods=-1)*60
    df['bl2diff']=df._lat2.diff(periods=-1)*60
    df['bg1diff']=df._lng1.diff(periods=-1)*60
    df['bg2diff']=df._lng2.diff(periods=-1)*60
    df['bdtdiff']=df._mjd.diff(periods=-1)*86400
    df['bstdiff']=df.numstats.diff(periods=-1)
    df = df.fillna(999)

    df2 = df[(abs(df.dtdiff) <= 1.0) | (abs(df.bdtdiff) <= 1.0)]
    df2 = df2[(abs(df2.l1diff) <= 2) | (abs(df2.bl1diff) <= 2)]
    df2 = df2[(abs(df2.l2diff) <= 2) | (abs(df2.bl2diff) <= 2)]
    df2 = df2[(abs(df2.g1diff) <= 2) | (abs(df2.bg1diff) <= 2)]
    df2 = df2[(abs(df2.g2diff) <= 2) | (abs(df2.bg2diff) <= 2)]

    numsame=0
    for i,rw in df2.iterrows():
        if df.iloc[i-1].stations != rw.stations:
            numsame +=1
            print(rw._localtime)
        print(f' number with the same cameras:  {numsame}')
        print(f' number with different cameras: {len(df2)-numsame}')
