# Python class to parse a UFOCapture XML files
#
# disable some linter warnings
# Copyright (C) 2018-2023 Mark McIntyre

import xmltodict
import numpy


class UCXml:
    """ Load and manage a UFOCapture XML file containing potential detections """
    MAXGAP = 50

    def setMaxGap(self, mg):
        self.MAXGAP = mg

    def __init__(self, fname):
        """ Construct a UCXML object from fname """
        with open(fname) as fd:
            self.ucxml = xmltodict.parse(fd.read())

    def getDate(self):
        ur = self.ucxml['ufocapture_record']
        return int(ur['@y']) * 10000 + int(ur['@mo']) * 100 + int(ur['@d'])

    def getDateYMD(self):
        yr = int(self.ucxml['ufocapture_record']['@y'])
        mo = int(self.ucxml['ufocapture_record']['@mo'])
        dy = int(self.ucxml['ufocapture_record']['@d'])
        return yr, mo, dy

    def getDateStr(self):
        ur = self.ucxml['ufocapture_record']
        return ur['@y'] + "-" + ur['@mo'] + "-" + ur['@d']

    def getTime(self):
        ur = self.ucxml['ufocapture_record']
        return int(ur['@h']) * 3600 + int(ur['@m']) * 60 + float(ur['@s'])

    def getTimeStr(self):
        ur = self.ucxml['ufocapture_record']
        return ur['@h'] + ":" + ur['@m'] + ":" + ur['@s']

    def getTimeHMS(self):
        h = int(self.ucxml['ufocapture_record']['@h'])
        m = int(self.ucxml['ufocapture_record']['@m'])
        s = float(self.ucxml['ufocapture_record']['@s'])
        return h, m, s

    def getCameraDetails(self):
        fps = float(self.ucxml['ufocapture_record']['@fps'])
        cx = float(self.ucxml['ufocapture_record']['@cx'])
        cy = float(self.ucxml['ufocapture_record']['@cy'])
        return fps, cx, cy

    def getStationDetails(self):
        sta = self.ucxml['ufocapture_record']['@lid'] + "_" + self.ucxml['ufocapture_record']['@sid']
        lid = self.ucxml['ufocapture_record']['@lid']
        sid = self.ucxml['ufocapture_record']['@sid']
        lat = float(self.ucxml['ufocapture_record']['@lat'])
        lng = float(self.ucxml['ufocapture_record']['@lng'])
        alt = float(self.ucxml['ufocapture_record']['@alt'])
        return sta, lid, sid, lat, lng, alt

    def getHits(self):
        uc = self.ucxml['ufocapture_record']['ufocapture_paths']
        return int(uc['@hit'])

    def getNumObjs(self):
        try:
            uc = self.ucxml['ufocapture_record']['ufocapture_paths']
        except:
            return 0, None
        nhits = int(uc['@hit'])
        objlist = numpy.zeros(nhits)
        nobjs = 0
        for i in range(nhits):
            if nhits == 1:
                p = uc['uc_path']
            else:
                p = uc['uc_path'][i]
            ono = int(p['@ono'])
            if ono not in objlist:
                objlist[nobjs] = ono
                nobjs = nobjs + 1
        objlist = numpy.resize(objlist, nobjs)
        return nobjs, objlist

    def getPath(self):
        try:
            uc = self.ucxml['ufocapture_record']['ufocapture_paths']
        except:
            # print('xml file not valid - no ufocapture_paths')
            pathx = numpy.zeros(1)
            pathy = numpy.zeros(1)
            bri = numpy.zeros(1)
            return pathx, pathy, bri, 0
        nhits = int(uc['@hit'])
        pathx = numpy.zeros(nhits)
        pathy = numpy.zeros(nhits)
        bri = numpy.zeros(nhits)
        if nhits < 2:
            return pathx, pathy, bri, 0
        lastono = 0
        for i in range(nhits):
            p = uc['uc_path'][i]
            ono = int(p['@ono'])
            # its possible for one path to include two events
            # at different times. This is a UFO feature...
            if lastono > 0 and lastono != ono:
                pathx = numpy.resize(pathx, i)
                pathy = numpy.resize(pathy, i)
                bri = numpy.resize(bri, i)
                return pathx, pathy, bri, i
            lastono = ono
            pathx[i] = p['@x']
            pathy[i] = p['@y']
            bri[i] = p['@bmax']
        return pathx, pathy, bri, 0

    def getPathv2(self, objno):
        try:
            uc = self.ucxml['ufocapture_record']['ufocapture_paths']
        except:
            pathx = numpy.zeros(1)
            pathy = numpy.zeros(1)
            bri = numpy.zeros(1)
            pxls = numpy.zeros(1)
            fnos = numpy.zeros(1)
            return pathx, pathy, bri, pxls, fnos
        pfno = 0  # previous frame number, to check for unrealistic gaps in trails
        fno = 0  # current frame number, to check for unrealistic gaps in trails
        nhits = int(uc['@hit'])
        pathx = numpy.zeros(nhits)
        pathy = numpy.zeros(nhits)
        bri = numpy.zeros(nhits)
        pxls = numpy.zeros(nhits)
        fnos = numpy.zeros(nhits)
        j = 0
        for i in range(nhits):
            if nhits == 1:
                p = uc['uc_path']
            else:
                p = uc['uc_path'][i]
            ono = int(p['@ono'])
            # npx = int(p['@pixel'])
            fno = int(p['@fno'])
            if pfno == 0:
                pfno = fno
            #fdiff = fno - pfno
            if ono == objno:  # and fdiff < self.MAXGAP:  # and npx > 3:
                # its possible for one path to include two events
                # at different times. This is a UFO feature...
                pathx[j] = p['@x']
                pathy[j] = p['@y']
                bri[j] = p['@bmax']
                pxls[j] = p['@pixel']
                fnos[j] = p['@fno']
                j = j + 1
        if j > 0:
            pathx = numpy.resize(pathx, j)
            pathy = numpy.resize(pathy, j)
            bri = numpy.resize(bri, j)
            pxls = numpy.resize(pxls, j)
            fnos = numpy.resize(fnos, j)
        else:
            pathx = numpy.zeros(1)
            pathy = numpy.zeros(1)
            bri = numpy.zeros(1)
            pxls = numpy.zeros(1)
            fnos = numpy.zeros(1)
        return pathx, pathy, bri, pxls, fnos

    def getPathElement(self, fno):
        uc = self.ucxml['ufocapture_record']['ufocapture_paths']
        pth = uc['uc_path'][fno]
        return pth['@fno'], pth['@ono'], pth['@pixel'], pth['@bmax'], pth['@x'], pth['@y']
