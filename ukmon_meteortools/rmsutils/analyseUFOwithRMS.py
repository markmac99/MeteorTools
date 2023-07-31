# Copyright (C) 2018-2023 Mark McIntyre
#
# analyse a UFO dataset using RMS - well, a start at it anyway ! 
#
import os
import argparse
try: 
    import RMS.ConfigReader as cr
    from RMS.DetectStarsAndMeteors import detectStarsAndMeteors
except:
    print('RMS not available')


def analyseUFOwithRMS(config, ff_directory, ff_name):
    """
    Analyse a UFO video clip using RMS, to get a list of stars and meteors  

    Arguments:
        config: [string] An RMS-style config file for the  UFO camera  
        ff_directory: [string] The location of the file to analyse  
        ff_name: [string] A video file to analyse.   

    Returns:  
        (star_list, meteor_list): tuple containing a list of stars and a list of meteors  
        
    Note: the name of the video clip must be in %Y%m%d_%H%M%S.%f format.   
    """ 
    flat_struct=None
    dark=None
    mask=None
    _, star_list, meteor_list = detectStarsAndMeteors(ff_directory, ff_name, config, flat_struct, dark, mask)

    return star_list, meteor_list

   
if __name__ == '__main__':
    # COMMAND LINE ARGUMENTS
    # Init the command line arguments parser
    arg_parser = argparse.ArgumentParser(description="Analyses a UFO avi with RMS.")

    arg_parser.add_argument('ff_path', nargs='+', metavar='FILE_PATH', type=str,
        help='Full path and name of the file to analyse')

    arg_parser.add_argument('-c', '--config', nargs=1, metavar='CONFIG_PATH', type=str,
        help="Path to a config file which will be used instead of the default one.")
    
    # Parse the command line arguments
    cml_args = arg_parser.parse_args()

    #########################

    ff_directory, ff_name = os.path.split(cml_args.ff_path[0])

    print(ff_directory, ff_name)
    config = cr.loadConfigFromDirectory(cml_args.config[0], ff_directory)
    print("loaded config \n\n\n")
    
    analyseUFOwithRMS(config, ff_directory, ff_name)
