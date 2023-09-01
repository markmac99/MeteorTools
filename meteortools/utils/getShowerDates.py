# Copyright (C) 2018-2023 Mark McIntyre
#
# simple script to get the active shower list from the IMO working list

import datetime
import os
import numpy as np

from ..fileformats import imoWorkingShowerList as iwsl


def getShowerDets(shwr, stringFmt=False, dataPth=None):
    """ Get details of a shower 
    
    Arguments:  
        shwr:   [string] three-letter shower code eg PER  
    Keyword Arguments:
        stringFmt [bool] default False, return a string rather than a list
        dataPth   [string] path to the datafiles. Default None means data read from internal files. 
         
    Returns:  
        (id, full name, peak solar longitude, peak date mm-dd)  
    """
    sl = iwsl.IMOshowerList()
    mtch = sl.getShowerByCode(shwr, useFull=True)
    if len(mtch) > 0 and mtch['@id'] is not None:
        id = int(mtch['@id'])
        nam = mtch['name']
        pkdtstr = mtch['peak']
        dt = datetime.datetime.now()
        yr = dt.year
        pkdt = datetime.datetime.strptime(f'{yr} {pkdtstr}','%Y %b %d')
        dtstr = pkdt.strftime('%m-%d')
        pksollong = mtch['pksollon']
    else:
        id, nam, pksollong, dtstr = 0, 'Unknown', 0, 'Unknown'
    if stringFmt:
        return f"{pksollong},{dtstr},{nam},{shwr}"
    else:
        return id, nam, pksollong, dtstr


def getShowerPeak(shwr):
    """ Get date of a shower peak in MM-DD format
    
    Arguments:  
        shwr:   [string] three-letter shower code eg PER  
         
    Returns:  
        peak date mm-dd  
    """
    _, _, _, pk = getShowerDets(shwr)
    return pk


def numpifyShowerData():
    """Refresh the numpy versions of the shower data files """
    abs_path = os.getenv('WMPL_LOC', default='/home/ec2-user/src/WesternMeteorPyLib')
    iau_shower_table_file = os.path.join(abs_path, 'wmpl', 'share', 'streamfulldata.csv')
    iau_shower_table_npy = os.path.join(abs_path, 'wmpl', 'share', 'streamfulldata.npy')
    iau_shower_list = np.loadtxt(iau_shower_table_file, delimiter="|", usecols=range(20), dtype=str)
    np.save(iau_shower_table_npy, iau_shower_list)

    gmn_shower_table_file = os.path.join(abs_path, 'wmpl', 'share', 'gmn_shower_table_20230518.txt')
    gmn_shower_table_npy = os.path.join(abs_path, 'wmpl', 'share', 'gmn_shower_table_20230518.npy')
    gmn_shower_list = _loadGMNShowerTable(*os.path.split(gmn_shower_table_file))
    np.save(gmn_shower_table_npy, gmn_shower_list)


def _loadGMNShowerTable(dir_path, file_name):
    gmn_shower_list = []
    with open(os.path.join(dir_path, file_name), encoding='cp1252') as f:
        for line in f:
            if line.startswith('#'):
                continue
            line = line.strip()
            line = line.replace('\n', '').replace('\r', '')
            if not line:
                continue
            la_sun, L_g, B_g, v_g, dispersion, IAU_no, IAU_code = line.split()
            gmn_shower_list.append([
                np.radians(float(la_sun)), 
                np.radians(float(L_g)),
                np.radians(float(B_g)), 
                1000*float(v_g), 
                np.radians(float(dispersion)), 
                int(IAU_no)]
            )
    return np.array(gmn_shower_list)
