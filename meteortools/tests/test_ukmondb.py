import os
import boto3
import datetime
import shutil

from ukmondb import matchApiCall, detailApiCall1, detailApiCall2
from ukmondb import getLiveimageList, getFireballFiles, getMatchPickle
from ukmondb import createTxtFile, getFBfiles, getLiveJpgs
from ukmondb import trajectoryKML, getECSVs, trajectoryAPI, getDetections
from ukmondb import getTrajPickle


here = os.path.split(os.path.abspath(__file__))[0]


def test_matchapicall():
    reqtyp = 'matches'
    reqval = '20211121'
    df = matchApiCall(reqtyp, reqval)
    assert df.head(1).orbname[0] != 59539.1405057791


def test_detailapicall1():
    reqtyp = 'detail'
    reqval = '20211121_032219.699_UK'
    evtlist = detailApiCall1(reqtyp, reqval)
    assert evtlist._mjd != 59539.1405057791


def test_detailapicall2():
    reqtyp = 'matches'
    reqval = '20211121'
    matchlist = matchApiCall(reqtyp, reqval)

    reqtyp = 'detail'
    df = detailApiCall2(reqtyp, matchlist)
    assert df.head(1)._mjd[0] != 59539.1405057791


def test_trajectoryAPI():
    traj = '20230213_025913.678_UK'
    retval = trajectoryAPI(traj)
    assert retval is not None


def test_getMatchPickle():
    patt = '20230501_002536.754_UK'
    pf = getMatchPickle(patt)
    assert pf['file_name'] == '20230501_002536'


def test_getLiveImages():
    dtstr = '20230506_0250'
    lst = getLiveimageList(dtstr)
    assert len(lst) == 3


def test_getFireballFiles():
    patt = 'UK0006_20230421_2122'
    fblist = getFireballFiles(patt)
    assert len(fblist) > 0


def test_createTxtFile():
    patt = 'FF_UK0006_20230506_210101'
    outdir = os.path.join(here,'data')
    createTxtFile(patt, outdir)
    outfname = os.path.join(outdir, 'uk0006.txt')
    assert os.path.isfile(outfname)
    os.remove(outfname)


def test_createTxtFileHere():
    patt = 'FF_UK0006_20230506_210101'
    outdir = None
    createTxtFile(patt, outdir)
    outfname = 'uk0006.txt'
    assert os.path.isfile(outfname)
    os.remove(outfname)


def test_createTxtFileMtype():
    patt = 'M20230506_210101_foobar_UK0007'
    outdir = os.path.join(here,'data')
    createTxtFile(patt, outdir)
    outfname = os.path.join(outdir, 'uk0007.txt')
    assert os.path.isfile(outfname)
    os.remove(outfname)


def test_trajectoryKML():
    orbname = '20230202_014115.520_UK'
    outdir = os.path.join(here, 'data')
    trajectoryKML(orbname, outdir)
    newf = open(os.path.join(outdir,'20230202_014115.520_UK.kml')).readlines()
    assert len(newf) == 246
    assert newf[3].split('<')[1] == 'name>20230202_014115.520_UK'
    os.remove(os.path.join(outdir,'20230202_014115.520_UK.kml'))


def test_getECSVs():
    ecsv = getECSVs('UK0006','2023-05-02T00:25:59')
    assert ecsv[0] == "# %ECSV 0.9"


def test_getECSVsSave():
    outdir = os.path.join(here, 'data')
    ecsv = getECSVs('UK0006','2023-05-02T00:25:59', savefiles=True, outdir=outdir)
    assert ecsv[0] == "# %ECSV 0.9"
    assert os.path.isfile(os.path.join(outdir, '2023-05-02T00_25_59.ecsv'))
    os.remove(os.path.join(outdir, '2023-05-02T00_25_59.ecsv'))


def test_getECSVsMulti():
    outdir = os.path.join(here, 'data')
    ecsv = getECSVs('UK0025','2023-05-04T02:16:27', savefiles=True, outdir=outdir)
    assert ecsv[0] == "# %ECSV 0.9"
    assert os.path.isfile(os.path.join(outdir, '2023-05-04T02_16_27_M003.ecsv'))
    os.remove(os.path.join(outdir, '2023-05-04T02_16_27_M001.ecsv'))
    os.remove(os.path.join(outdir, '2023-05-04T02_16_27_M002.ecsv'))
    os.remove(os.path.join(outdir, '2023-05-04T02_16_27_M003.ecsv'))


def test_getDetections():
    ret = getDetections('20230508_0132')
    assert ret['ID'][0] == 'UK007H'


def test_getTrajPickle():
    traj = getTrajPickle('20230502_025228.374_UK_BE')
    assert len(traj.observations) == 17


def test_getTrajPickleNonExistent():
    traj = getTrajPickle('20230502_025228.374_UK_XX')
    assert traj is None


def test_getLiveJpgs():
    s3 = boto3.client('s3')
    dtstr = datetime.datetime.now().strftime('%Y%m%d')
    x = s3.list_objects_v2(Bucket='ukmon-live',Prefix=f'M{dtstr}')
    if x['KeyCount'] > 0:
        fname = x['Contents'][0]['Key']
        dtstr = fname[1:16]
    else:
        dtstr = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y%m%d')
        x = s3.list_objects_v2(Bucket='ukmon-live',Prefix=f'M{dtstr}')
        fname = x['Contents'][0]['Key']
        dtstr = fname[1:16]

    outdir = os.path.join(here, 'data')
    getLiveJpgs(dtstr, outdir=outdir, create_txt=False)
    outfj = os.path.join(outdir, fname).replace('.xml','P.jpg')
    assert os.path.isfile(outfj)
    assert os.path.isfile(os.path.join(outdir, fname))
    os.remove(outfj)
    os.remove(os.path.join(outdir, fname))


def test_getLiveJpgsNonExistent():
    key = os.getenv('AWS_ACCESS_KEY_ID', default='notset')
    if key != 'notset':
        x = getLiveJpgs('20000101_000000', outdir=None, create_txt=False)
        assert x is None
    else:
        assert 1==1


def test_getFBfiles():
    outdir = os.path.join(here, 'data', 'tmp')
    res = getFBfiles('UK0006_20230421_2120', outdir)
    assert res['filename'][0] == 'platepar_cmn2010.cal'
    assert os.path.isfile(os.path.join(outdir, 'platepar_cmn2010.cal'))
    shutil.rmtree(outdir)
