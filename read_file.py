from utils import *
import site_dict as site
import pickle
import os
import pandas as pd

path = "./data/"
filename = "GPW_IBGE_BRASIL.dat"

# The fuction must return a DataFrame (representing the complete grid), number of rows and number of columns, in this order. 

def pandas_read():
    if not os.path.exists(f'{path}/sites_util.pkl'):
        with open(path + filename, 'r') as f:
            line = f.readline()
            field = line.split()

            lx = int(field[0]) # Number of rows
            ly = int(field[1]) # Number of columns

            grid = [[0 for _ in range(lx)] for _ in range(ly)] # Builds the grid

            lon_nw = float(field[2]) # Northwest longitude
            lat_nw = float(field[3]) # Northwest latitude
            delta = 0.00833333#float(field[4]) # Distance between centroids of two sites in degrees

            for line in f:
                field = line.split()

                i = int(field[0]) # column
                j = int(field[1]) # row
                population = float(field[2])

                lon_k_nw = lon_nw + delta * i
                lat_k_nw = lat_nw - delta * j

                coords=[(lon_k_nw, lat_k_nw), # Coordinates of the site
                        (lon_k_nw, lat_k_nw - delta),
                        (lon_k_nw + delta, lat_k_nw - delta),
                        (lon_k_nw + delta, lat_k_nw)]

                longitude = float(lon_k_nw + delta / 2)
                latitude = float(lat_k_nw - delta / 2)
                area = float(spherical_polygon_area(coords)) # Calculates the area of the site
                

                site_info = site.build_site(population=population, area=area, longitude=longitude, latitude=latitude) # Check this function
                site_info['x'] = i
                site_info['y'] = j
                grid[j][i] = site_info

            sites_infos_list = np.array(grid).ravel().tolist()
            fill_infos = lambda x: site.build_site(0, 1, 0, 0) if x == 0 else x # Even if the area doesn't exist, it must be created to populate the dataframe
            sites_infos_list = list(map(fill_infos, sites_infos_list))
            
            df_sites = pd.DataFrame(sites_infos_list)

            with open(f"{path}/sites_util.pkl", 'wb') as f:
                pickle.dump([df_sites, lx, ly], f)

    else:
        with open(f"{path}/sites_util.pkl", 'rb') as f:
            df_sites, lx, ly = pickle.load(f)
    
    return df_sites, lx, ly
