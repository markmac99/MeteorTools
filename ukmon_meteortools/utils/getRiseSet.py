# Copyright (C) 2018-2023 Mark McIntyre
#
import ephem


def getNextRiseSet(lati, longi, elev, fordate=None):
    """ Calculate the next rise and set times for a given lat, long, elev  

    Paramters:  
        lati:   [float] latitude in degrees  
        longi:  [float] longitude in degrees (+E)  
        elev:   [float] latitude in metres  
        fordate:[datetime] date to calculate for, today if none

    Returns:  
        rise, set:  [date tuple] next rise and set as datetimes  

    Note that set may be earlier than rise, if you're invoking the function during daytime.  

    """
    obs = ephem.Observer()
    obs.lat = float(lati) / 57.3 # convert to radians, close enough for this
    obs.lon = float(longi) / 57.3
    obs.elev = float(elev)
    obs.horizon = -6.0 / 57.3 # degrees below horizon for darkness
    if fordate is not None:
        obs.date = fordate

    sun = ephem.Sun()
    rise = obs.next_rising(sun).datetime()
    set = obs.next_setting(sun).datetime()
    return rise, set
