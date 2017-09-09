"""
Author: Casey McGinley

Code is only lightly modified from source. All credit goes to the k-means 
algorithm (Lloyd's algo) implementation courtesy of:
https://datasciencelab.wordpress.com/tag/lloyds-algorithm/
"""

import numpy as np
import random


# TODO: is the cluster_map stuff really needed?
def _cluster_points(X, mu):
    """
    Assigns each point x of X to a centroid (in the list mu) (it's closets 
    center)

    Returns a dictionary mapping centroids to lists of points
    """
    cluster_map = []
    clusters  = {}

    # iterate over points
    for x in X:
        # identify closest centroid
        # NOTE: bestmukey is the index into the list mu, not the centroid itself
        bestmukey = min([(i[0], np.linalg.norm(x-mu[i[0]])) \
                    for i in enumerate(mu)], key=lambda t:t[1])[0]
        cluster_map.append(bestmukey)
        try:
            clusters[bestmukey].append(x)
        except KeyError:
            clusters[bestmukey] = [x]
    return clusters, cluster_map


def _reevaluate_centers(clusters):
    """
    Given some existing clustering, calculate new means/centroids
    
    Returns this list of new centroids
    """
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        # calculate a new centroid
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu
 

def _has_converged(mu, oldmu):
    """
    Boolean check for convergeance between previosu and new centroids
    
    Returns True if the new and old centers (mu) have converged (i.e. they are
    equivalent)
    """
    if mu is None or oldmu is None:
        return False
    return (set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu]))
 

def find_centers(X, K):
    """
    Main routine of the iterative k-means implementation
    
    Returns a list of the centroids and a map of the centroids to their clusters 
    """
    # convert to list of lists (e.g. if X is a numpy array)
    X = list(X)
    for i in range(len(X)): 
        x = X[i]
        x = list(x)
        X[i] = x

    # mu are the means (the centers); initialize to random points
    oldmu = None
    mu = random.sample(X, K)

    # iteratively improve our centroids until no improvement can be made
    while not _has_converged(mu, oldmu):
        oldmu = mu

        # Assign all points in X to clusters
        X = np.array(X) # convert back to numpy array
        clusters, cluster_map = _cluster_points(X, mu)

        # Reevaluate centers
        mu = _reevaluate_centers(clusters)
    return mu, clusters, cluster_map
