import sklearn
from matplotlib import pyplot

from sklearn.metrics import silhouette_score
from sklearn import cluster, datasets, mixture
from sklearn.neighbors import kneighbors_graph
import pandas as pd

df = pd.read_csv('int_counts-Numberphile.tab', sep='\t')

pyplot.scatter(df['int'], df['count'], s=1)


connect = kneighbors_graph(df, n_neighbors=5, include_self=False)
hc_dataset2_connectivity = cluster.AgglomerativeClustering(n_clusters=3, affinity='euclidean', 
                                              linkage='complete',connectivity=connect).fit_predict(df)
