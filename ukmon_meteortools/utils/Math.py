# Various maths functions scraped from WMPL

import numpy as np
import math
from datetime import datetime, timedelta, MINYEAR
# Copyright (C) 2018-2023 Mark McIntyre

# Define Julian epoch
JULIAN_EPOCH = datetime(2000, 1, 1, 12) # J2000.0 noon
J2000_JD = timedelta(2451545) # J2000.0 epoch in julian days


def jd2Date(jd, UT_corr=0, dt_obj=False):
    """ Converts the given Julian date to (year, month, day, hour, minute, second, millisecond) tuple or a datetime.  

    Arguments:  
        jd: [float] Julian date  

    Keyword arguments:  
        UT_corr: [float] UT correction in hours (difference from local time to UT)  
        dt_obj: [bool] returns a datetime object if True. False by default.  

    Return:  
        (year, month, day, hour, minute, second, millisecond) or a datetime

    """

    try:

        dt = timedelta(days=jd)
        
        date = dt + JULIAN_EPOCH - J2000_JD + timedelta(hours=UT_corr) 

    # If the date is out of range (i.e. before year 1) use year 1. This is the limitation in the datetime
    # library. Time handling should be switched to astropy.time
    except OverflowError:
        date = datetime(MINYEAR, 1, 1, 0, 0, 0)


    # Return a datetime object if dt_obj == True
    if dt_obj:
        return date

    return date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond/1000.0


def datetime2JD(dt):
    """ Convert a datetime to a julian date  
    """

    return date2JD(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond/1000.0)


def date2JD(year, month, day, hour, minute, second, millisecond=0, UT_corr=0.0):
    """ Convert date and time to Julian Date in J2000.0.  
    
    Arguments:  
        year: [int] year  
        month: [int] month  
        day: [int] day of the date  
        hour: [int] hours  
        minute: [int] minutes  
        second: [int] seconds  

    Kwargs:  
        millisecond: [int] milliseconds (optional)  
        UT_corr: [float] UT correction in hours (difference from local time to UT)  
    
    Return:  
        [float] julian date, J2000.0 epoch  
    """

    # Convert all input arguments to integer (except milliseconds)
    year, month, day, hour, minute, second = map(int, (year, month, day, hour, minute, second))

    # Create datetime object of current time
    dt = datetime(year, month, day, hour, minute, second, int(millisecond*1000))

    # Calculate Julian date
    julian = dt - JULIAN_EPOCH + J2000_JD - timedelta(hours=UT_corr)
    
    # Convert seconds to day fractions
    return julian.days + (julian.seconds + julian.microseconds/1000000.0)/86400.0


def jd2LST(julian_date, lon):
    """ Convert Julian date to Local Sidereal Time and Greenwich Sidereal Time. The times used are apparent 
        times, not mean times.  

    Source: J. Meeus: Astronomical Algorithms  

    Arguments:  
        julian_date: [float] decimal julian date, epoch J2000.0  
        lon: [float] longitude of the observer in degrees  
    
    Return:  
        (LST, GST): [tuple of floats] a tuple of Local Sidereal Time and Greenwich Sidereal Time  
    """

    # t = (julian_date - J2000_JD.days)/36525.0

    # Greenwich Sidereal Time
    #GST = 280.46061837 + 360.98564736629*(julian_date - J2000_JD.days) + 0.000387933*t**2 - (t**3)/38710000
    #GST = (GST + 360)%360

    GST = np.degrees(calcApparentSiderealEarthRotation(julian_date))

    # Local Sidereal Time
    LST = (GST + lon + 360) % 360
    
    return LST, GST


def jd2DynamicalTimeJD(jd):
    """ Converts the given Julian date to dynamical time (i.e. Terrestrial Time, TT) Julian date. The 
        conversion takes care of leap seconds.   

    Arguments:  
        jd: [float] Julian date.  

    Return:  
        [float] Dynamical time Julian date.  
    """

    # Leap seconds as of 2017 (default)
    leap_secs = 37.0


    # Get the relevant number of leap seconds for the given JD
    # COMMENTED OUT as tai-utc.dat is empty
    #for jd_leap, ls in config.leap_seconds:
    #    
    #    if jd > jd_leap:
    #        leap_secs = ls
            

    # Calculate the dynamical JD
    jd_dyn = jd + (leap_secs + 32.184)/86400.0


    return jd_dyn


def greatCircleDistance(lat1, lon1, lat2, lon2):
    """ Calculate the great circle distance in kilometers between two points on the Earth. 
        Source: https://gis.stackexchange.com/a/56589/15183  

    Arguments:  
        lat1: [float] Latitude 1 (radians).  
        lon1: [float] Longitude 1 (radians).  
        lat2: [float] Latitude 2 (radians).  
        lon2: [float] Longitude 2 (radians).  

    Return:  
        [float]: Distance in kilometers.  
    """
    
    # Haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 

    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2*np.arcsin(np.sqrt(a))

    # Distance in kilometers.
    dist = 6371*c

    return dist


def angleBetweenSphericalCoords(phi1, lambda1, phi2, lambda2):
    """ Calculates the angle between two points on a sphere.  
    
    Arguments:  
        phi1: [float] Latitude 1 (radians).  
        lambda1: [float] Longitude 1 (radians).  
        phi2: [float] Latitude 2 (radians).  
        lambda2: [float] Longitude 2 (radians).  

    Return:  
        [float] Angle between two coordinates (radians).  
    """

    return np.arccos(np.sin(phi1)*np.sin(phi2) + np.cos(phi1)*np.cos(phi2)*np.cos(lambda2 - lambda1))


def equatorialCoordPrecession(start_epoch, final_epoch, ra, dec):
    """ Precess right Ascension and declination from one epoch to another, taking only precession into 
        account.  

        Implemented from: Jean Meeus - Astronomical Algorithms, 2nd edition, pages 134-135  
    
    Arguments:  
        start_epoch: [float] Julian date of the starting epoch  
        final_epoch: [float] Julian date of the final epoch  
        ra: [float] non-corrected right ascension in radians  
        dec: [float] non-corrected declination in radians  
    
    Return:  
        (ra, dec): [tuple of floats] precessed equatorial coordinates in radians  

    """


    T = (start_epoch - J2000_JD.days)/36525.0
    t = (final_epoch - start_epoch)/36525.0

    # Calculate correction parameters
    zeta = ((2306.2181 + 1.39656*T - 0.000139*T**2)*t + (0.30188 - 0.000344*T)*t**2 + 0.017998*t**3)/3600
    z = ((2306.2181 + 1.39656*T - 0.000139*T**2)*t + (1.09468 + 0.000066*T)*t**2 + 0.018203*t**3)/3600
    theta = ((2004.3109 - 0.85330*T - 0.000217*T**2)*t - (0.42665 + 0.000217*T)*t**2 - 0.041833*t**3)/3600

    # Convert parameters to radians
    zeta, z, theta = map(math.radians, (zeta, z, theta))

    # Calculate the next set of parameters
    A = np.cos(dec) * np.sin(ra + zeta)
    B = np.cos(theta)* np.cos(dec) * np.cos(ra + zeta) - np.sin(theta) * np.sin(dec)
    C = np.sin(theta)* np.cos(dec) * np.cos(ra + zeta) + np.cos(theta) * np.sin(dec)

    # Calculate right ascension
    ra_corr = np.arctan2(A, B) + z

    # Calculate declination (apply a different equation if close to the pole, closer then 0.5 degrees)
    if (np.pi/2 - np.abs(dec)) < np.radians(0.5):
        dec_corr = np.sign(C)*np.arccos(np.sqrt(A**2 + B**2))
    else:
        dec_corr = np.arcsin(C)

    # Wrap right ascension to [0, 2*pi] range
    ra_corr = ra_corr % (2*np.pi)

    # Wrap declination to [-pi/2, pi/2] range
    dec_corr = (dec_corr + np.pi/2) % np.pi - np.pi/2

    return ra_corr, dec_corr


equatorialCoordPrecession_vect = np.vectorize(equatorialCoordPrecession, excluded=['start_epoch'])
"""Vectorize the equatorialCoordPrecession, so ra and dec can be passed as numpy arrays"""


def raDec2AltAz(ra, dec, jd, lat, lon):
    """ Convert right ascension and declination to azimuth (+east of sue north) and altitude.  

    Arguments:  
        ra: [float] right ascension in radians  
        dec: [float] declination in radians  
        jd: [float] Julian date  
        lat: [float] latitude in radians  
        lon: [float] longitude in radians  

    Return:  
        (azim, elev): [tuple]  
            azim: [float] azimuth (+east of due north) in radians  
            elev: [float] elevation above horizon in radians  

        """

    # Calculate Local Sidereal Time
    lst = np.radians(jd2LST(jd, np.degrees(lon))[0])

    # Calculate the hour angle
    ha = lst - ra

    # Constrain the hour angle to [-pi, pi] range
    ha = (ha + np.pi) % (2*np.pi) - np.pi

    # Calculate the azimuth
    azim = np.pi + np.arctan2(np.sin(ha), np.cos(ha)*np.sin(lat) - np.tan(dec)*np.cos(lat))

    # Calculate the sine of elevation
    sin_elev = np.sin(lat)*np.sin(dec) + np.cos(lat)*np.cos(dec)*np.cos(ha)

    # Wrap the sine of elevation in the [-1, +1] range
    sin_elev = (sin_elev + 1) % 2 - 1

    elev = np.arcsin(sin_elev)

    return azim, elev


raDec2AltAz_vect = np.vectorize(raDec2AltAz, excluded=['lat', 'lon'])
"""Vectorize the raDec2AltAz function so it can take numpy arrays for: ra, dec, jd"""


def altAz2RADec(azim, elev, jd, lat, lon):
    """ Convert azimuth and altitude in a given time and position on Earth to right ascension and 
        declination.   

    Arguments:  
        azim: [float] azimuth (+east of due north) in radians  
        elev: [float] elevation above horizon in radians  
        jd: [float] Julian date  
        lat: [float] latitude of the observer in radians  
        lon: [float] longitde of the observer in radians  

    Return:  
        (RA, dec): [tuple]  
            RA: [float] right ascension (radians)  
            dec: [float] declination (radians)  
    """
    
    # Calculate hour angle
    ha = np.arctan2(-np.sin(azim), np.tan(elev)*np.cos(lat) - np.cos(azim)*np.sin(lat))

    # Calculate Local Sidereal Time
    lst = np.radians(jd2LST(jd, np.degrees(lon))[0])
    
    # Calculate right ascension
    ra = (lst - ha) % (2*np.pi)

    # Calculate declination
    dec = np.arcsin(np.sin(lat)*np.sin(elev) + np.cos(lat)*np.cos(elev)*np.cos(azim))

    return ra, dec


altAz2RADec_vect = np.vectorize(altAz2RADec, excluded=['lat', 'lon'])
""" Vectorize the altAz2RADec function so it can take numpy arrays for: azim, elev, jd """


def calcApparentSiderealEarthRotation(julian_date):
    """ Calculate apparent sidereal rotation GST of the Earth.  
        
        Calculated according to:  
        Clark, D. L. (2010). Searching for fireball pre-detections in sky surveys. The School of Graduate and 
        Postdoctoral Studies. University of Western Ontario, London, Ontario, Canada, MSc Thesis.  

    """

    t = (julian_date - J2000_JD.days)/36525.0

    # Calculate the Mean sidereal rotation of the Earth in radians (Greenwich Sidereal Time)
    GST = 280.46061837 + 360.98564736629*(julian_date - J2000_JD.days) + 0.000387933*t**2 - (t**3)/38710000
    GST = (GST + 360) % 360
    GST = math.radians(GST)

    # print('GST:', np.degrees(GST), 'deg')

    # Calculate the dynamical time JD
    jd_dyn = jd2DynamicalTimeJD(julian_date)


    # Calculate Earth's nutation components
    delta_psi, delta_eps = calcNutationComponents(jd_dyn)

    # print('Delta Psi:', np.degrees(delta_psi), 'deg')
    # print('Delta Epsilon:', np.degrees(delta_eps), 'deg')


    # Calculate the mean obliquity (in arcsec)
    u = (jd_dyn - 2451545.0)/3652500.0
    eps0 = 84381.448 - 4680.93*u - 1.55*u**2 + 1999.25*u**3 - 51.38*u**4 - 249.67*u**5 - 39.05*u**6 \
        + 7.12*u**7 + 27.87*u**8 + 5.79*u**9 + 2.45*u**10

    # Convert to radians
    eps0 /= 3600
    eps0 = np.radians(eps0)

    # print('Mean obliquity:', np.degrees(eps0), 'deg')

    # Calculate apparent sidereal Earth's rotation
    app_sid_rot = (GST + delta_psi*math.cos(eps0 + delta_eps)) % (2*math.pi)

    return app_sid_rot


def calcNutationComponents(jd_dyn):
    """ Calculate Earth's nutation components from the given Julian date.  

    Source: Meeus (1998) Astronomical algorithms, 2nd edition, chapter 22.  
    
    The precision is limited to 0.5" in nutation in longitude and 0.1" in nutation in obliquity. The errata 
    for the 2nd edition was used to correct the equation for delta_psi.
    
    Arguments:  
        jd_dyn: [float] Dynamical Julian date. See wmpl.Utils.TrajConversions.jd2DynamicalTimeJD function.  

    Return:  
        (delta_psi, delta_eps): [tuple of floats] Differences from mean nutation due to the influence of
            the Moon and minor effects (radians).  
    """


    T = (jd_dyn - J2000_JD.days)/36525.0

    # # Mean Elongation of the Moon from the Sun
    # D = 297.85036 + 445267.11148*T - 0.0019142*T**2 + (T**3)/189474

    # # Mean anomaly of the Earth with respect to the Sun
    # M = 357.52772 + 35999.05034*T - 0.0001603*T**2 - (T**3)/300000

    # # Mean anomaly of the Moon
    # Mm = 134.96298 + 477198.867398*T + 0.0086972*T**2 + (T**3)/56250

    # # Argument of latitude of the Moon
    # F = 93.27191  + 483202.017538*T - 0.0036825*T**2 + (T**3)/327270


    # Longitude of the ascending node of the Moon's mean orbit on the ecliptic, measured from the mean equinox
    # of the date
    omega = 125.04452 - 1934.136261*T


    # Mean longitude of the Sun (deg)
    L = 280.4665 + 36000.7698*T

    # Mean longitude of the Moon (deg)
    Ll = 218.3165 + 481267.8813*T


    # Nutation in longitude
    delta_psi = -17.2*math.sin(math.radians(omega)) - 1.32*math.sin(np.radians(2*L)) \
        - 0.23*math.sin(math.radians(2*Ll)) + 0.21*math.sin(math.radians(2*omega))

    # Nutation in obliquity
    delta_eps = 9.2*math.cos(math.radians(omega)) + 0.57*math.cos(math.radians(2*L)) \
        + 0.1*math.cos(math.radians(2*Ll)) - 0.09*math.cos(math.radians(2*omega))


    # Convert to radians
    delta_psi = np.radians(delta_psi/3600)
    delta_eps = np.radians(delta_eps/3600)

    return delta_psi, delta_eps
