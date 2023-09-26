#
# Example showing how to use the matchdata API from Python
#
# Copyright (C) 2018-2023 Mark McIntyre

"""
Examples showing how to use the APIs. 
"""
import pandas as pd


def getMatchesForDate(dtstr):
    """get names of all matches for a given date 
    
    Arguments:  
        dtstr:   [string] date in YYYYMMDD format

    Returns:
        list of matches for that date

    """
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    apicall = f'{apiurl}?reqtyp=matches&reqval={dtstr}'
    matchlist = pd.read_json(apicall, lines=True)
    return matchlist


def getDetailsOfMatch(eventstr):
    """ get details of one matched event 
    
    Arguments:  
        dtstr:   [string] event name eg 20230826_000424.273_UK

    Returns:
        pandas series containing the event details

    """
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    apicall = f'{apiurl}?reqtyp=detail&reqval={eventstr}'
    evtdetail = pd.read_json(apicall, typ='series')
    return evtdetail


def getDetailOfMatchList(matchlist):
    """
    get details for multiple events 
    
    Arguments:  
        matchlist:   [list] list of matched events as returned by getMatchesForDate

    Returns:
        pandas dataframe containing the event details

    """
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    details = []
    for id in matchlist.orbname:
        reqval = id
        apicall = f'{apiurl}?reqtyp=detail&reqval={reqval}'
        details.append(pd.read_json(apicall, typ='series'))
    df = pd.DataFrame(details)
    df = df.sort_values(by=['_mag'])
    return df
