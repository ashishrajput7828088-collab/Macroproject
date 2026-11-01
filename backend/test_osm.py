"""Offline test of the OpenStreetMap importer (no internet needed): feeds it a made-up Overpass answer.
Run:  python test_osm.py"""
from osm_import import parse_elements, build_query

sample = [
    {"type": "node", "id": 1, "lat": 26.22, "lon": 78.18,
     "tags": {"amenity": "hospital", "name": "Test Govt Hospital", "operator:type": "government",
              "emergency": "yes", "phone": "+91 751 1234567; +91 751 7654321", "addr:street": "Fort Road", "addr:city": "Gwalior"}},
    {"type": "way", "id": 2, "center": {"lat": 26.25, "lon": 78.2},
     "tags": {"amenity": "hospital", "name": "Test Private Heart Hospital", "operator:type": "private",
              "healthcare:speciality": "cardiology;general"}},
    {"type": "node", "id": 3, "lat": 26.2, "lon": 78.1, "tags": {"amenity": "hospital"}},             # no name -> skipped
    {"type": "relation", "id": 4, "tags": {"amenity": "hospital", "name": "No position"}},            # no position -> skipped
    {"type": "node", "id": 5, "lat": 26.3, "lon": 78.3, "tags": {"name": "Weird <b>phone</b>", "phone": "call me"}},
]
hospitals, skipped = parse_elements(sample)
assert skipped == 2 and len(hospitals) == 3, (len(hospitals), skipped)
a, b, c = hospitals
assert a["type"] == "Government" and a["emergency"] and a["phone"] == "+91 751 1234567" and a["osm_id"] == "node/1"
assert "Fort Road" in a["address"]
assert b["type"] == "Private" and (b["lat"], b["lng"]) == (26.25, 78.2) and "Cardiology" in b["services"]
assert c["phone"] == "" and c["type"] == "Unknown" and c["address"].startswith("Address not listed")
assert "around:15000" in build_query(26.2183, 78.1828, 15000)
print("OSM PARSER TESTS PASSED")
