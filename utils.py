import numpy as np
from math import radians, sin, cos, asin

R = 6378.137 # Earth's radius in km

def spherical_polygon_area(coords):    
    longitude, latitude = zip(*coords)
    
    longitude = np.radians(longitude)
    latitude = np.radians(latitude)
    
    area = np.sum((np.roll(longitude, -1) - np.roll(longitude, 1)) * np.sin(latitude))
    area = -(R ** 2 / 2) * area
    
    return area


def haversine_distance(latitude1, longitude1, latitude2, longitude2):    
    latitude1, longitude1, latitude2, longitude2 = radians(latitude1), radians(longitude1), radians(latitude2), radians(longitude2)
    
    delta_lat = latitude2 - latitude1
    delta_lon = longitude2 - longitude1
    
    theta = (sin(delta_lat / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(delta_lon / 2) ** 2) ** (1/2)
    
    return 2 * R * asin(theta)