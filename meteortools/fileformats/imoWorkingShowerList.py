#
# python module to read the IMO Working Shower short List
#
# Copyright (C) 2018-2023 Mark McIntyre

import xmltodict
import datetime
import os
import numpy as np
from ..utils import jd2Date, sollon2jd
import copy

# imported from $SRC/share
try:
    from majorminor import majorlist, minorlist
except:
    majorlist = ['QUA', 'LYR', 'ETA', 'CAP', 'SDA', 'PER', 'AUR', 'ORI', 'NTA', 'STA', 'LEO', 'GEM', 'URS']
    minorlist = ['SPE','OCT','DRA','EGE','MON','HYD','COM','NOO']


class IMOshowerList:
    """
    Class that loads and parses the IMO Working Shower list, or if needed, the unconfirmed list. 
    Not all known showers are in the IMO working list. If a shower is not in the Working List then 
    this library will reference the full shower list curated by Peter Jenniskens which contains 
    debated and unconfirmed showers. 

    These list are updated whenever the library version is bumped, but if you want to override the files, define an 
    environment variable DATADIR, and place your own copies of the files at $DATADIR/share. See the share submodule 
    for more information. 

    """
    def __init__(self, fname=None, fullstreamname=None):
        if fname is None:
            datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
            fname = os.path.join(datadir, 'share', 'IMO_Working_Meteor_Shower_List.xml')
            if not os.path.isfile(fname):
                datadir=os.path.split(os.path.abspath(__file__))[0]
                fname = os.path.join(datadir, '..', 'share', 'IMO_Working_Meteor_Shower_List.xml')
        
        tmplist = xmltodict.parse(open(fname, 'rb').read())
        self.showerlist = tmplist['meteor_shower_list']['shower']
        if fullstreamname is None:
            fullstreamname = os.path.join(datadir, 'share', 'streamfulldata.npy')
            if not os.path.isfile(fullstreamname):
                datadir=os.path.split(os.path.abspath(__file__))[0]
                fullstreamname = os.path.join(datadir, '..', 'share', 'streamfulldata.npy')
        self.fullstreamdata = np.load(fullstreamname)
        #print('initialised')

    
    def getShowerByCode(self, iaucode, useFull=False):
        ds = {'@id':None, 'IAU_code':None,'start':None, 'end':None, 
            'peak':None, 'r':None, 'name':None, 'V':None, 'ZHR':None, 'RA':None, 'DE':None, 'pksollon': None}
        ds2 = {'@id':None, 'IAU_code':None,'start':None, 'end':None, 
            'peak':None, 'r':None, 'name':None, 'V':None, 'ZHR':None, 'RA':None, 'DE':None, 'pksollon': None}
        for shower in self.showerlist:
            if shower['IAU_code'] == iaucode:
                ds = shower
        pksollong = -1
        subset = self.fullstreamdata[np.where(self.fullstreamdata[:,3]==iaucode)]
        if subset is not None:
            mtch = [sh for sh in subset if int(sh[6]) > -1]
            if len(mtch) > 0:
                ds2 = copy.deepcopy(ds)
                ds2['IAU_code'] = mtch[-1][3].strip()
                ds2['name'] = mtch[-1][4].strip()
                ds2['V'] = mtch[-1][12]
                ds2['@id'] = mtch[-1][1]
                ds2['RA'] = mtch[-1][8]
                ds2['DE'] = mtch[-1][9]

                pksollong = float(mtch[-1][7])
                dt = datetime.datetime.now()
                yr = dt.year
                mth = dt.month
                jd = sollon2jd(yr, mth, pksollong)
                pkdt = jd2Date(jd, dt_obj=True)
                ds2['peak'] = pkdt.strftime('%h %d')
                # start/end pop idx, ZHR not available in the IAU data
                ds2['start'] = (pkdt + datetime.timedelta(days=-2)).strftime('%h %d')
                ds2['end'] = (pkdt + datetime.timedelta(days=2)).strftime('%h %d')
                ds2['pksollon'] = pksollong
        #print(ds)
        #print(ds2)
        if useFull is False:
            ds['pksollon'] = pksollong
            ds['@id'] = ds2['@id']
            return ds
        else:
            ds2['ZHR'] = ds['ZHR']
            ds2['r'] = ds['r']
            return ds2

    def getStart(self, iaucode, currdt=None):
        shower = self.getShowerByCode(iaucode)
        if currdt is None:
            now = datetime.datetime.today().year
            mth = datetime.datetime.today().month
        else:
            now = datetime.datetime.strptime(str(currdt), '%Y%m%d')
            mth = now.month
            now = now.year
        startdate = datetime.datetime.strptime(shower['start'], '%b %d')
        if iaucode == 'QUA' and mth !=12:
            # quadrantids straddle yearend
            now = now - 1
        startdate = startdate.replace(year=now)
        return startdate

    def getEnd(self, iaucode, currdt=None):
        shower = self.getShowerByCode(iaucode)
        if currdt is None:
            now = datetime.datetime.today().year
            mth = datetime.datetime.today().month
        else:
            now = datetime.datetime.strptime(str(currdt), '%Y%m%d')
            mth = now.month
            now = now.year
        enddate = datetime.datetime.strptime(shower['end'], '%b %d')
        if iaucode == 'QUA' and mth == 12:
            # quadrantids straddle yearend
            now = now + 1
        enddate = enddate.replace(year=now)
        return enddate

    def getPeak(self, iaucode, currdt=None):
        shower = self.getShowerByCode(iaucode)
        if currdt is None:
            now = datetime.datetime.today().year
            mth = datetime.datetime.today().month
        else:
            now = datetime.datetime.strptime(str(currdt), '%Y%m%d')
            mth = now.month
            now = now.year
        enddate = datetime.datetime.strptime(shower['peak'], '%b %d')
        if iaucode == 'QUA' and mth == 12:
            # quadrantids straddle yearend
            now = now + 1
        enddate = enddate.replace(year=now)
        return enddate

    def getRvalue(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['r']

    def getName(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['name']

    def getVelocity(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['V']

    def getZHR(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        zhr = shower['ZHR']
        if zhr is None:
            return -1
        else:
            return int(zhr)

    def getRaDec(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return float(shower['RA']), float(shower['DE'])

    def getActiveShowers(self, datetotest, majorOnly=False, inclMinor=False):
        activelist = []
        for shower in self.showerlist:
            shwname = shower['IAU_code']
            start = self.getStart(shwname, datetotest.strftime('%Y%m%d'))
            end = self.getEnd(shwname, datetotest.strftime('%Y%m%d')) + datetime.timedelta(days=3)
            if datetotest > start and datetotest < end:
                if majorOnly is False or (majorOnly is True and shwname in majorlist):
                    activelist.append(shwname)
                elif inclMinor is True and shwname in minorlist:
                    activelist.append(shwname)
        return activelist

    def getMajorShowers(self, includeSpo=False, stringFmt=False):
        majlist = majorlist 
        if includeSpo is True:
            majlist.append('spo')
        if stringFmt is True:
            tmplist = ''
            for shwr in majlist:
                tmplist = tmplist + shwr + ' '
            majlist = tmplist
        return majlist
