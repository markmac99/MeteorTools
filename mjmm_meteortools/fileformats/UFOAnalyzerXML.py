#  A class to handle UFO Analyser xml files
# Copyright (C) 2018-2023 Mark McIntyre

import xmltodict
import datetime
import math
import numpy
from ukmon_meteortools.utils import datetime2JD, altAz2RADec


class UAXml:
    """" Load and manage a UFO-Analyser XML file containing meteor detections """
    def __init__(self, fname):
        """Construct a UAxml object from fname"""
        with open(fname) as fd:
            self.uaxml = xmltodict.parse(fd.read())

    def getDateTime(self):
        y, m, d = UAXml.getDateYMD(self)
        h, mi, s = UAXml.getTimeHMS(self)
        ss = int(math.floor(s))
        ms = int((s - ss) * 1000000)

        dtim = datetime.datetime(y, m, d, h, mi, ss, ms)
        return dtim

    def getDate(self):
        ur = self.uaxml['ufoanalyzer_record']
        return int(ur['@y']) * 10000 + int(ur['@mo']) * 100 + int(ur['@d'])

    def getDateYMD(self):
        yr = int(self.uaxml['ufoanalyzer_record']['@y'])
        mo = int(self.uaxml['ufoanalyzer_record']['@mo'])
        dy = int(self.uaxml['ufoanalyzer_record']['@d'])
        return yr, mo, dy

    def getDateStr(self):
        ur = self.uaxml['ufoanalyzer_record']
        return f'{ur["@y"]}-{int(ur["@mo"]):02d}-{int(ur["@d"]):02d}'

    def getTime(self):
        ur = self.uaxml['ufoanalyzer_record']
        return int(ur['@h']) * 3600 + int(ur['@m']) * 60 + float(ur['@s'])

    def getTimeStr(self):
        ur = self.uaxml['ufoanalyzer_record']
        return ur['@h'] + ":" + ur['@m'] + ":" + ur['@s']

    def getTimeHMS(self):
        h = int(self.uaxml['ufoanalyzer_record']['@h'])
        m = int(self.uaxml['ufoanalyzer_record']['@m'])
        s = float(self.uaxml['ufoanalyzer_record']['@s'])
        return h, m, s

    def getCameraDetails(self):
        fps = float(self.uaxml['ufoanalyzer_record']['@fps'])
        cx = float(self.uaxml['ufoanalyzer_record']['@cx'])
        cy = float(self.uaxml['ufoanalyzer_record']['@cy'])
        isintl = int(self.uaxml['ufoanalyzer_record']['@interlaced'])
        return fps, cx, cy, isintl

    def getStationDetails(self):
        sta = self.uaxml['ufoanalyzer_record']['@lid'] + "_" + self.uaxml['ufoanalyzer_record']['@sid']
        lid = self.uaxml['ufoanalyzer_record']['@lid']
        sid = self.uaxml['ufoanalyzer_record']['@sid']
        lat = float(self.uaxml['ufoanalyzer_record']['@lat'])
        lng = float(self.uaxml['ufoanalyzer_record']['@lng'])
        alt = float(self.uaxml['ufoanalyzer_record']['@alt'])
        return sta, lid, sid, lat, lng, alt

    def getProfDetails(self):
        az = float(self.uaxml['ufoanalyzer_record']['@az'])
        ev = float(self.uaxml['ufoanalyzer_record']['@ev'])
        rot = float(self.uaxml['ufoanalyzer_record']['@rot'])
        fovh = float(self.uaxml['ufoanalyzer_record']['@vx'])
        yx = float(self.uaxml['ufoanalyzer_record']['@yx'])
        dx = float(self.uaxml['ufoanalyzer_record']['@dx'])
        dy = float(self.uaxml['ufoanalyzer_record']['@dy'])
        lnk = float(self.uaxml['ufoanalyzer_record']['@dl'])
        return az, ev, rot, fovh, yx, dx, dy, lnk

    def getObjectCount(self):
        return int(self.uaxml['ufoanalyzer_record']['@o'])

    def getObjectBasics(self, objno):
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        sec = float(uo['@sec'])
        av = float(uo['@av'])
        pix = int(uo['@pix'])
        bmax = float(uo['@bmax'])
        mag = float(uo['@mag'])
        fcount = int(uo['@sN'])
        return sec, av, pix, bmax, mag, fcount

    def getObjectStart(self, objno):
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        ra1 = uo['@ra1']
        dc1 = uo['@dc1']
        h1 = uo['@h1']
        dist1 = uo['@dist1']
        lng1 = uo['@lng1']
        lat1 = uo['@lat1']
        az1 = uo['@az1']
        ev1 = uo['@ev1']
        fs = uo['@fs']
        return ra1, dc1, h1, dist1, lng1, lat1, az1, ev1, fs

    def getObjectEnd(self, objno):
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        ra2 = uo['@ra2']
        dc2 = uo['@dc2']
        h2 = uo['@h2']
        dist2 = uo['@dist2']
        lng2 = uo['@lng2']
        lat2 = uo['@lat2']
        az2 = uo['@az2']
        ev2 = uo['@ev2']
        fe = uo['@fe']
        return ra2, dc2, h2, dist2, lng2, lat2, az2, ev2, fe

    def getObjectFrameDetails(self, objno, fno):
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        uop = uo['ua2_objpath']['ua2_fdata2'][fno]
        fno = int(uop['@fno'])
        b = int(uop['@b'])
        lsum = float(uop['@Lsum'])
        mag = float(uop['@mag'])
        az = float(uop['@az'])
        ev = float(uop['@ev'])
        ra = float(uop['@ra'])
        dec = float(uop['@dec'])
        return fno, ra, dec, mag, az, ev, lsum, b

    def getPathVector(self, objno):
        fps, _, _, isintl = UAXml.getCameraDetails(self)
        dtim = UAXml.getDateTime(self)

        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = UAXml.getObjectCount(self)
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        fcount = int(uo['@sN'])
        fs = int(uo['@fs'])
        fno = numpy.zeros(fcount)
        ra = numpy.zeros(fcount)
        dec = numpy.zeros(fcount)
        alt = numpy.zeros(fcount)
        az = numpy.zeros(fcount)
        tt = numpy.zeros(fcount)
        mag = numpy.zeros(fcount)
        b = numpy.zeros(fcount)
        lsum = numpy.zeros(fcount)
        for fc in range(fcount):
            uop = uo['ua2_objpath']['ua2_fdata2'][fc]
            fno[fc] = int(uop['@fno'])
            ra[fc] = float(uop['@ra'])
            dec[fc] = float(uop['@dec'])
            az[fc] = float(uop['@az'])
            alt[fc] = float(uop['@ev'])
            mag[fc] = float(uop['@mag'])
            b[fc] = float(uop['@b'])
            lsum[fc] = float(uop['@Lsum'])

            # UFO timestamps the first half-frame in which a detection happens and
            # the framenumber of this is stored in "fs"
            us = int((fno[fc] - fs) / fps * 1000000)
            tt[fc] = round((dtim + datetime.timedelta(microseconds=us)).timestamp(), 2)
        return fno, tt, ra, dec, mag, fcount, alt, az, b, lsum


    def makePlateParEntry(self, statid):
        """ Make a fake platepar file from the data, so it can be processed with RMS/WMPL """
        imgdt = self.getDateTime()
        _, cx, cy, _ = self.getCameraDetails()
        az, ev, _, fovh, yx, _, _, _ = self.getProfDetails()
        _, lid, sid, lat, lng, alt = self.getStationDetails()

        ff_name = 'FF_' + statid +'_'
        ff_name = ff_name + imgdt.strftime('%Y%m%d_%H%M%S_') 
        ms = '{:03d}'.format(int(imgdt.microsecond / 1000))
        ff_name = ff_name + ms + '_0000000.fits'

        fovv = fovh*(cx*yx/cy)

        ref_jd = datetime2JD(imgdt)
        ra_d, dec_d = altAz2RADec(numpy.radians(az), numpy.radians(ev), ref_jd, 
            numpy.radians(lat), numpy.radians(lng))

        pp = '"' + ff_name + '": {\n'
        pp = pp + '    "lat": {:f},\n'.format(lat)
        pp = pp + '    "lon": {:f},\n'.format(lng)
        pp = pp + '    "elev": {:f},\n'.format(alt)
        pp = pp + '    "X_res": {:d},\n'.format(int(cx))
        pp = pp + '    "Y_res": {:d},\n'.format(int(cy))
        pp = pp + '    "JD": {:.8f},\n'.format(ref_jd)
        pp = pp + '    "RA_d": {:.8f},\n'.format(numpy.degrees(ra_d))
        pp = pp + '    "dec_d": {:.8f},\n'.format(numpy.degrees(dec_d))
        pp = pp + '    "fov_h": {:f},\n'.format(fovh)
        pp = pp + '    "fov_v": {:f},\n'.format(fovv)
        pp = pp + '    "station_code": "{:s}",\n'.format(statid)
        pp = pp + '    "auto_recalibrated": true,\n'
        pp = pp + '    "az_centre": 0,\n'
        pp = pp + '    "alt_centre": 0,\n'
        pp = pp + '    "rotation_from_horiz": 0,\n'
        pp = pp + '    "pos_angle_ref": 0,\n'
        pp = pp + '    "Ho": 0,\n'
        pp = pp + '    "UT_corr": 0,\n'
        pp = pp + '    "F_scale": 0,\n'
        pp = pp + '    "version": 2\n'
        pp = pp + '}'

        return pp
