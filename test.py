"""
Author: Casey McGinley

Basic test script demonstrating the k-means implementation
"""

import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as matcol
import kmeans
 

def init_board(N):
    """
    Returns an numpy array of N vectors of length 2
    """
    X = np.array([(random.uniform(-1, 1), random.uniform(-1, 1)) for i in range(N)])
    return X


def main():
    """
    Main routine
    """
    # initialize data points
    X = init_board(100)

    # cluster our data
    centers, clusters, _ = kmeans.find_centers(X,7)
    print centers
    print clusters.keys()
    print clusters
    print _

    # select a random subset of colors
    all_colors = list(matcol.cnames.keys()) #150 colors
    colors = random.sample(all_colors,len(clusters)+1)

    # divide our centroids up into X/Y lists
    centers_x = []
    centers_y = []
    for c in centers:
        centers_x.append(c[0])
        centers_y.append(c[1])

    # divide our cluster members up into X/Y lists
    clusters_2 = []
    for i in range(len(clusters)):
        cl = clusters[i]
        x = []
        y = []
        for xy in cl:
            x.append(xy[0])
            y.append(xy[1])
        clusters_2.append([x,y])
    
    # plot the centers
    plt.scatter(centers_x, centers_y, c=colors[0])
    
    # plot the cluster members
    c = 1
    for x,y in clusters_2:
        plt.scatter(x,y,c=colors[c],alpha=0.5)
        c += 1

    # show th eplot
    plt.show()


if __name__ == "__main__":
    main()
