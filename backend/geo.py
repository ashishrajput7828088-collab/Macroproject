"""Distance helpers shared by every algorithm."""
import math

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lng1, lat2, lng2):
    """Straight-line (great-circle) distance between two lat/lng points, in km."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat, dlng = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def to_xy_km(lat, lng, ref_lat):
    """Flatten lat/lng into x/y kilometres (equirectangular projection).
    Accurate enough for city-sized areas, and lets the trees use simple 2D maths."""
    x = math.radians(lng) * EARTH_RADIUS_KM * math.cos(math.radians(ref_lat))
    y = math.radians(lat) * EARTH_RADIUS_KM
    return x, y