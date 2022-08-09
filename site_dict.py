def build_site(population: int, area: float, longitude: float, latitude: float):
    site = {'population': population,
            'area': area,
            'density': population / area, 
            'latitude': latitude,
            'longitude': longitude
            }

    return site