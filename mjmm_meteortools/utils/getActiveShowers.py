# Copyright (C) 2018-2023 Mark McIntyre
#
# simple script to get the active shower list from the IMO working list

from ukmon_meteortools.fileformats import imoWorkingShowerList as iwsl
import datetime


def getActiveShowers(targdate, retlist=False, inclMinor=False):
    """
    Return a list of showers active at the specified date  

    Arguments:  
        targdate:   [str] Date in YYYYMMDD format  

    Keyword Arguments:  
        retlist:    [bool] return a list, or print to console. Default False=print  
        inclMinor:  [bool] include minor showers or only return major showers  

    Returns:  
        If retlist is true, returns a python list of shower short-codes eg ['PER','LYR']  

    """
    sl = iwsl.IMOshowerList()
    testdate = datetime.datetime.strptime(targdate, '%Y%m%d')
    listofshowers=sl.getActiveShowers(testdate, True, inclMinor=inclMinor)
    if retlist is False:
        for shwr in listofshowers:
            print(shwr)
    else:
        return listofshowers


def getActiveShowersStr(targdatestr):
    """
    Prints a comma-separated list of showers active at the specified date  

    Arguments:  
        targdate:   [str] Date in YYYYMMDD format  

    Returns:  
        nothing  

    """
    shwrs = getActiveShowers(targdatestr, retlist=True)
    shwrs.append('spo')
    for s in shwrs:
        print(s)
