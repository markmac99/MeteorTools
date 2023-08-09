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

from ..ukmondb.getLiveImages import _download


def getTrajPickle(trajname):
    """ Retrieve a the pickled trajectory for a matched detection 
    
    Arguments:  
        trajname:   [string] Name of the trajectory eg 20230502_025228.374_UK_BE

    Returns:
        WMPL traj object

    Notes:
        WMPL must be in the $PYTHONPATH for this function to be available

    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
    fmt = 'pickle'
    apicall = f'{apiurl}?reqval={trajname}&format={fmt}'
    matchpickle = pd.read_json(apicall, lines=True)
    if 'url' in matchpickle:
        outdir = tempfile.mkdtemp()
        _download(matchpickle.url[0], outdir, matchpickle.filename[0])

        localfile = os.path.join(outdir, matchpickle.filename[0])
        with open(localfile, 'rb') as f:
            traj = pickle.load(f, encoding='latin1')
        try:
            os.remove(localfile)
        except:
            print(f'unable to remove {localfile}')
    else:
        traj = None
    return traj
