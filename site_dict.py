#This funcion return a dictionary, any item can be added. The keys longitude, latitude and density must be kept.
def build_site(population: int, area: float, longitude: float, latitude: float):
    site = {'population': population,
            'area': area,
            'density': population / area, 
            'latitude': latitude,
            'longitude': longitude
            }

    return site
