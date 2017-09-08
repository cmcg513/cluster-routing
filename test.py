import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as matcol
 
def cluster_points(X, mu):
    clusters  = {}
    for x in X:
        bestmukey = min([(i[0], np.linalg.norm(x-mu[i[0]])) \
                    for i in enumerate(mu)], key=lambda t:t[1])[0]
        try:
            clusters[bestmukey].append(x)
        except KeyError:
            clusters[bestmukey] = [x]
    return clusters
 
def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu
 
def has_converged(mu, oldmu):
    return (set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu]))
 

def find_centers(X, K):
    # Initialize to K random centers
    X = list(X)
    for i in range(len(X)):
        x = X[i]
        x = list(x)
        X[i] = x
    oldmu = random.sample(X, K)
    mu = random.sample(X, K)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        X = np.array(X)
        clusters = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    return(mu, clusters)
 
def init_board(N):
    X = np.array([(random.uniform(-1, 1), random.uniform(-1, 1)) for i in range(N)])
    return X

def main():
    X = init_board(100)
    import IPython; IPython.embed()
    all_colors = list(matcol.cnames.keys()) #150 colors
    centers,clusters = find_centers(X,7)
    colors = random.sample(all_colors,len(clusters)+1)
    centers_x = []
    centers_y = []
    for c in centers:
        centers_x.append(c[0])
        centers_y.append(c[1])
    # import IPython; IPython.embed()
    clusters_2 = []
    for i in range(len(clusters)):
        cl = clusters[i]
        x = []
        y = []
        for xy in cl:
            x.append(xy[0])
            y.append(xy[1])
        clusters_2.append([x,y])
    # import IPython; IPython.embed()
    plt.scatter(centers_x, centers_y, c=colors[0])
    c = 1
    for x,y in clusters_2:
        plt.scatter(x,y,c=colors[c],alpha=0.5)
        c += 1
    plt.show()
main()