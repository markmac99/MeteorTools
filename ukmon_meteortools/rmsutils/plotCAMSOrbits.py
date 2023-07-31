# Copyright (C) 2018-2023 Mark McIntyre

#
# python code to plot orbits given a CAMS style Orbit Info file
#

import sys
import os
import datetime
import matplotlib.pyplot as plt
try:
    from wmpl.Utils.PlotOrbits import plotOrbits
except:
    print('WMPL not available')


def plotCAMSOrbits(orbitFile, outdir=None, hideplot=True):
    """
    plots a set of orbits from CAMS data, with one line per set of osculations  

    Arguments:  
        orbitFile:  [string] full path to CAMS orbit details file  
        outdir:     [string] the location to write to. defaults to folder of CAMS file  
        hideplot:   [bool] don't display the plot. Default true  

    Returns:  
        none  
    """
    if outdir is None:
        outdir, _ = os.path.split(orbitFile)
    
    evttime = None

    # read in the data file as a list of lines
    lis = open(orbitFile, 'r').readlines()
    
    # create an empty array to contain the orbital elements
    orb_elements=[]

    # ignore the first two lines, split the remaining lines up and find the 
    # elements we want
    for i in range(3,len(lis)):
        li = lis[i].split()
        if evttime is None:
            evttime = li[1]+'T'+li[2][:8]
        a = float(li[25])
        e = float(li[26])
        if a < 0:
            q = float(li[22])
            if e==1.0:
                e=1.0001
            a = q/(1-e)
        elemline = [a,e,float(li[28]),float(li[30]),float(li[32])]
        # print(elemline)
        # add the elements to the array
        orb_elements.append(elemline)

    # plot and save the orbits
    
    plotOrbits(orb_elements, datetime.datetime.strptime(evttime, '%Y-%m-%dT%H:%M:%S'), color_scheme='light')
    evttime = evttime.replace(':','-')
    plt.savefig(os.path.join(outdir, f'CAMS_{evttime}.png'))
    if not hideplot:
        plt.show()
    plt.close()

#    with open(os.path.join(outdir, 'sampleRMSdata.txt'), 'w') as outf:
#        for li in orb_elements:
#            outf.write(f'{li[0]},{li[1]},{li[2]},{li[3]},{li[4]},{evttime}\n')

    return 


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python plotCAMSOrbits source_file target_folder')

    plotCAMSOrbits(sys.argv[1], sys.argv[2])
