# Copyright (C) 2018-2023 Mark McIntyre

from PIL import Image, ImageFont, ImageDraw 
import datetime


def annotateImage(img_path, statid, metcount, rundate=None):
    """
    Annotate an image with the station ID and date in the bottom left and meteor count in the  
    bottom right  

    Arguments:  
        img_path:   [str] full path and filename of the image to be annotated  
        statid:     [str] station ID string to use  
        metcount:   [int] number of meteors in the image  

    
    Keyword Args:  
        rundate:    [str] rundate in 'YYYYMM' or 'YYYYMMDD' format. Default is today.   

    """
    if rundate is not None:
        if len(rundate) > 6:
            now = datetime.datetime.strptime(rundate, '%Y%m%d')
            title = '{} {}'.format(statid, now.strftime('%Y-%m-%d'))
        else:
            now = datetime.datetime.strptime(rundate, '%Y%m')
            title = '{} {}'.format(statid, now.strftime('%Y-%m'))
    else:
        now = datetime.datetime.now()
        title = '{} {}'.format(statid, now.strftime('%Y-%m-%d'))

    my_image = Image.open(img_path)
    width, height = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    fntheight=30
    try:
        fnt = ImageFont.truetype("arial.ttf", fntheight)
    except:
        fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
    #fnt = ImageFont.load_default()
    image_editable.text((15,height-fntheight-15), title, font=fnt, fill=(255))
    metmsg = 'meteors: {:04d}'.format(metcount)
    image_editable.text((width-7*fntheight-15,height-fntheight-15), metmsg, font=fnt, fill=(255))
    my_image.save(img_path)


def annotateImageArbitrary(img_path, message, color='#000'):
    """
    Annotate an image with an arbitrary message in the selected colour at the bottom left  

    Arguments:  
        img_path:   [str] full path and filename of the image to be annotated  
        message:    [str] message to put on the image  
        color:      [str] hex colour string, default '#000' which is black  

    """
    my_image = Image.open(img_path)
    width, height = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    fntheight=30
    try:
        fnt = ImageFont.truetype("arial.ttf", fntheight)
    except:
        fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
    #fnt = ImageFont.load_default()
    image_editable.text((15,height-fntheight-15), message, font=fnt, fill=color)
    my_image.save(img_path)
