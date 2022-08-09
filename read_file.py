from utils import *
import site_dict as site
import pickle
import os
import pandas as pd

path = "./data/"
filename = "GPW_IBGE_BRASIL.dat"

def pandas_read():
    if not os.path.exists(f'{path}/sites_util.pkl'):
        with open(path + filename, 'r') as f:
            line = f.readline()
            field = line.split()

            lx = int(field[0])
            ly = int(field[1])

            grid = [[0 for _ in range(lx)] for _ in range(ly)]

            lon_nw = float(field[2])
            lat_nw = float(field[3])
            delta = 0.00833333#float(field[4])

            for line in f:
                field = line.split()

                i = int(field[0]) # column
                j = int(field[1]) # row
                population = float(field[2])

                lon_k_nw = lon_nw + delta * i
                lat_k_nw = lat_nw - delta * j

                coords=[(lon_k_nw, lat_k_nw),
                        (lon_k_nw, lat_k_nw - delta),
                        (lon_k_nw + delta, lat_k_nw - delta),
                        (lon_k_nw + delta, lat_k_nw)]

                longitude = float(lon_k_nw + delta / 2)
                latitude = float(lat_k_nw - delta / 2)
                area = float(spherical_polygon_area(coords))
                

                site_info = site.build_site(population=population, area=area, longitude=longitude, latitude=latitude)
                site_info['x'] = i
                site_info['y'] = j
                grid[j][i] = site_info

            sites_infos_list = np.array(grid).ravel().tolist()
            fill_infos = lambda x: site.build_site(0, 1, 0, 0) if x == 0 else x
            sites_infos_list = list(map(fill_infos, sites_infos_list))
            
            df_sites = pd.DataFrame(sites_infos_list)

            with open(f"{path}/sites_util.pkl", 'wb') as f:
                pickle.dump([df_sites, lx, ly], f)

    else:
        with open(f"{path}/sites_util.pkl", 'rb') as f:
            df_sites, lx, ly = pickle.load(f)

    return df_sites, lx, ly