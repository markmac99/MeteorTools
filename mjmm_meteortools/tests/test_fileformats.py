from fileformats import filterFTPforSpecificTime
from fileformats import IMOshowerList, majorlist, minorlist
from fileformats import loadPlatepars
from fileformats import UAXml, UCXml
from fileformats import readCameraKML, trackCsvtoKML, trackKMLtoCsv #, getTrackDetails

import shutil
import filecmp
import os
import datetime
import json

here = os.path.split(os.path.abspath(__file__))[0]


# loadFTPDetectInfo and writeNewFTPFile are also tested by this
def test_filterFTPforSpecificTime():
    srcftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt.orig')
    ftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt')
    oldftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt.old')
    shutil.copy(srcftpfile, ftpfile)
    dtstr = '20230112_210240'
    newname, nummets = filterFTPforSpecificTime(ftpfile, dtstr)
    print(newname)
    assert nummets == 1
    assert filecmp.cmp(oldftpfile, srcftpfile) is True
    lis = open(newname, 'r').readlines()
    assert lis[0] == 'Meteor Count = 000001\n'
    os.remove(ftpfile)
    os.remove(oldftpfile)
    

def test_IMOShowerList():
    iwsl = IMOshowerList()
    shwr = iwsl.getShowerByCode('PER')
    assert shwr['IAU_code'] == 'PER'


def test_MajMin():
    assert majorlist[0] == 'QUA'
    assert minorlist[0] == 'SPE'
    

def test_loadPlatepars():
    fldr = os.path.join(here, 'data')
    pps = loadPlatepars(fldr)
    assert pps['UK0006']['station_code'] == 'UK0006'


def test_loadUFOCapFormat():
    uc = UCXml(os.path.join(here, 'data', 'ucexample.xml'))
    sta, lid, sid, lat, lng, alt = uc.getStationDetails()
    assert sta == 'TACKLEY_TC'
    nhits = uc.getHits()
    assert nhits == 22
    fno, ono, pixel, bmax, x, y = uc.getPathElement(1)
    assert fno == '30'
    assert uc.getDate() == 20210317
    assert uc.getDateStr() == '2021-03-17'
    assert uc.getDateYMD() == (2021,3,17)
    assert abs(uc.getTime() - 85339.34) < 0.01
    assert uc.getTimeStr() == '23:42:19.34'
    assert uc.getTimeHMS() == (23,42,19.34)
    fps, cx, cy = uc.getCameraDetails()
    assert fps == 25
    nobjs, objlist = uc.getNumObjs()
    assert nobjs == 2
    pathx, pathy, bri, _ = uc.getPath()
    assert bri[0] == 73
    assert bri[-1] == 172

    pathx, pathy, bri, pxls, fnos = uc.getPathv2(19)
    assert bri[0] == 73
    assert bri[-1] == 172
    fno, ono, pixel, bmax, x, y = uc.getPathElement(0)
    assert int(fno) == 30
    assert int(bmax) == 73



def test_loadUFOAnalyserFormat():
    ua = UAXml(os.path.join(here, 'data', 'uaexample.xml'))
    fps, cx, cy, isintl = ua.getCameraDetails()
    assert fps == 25.0
    assert ua.getObjectCount() == 1
    sec, av, pix, bmax, mag, fcount = ua.getObjectBasics(1)
    assert abs(sec - 0.78) < 0.001
    assert fcount == 40
    assert abs(bmax - 213.0) < 0.1
    assert abs(mag - (-2.66)) < 0.01
    fno, ra, dec, mag, az, ev, lsum, b = ua.getObjectFrameDetails(1, 3)
    assert fno == 61
    assert b == 138
    assert ua.getDateTime() == datetime.datetime(2021, 3, 17, 23, 42, 19, 339999)
    assert ua.getDate() == 20210317
    assert ua.getDateStr() == '2021-03-17'
    assert abs(ua.getTime() - 85339.34) < 0.01
    assert ua.getTimeStr() == '23:42:19.340000'
    assert ua.getTimeHMS() == (23,42,19.34)
    sta, lid, sid, lat, lng, alt = ua.getStationDetails()
    assert sta =='TACKLEY_TC'
    az, ev, rot, fovh, yx, dx, dy, lnk = ua.getProfDetails()
    assert abs(fovh - 70.468361) < 0.001
    assert abs(az - 325.378082) < 0.001
    ra1, dc1, h1, dist1, lng1, lat1, az1, ev1, fs = ua.getObjectStart(1)
    assert abs(float(ra1) - 131.886932) < 0.001
    assert int(fs) == 58
    ra1, dc1, h1, dist1, lng1, lat1, az1, ev1, fs = ua.getObjectEnd(1)
    assert abs(float(ra1) - 121.012169) < 0.001
    assert int(fs) == 97
    fno, tt, ra, dec, mag, fcount, alt, az, b, lsum = ua.getPathVector(1)
    assert len(fno) == fcount
    assert fno[0] == 58
    pp = ua.makePlateParEntry('UK123456')
    jsdata = json.loads('{'+pp+'}')
    assert jsdata['FF_UK123456_20210317_234219_339_0000000.fits']['station_code'] == 'UK123456'


def test_readCameraKML():
    kmlfile = os.path.join(here, 'data','UK0006-70km.kml')
    kml = readCameraKML(kmlfile, True)
    assert kml[0]=='UK0006'


def test_trackCsvtoKML():
    srcfile = os.path.join(here, 'data','sample_track.csv')
    kml = trackCsvtoKML(srcfile)
    assert 'sample_track' in kml.document.name 
    os.remove(os.path.join(here, 'data','sample_track.kml'))


def test_trackKMLtoCsvSave():
    srcfile = os.path.join(here, 'data','sample_track2.kml')
    df = trackKMLtoCsv(srcfile)
    assert abs(df['lats'][0] - 49.922338) < 0.0001
    assert os.path.isfile(os.path.join(here, 'data','sample_track2.csv'))
    os.remove(os.path.join(here, 'data','sample_track2.csv'))


def test_trackKMLtoCsvNoSave():
    srcfile = os.path.join(here, 'data','sample_track2.kml')
    df = trackKMLtoCsv(srcfile, saveOutput=False)
    assert abs(df['lats'][0] - 49.922338) < 0.0001
