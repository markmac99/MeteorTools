# copyright Mark McIntyre, 2023-

# flake8: noqa: E501
# an attempt to use DBSCAN to identify clusters of meteors
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn import metrics
from sklearn.cluster import DBSCAN

from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances

"""
===================================
Demo of DBSCAN clustering algorithm
===================================

DBSCAN (Density-Based Spatial Clustering of Applications with Noise) finds core
samples in regions of high density and expands clusters from them. This
algorithm is good for data which contains clusters of similar density.

See the :ref:`sphx_glr_auto_examples_cluster_plot_cluster_comparison.py`
example for a demo of different clustering algorithms on 2D datasets.

"""


def getNthClosestEps(npdata, pct=23, nsamples=5):
    """ 
    Get the epsilon parameter for DBSCAN. Following Sugar et al.
    I'm calculating the pairwise distances between points, then finding the nth-closest 
    where n+1 is the number of points in a cluster. 
    For example if we consider a cluster to be 5 or more points
    then i find the 4th closest distance. Note that pairwise_distances returns the distance 
    from the point to itself so we add one to the index. 
    I then arrange the points in order of distance and take the value at a given percentage 
    of the dataset. Sugar et al found 23% to be a good value so i'm using that as a default. 
    """
    pwds = pairwise_distances(npdata)
    dists = []
    for pw in pwds:
        pw.sort()
        dists.append(pw[nsamples])
    dists.sort() 
    return dists[int(pct/100*len(dists))]


def loadUkmonData(mthstr):
    """
    Load the UKMON dataset. We're only interested in a subset of the data. 
    Having loaded it, calculate the six elements of the vector we're going to use
    for the clustering analysis. 
    """
    datadir = os.getenv('DATADIR', default='f:/videos/meteorcam/ukmondata')
    fname = os.path.join(datadir, f'{mthstr}-matches.csv')
    df = pd.read_csv(fname)
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
    print("Estimated number of clusters: %d" % n_clusters_)
    print("Estimated number of noise points: %d" % n_noise_)
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
    labels = db.labels_
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
    plt.title(f"Estimated number of clusters: {n_clusters_}")
    plt.savefig(fname, dpi=100)
    plt.show()
    return 


def genDummyData():
# Dummy 2-d Data generation
# We use :class:`~sklearn.datasets.make_blobs` to create 3 synthetic clusters.
    centers = [[1, 1], [-1, -1], [1, -1]]
    X, labels_true = make_blobs(
        n_samples=750, centers=centers, cluster_std=0.4, random_state=0
    )

    X = StandardScaler().fit_transform(X)
    # %%
    # We can visualize the resulting data:

    plt.scatter(X[:, 0], X[:, 1])
    plt.show()
    return X, labels_true


def plotResults(db, X):
    """
    Plot results - only useful for 2-d datasets
    # ------------
    # Core samples (large dots) and non-core samples (small dots) are color-coded
    # according to the assigned cluster. Samples tagged as noise are represented in
    # black.
    """
    labels = db.labels_
    unique_labels = set(labels)
    core_samples_mask = np.zeros_like(labels, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True

    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]  # noqa:E501
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = labels == k

        xy = X[class_member_mask & core_samples_mask]
        plt.plot(
            xy[:, 0],
            xy[:, 1],
            "o",
            markerfacecolor=tuple(col),
            markeredgecolor="k",
            markersize=14,
        )

        xy = X[class_member_mask & ~core_samples_mask]
        plt.plot(
            xy[:, 0],
            xy[:, 1],
            "o",
            markerfacecolor=tuple(col),
            markeredgecolor="k",
            markersize=6,
        )
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    plt.title(f"Estimated number of clusters: {n_clusters_}")
    plt.show()


if __name__ == '__main__':
    mthstr = '202310'
    pct=20
    nsamples = 5
    df, npdata = loadUkmonData(mthstr)
    eps = getNthClosestEps(npdata, pct=pct)
    db = computeDBScan(npdata, eps=eps, min_samples=nsamples, labels_true=None)
    df['label'] = db.labels_
    datadir = os.getenv('DATADIR', default='f:/videos/meteorcam/ukmondata')
    df.to_csv(os.path.join(datadir, f'{mthstr}-grouped.csv'), index=False)
    plotRaDecGraph(df, os.path.join(datadir, f'{mthstr}-clusters.jpg'))

#    X, labels_true = genDummyData()
#    db = computeDBScan(X, eps=0.3, min_samples=10, labels_true=labels_true)
#    plotResults(db, X)
