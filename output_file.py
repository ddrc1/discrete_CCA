import os

path = "./data"

if not os.path.exists(f"{path}/output"):
    os.mkdir(f"{path}/output")


def write_df_clusters(df_sites, d_cutoff, l_cutoff):
    if not os.path.exists(f'{path}/output/d{d_cutoff}'):
        os.mkdir(f'{path}/output/d{d_cutoff}')
        
    df_sites.to_csv(f"{path}/output/d{d_cutoff}/d{d_cutoff}_l{l_cutoff}.csv")