# Copyright (C) 2018-2023 Mark McIntyre
#
# simple script to get the active shower list from the IMO working list

import datetime

from ukmon_meteortools.fileformats import imoWorkingShowerList as iwsl


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
    mtch = sl.getShowerByCode(shwr)
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
