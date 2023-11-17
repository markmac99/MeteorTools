# copyright Mark McIntyre, 2023-

# flake8: noqa: E501
# an attempt to use DBSCAN to identify clusters of meteors
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn import metrics
from sklearn.cluster import DBSCAN

from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances


def getNthClosestEps(npdata, pct=23, nsamples=5):
    """ 
    Get the epsilon parameter for DBSCAN. Following Sugar et al., 
    I'm calculating the pairwise distances between points, then finding the nth-closest 
    where n+1 is the number of points in a cluster. 
    For example if we consider a cluster to be 5 or more points
    then i find the 4th closest distance. Note that pairwise_distances returns the distance 
    from the point to itself so the 4th closest is the 5th entry in the array. 
    I then arrange the points in order of distance and take the value at a given percentage 
    of the dataset. Sugar et al found 23% to be a good value so i'm using that as a default. 
    """
    pwds = pairwise_distances(npdata)
    dists = []
    for pw in pwds:
        pw.sort()
        dists.append(pw[nsamples-1])
    dists.sort() 
    return dists[int(pct/100*len(dists))]


def loadUkmonData(mthstr):
    """
    Load the dataset. We're only interested in a subset of the data. 
    Having loaded it, calculate the six elements of the vector we're going to use
    for the clustering analysis. 
    """
    urlstr = f'https://archive.ukmeteors.co.uk/browse/monthly/{mthstr}-matches.csv'
    datadir = os.getenv('DATADIR', default='f:/videos/meteorcam/ukmondata')
    fname = os.path.join(datadir, f'{mthstr}-matches.csv')
    df = pd.read_csv(urlstr)
    df.to_parquet(fname + '.snap', compression='snappy')
    cols = ['_localtime','_mjd','_sol','_ra_o','_dc_o','_vg','_sol','_elng','_elat', '_stream']
    df = pd.read_parquet(fname + '.snap', columns=cols)
    df['cosls'] = np.cos(np.radians(df._sol))
    df['sinls'] = np.sin(np.radians(df._sol))
    df['uvx'] = np.sin(np.radians(df._elng - df._sol)) * np.cos(np.radians(df._elat))
    df['uvy'] = np.cos(np.radians(df._elng - df._sol)) * np.cos(np.radians(df._elat))
    df['uvz'] = np.sin(np.radians(df._elat))
    df['vnorm'] = df._vg / max(df._vg)
    df2 = df.filter(['cosls','sinls','uvx','uvy','uvz','vnorm'])
    npdata = df2.to_numpy()
    return df, npdata


def computeDBScan(X, eps=0.3, min_samples=5, labels_true=None):
    """
    Compute DBSCAN
    One can access the labels assigned by :class:`~sklearn.cluster.DBSCAN` using
    the `labels_` attribute. Noisy samples are given the label math:`-1`.
    """
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    labels = db.labels_
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    print(f"Estimated number of clusters: {n_clusters_}")
    print(f"Estimated number of noise points: {n_noise_}")
    # Clustering algorithms are fundamentally unsupervised learning methods.
    # However, if we have the true labels we can do some evaluation of the 
    # quality. 
    #
    # If the ground truth labels are not known, evaluation can only be
    # performed using the model results itself. In that case, the
    # Silhouette Coefficient comes in handy.
    #
    # For more information, see the
    # :ref:`sphx_glr_auto_examples_cluster_plot_adjusted_for_chance_measures.py`
    # example or the :ref:`clustering_evaluation` module.
    if labels_true is not None:
        print(f"Homogeneity: {metrics.homogeneity_score(labels_true, labels):.3f}")
        print(f"Completeness: {metrics.completeness_score(labels_true, labels):.3f}")  # noqa:E501
        print(f"V-measure: {metrics.v_measure_score(labels_true, labels):.3f}")
        print(f"Adjusted Rand Index: {metrics.adjusted_rand_score(labels_true, labels):.3f}")  # noqa:E501
        print(f"Adjusted Mutual Information: {metrics.adjusted_mutual_info_score(labels_true, labels):.3f}" )
        
    print(f"Silhouette Coefficient: {metrics.silhouette_score(X, labels):.3f}")
    return db


def plotRaDecGraph(df, fname):
    labels = df['label']
    unique_labels = set(labels)
#    core_samples_mask = np.zeros_like(labels, dtype=bool)
#    core_samples_mask[db.core_sample_indices_] = True
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]  # noqa:E501
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # dont plot the unclassified meteors
            continue
        subdf = df[df.label == k]
        plt.plot(subdf._ra_o, subdf._dc_o, 'o', markerfacecolor=tuple(col),
            markeredgecolor="k",
            markersize=4,
            )
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)        
    plt.title(f"Estimated number of clusters: {n_clusters_ }")
    plt.savefig(fname, dpi=100)
    plt.show()
    return 


def calcClumpMeanVals(df):
    labels = df['label']
    unique_labels = set(labels)
    res = []
    for k in unique_labels:
        subdf = df[df.label == k]
        avgsl = subdf._sol.mean()
        avgra = subdf._ra_o.mean()
        avgdc = subdf._dc_o.mean()
        avgvg = subdf._vg.mean()
        numpt = len(subdf)
        dtaset = {'label': k, 'avgra': avgra, 'avgdc': avgdc, 'avgvg': avgvg, 'avgsl': avgsl, 'count': numpt}
        res.append(dtaset)
    resdf = pd.DataFrame(res)
    resdf = resdf.sort_values(by=['count','avgra'], ascending=False)
    return resdf


def loadStreamFullData():
    npdata = np.load('e:/dev/meteorhunting/WesternMeteorPyLib/wmpl/share/streamfulldata.npy')
    tmpdata = pd.DataFrame(npdata)
    strmdata = tmpdata[[1,2,3,4,6,7,8,9,12]].copy()
    strmdata.columns = ['No','Ad','Code','Name','sts','Ls','Ra','Dc','Vg']
    strmdata = strmdata.replace(r'^\s*$', np.nan, regex=True)
    strmdata = strmdata.replace(r'\(','', regex=True).replace(r'\)','', regex=True)
    strmdata['No'] = [ int(x) for x in strmdata['No']]
    strmdata['sts'] = [ int(x) for x in strmdata['sts']]
    strmdata['Ls'] = [ float(x) for x in strmdata['Ls']]
    strmdata['Ra'] = [ float(x) for x in strmdata['Ra']]
    strmdata['Dc'] = [ float(x) for x in strmdata['Dc']]
    strmdata['Vg'] = [ float(x) for x in strmdata['Vg']]
    strmdata = strmdata[strmdata.sts > -1]    
    return strmdata


if __name__ == '__main__':

    if len(sys.argv) > 1:
        mthstr = sys.argv[1]
    else:
        mthstr = '202310'
    pct=20
    datadir = os.getenv('DATADIR', default='f:/videos/meteorcam/ukmondata')
    nsamples = 5

    df, npdata = loadUkmonData(mthstr)
    eps = getNthClosestEps(npdata, pct=pct)
    db = computeDBScan(npdata, eps=eps, min_samples=nsamples, labels_true=None)
    df['label'] = db.labels_
    df.to_csv(os.path.join(datadir, f'{mthstr}-grouped.csv'), index=False)
    plotRaDecGraph(df, os.path.join(datadir, f'{mthstr}-clusters.jpg'))
    meanvals = calcClumpMeanVals(df)
    meanvals.to_csv(os.path.join(datadir, f'{mthstr}-clump-avgs.csv'), index=False)
