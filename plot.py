import pandas as pd
import numpy as np
import random
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid.inset_locator import inset_axes

plt.rc('patch',linewidth=2)
plt.rc('axes', linewidth=2, labelpad=10)
plt.rc('xtick.minor', size=4, width=2)
plt.rc('xtick.major', size=8, width=2, pad=8)
plt.rc('ytick.minor', size=4, width=2)
plt.rc('ytick.major', size=8, width=2, pad=8)
plt.rc('text', usetex=True)
plt.rc('font', family='serif', serif='Computer Modern', size=30)


def plot_clusters():            
    dpi=300
    xbox=lx/dpi
    ybox=ly/dpi
    
    fig, ax = plt.subplots(figsize=(xbox, ybox), dpi=dpi)
    
    random.seed(421)
    colors=[(0.9, 0.9, 0.9)] + [(0.0, 0.0, 0.0)] + [(0.2 + 0.8 * random.random(), 0.2 + 0.8 * random.random(), 0.2 + 0.8 * random.random()) for _ in range(n_clusters - 2)]
    map = mpl.colors.LinearSegmentedColormap.from_list('map', colors, N=n_clusters)
    
    plt.imshow(cluster, cmap=map, interpolation='none', aspect='equal')

    plt.axis('off')
    
    plt.tight_layout(pad=0.0)
    
    plt.savefig(f'./data/images/d{d_cutoff}_l{l_cutoff}.pdf', dpi=dpi)


d_cutoff = 100
l_cutoff = 5
path = "./data/output"
print('Opening...')
df = pd.read_csv(f'{path}/d{d_cutoff}_l{l_cutoff}.csv')
lx = 4990
ly = 4682

population = np.zeros((ly,lx),dtype=np.int32)
cluster = np.zeros((ly,lx),dtype=np.int32)
n_clusters = len(df.cluster.unique())

for row in df.itertuples():
	population[row.y][row.x] = row.population
	cluster[row.y][row.x] = row.cluster

plot_clusters()
