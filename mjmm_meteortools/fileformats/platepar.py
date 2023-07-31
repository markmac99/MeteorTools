# 
# class to read a single or multiple platepar files
#
# Copyright (C) 2018-2023 Mark McIntyre

import json
import os
import glob


class platepar:
    """ Load and manage an RMS platepar object, used to map an image to the sky """
    def __init__(self, plateparfile):
        """" Create and load a platepar object from a file plateparfile """
        with open(plateparfile, 'r') as pp:
            self.jsd = json.load(pp)
            try: 
                self.id = self.jsd['station_code']
                # field of view details
                self.alt_centre = self.jsd['alt_centre']
                self.az_centre = self.jsd['az_centre']
                self.Ho = self.jsd['Ho']
                self.fov_h = self.jsd['fov_h']
                self.fov_v = self.jsd['fov_v']
                self.rotation_from_horiz = self.jsd['rotation_from_horiz']
                self.RA_d = self.jsd['RA_d']
                self.dec_d = self.jsd['dec_d']
                self.pos_angle_ref = self.jsd['pos_angle_ref']

                # camera location
                self.lat = self.jsd['lat']
                self.lon = self.jsd['lon']
                self.elev = self.jsd['elev']

                # camera resolution
                self.X_res = self.jsd['X_res']
                self.Y_res = self.jsd['Y_res']

                # Reference time and date
                self.time = 0
                self.JD = self.jsd['JD']
                self.UT_corr =self.jsd['UT_corr']

                # FOV scale (px/deg)
                self.F_scale = self.jsd['F_scale']

            except:
                print('invalid json file')

    def getLocation(self):
        """ get the lat, lon and elevation from the platepar"""
        return [self.lat, self.lon, self.elev]

    def getView(self):
        """ get the pointing direction (alt/az), field of view (h/v) and rotation """
        return [self.altcentre, self.azcentre, self.fov_h, self.fov_v, self.rot]

    def getResolution(self):
        """ Get the reported camera resolution """
        return [self.xres, self.yres]


def loadPlatepars(fldr):
    """ Create a dictionary of multiple platepars  
    
    Arguments:  
        fldr:   [string] A folder containing one or more platepar files  

    Returns:  
        a json dict containing each platepar indexed by the corresponding filename  
    """
    platepars ='{'
    pth = os.path.join(fldr, '*.json')
    pps = glob.glob(pth)
    for pp in pps:
        thispl = platepar(pp)
        if thispl is not None:
            if len(platepars) > 1: # and pp != pps[-1]:
                platepars = platepars + ','
            platepars = platepars + '"' + thispl.id +'": '+ json.dumps(thispl.jsd)
    platepars = platepars + '}'
    #print(platepars)
    ppjson = json.loads(platepars)
    return ppjson
