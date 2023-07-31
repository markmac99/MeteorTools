# test the RMS and WMPL utils in the library

import os
from rmsutils import multiEventGroundMap
from rmsutils import plotCAMSOrbits, plotRMSOrbits

here = os.path.split(os.path.abspath(__file__))[0]


def test_multiEventGroundMapLyrOneStation():
    startdt = '20230421'
    enddt = '20230423'
    statid = 'UK0006'
    outdir = os.path.join(here, 'data')
    multiEventGroundMap(startdt, enddt, statid=statid, shwr='LYR', outdir=outdir)
    assert os.path.isfile(os.path.join(outdir, '20230421-20230423-LYR-UK0006.jpg'))
    os.remove(os.path.join(outdir, '20230421-20230423-LYR-UK0006.jpg'))
    

def test_multiEventGroundMapLyrAllStats():
    startdt = '20230421'
    enddt = '20230423'
    statid = None 
    outdir = os.path.join(here, 'data')
    multiEventGroundMap(startdt, enddt, statid=statid, shwr='LYR', outdir=outdir)
    assert os.path.isfile(os.path.join(outdir, '20230421-20230423-LYR-None.jpg'))
    os.remove(os.path.join(outdir, '20230421-20230423-LYR-None.jpg'))
    

def test_multiEventGroundMapAllAllStats():
    startdt = '20230421'
    enddt = '20230423'
    statid = None 
    outdir = os.path.join(here, 'data')
    multiEventGroundMap(startdt, enddt, statid=statid, shwr=None, outdir=outdir)
    assert os.path.isfile(os.path.join(outdir, '20230421-20230423-None-None.jpg'))
    os.remove(os.path.join(outdir, '20230421-20230423-None-None.jpg'))


def test_plotCAMSOrbits():
    camsfile = os.path.join(here, 'data', 'sampleCAMSdata.txt')
    outdir = os.path.join(here, 'data')
    plotCAMSOrbits(camsfile, outdir, True)
    assert os.path.isfile(os.path.join(outdir, 'CAMS_2021-06-16T04-00-41.png'))
    os.remove(os.path.join(outdir, 'CAMS_2021-06-16T04-00-41.png'))


def test_plotRMSOrbits():
    rmsfile = os.path.join(here, 'data', 'sampleRMSdata.txt')
    outdir = os.path.join(here, 'data')
    plotRMSOrbits(rmsfile, outdir, True)
    assert os.path.isfile(os.path.join(outdir, 'RMS_2021-06-16T04-00-41.png'))
    os.remove(os.path.join(outdir, 'RMS_2021-06-16T04-00-41.png'))
