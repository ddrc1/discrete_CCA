import pandas as pd
from read_file import *
import multiprocessing as mp
import numpy as np
from copy import copy
from output_file import *
from utils import *
import time

def neighborhood(running_site_id: int):
    if running_site_id < lx: # If the site is located in the first line of the matrix
        if running_site_id % lx == 0: # If the site is located in the first column of the matrix
            neighborhood_dict = {"RIGHT": running_site_id + 1, "DOWN": running_site_id + lx}
        elif running_site_id % lx == lx - 1: # If the site is located in the last column of the matrix
            neighborhood_dict = {"LEFT": running_site_id - 1, "DOWN": running_site_id + lx}
        else:
            neighborhood_dict = {"LEFT": running_site_id - 1, "RIGHT": running_site_id + 1, "DOWN": running_site_id + lx}

    elif running_site_id >= lx * (ly - 1): # If the site is located in the last line of the matrix
        if running_site_id % lx == 0: # If the site is located in the first column of the matrix
            neighborhood_dict = {"RIGHT": running_site_id + 1, "UP": running_site_id - lx}
        elif running_site_id % lx == lx - 1: # If the site is located in the last column of the matrix
            neighborhood_dict = {"LEFT": running_site_id - 1, "UP": running_site_id - lx}
        else:
            neighborhood_dict = {"LEFT": running_site_id - 1, "RIGHT": running_site_id + 1, "UP": running_site_id - lx}
    
    else:
        if running_site_id % lx == 0:
            neighborhood_dict = {"RIGHT": running_site_id + 1, "DOWN": running_site_id + lx, "UP": running_site_id - lx}
        elif running_site_id % lx == lx - 1:
            neighborhood_dict = {"LEFT": running_site_id - 1, "DOWN": running_site_id + lx, "UP": running_site_id - lx}
        else:
            neighborhood_dict = {"LEFT": running_site_id - 1, "RIGHT": running_site_id + 1, "UP": running_site_id - lx, "DOWN": running_site_id + lx}

    return neighborhood_dict


def calc_distances(clusterA, clusterB, l_cutoff):
    for lonA, latA in zip(clusterA[3], clusterA[4]):
        for lonB, latB in zip(clusterB[3], clusterB[4]):
            distance = haversine_distance(longitude1=lonA, latitude1=latA, longitude2=lonB, latitude2=latB)

            if distance < l_cutoff:
                return clusterB[1]

    return None


def d_filter(df_sites, status, d_cutoff):
    df_sites = df_sites.query(f'density > {d_cutoff}')

    for index in df_sites.index:
        status[index] = 1

    return df_sites, status


def percolation(df_sites, status):
    df_sites['cluster'] = df_sites.index

    for site_id in df_sites.index:
        if status[site_id] != 1: # if the site has been already burned (status 2)
            continue

        status[site_id] = 2

        burns = np.zeros(lx * ly, dtype="uint32")
        nburn = 0
        burns[nburn] = site_id

        iburn = 0
        while iburn <= nburn: # It builds a tree. The leaves are the neighbors of the root site
            running_site_id = burns[iburn]

            neighborhood_dict = neighborhood(running_site_id)

            for neighbor_id in neighborhood_dict.values():
                if status[neighbor_id] == 1: # If the neighbor status is 1, the tree grows
                    status[neighbor_id] = 2

                    df_sites.loc[neighbor_id, 'cluster'] = site_id

                    nburn += 1
                    burns[nburn] = neighbor_id

            iburn += 1 # Burns a root site


def l_filter(df_sites, l_cutoff):
    useful_columns = ["cluster", "longitude", "latitude"] # For performance reasons, selecting only the columns needed
    useful_df_sites = df_sites.copy()[useful_columns].reset_index() # Reducing the dataframe size and copying it

    useful_df_cluster = useful_df_sites.groupby(by='cluster').agg(lambda x: list(x)).reset_index()
    useful_df_cluster['index_list'] = range(len(useful_df_cluster))

    useful_df_cluster = useful_df_cluster[['index_list'] + list(useful_df_cluster.columns)].to_numpy()
    # indexes: 0=index, 1=cluster, 2=site ids, 3=longitude, 4=latitude

    for clusterA in useful_df_cluster[:-1]:
        # Calculating the distance and returning None if > l_cutoff or the cluster to be replaced
        results = [calc_distances(clusterA, clusterB, l_cutoff) for clusterB in useful_df_cluster[clusterA[0] + 1:] if clusterA[1] != clusterB[1]]
        results = [result for result in results if result != None] # Cleans the None values

        for clusterB_index in results:
            useful_df_cluster[useful_df_cluster[:, 1] == clusterB_index, 1] = clusterA[1] # Replace the clusterB by the clusterA


    for cluster in useful_df_cluster: 
        df_sites.loc[cluster[2], 'cluster'] = cluster[1] # Updates the original dataframe with the new cluster values
            

def CCA(df_sites: pd.DataFrame, d_cutoff: int, l_cutoff: int):
    print("D*:", d_cutoff, "- l:", l_cutoff)
    start = time.time()

    status = np.zeros(lx * ly)
    df_sites, status = d_filter(df_sites, status, d_cutoff)
    percolation(df_sites, status)
    print("L filtering...")
    l_filter(df_sites, l_cutoff)
    print("Writing...")
    write_df_clusters(df_sites, d_cutoff, l_cutoff)

    n_clusters = len(df_sites.cluster.unique())

    end = time.time()
    print("finished in", end - start)

    return n_clusters


if __name__ == "__main__":
    df_sites, lx, ly = pandas_read()

    d_cutoffs = range(60, 501, 10) # List of D* values to run
    processes = 11 # Number of CPU processes to be used
    
    print("running...")
    for d_cutoff in d_cutoffs:
        n_clusters_list = []

        min_l = 2 # The floor of the l range 
        while True:
            max_l = min_l + processes # The ceil of the l range

            l_cutoffs = range(min_l, max_l, 1) 

            params = [(df_sites, d_cutoff, l_cutoff) for l_cutoff in l_cutoffs]
            
            with mp.Pool(processes=processes) as p:
                n_clusters_list.append(p.starmap(CCA, params))

                p.close()
                p.join()

            if 1 in n_clusters_list: # If there is a 1 in the list, the while loop breaks. 
                                     # That means, that in one of the executions, all the sites are in one cluster, so no need to increase l
                break

            min_l = max_l

