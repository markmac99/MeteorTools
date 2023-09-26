# Copyright (C) 2018-2023 Mark McIntyre
import pickle
import tempfile
import pandas as pd
import os
# imports are required to load the picklefiles
try:
    from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced, DatabaseJSON # noqa: F401
    from wmpl.Trajectory.CorrelateRMS import MeteorObsRMS, PlateparDummy, MeteorPointRMS # noqa: F401
except:
    print('WMPL not available')

try:
    from ..ukmondb.getLiveImages import _download
except Exception:
    from meteortools.ukmondb.getLiveImages import _download


def getTrajPickle(trajname, outdir=None):
    """ Retrieve a the pickled trajectory for a matched detection 
    
    Arguments:  
        trajname:   [string] Name of the trajectory eg 20230502_025228.374_UK_BE
        outdir:     [string] default None. Where to save the pickle. 

    Returns:
        WMPL traj object

    Notes:
        WMPL must be in the $PYTHONPATH for this function to be available

    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
    fmt = 'pickle'
    apicall = f'{apiurl}?reqval={trajname}&format={fmt}'
    matchpickle = pd.read_json(apicall, lines=True)
    if outdir is None:
        outdir = tempfile.mkdtemp()
        saveme = False
    else:
        saveme = True
    if 'url' in matchpickle:
        _download(matchpickle.url[0], outdir, matchpickle.filename[0])
        localfile = os.path.join(outdir, matchpickle.filename[0])
        with open(localfile, 'rb') as f:
            traj = pickle.load(f, encoding='latin1')
        if saveme is False:
            try:
                os.remove(localfile)
            except:
                print(f'unable to remove {localfile}')
    else:
        traj = None
    return traj
