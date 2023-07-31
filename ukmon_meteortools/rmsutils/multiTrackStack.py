# Copyright (C) 2018-2023 Mark McIntyre

# python script to call TrackStack to stack several nights/cameras

import os
import glob
import datetime
import argparse
try:
    from Utils.TrackStack import trackStack
    import RMS.ConfigReader as cr
except Exception:
    print('RMS not available')


def multiTrackStack(camlist, start, end, outdir=None, shwr=None, scale=None, draw_cons=False, noplot=True, datadir=None):
    """
    create a multi camera and/or multi night trackstack  

    Arguments:  
        camlist:    [list] list of camera IDs eg ['UK0006','UK000F']  
        start:      [string] start date as a string yyyymmdd  
        end:        [string] end date as a string yyyymmdd  
    
    Keyword Arguments: 
        outdir:     [string] where to save to. Default current working directory.  
        shwr:       [string] filter for a specific shower eg 'PER'. Default all showers.  
        scale:      [int] scale the image to avoid cropping. Default 1.  
        draw_cons:  [bool] Draw constellation stick figures. Default false.  
        noplot:     [bool] Don't display the plot, just save it. Default true.  
        datadir:    [string] Root of where to read the data from.   

    Notes:  
        The function expects data to be stored in RMS folder structures as follows  
            {datadir}/{cameraid}/ConfirmedFiles/{cameraid_date_time_*}  

        Each folder must contain an FTPdetectinfo file and a platepars_all file. 
        The first-named folder must contain a valid RMS config file.  

        It is assumed that all cameras are at the same location. The output for cameras 
        at different locations has not been tested.  

        If you find the image is being cropped, try increasing scale. This will use more memory.  

    """
    if datadir is None:
        locfld = os.getenv('LOCALFOLDER', default='f:/videos/meteorcam/fireballs')
        datadir, _ = os.path.split(locfld)
    if outdir is None:
        outdir = '.'
    print(f'stacking {camlist} for dates {start},{end}, reading from {datadir}, saving to {outdir}')

    sdt = datetime.datetime.strptime(start, '%Y%m%d')
    edt = datetime.datetime.strptime(end, '%Y%m%d')
    d = sdt
    dir_paths = []
    while d <= edt:
        dtstr = d.strftime('%Y%m%d')
        for cam in camlist:
            cam = cam.upper()
            camdir = os.path.join(datadir, cam, 'ConfirmedFiles')
            dirs = glob.glob1(camdir, f'{cam}_{dtstr}*')
            if len(dirs) > 0: 
                srcdir = os.path.join(camdir, dirs[0])
                ftpdet = os.path.join(srcdir, f'FTPdetectinfo_{dirs[0]}.txt')
                if os.path.isfile(ftpdet):
                    print(f'using {ftpdet}')
                    dir_paths.append(srcdir)
        d = d + datetime.timedelta(days=1)

    config = cr.loadConfigFromDirectory('.config', dir_paths[0])
    if shwr is not None:
        shwr = [shwr]

    trackStack(dir_paths, config, border=5, background_compensation=True, 
        hide_plot=noplot, showers=shwr, darkbackground=False, out_dir=outdir, scalefactor=scale,
        draw_constellations=draw_cons)

    if len(camlist) > 1:
        bn = os.path.basename(dir_paths[-1])
        outf = os.path.join(outdir, bn + "_track_stack.jpg")
        bn = f'{len(camlist)}CAMS{bn[6:]}'
        newf = os.path.join(outdir, bn + "_track_stack.jpg")
        if os.path.isfile(newf):
            os.remove(newf)
        os.rename(outf, newf)

    return


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Perform multiday/camera trackstack.")

    arg_parser.add_argument('cams', metavar='CAMS', nargs='+', type=str,
        help='List of cameras, comma-separated.')

    arg_parser.add_argument('dates', metavar='DATES', nargs='+', type=str,
        help='Start and end date, comma-separated in yyyymmdd format.')

    arg_parser.add_argument('-s', '--shower', metavar='SHOWER', type=str,
        help="Associate just this single shower given its code (e.g. PER, ORI, ETA).")

    arg_parser.add_argument('-o', '--outdir', metavar='OUTDIR', type=str,
        help="Where to save the output file.")

    arg_parser.add_argument('-f', '--scalefactor', metavar='SCALEFACTOR', type=int,
        help="Scale factor to apply when creating canvas.")

    arg_parser.add_argument('--constellations', help="Overplot constellations", action="store_true")

    cml_args = arg_parser.parse_args()
    cams = cml_args.cams[0]
    if ',' in cams:
        cams = cams.split(',')
    else:
        cams = [cams]

    dates = cml_args.dates[0]
    if ',' in dates:
        start, end = dates.split(',')
    else:
        start = dates
        end = start

    shwr = None
    if cml_args.shower:
        shwr = cml_args.shower
        if shwr == 'ALL': # special case for ALLs
            shwr = None
    
    outdir = '.'
    if cml_args.outdir:
        outdir = cml_args.outdir

    scalefactor = 1
    if cml_args.scalefactor:
        scalefactor = cml_args.scalefactor

    multiTrackStack(cams, start, end, outdir, shwr, scalefactor,draw_constellations=cml_args.constellations)
