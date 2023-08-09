# Copyright (C) 2018-2023 Mark McIntyre
#
# python script to get all live JPGs for a specified time
#
import os
import pandas as pd
import requests


def getLiveJpgs(dtstr, outdir=None, create_txt=False):
    """
    Retrieve live images from the ukmon website that match a pattern  

    Arguments:  
        dtstr:      [str] Date in YYYYMMDD_HHMMSS format. Partial strings allowed  
        outdir:     [str] Where to save the file. Default is to create a folder named dtstr  
        create_txt: [bool] If true, create a text file containing the pattern matches  

    Notes:  
        We only keep the last few thousand live images so this function will return nothing
        for older data. 
    """
    if outdir is None:
        outdir = dtstr
    os.makedirs(outdir, exist_ok=True)

    apiurl = 'https://api.ukmeteornetwork.co.uk/liveimages/getlive'
    liveimgs = pd.read_json(f'{apiurl}?pattern={dtstr}')

    weburl = 'https://live.ukmeteornetwork.co.uk/'

    for _, img in liveimgs.iterrows():
        try:
            jpgurl = f'{weburl}{img.image_name}'
            _download(jpgurl, outdir)
            xmlurl = jpgurl.replace('P.jpg', '.xml')
            _download(xmlurl, outdir)
            print(f'retrieved {jpgurl}')
            if create_txt:
                createTxtFile(img.image_name, outdir)
        except:
            print(f'{img.image_name} unavailable')


def getFBfiles(patt, outdir=None):
    """
    Retrieve fireball files from the ukmon website that match a pattern  

    Arguments:  
        patt:      [str] pattern to match.  
        outdir:     [str] Where to save the files. See notes.  

    Returns:  
        a pandas dataframe containing the filenames and presigned URLs

    Example:  
        import pandas as pd  
        df = getFBfiles('UK0006_20230421_2122', 'c:/temp/uk0006')  

    Notes:  
        The function retrieves the FF and FR files matching the pattern, plus the config and platepar 
        for the camera, provided the files are available on our server.  
        If outdir is not supplied, a folder will be created in the current working directory named
        using the station ID code. 
    """
    if outdir is None:
        outdir = patt[:6]
    os.makedirs(outdir, exist_ok=True)
    apiurl = 'https://api.ukmeteornetwork.co.uk/fireballs/getfb'
    fbfiles = pd.read_json(f'{apiurl}?pattern={patt}')
    if len(fbfiles) == 0:
        print('no matching data found')
        return None
    for _,fil in fbfiles.iterrows():
        fname = fil['filename']
        url = fil['url']
        _download(url, outdir, fname)
        print(fname)
    return fbfiles


def createTxtFile(fname, outdir=None):
    """
    Create a text file named after the cameraID, containing a list of fireball files 
    to be retrieved from a remote camera.  

    Arguments:  
        fname:  [str] the name of the FF file to be retrieved. 
        outdir: [str] where to save the files. See notes.  

    Notes:  
        the fname parameter should be the name of the live JPG for which you wish to 
        retrieve the corresponding FF and FR files.  
        If outdir is not supplied, the files will be saved in the current directory.   
    """
    if fname[0] == 'M':
        spls = fname.split('_')
        stationid = spls[-1][:6].lower()
        dtime = fname[1:16]
        patt = f'FF_{stationid}_{dtime}'
        stationid = stationid.lower()
    else:
        patt = fname[:25]
        stationid = fname[3:9].lower()
    if outdir is None:
        outdir = '.' 
    os.makedirs(outdir, exist_ok=True)
    
    txtf = os.path.join(outdir, f'{stationid}.txt')
    if os.path.isfile(txtf):
        os.remove(txtf)
    patt = patt.upper()
    with open(txtf,'w') as outf:
        outf.write(f'{patt}\n{patt.replace("FF_", "FR_")}\n')
    return txtf


def _download(url, outdir, fname=None):
    get_response = requests.get(url, stream=True)
    if fname is None:
        fname = url.split("/")[-1]
    with open(os.path.join(outdir, fname), 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=4096):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
