# Copyright (C) 2018-2023 Mark McIntyre

#
# python code to plot orbits given a CAMS style Orbit Info file
#

import sys
import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt
try:
    from wmpl.Utils.PlotOrbits import plotOrbits
except:
    print('WMPL not available')


def plotRMSOrbits(orbitFile, outdir=None, hideplot=True):
    """
    plots a set of orbits from RMS data, with one line per set of osculations  

    Arguments:  
        orbitFile:  [string] full path to RMS orbit details file   
        outdir:     [string] the location to write to. defaults to folder of source file  
        hideplot:   [bool] don't display the plot. Default true  

    Returns:  
        none  

    Notes:   
        Orbitfile should be a csv file with the following labelled columns:  
            _a, _e, _incl, _peri, _node, _datetime  

        _datetime should be in the format YYYY-MM-DDTHH-MM-SS

    """
    if outdir is None:
        outdir, _ = os.path.split(orbitFile)

    evttime = None

    # read in the data file as a list of lines
    data = pd.read_csv(orbitFile)
    avals = list(data['_a'])
    evals = list(data['_e'])
    ivals = list(data['_incl'])
    wvals = list(data['_peri'])
    nvals = list(data['_node'])
    dvals = list(data['_datetime'])
    # create an empty array to contain the orbital elements
    orb_elements=[]

    # ignore the first two lines, split the remaining lines up and find the 
    # elements we want
    for i in range(len(avals)):
        if avals[i] > 0 and avals[i]<=10:
            elemline = [avals[i],evals[i],ivals[i],wvals[i],nvals[i]]
            # add the elements to the array
            orb_elements.append(elemline)
        if evttime is None:
            evttime = dvals[i]

    # plot and save the orbits
    plotOrbits(orb_elements, datetime.datetime.strptime(evttime, '%Y-%m-%dT%H-%M-%S'), color_scheme='light')
    plt.savefig(os.path.join(outdir, f'RMS_{evttime}.png'))
    if not hideplot:
        plt.show()
    plt.close()

    return 


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python plotRMSOrbits source_file target_folder')

    plotRMSOrbits(sys.argv[1], sys.argv[2])
