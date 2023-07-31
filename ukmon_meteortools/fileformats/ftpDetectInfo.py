#
# Load an FTPdetectInfo file - copied from RMS
#
# Copyright (C) 2018-2023 Mark McIntyre

import os
import numpy as np
import configparser as crp
import json
import datetime

from ukmon_meteortools.utils import date2JD, angleBetweenSphericalCoords


def filterFTPforSpecificTime(ftpfile, dtstr):
    """ filter FTPdetect file for a specific event, by time, and copy it into a new file  

    Arguments:  
        ftpfile - [string] full path to the ftpdetect file to filter  
        dtstr   - [string] date/time of required event in yyyymmdd_hhmmss format  

    Returns:  
        tuple containing  
            full name of the new file containing just matching events  
            the number of matching events  
    """
    meteor_list = loadFTPDetectInfo(ftpfile, time_offsets=None, join_broken_meteors=True, locdata=None)
    refdt = datetime.datetime.strptime(dtstr, '%Y%m%d_%H%M%S')
    #print(refdt)
    new_met_list = []
    for met in meteor_list:
        #print(met.ff_name)
        dtpart = datetime.datetime.strptime(met.ff_name[10:25], '%Y%m%d_%H%M%S')
        tdiff = (refdt - dtpart).seconds
        #print(tdiff)
        if abs(tdiff) < 21:
            print('adding one entry')
            new_met_list.append(met)
    newname = writeNewFTPFile(ftpfile, new_met_list)
    return newname, len(new_met_list)


def writeNewFTPFile(srcname, metlist):
    """ creates a FTPDetect file from a list of MeteorObservation objects  
        
    Arguments: 
        srcname     - [string] full path to the original FTP file  
        metlist     - list of MeteorObservation objects  

    Returns: 
        the full path to the created file 

    """
    outdir, fname = os.path.split(srcname)
    newname = os.path.join(outdir, f'{fname}.old')
    try:
        os.rename(srcname, newname)
    except:
        pass
    if os.path.isfile(srcname):
        srcname = srcname[:-4] + '_new.txt'
    with open(srcname, 'w') as ftpf:
        _writeFTPHeader(ftpf, len(metlist), outdir, False)
        metno = 1
        ffname = ''
        for met in metlist:
            if ffname == met.ff_name:
                metno = metno + 1
            else:
                metno = 1
                ffname = met.ff_name
            _writeOneMeteor(ftpf, metno, met.station_id, met.time_data, len(met.frames), met.fps, met.frames, 
                np.degrees(met.ra_data), np.degrees(met.dec_data), 
                np.degrees(met.azim_data), np.degrees(met.elev_data),
                None, met.mag_data, False, met.x_data, met.y_data, met.ff_name)
    return srcname


def loadFTPDetectInfo(ftpdetectinfo_file_name, time_offsets=None,
        join_broken_meteors=True, locdata=None):
    """ Loads an FTPDEtect file into a list of MeteorObservation objects  

    Arguments:  
        ftpdetectinfo_file_name: [str] Path to the FTPdetectinfo file.  
        stations: [dict] A dictionary where the keys are stations IDs, and values are lists of:  
            - latitude +N in radians  
            - longitude +E in radians  
            - height in meters  
        

    Keyword arguments:  
        time_offsets: [dict] (key, value) pairs of (stations_id, time_offset) for every station. None by 
            default.
        join_broken_meteors: [bool] Join meteors broken across 2 FF files.


    Return:  
        meteor_list: [list] A list of MeteorObservation objects filled with data from the FTPdetectinfo file.  

    """
    stations={}
    if locdata is None:
        dirname, fname = os.path.split(ftpdetectinfo_file_name)
        cfgfile = os.path.join(dirname, '.config')
        cfg = crp.ConfigParser()
        cfg.read(cfgfile)
        try: 
            lat = float(cfg['System']['latitude'].split()[0])
            lon = float(cfg['System']['longitude'].split()[0])
            height = float(cfg['System']['elevation'].split()[0])
        except:
            # try reading from platepars file
            ppf = os.path.join(dirname, 'platepars_all_recalibrated.json')
            if not os.path.isfile(ppf):
                return []
            js = json.load(open(ppf, 'r'))
            if len(js) < 10:
                return []
            lat = js[list(js.keys())[0]]['lat']
            lon = js[list(js.keys())[0]]['lon']
            height = js[list(js.keys())[0]]['elev']
        statid= fname.split('_')[1]
    else:
        statid = locdata['station_code']
        lat = float(locdata['lat'])
        lon = float(locdata['lon'])
        height = float(locdata['elev'])

    stations[statid] = [np.radians(lat), np.radians(lon), height*1000]
    meteor_list = []

    with open(ftpdetectinfo_file_name) as f:
        # Skip the header
        for i in range(11):
            next(f)

        current_meteor = None

        bin_name = False
        cal_name = False
        meteor_header = False

        for line in f:
            # Skip comments
            if line.startswith("#"):
                continue

            line = line.replace('\n', '').replace('\r', '')

            # Skip the line if it is empty
            if not line:
                continue

            if '-----' in line:
                # Mark that the next line is the bin name
                bin_name = True

                # If the separator is read in, save the current meteor
                if current_meteor is not None:
                    current_meteor._finish()
                    meteor_list.append(current_meteor)
                continue

            if bin_name:
                bin_name = False

                # Mark that the next line is the calibration file name
                cal_name = True

                # Save the name of the FF file
                ff_name = line

                # Extract the reference time from the FF bin file name
                line = line.split('_')

                # Count the number of string segments, and determine if it the old or new CAMS format
                if len(line) == 6:
                    sc = 1
                else:
                    sc = 0

                ff_date = line[1 + sc]
                ff_time = line[2 + sc]
                milliseconds = line[3 + sc]

                year = ff_date[:4]
                month = ff_date[4:6]
                day = ff_date[6:8]

                hour = ff_time[:2]
                minute = ff_time[2:4]
                seconds = ff_time[4:6]

                year, month, day, hour, minute, seconds, milliseconds = map(int, [year, month, day, hour, 
                    minute, seconds, milliseconds])

                # Calculate the reference JD time
                jdt_ref = date2JD(year, month, day, hour, minute, seconds, milliseconds)
                continue

            if cal_name:
                cal_name = False
                # Mark that the next line is the meteor header
                meteor_header = True
                continue

            if meteor_header:
                meteor_header = False
                line = line.split()

                # Get the station ID and the FPS from the meteor header
                station_id = line[0].strip()
                fps = float(line[3])

                # Try converting station ID to integer
                try:
                    station_id = int(station_id)
                except:
                    pass

                # If the time offsets were given, apply the correction to the JD
                if time_offsets is not None:
                    if station_id in time_offsets:
                        print('Applying time offset for station {:s} of {:.2f} s'.format(str(station_id),
                            time_offsets[station_id]))

                        jdt_ref += time_offsets[station_id]/86400.0
                    else:
                        print('Time offset for given station not found!')

                # Get the station data
                if station_id in stations:
                    lat, lon, height = stations[station_id]
                else:
                    print('ERROR! No info for station ', station_id, ' found in CameraSites.txt file!')
                    print('Exiting...')
                    break
                # Init a new meteor observation
                current_meteor = MeteorObservation(jdt_ref, station_id, lat, lon, height, fps,
                    ff_name=ff_name)
                continue

            # Read in the meteor observation point
            if (current_meteor is not None) and (not bin_name) and (not cal_name) and (not meteor_header):

                line = line.replace('\n', '').split()

                # Read in the meteor frame, RA and Dec
                frame_n = float(line[0])
                x = float(line[1])
                y = float(line[2])
                ra = float(line[3])
                dec = float(line[4])
                azim = float(line[5])
                elev = float(line[6])

                # Read the visual magnitude, if present
                if len(line) > 8:
                    mag = line[8]
                    if mag == 'inf':
                        mag = None
                    else:
                        mag = float(mag)
                else:
                    mag = None

                # Add the measurement point to the current meteor 
                current_meteor._addPoint(frame_n, x, y, azim, elev, ra, dec, mag)

        # Add the last meteor the the meteor list
        if current_meteor is not None:
            current_meteor._finish()
            meteor_list.append(current_meteor)

    # Concatenate observations across different FF files ###
    if join_broken_meteors:

        # Go through all meteors and compare the next observation
        merged_indices = []
        for i in range(len(meteor_list)):

            # If the next observation was merged, skip it
            if (i + 1) in merged_indices:
                continue

            # Get the current meteor observation
            met1 = meteor_list[i]

            if i >= (len(meteor_list) - 1):
                break

            # Get the next meteor observation
            met2 = meteor_list[i + 1]
            
            # Compare only same station observations
            if met1.station_id != met2.station_id:
                continue

            # Extract frame number
            met1_frame_no = int(met1.ff_name.split("_")[-1].split('.')[0])
            met2_frame_no = int(met2.ff_name.split("_")[-1].split('.')[0])

            # Skip if the next FF is not exactly 256 frames later
            if met2_frame_no != (met1_frame_no + 256):
                continue


            # Check for frame continouty
            if (met1.frames[-1] < 254) or (met2.frames[0] > 2):
                continue

            # Check if the next frame is close to the predicted position 

            # Compute angular distance between the last 2 points on the first FF
            ang_dist = angleBetweenSphericalCoords(met1.dec_data[-2], met1.ra_data[-2], met1.dec_data[-1],
                met1.ra_data[-1])

            # Compute frame difference between the last frame on the 1st FF and the first frame on the 2nd FF
            df = met2.frames[0] + (256 - met1.frames[-1])

            # Skip the pair if the angular distance between the last and first frames is 2x larger than the 
            #   frame difference times the expected separation
            ang_dist_between = angleBetweenSphericalCoords(met1.dec_data[-1], met1.ra_data[-1],
                met2.dec_data[0], met2.ra_data[0])

            if ang_dist_between > 2*df*ang_dist:
                continue

            # If all checks have passed, merge observations ###
            # Recompute the frames
            frames = 256.0 + met2.frames

            # Recompute the time data
            time_data = frames/met1.fps

            # Add the observations to first meteor object
            met1.frames = np.append(met1.frames, frames)
            met1.time_data = np.append(met1.time_data, time_data)
            met1.x_data = np.append(met1.x_data, met2.x_data)
            met1.y_data = np.append(met1.y_data, met2.y_data)
            met1.azim_data = np.append(met1.azim_data, met2.azim_data)
            met1.elev_data = np.append(met1.elev_data, met2.elev_data)
            met1.ra_data = np.append(met1.ra_data, met2.ra_data)
            met1.dec_data = np.append(met1.dec_data, met2.dec_data)
            met1.mag_data = np.append(met1.mag_data, met2.mag_data)

            # Merge the FF file name and create a list
            if (met1.ff_name is not None) and (met2.ff_name is not None):
                met1.ff_name = met1.ff_name + ',' + met2.ff_name

            # Sort all observations by time
            met1._finish()

            # Indicate that the next observation is to be skipped
            merged_indices.append(i + 1)

        # Removed merged meteors from the list
        meteor_list = [element for i, element in enumerate(meteor_list) if i not in merged_indices]

    return meteor_list


class MeteorObservation(object):
    """ Container for meteor observations.  
    """
    def __init__(self, jdt_ref, station_id, latitude, longitude, height, fps, ff_name=None):
        """ Construct the MeteorObservation object.  
        Arguments:  
            jdt_ref: [float] Reference Julian date when the relative time is t = 0s.  
            station_id: [str] Station ID.  
            latitude: [float] Latitude +N in radians.  
            longitude: [float] Longitude +E in radians.  
            height: [float] Elevation above sea level (MSL) in meters. 
            fps: [float] Frames per second. 

        Keyword arguments:  
            ff_name: [str] Name of the originating FF file. 
        """
        self.jdt_ref = jdt_ref
        self.station_id = station_id
        self.latitude = latitude
        self.longitude = longitude
        self.height = height
        self.fps = fps
        self.ff_name = ff_name
        self.frames = []
        self.time_data = []
        self.x_data = []
        self.y_data = []
        self.azim_data = []
        self.elev_data = []
        self.ra_data = []
        self.dec_data = []
        self.mag_data = []
        self.abs_mag_data = []

    def _addPoint(self, frame_n, x, y, azim, elev, ra, dec, mag):
        """ Adds the measurement point to the meteor.

        Arguments:
            frame_n: [flaot] Frame number from the reference time.
            x: [float] X image coordinate.
            y: [float] X image coordinate.
            azim: [float] Azimuth, J2000 in degrees.
            elev: [float] Elevation angle, J2000 in degrees.
            ra: [float] Right ascension, J2000 in degrees.
            dec: [float] Declination, J2000 in degrees.
            mag: [float] Visual magnitude.
        """
        self.frames.append(frame_n)

        # Calculate the time in seconds w.r.t. to the reference JD
        point_time = float(frame_n)/self.fps
        self.time_data.append(point_time)
        self.x_data.append(x)
        self.y_data.append(y)

        # Angular coordinates converted to radians
        self.azim_data.append(np.radians(azim))
        self.elev_data.append(np.radians(elev))
        self.ra_data.append(np.radians(ra))
        self.dec_data.append(np.radians(dec))
        self.mag_data.append(mag)

    def _finish(self):
        """ When the initialization is done, convert data lists to numpy arrays. """
        self.frames = np.array(self.frames)
        self.time_data = np.array(self.time_data)
        self.x_data = np.array(self.x_data)
        self.y_data = np.array(self.y_data)
        self.azim_data = np.array(self.azim_data)
        self.elev_data = np.array(self.elev_data)
        self.ra_data = np.array(self.ra_data)
        self.dec_data = np.array(self.dec_data)
        self.mag_data = np.array(self.mag_data)
        # Sort by frame
        temp_arr = np.c_[self.frames, self.time_data, self.x_data, self.y_data, self.azim_data, 
        self.elev_data, self.ra_data, self.dec_data, self.mag_data]
        temp_arr = temp_arr[np.argsort(temp_arr[:, 0])]
        self.frames, self.time_data, self.x_data, self.y_data, self.azim_data, self.elev_data, self.ra_data, \
            self.dec_data, self.mag_data = temp_arr.T


def _writeFTPHeader(ftpf, metcount, fldr, ufo=True):
    """
    Internal function to create the header of the FTPDetect file  
    """
    l1 = 'Meteor Count = {:06d}\n'.format(metcount)
    ftpf.write(l1)
    ftpf.write('-----------------------------------------------------\n')
    if ufo is True:
        ftpf.write('Processed with UFOAnalyser\n')
    else:
        ftpf.write('Processed with RMS 1.0\n')
    ftpf.write('-----------------------------------------------------\n')
    l1 = 'FF  folder = {:s}\n'.format(fldr)
    ftpf.write(l1)
    l1 = 'CAL folder = {:s}\n'.format(fldr)
    ftpf.write(l1)
    ftpf.write('-----------------------------------------------------\n')
    ftpf.write('FF  file processed\n')
    ftpf.write('CAL file processed\n')
    ftpf.write('Cam# Meteor# #Segments fps hnr mle bin Pix/fm Rho Phi\n')
    ftpf.write('Per segment:  Frame# Col Row RA Dec Azim Elev Inten Mag\n')


def _writeOneMeteor(ftpf, metno, sta, evttime, fcount, fps, fno, ra, dec, az, alt, b, mag, 
        ufo=True, x=None, y=None, ffname = None):
    """   Internal function to write one meteor event into the file in FTPDetectInfo style
    """
    ftpf.write('-------------------------------------------------------\n')
    if ffname is None:
        ms = '{:03d}'.format(int(evttime.microsecond / 1000))

        fname = 'FF_' + sta + '_' + evttime.strftime('%Y%m%d_%H%M%S_') + ms + '_0000000.fits\n'
    else:
        fname = ffname + '\n'
    ftpf.write(fname)

    if ufo is True:
        ftpf.write('UFO UKMON DATA Recalibrated on: ')
    else:
        ftpf.write('RMS data reprocessed on: ')
    ftpf.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f UTC\n'))
    li = f'{sta} {metno:04d} {fcount:04d} {fps:04.2f} 000.0 000.0  00.0 000.0 0000.0 0000.0\n'
    ftpf.write(li)

    for i in range(len(fno)):
        #    204.4909 0422.57 0353.46 262.3574 +16.6355 267.7148 +23.0996 000120 3.41
        bri = 0
        if b is not None:
            bri = int(b[i])
        if ufo is True:
            # UFO is timestamped as at the first detection
            thisfn = fno[i] - fno[0]
            thisx = 0
            thisy = 0
        else:
            thisfn = fno[i]
            thisx = x[i]
            thisy = y[i]
        li = f'{thisfn:.4f} {thisx:07.2f} {thisy:07.2f} '
        li = li + f'{ra[i]:8.4f} {dec[i]:+7.4f} {az[i]:8.4f} '
        li = li + f'{alt[i]:+7.4f} {bri:06d} {mag[i]:.02f}\n'
        ftpf.write(li)
