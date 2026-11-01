"""Fetch hospital locations from OpenStreetMap (Overpass API) and turn them into our hospital format.

IMPORTANT - what OpenStreetMap does and does NOT tell us
  * It gives: name, location, and (only when mappers added them) phone, address, type, specialities, emergency tag.
  * It does NOT give: live bed, ICU, ventilator or ambulance availability.
  So every imported hospital is stored with verified = 0. The website shows "not verified" instead of numbers
  until an admin checks the information with the hospital and ticks "verified" in the admin dashboard.

Data (c) OpenStreetMap contributors, available under the ODbL licence: https://www.openstreetmap.org/copyright
Overpass API etiquette: do not call it in a loop. Import once, then use the saved copy in our own database.
"""
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
USER_AGENT = "GwaliorHospitalFinder/2.0 (college project; contact: your-email@example.com)"
PHONE_OK = re.compile(r"^[0-9+()\-\s]{5,25}$")


class OsmError(Exception):
    """Readable error for the admin dashboard."""


def build_query(lat, lng, radius_m):
    around = f"(around:{int(radius_m)},{lat},{lng})"
    return (
        "[out:json][timeout:50];\n"
        "(\n"
        f'  node["amenity"="hospital"]{around};\n'
        f'  way["amenity"="hospital"]{around};\n'
        f'  relation["amenity"="hospital"]{around};\n'
        ");\n"
        "out center tags;"
    )


def fetch_overpass(lat, lng, radius_m=15000, timeout=90):
    """Ask the Overpass API for hospitals around a point. Returns the list of OSM elements.
    Tries every server twice (they are sometimes busy) and reports the REAL reason when everything fails."""
    body = urllib.parse.urlencode({"data": build_query(lat, lng, radius_m)}).encode()
    problems = []
    for attempt in range(2):
        for url in OVERPASS_URLS:
            request = urllib.request.Request(url, data=body, headers={
                "User-Agent": USER_AGENT, "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"})
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                return data.get("elements", [])
            except urllib.error.HTTPError as e:
                problems.append(f"{url.split('/')[2]}: HTTP {e.code} {e.reason}")
            except ssl.SSLError as e:
                problems.append(f"{url.split('/')[2]}: SSL problem ({e})")
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                problems.append(f"{url.split('/')[2]}: {getattr(e, 'reason', e)}")
        if attempt == 0:
            time.sleep(3)
    raise OsmError("The server could not download from OpenStreetMap. Reasons: " + "; ".join(dict.fromkeys(problems)))


def _address(tags):
    parts = [tags.get("addr:housenumber"), tags.get("addr:street"), tags.get("addr:suburb"),
             tags.get("addr:city"), tags.get("addr:postcode")]
    text = ", ".join(p.strip() for p in parts if p and p.strip())
    return text[:200] if text else "Address not listed on OpenStreetMap"


def _phone(tags):
    raw = tags.get("phone") or tags.get("contact:phone") or ""
    first = raw.split(";")[0].strip()
    return first if PHONE_OK.match(first) else ""


def _type(tags):
    operator_type = (tags.get("operator:type") or "").lower()
    operator = (tags.get("operator") or "").lower()
    if operator_type in ("government", "public") or "government" in operator or "govt" in operator:
        return "Government"
    if operator_type == "private":
        return "Private"
    if operator_type in ("charitable", "religious", "community", "ngo"):
        return "Trust"
    speciality = (tags.get("healthcare:speciality") or "").lower()
    if speciality and speciality not in ("general", "general;internal"):
        return "Specialty"
    return "Unknown"


def _services(tags):
    found = []
    for s in (tags.get("healthcare:speciality") or "").split(";"):
        s = s.strip().replace("_", " ").capitalize()
        if s and len(s) <= 40 and s not in found:
            found.append(s)
    return found[:10]


def parse_elements(elements):
    """OSM elements -> (hospitals, skipped_count). Unnamed or position-less elements are skipped."""
    hospitals, skipped, seen = [], 0, set()
    for el in elements:
        if not isinstance(el, dict):
            skipped += 1
            continue
        tags = el.get("tags")
        tags = {str(k): str(v) for k, v in tags.items()} if isinstance(tags, dict) else {}
        name = (tags.get("name") or tags.get("name:en") or "").strip()
        center = el.get("center") or {}
        lat = el.get("lat", center.get("lat"))
        lng = el.get("lon", center.get("lon"))
        osm_id = f"{el.get('type')}/{el.get('id')}"
        if not name or lat is None or lng is None or osm_id in seen:
            skipped += 1
            continue
        try:
            lat, lng = float(lat), float(lng)
        except (TypeError, ValueError):
            skipped += 1
            continue
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            skipped += 1
            continue
        seen.add(osm_id)
        hospitals.append({
            "osm_id": osm_id, "name": name[:120], "lat": lat, "lng": lng,
            "address": _address(tags), "phone": _phone(tags), "type": _type(tags),
            "emergency": (tags.get("emergency") or "").lower() == "yes",
            "services": _services(tags),
        })
    return hospitals, skipped


if __name__ == "__main__":
    # Diagnostic:  python osm_import.py    -> shows whether this computer can reach OpenStreetMap
    try:
        found, skipped = parse_elements(fetch_overpass(26.2183, 78.1828, 15000))
        print(f"OK: {len(found)} hospitals found ({skipped} skipped). First ones:")
        for h in found[:10]:
            print(" -", h["name"], h["lat"], h["lng"])
    except OsmError as e:
        print("FAILED:", e)