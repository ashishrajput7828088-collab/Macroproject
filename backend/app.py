"""Arogya Gwalior - Enterprise Healthcare, Hospital Network & Emergency API Backend
Production-Grade Flask Backend with Spatial DSA Indexing (KD-Tree & Quadtree),
Online Appointment Booking Engine, Real-time Blood Bank & Ambulance Tracking,
Clinical AI Triage Assistant, and Mapbox GIS Integration.
"""
import json
import math
import os
import random
import secrets
import threading
import time
from urllib.parse import urlsplit
import urllib.request
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

from ai_assistant import GeminiApiError, call_gemini_api, gemini_api_configured, offline_triage
from config import (
    FRONTEND_DIR, JSON_EXPORT_PATH, SECRET_KEY_PATH, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD,
    DEFAULT_MAPBOX_KEY, DEFAULT_CENTER_LAT, DEFAULT_CENTER_LNG,
)
from database import get_db, init_tables, now_iso
from geo import haversine_km, to_xy_km
from kdtree import KDTree
from osm_import import OsmError, fetch_overpass, parse_elements
from quadtree import Quadtree

BED_KEYS = ("general", "icu", "emergency", "oxygen", "ventilator")
ALGORITHMS = ("kdtree", "quadtree", "linear")
FRONTEND_FILES = (
    "index.html", "style.css", "script.js", "hospitals-data.js",
    "admin.html", "admin.js", "lab.js", "config.js"
)

def session_secret():
    configured = os.environ.get("SECRET_KEY")
    if configured:
        return configured
    try:
        existing = SECRET_KEY_PATH.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    except FileNotFoundError:
        pass
    value = secrets.token_urlsafe(48)
    SECRET_KEY_PATH.write_text(value, encoding="utf-8")
    return value


app = Flask(__name__, static_folder=None)
app.config.update(
    SECRET_KEY=session_secret(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
)
app.json.sort_keys = False

# CORS Configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Spatial Index State
STATE_LOCK = threading.RLock()
STATE = {"all": [], "active": [], "by_id": {}, "ref_lat": DEFAULT_CENTER_LAT, "entries": [], "kd": None, "quad": None}

def to_xy(h, ref_lat):
    return to_xy_km(h["lat"], h["lng"], ref_lat)

def planar(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def read_all_hospitals_from_db():
    conn = get_db()
    try:
        services, beds = {}, {}
        for r in conn.execute("SELECT hospital_id, service FROM services ORDER BY rowid"):
            services.setdefault(r["hospital_id"], []).append(r["service"])
        for r in conn.execute("SELECT hospital_id, bed_type, total, occupied FROM beds"):
            beds.setdefault(r["hospital_id"], {})[r["bed_type"]] = [r["total"], r["occupied"]]

        rows = conn.execute("SELECT * FROM hospitals ORDER BY rating DESC, id ASC").fetchall()
        result = []
        for r in rows:
            keys = r.keys()
            hb = beds.get(r["id"], {})
            result.append({
                "id": r["id"],
                "name": r["name"],
                "type": r["type"],
                "category": r["category"] if "category" in keys else "Multispeciality",
                "address": r["address"],
                "locality": r["locality"] if "locality" in keys else "Gwalior",
                "phone": r["phone"],
                "emergencyPhone": r["emergency_phone"] if "emergency_phone" in keys and r["emergency_phone"] else r["phone"],
                "ambulancePhone": r["ambulance_phone"] if "ambulance_phone" in keys and r["ambulance_phone"] else "108",
                "email": r["email"] if "email" in keys else "",
                "website": r["website"] if "website" in keys else "",
                "lat": r["lat"],
                "lng": r["lng"],
                "emergency24x7": bool(r["emergency_24x7"]),
                "traumaCenter": bool(r["trauma_center"]) if "trauma_center" in keys else False,
                "rating": float(r["rating"]) if "rating" in keys and r["rating"] else 4.6,
                "reviewsCount": int(r["reviews_count"]) if "reviews_count" in keys and r["reviews_count"] else 150,
                "opdTimings": r["opd_timings"] if "opd_timings" in keys and r["opd_timings"] else "09:00 AM - 05:00 PM",
                "consultationFee": int(r["consultation_fee"]) if "consultation_fee" in keys and r["consultation_fee"] is not None else 500,
                "description": r["description"] if "description" in keys and r["description"] else "",
                "verified": bool(r["verified"]) if "verified" in keys else True,
                "active": bool(r["active"]) if "active" in keys else True,
                "source": r["source"] if "source" in keys else "real",
                "photoUrl": r["photo_url"] if "photo_url" in keys and r["photo_url"] else "",
                "photoCredit": r["photo_credit"] if "photo_credit" in keys and r["photo_credit"] else "",
                "services": services.get(r["id"], []),
                "beds": {k: hb.get(k, [0, 0]) for k in BED_KEYS},
                "lastUpdated": r["updated_at"] if "updated_at" in keys else now_iso()
            })
        return result
    finally:
        conn.close()

def refresh_state():
    hospitals = read_all_hospitals_from_db()
    active = [h for h in hospitals if h["active"]]
    ref_lat = sum(h["lat"] for h in active) / len(active) if active else DEFAULT_CENTER_LAT

    entries = [(to_xy(h, ref_lat), h["id"]) for h in active]
    kd = KDTree(entries) if entries else None
    quad = Quadtree(entries) if entries else None

    new_state = {
        "all": hospitals,
        "active": active,
        "by_id": {h["id"]: h for h in active},
        "ref_lat": ref_lat,
        "entries": entries,
        "kd": kd,
        "quad": quad
    }

    with STATE_LOCK:
        STATE.update(new_state)
        try:
            JSON_EXPORT_PATH.write_text(json.dumps(hospitals, indent=2), encoding="utf-8")
        except OSError:
            pass

def json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}

def parse_finite_float(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("A finite number is required")
    return parsed

def validate_coordinates(lat, lng):
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        raise ValueError("Coordinates are outside the valid latitude/longitude range")

def parse_integer(value):
    if isinstance(value, bool):
        raise ValueError("An integer is required")
    try:
        if isinstance(value, float) and (not math.isfinite(value) or not value.is_integer()):
            raise ValueError("An integer is required")
        return int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("An integer is required") from error

# =====================================================================
# 1. System Config & Health APIs
# =====================================================================
@app.get("/api/health")
def health():
    with STATE_LOCK:
        hosp_count = len(STATE["active"])
    return jsonify(
        status="ok",
        system="Arogya Gwalior Enterprise API",
        hospitalsCount=hosp_count,
        algorithms=ALGORITHMS,
        defaultCenter={"lat": DEFAULT_CENTER_LAT, "lng": DEFAULT_CENTER_LNG},
        timestamp=now_iso()
    )

@app.get("/api/config")
def get_config():
    return jsonify(
        mapboxAccessToken=DEFAULT_MAPBOX_KEY,
        city="Gwalior, Madhya Pradesh",
        defaultCoordinates={"lat": DEFAULT_CENTER_LAT, "lng": DEFAULT_CENTER_LNG},
        emergencyHotlines={
            "ambulance": "108",
            "policeMedical": "112",
            "womenHelpline": "1090",
            "jahTrauma": "0751-2403222",
            "bimrEmergency": "0751-2405605",
            "chriEmergency": "0751-2415125"
        }
    )

# =====================================================================
# 1B. Admin directory management
# =====================================================================
def admin_error():
    if session.get("admin_username"):
        return None
    return jsonify(error="Admin login required"), 401


@app.post("/api/admin/login")
def admin_login():
    data = json_body()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    conn = get_db()
    try:
        row = conn.execute("SELECT username, password_hash FROM admins WHERE username = ?", (username,)).fetchone()
    finally:
        conn.close()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify(error="Username or password is incorrect"), 401
    session.clear()
    session["admin_username"] = row["username"]
    session.permanent = True
    return jsonify(loggedIn=True)


@app.get("/api/admin/me")
def admin_me():
    username = session.get("admin_username")
    if not username:
        return jsonify(loggedIn=False)
    conn = get_db()
    try:
        row = conn.execute("SELECT password_hash FROM admins WHERE username = ?", (username,)).fetchone()
    finally:
        conn.close()
    if not row:
        session.pop("admin_username", None)
        return jsonify(loggedIn=False)
    default_password = (
        username == DEFAULT_ADMIN_USER
        and check_password_hash(row["password_hash"], DEFAULT_ADMIN_PASSWORD)
    )
    return jsonify(loggedIn=True, defaultPassword=default_password)


@app.post("/api/admin/logout")
def admin_logout():
    session.pop("admin_username", None)
    return jsonify(loggedIn=False)


@app.post("/api/admin/password")
def admin_change_password():
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    data = json_body()
    current = str(data.get("current", ""))
    new_password = str(data.get("new", ""))
    if len(new_password) < 8 or len(new_password) > 128:
        return jsonify(error="New password must be between 8 and 128 characters"), 400
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT password_hash FROM admins WHERE username = ?",
            (session["admin_username"],),
        ).fetchone()
        if not row or not check_password_hash(row["password_hash"], current):
            return jsonify(error="Current password is incorrect"), 400
        conn.execute(
            "UPDATE admins SET password_hash = ? WHERE username = ?",
            (generate_password_hash(new_password), session["admin_username"]),
        )
        conn.commit()
    finally:
        conn.close()
    return jsonify(changed=True)


def parse_hospital_payload(data):
    name = str(data.get("name", "")).strip()
    hospital_type = str(data.get("type", "Unknown")).strip()
    address = str(data.get("address", "")).strip()
    phone = str(data.get("phone", "")).strip()
    if not name or len(name) > 120:
        raise ValueError("Hospital name is required and must be at most 120 characters")
    if hospital_type not in ("Government", "Private", "Trust", "Specialty", "Unknown"):
        raise ValueError("Choose a valid hospital type")
    if not address or len(address) > 200:
        raise ValueError("Address is required and must be at most 200 characters")
    if not phone or len(phone) > 25:
        raise ValueError("Phone number is required and must be at most 25 characters")
    lat = parse_finite_float(data.get("lat"))
    lng = parse_finite_float(data.get("lng"))
    validate_coordinates(lat, lng)

    photo_url = str(data.get("photoUrl", data.get("photo_url", ""))).strip()
    photo_credit = str(data.get("photoCredit", data.get("photo_credit", ""))).strip()
    if photo_url:
        parsed_photo_url = urlsplit(photo_url)
        if parsed_photo_url.scheme != "https" or not parsed_photo_url.netloc:
            raise ValueError("Photo URL must use HTTPS")
    if len(photo_url) > 1000 or len(photo_credit) > 200:
        raise ValueError("Photo URL or credit is too long")

    services = data.get("services", [])
    if not isinstance(services, list) or len(services) > 30:
        raise ValueError("Services must be a list of at most 30 entries")
    clean_services = []
    for service in services:
        value = str(service).strip()
        if value and len(value) <= 80 and value.casefold() not in {s.casefold() for s in clean_services}:
            clean_services.append(value)

    beds = data.get("beds", {})
    if not isinstance(beds, dict):
        raise ValueError("Bed details must be an object")
    clean_beds = {}
    for bed_type in BED_KEYS:
        values = beds.get(bed_type, [0, 0])
        if not isinstance(values, (list, tuple)) or len(values) != 2:
            raise ValueError(f"Invalid {bed_type} bed details")
        total, occupied = (parse_integer(value) for value in values)
        if not 0 <= occupied <= total <= 100000:
            raise ValueError(f"Invalid {bed_type} bed counts")
        clean_beds[bed_type] = (total, occupied)

    return {
        "name": name, "type": hospital_type, "address": address, "phone": phone,
        "lat": lat, "lng": lng, "photo_url": photo_url, "photo_credit": photo_credit,
        "emergency_phone": str(data.get("emergencyPhone", data.get("emergency_phone", phone))).strip()[:25] or phone,
        "emergency_24x7": int(bool(data.get("emergency24x7", data.get("emergency_24x7", False)))),
        "verified": int(bool(data.get("verified", False))),
        "active": int(bool(data.get("active", True))),
        "services": clean_services, "beds": clean_beds,
    }


def save_hospital_relations(conn, hospital_id, hospital):
    conn.execute("DELETE FROM services WHERE hospital_id = ?", (hospital_id,))
    conn.execute("DELETE FROM beds WHERE hospital_id = ?", (hospital_id,))
    conn.executemany(
        "INSERT INTO services (hospital_id, service) VALUES (?, ?)",
        [(hospital_id, service) for service in hospital["services"]],
    )
    conn.executemany(
        "INSERT INTO beds (hospital_id, bed_type, total, occupied) VALUES (?, ?, ?, ?)",
        [(hospital_id, bed_type, values[0], values[1]) for bed_type, values in hospital["beds"].items()],
    )


@app.get("/api/admin/hospitals")
def admin_list_hospitals():
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    return jsonify(read_all_hospitals_from_db())


@app.post("/api/admin/hospitals")
def admin_create_hospital():
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    try:
        hospital = parse_hospital_payload(json_body())
    except (TypeError, ValueError) as error:
        return jsonify(error=str(error)), 400
    conn = get_db()
    try:
        cursor = conn.execute("""
            INSERT INTO hospitals (
                name, type, category, address, locality, phone, emergency_phone, lat, lng,
                emergency_24x7, rating, reviews_count, description, verified, active,
                source, photo_url, photo_credit, updated_at
            ) VALUES (?, ?, 'Multispeciality', ?, 'Gwalior', ?, ?, ?, ?, ?, 0, 0, '',
                      ?, ?, 'manual', ?, ?, ?)
        """, (
            hospital["name"], hospital["type"], hospital["address"], hospital["phone"],
            hospital["emergency_phone"], hospital["lat"], hospital["lng"],
            hospital["emergency_24x7"], hospital["verified"], hospital["active"],
            hospital["photo_url"], hospital["photo_credit"], now_iso(),
        ))
        hospital_id = cursor.lastrowid
        save_hospital_relations(conn, hospital_id, hospital)
        conn.commit()
    finally:
        conn.close()
    refresh_state()
    return jsonify(id=hospital_id, created=True), 201


@app.route("/api/admin/hospitals/<int:hospital_id>", methods=["PUT", "DELETE"])
def admin_update_or_delete_hospital(hospital_id):
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    conn = get_db()
    try:
        existing = conn.execute("SELECT * FROM hospitals WHERE id = ?", (hospital_id,)).fetchone()
        if not existing:
            return jsonify(error="Hospital not found"), 404
        if request.method == "DELETE":
            conn.execute("DELETE FROM hospitals WHERE id = ?", (hospital_id,))
            conn.commit()
            refresh_state()
            return jsonify(deleted=True)

        try:
            hospital = parse_hospital_payload(json_body())
        except (TypeError, ValueError) as error:
            return jsonify(error=str(error)), 400
        conn.execute("""
            UPDATE hospitals SET name = ?, type = ?, address = ?, phone = ?, emergency_phone = ?,
                lat = ?, lng = ?, emergency_24x7 = ?, verified = ?, active = ?, photo_url = ?,
                photo_credit = ?, updated_at = ? WHERE id = ?
        """, (
            hospital["name"], hospital["type"], hospital["address"], hospital["phone"],
            hospital["emergency_phone"], hospital["lat"], hospital["lng"],
            hospital["emergency_24x7"], hospital["verified"], hospital["active"],
            hospital["photo_url"], hospital["photo_credit"], now_iso(), hospital_id,
        ))
        save_hospital_relations(conn, hospital_id, hospital)
        conn.commit()
    finally:
        conn.close()
    refresh_state()
    return jsonify(id=hospital_id, updated=True)


def import_osm_hospitals(elements):
    records, skipped = parse_elements(elements)
    conn = get_db()
    added = updated = kept_verified = 0
    try:
        for record in records:
            existing = conn.execute("SELECT id, verified FROM hospitals WHERE osm_id = ?", (record["osm_id"],)).fetchone()
            if existing:
                conn.execute("""
                    UPDATE hospitals SET name = ?, type = ?, address = ?, lat = ?, lng = ?,
                        phone = CASE WHEN ? = '' THEN phone ELSE ? END,
                        emergency_phone = CASE WHEN ? = '' THEN emergency_phone ELSE ? END,
                        emergency_24x7 = ?, updated_at = ? WHERE id = ?
                """, (
                    record["name"], record["type"], record["address"], record["lat"], record["lng"],
                    record["phone"], record["phone"], record["phone"], record["phone"],
                    int(record["emergency"]), now_iso(), existing["id"],
                ))
                if existing["verified"]:
                    kept_verified += 1
                else:
                    updated += 1
                hospital_id = existing["id"]
            else:
                same_name = conn.execute(
                    "SELECT id, osm_id FROM hospitals WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) LIMIT 1",
                    (record["name"],),
                ).fetchone()
                if same_name:
                    if not same_name["osm_id"]:
                        conn.execute("UPDATE hospitals SET osm_id = ? WHERE id = ?", (record["osm_id"], same_name["id"]))
                    kept_verified += 1
                    continue
                phone = record["phone"] or "Not listed"
                cursor = conn.execute("""
                    INSERT INTO hospitals (
                        name, type, category, address, locality, phone, emergency_phone,
                        lat, lng, emergency_24x7, trauma_center, rating, reviews_count,
                        consultation_fee, description, verified, active, source, osm_id, updated_at
                    ) VALUES (?, ?, 'Hospital', ?, 'Gwalior', ?, ?, ?, ?, ?, 0, 0, 0, 0, '',
                              0, 1, 'osm', ?, ?)
                """, (
                    record["name"], record["type"], record["address"], phone, phone,
                    record["lat"], record["lng"], int(record["emergency"]),
                    record["osm_id"], now_iso(),
                ))
                hospital_id = cursor.lastrowid
                added += 1
            if record["services"]:
                conn.execute("DELETE FROM services WHERE hospital_id = ?", (hospital_id,))
                conn.executemany(
                    "INSERT INTO services (hospital_id, service) VALUES (?, ?)",
                    [(hospital_id, service) for service in record["services"]],
                )
        conn.commit()
    finally:
        conn.close()
    refresh_state()
    return {
        "found": len(records), "added": added, "updated": updated,
        "keptVerified": kept_verified, "skippedUnnamed": skipped,
    }


@app.post("/api/admin/osm/import")
def admin_import_osm():
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    try:
        radius_km = parse_integer(json_body().get("radiusKm", 15))
        if not 1 <= radius_km <= 30:
            raise ValueError("radiusKm must be between 1 and 30")
        elements = fetch_overpass(DEFAULT_CENTER_LAT, DEFAULT_CENTER_LNG, radius_km * 1000)
        return jsonify(import_osm_hospitals(elements))
    except (TypeError, ValueError) as error:
        return jsonify(error=str(error)), 400
    except OsmError as error:
        return jsonify(error=str(error)), 502


@app.post("/api/admin/osm/import-elements")
def admin_import_osm_elements():
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    elements = json_body().get("elements")
    if not isinstance(elements, list) or len(elements) > 5000:
        return jsonify(error="elements must be a list containing at most 5000 records"), 400
    try:
        return jsonify(import_osm_hospitals(elements))
    except (TypeError, ValueError) as error:
        return jsonify(error=str(error)), 400


def parse_doctor_payload(data):
    name = str(data.get("name", "")).strip()
    qualification = str(data.get("qualification", "")).strip()
    specialty = str(data.get("specialty", "")).strip()
    category = str(data.get("category", "")).strip().lower()
    phone = str(data.get("phone", "")).strip()
    hospital_name = str(data.get("hospitalName", data.get("hospital_name", ""))).strip()
    clinic_address = str(data.get("clinicAddress", data.get("clinic_address", ""))).strip()
    opd_timings = str(data.get("opdTimings", data.get("opd_timings", ""))).strip()
    if not name or len(name) > 120:
        raise ValueError("Doctor name is required and must be at most 120 characters")
    if not qualification or len(qualification) > 160:
        raise ValueError("Qualification is required and must be at most 160 characters")
    if not specialty or len(specialty) > 120:
        raise ValueError("Specialty is required and must be at most 120 characters")
    if category not in {
        "general", "cardiology", "orthopedics", "gynecology", "pediatrics",
        "neurology", "ophthalmology", "oncology", "pulmonology", "dermatology", "gastro",
    }:
        raise ValueError("Choose a valid doctor category")
    if not phone or len(phone) > 25:
        raise ValueError("Phone number is required and must be at most 25 characters")
    if not hospital_name or len(hospital_name) > 120:
        raise ValueError("Hospital or clinic name is required")
    if not clinic_address or len(clinic_address) > 200:
        raise ValueError("Clinic address is required")
    if not opd_timings or len(opd_timings) > 120:
        raise ValueError("OPD timings are required")
    experience = parse_integer(data.get("experienceYears", data.get("experience_years", 0)))
    fee = parse_integer(data.get("fee", 0))
    if not 0 <= experience <= 80 or not 0 <= fee <= 100000:
        raise ValueError("Experience or consultation fee is outside the allowed range")
    hospital_id = data.get("hospitalId", data.get("hospital_id"))
    if hospital_id in ("", None):
        hospital_id = None
    else:
        hospital_id = parse_integer(hospital_id)
    about = str(data.get("about", "")).strip()
    if len(about) > 1000:
        raise ValueError("About section must be at most 1000 characters")
    return {
        "name": name, "qualification": qualification, "specialty": specialty,
        "category": category, "experience_years": experience, "hospital_id": hospital_id,
        "hospital_name": hospital_name, "clinic_address": clinic_address,
        "phone": phone, "opd_timings": opd_timings,
        "days_available": str(data.get("daysAvailable", data.get("days_available", "Mon - Sat"))).strip()[:80],
        "fee": fee, "about": about, "verified": int(bool(data.get("verified", False))),
        "badge": "Verified Doctor" if data.get("verified", False) else "Profile pending verification",
    }


@app.route("/api/admin/doctors", methods=["GET", "POST"])
def admin_list_or_create_doctors():
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    if request.method == "GET":
        conn = get_db()
        try:
            doctors = conn.execute("SELECT * FROM doctors ORDER BY name COLLATE NOCASE").fetchall()
            return jsonify([dict(row) for row in doctors])
        finally:
            conn.close()
    try:
        doctor = parse_doctor_payload(json_body())
    except (TypeError, ValueError) as error:
        return jsonify(error=str(error)), 400
    conn = get_db()
    try:
        if doctor["hospital_id"] is not None:
            hospital = conn.execute(
                "SELECT name, address FROM hospitals WHERE id = ?",
                (doctor["hospital_id"],),
            ).fetchone()
            if not hospital:
                return jsonify(error="Selected hospital was not found"), 400
            doctor["hospital_name"] = hospital["name"]
            doctor["clinic_address"] = hospital["address"]
        cursor = conn.execute("""
            INSERT INTO doctors (
                name, qualification, specialty, category, experience_years, hospital_id,
                hospital_name, clinic_address, phone, opd_timings, days_available, fee,
                badge, about, verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(doctor[key] for key in (
            "name", "qualification", "specialty", "category", "experience_years",
            "hospital_id", "hospital_name", "clinic_address", "phone", "opd_timings",
            "days_available", "fee", "badge", "about", "verified",
        )))
        doctor_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()
    return jsonify(id=doctor_id, created=True), 201


@app.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT", "DELETE"])
def admin_update_or_delete_doctor(doctor_id):
    unauthorized = admin_error()
    if unauthorized:
        return unauthorized
    conn = get_db()
    try:
        if not conn.execute("SELECT id FROM doctors WHERE id = ?", (doctor_id,)).fetchone():
            return jsonify(error="Doctor not found"), 404
        if request.method == "DELETE":
            conn.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
            conn.commit()
            return jsonify(deleted=True)
        try:
            doctor = parse_doctor_payload(json_body())
        except (TypeError, ValueError) as error:
            return jsonify(error=str(error)), 400
        if doctor["hospital_id"] is not None:
            hospital = conn.execute(
                "SELECT name, address FROM hospitals WHERE id = ?",
                (doctor["hospital_id"],),
            ).fetchone()
            if not hospital:
                return jsonify(error="Selected hospital was not found"), 400
            doctor["hospital_name"] = hospital["name"]
            doctor["clinic_address"] = hospital["address"]
        conn.execute("""
            UPDATE doctors SET name = ?, qualification = ?, specialty = ?, category = ?,
                experience_years = ?, hospital_id = ?, hospital_name = ?, clinic_address = ?,
                phone = ?, opd_timings = ?, days_available = ?, fee = ?, badge = ?,
                about = ?, verified = ? WHERE id = ?
        """, tuple(doctor[key] for key in (
            "name", "qualification", "specialty", "category", "experience_years",
            "hospital_id", "hospital_name", "clinic_address", "phone", "opd_timings",
            "days_available", "fee", "badge", "about", "verified",
        )) + (doctor_id,))
        conn.commit()
    finally:
        conn.close()
    return jsonify(id=doctor_id, updated=True)

# =====================================================================
# 2. Hospitals & Spatial Search APIs
# =====================================================================
@app.get("/api/hospitals")
def get_hospitals():
    q = request.args.get("q", "").lower().strip()
    h_type = request.args.get("type", "all").strip()
    emergency_only = request.args.get("emergency") == "1"

    with STATE_LOCK:
        list_h = list(STATE["active"])

    if h_type and h_type != "all":
        list_h = [h for h in list_h if h["type"].lower() == h_type.lower()]
    if emergency_only:
        list_h = [h for h in list_h if h["emergency24x7"]]
    if q:
        list_h = [
            h for h in list_h if
            q in h["name"].lower() or
            q in h["address"].lower() or
            q in h.get("locality", "").lower() or
            any(q in s.lower() for s in h["services"])
        ]
    return jsonify(list_h)

@app.get("/api/hospitals/<int:hospital_id>")
def get_hospital_details(hospital_id):
    with STATE_LOCK:
        h = STATE["by_id"].get(hospital_id)
    if not h:
        return jsonify(error="Hospital not found"), 404

    # Fetch associated doctors
    conn = get_db()
    try:
        doc_rows = conn.execute("SELECT * FROM doctors WHERE hospital_id = ?", (hospital_id,)).fetchall()
        doctors = [dict(r) for r in doc_rows]
    finally:
        conn.close()

    return jsonify({**h, "affiliatedDoctors": doctors})

@app.get("/api/hospitals/nearby")
def nearby_hospitals():
    try:
        lat = parse_finite_float(request.args["lat"])
        lng = parse_finite_float(request.args["lng"])
        radius = parse_finite_float(request.args.get("radius", 5.0))
        algo = request.args.get("algorithm", "kdtree").lower()
        validate_coordinates(lat, lng)
        if radius <= 0:
            raise ValueError("Radius must be greater than zero")
        if algo not in ALGORITHMS:
            raise ValueError("Unsupported search algorithm")
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Valid lat, lng and radius required"), 400

    with STATE_LOCK:
        entries = STATE["entries"]
        ref_lat = STATE["ref_lat"]
        by_id = STATE["by_id"]
        tree = STATE["kd"] if algo == "kdtree" else STATE["quad"]

    stats = {"nodes": 0, "points": 0}
    start = time.perf_counter()
    center_xy = to_xy_km(lat, lng, ref_lat)

    if algo == "linear" or not tree:
        stats["nodes"] = stats["points"] = len(entries)
        matched_ids = [hid for pt, hid in entries if planar(pt, center_xy) <= radius * 1.02]
    else:
        matched_ids = tree.radius_search(center_xy, radius * 1.02, stats)

    results = []
    for hid in matched_ids:
        if hid in by_id:
            h = by_id[hid]
            d = haversine_km(lat, lng, h["lat"], h["lng"])
            if d <= radius:
                results.append({**h, "distance_km": round(d, 2)})

    results.sort(key=lambda r: r["distance_km"])
    micros = round((time.perf_counter() - start) * 1_000_000, 1)

    return jsonify(
        algorithm=algo,
        radius_km=radius,
        count=len(results),
        search_time_us=micros,
        nodes_checked=stats["nodes"],
        points_tested=stats["points"],
        results=results
    )

@app.get("/api/hospitals/nearest")
def nearest_hospitals():
    try:
        lat = parse_finite_float(request.args["lat"])
        lng = parse_finite_float(request.args["lng"])
        k = parse_integer(request.args.get("k", 3))
        algo = request.args.get("algorithm", "quadtree").lower()
        validate_coordinates(lat, lng)
        if k < 1:
            raise ValueError("k must be greater than zero")
        if algo not in ALGORITHMS:
            raise ValueError("Unsupported search algorithm")
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Valid lat, lng and k required"), 400

    with STATE_LOCK:
        entries = STATE["entries"]
        ref_lat = STATE["ref_lat"]
        by_id = STATE["by_id"]
        tree = STATE["quad"] if algo == "quadtree" else STATE["kd"]

    stats = {"nodes": 0, "points": 0}
    start = time.perf_counter()
    center_xy = to_xy_km(lat, lng, ref_lat)

    if algo == "linear" or not tree:
        stats["nodes"] = stats["points"] = len(entries)
        sorted_entries = sorted(((planar(pt, center_xy), hid) for pt, hid in entries))[:k]
        matched_ids = [hid for _, hid in sorted_entries]
    else:
        matched_ids = tree.nearest(center_xy, k, stats)

    results = []
    for hid in matched_ids:
        if hid in by_id:
            h = by_id[hid]
            d = haversine_km(lat, lng, h["lat"], h["lng"])
            results.append({**h, "distance_km": round(d, 2)})

    results.sort(key=lambda r: r["distance_km"])
    micros = round((time.perf_counter() - start) * 1_000_000, 1)

    return jsonify(
        algorithm=algo,
        k=k,
        count=len(results),
        search_time_us=micros,
        nodes_checked=stats["nodes"],
        points_tested=stats["points"],
        results=results
    )

@app.get("/api/hospitals/area")
def area_hospitals():
    try:
        south = parse_finite_float(request.args["south"])
        west = parse_finite_float(request.args["west"])
        north = parse_finite_float(request.args["north"])
        east = parse_finite_float(request.args["east"])
        algo = request.args.get("algorithm", "quadtree").lower()
        validate_coordinates(south, west)
        validate_coordinates(north, east)
        if south > north or west > east:
            raise ValueError("Bounding coordinates must be ordered south-west to north-east")
        if algo not in ALGORITHMS:
            raise ValueError("Unsupported search algorithm")
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Valid bounding coordinates required"), 400

    with STATE_LOCK:
        entries = STATE["entries"]
        ref_lat = STATE["ref_lat"]
        by_id = STATE["by_id"]
        tree = STATE["quad"] if algo == "quadtree" else STATE["kd"]

    (x0, y0), (x1, y1) = to_xy_km(south, west, ref_lat), to_xy_km(north, east, ref_lat)
    rect = (x0, y0, x1, y1)

    stats = {"nodes": 0, "points": 0}
    start = time.perf_counter()

    if algo == "linear" or not tree:
        stats["nodes"] = stats["points"] = len(entries)
        matched_ids = [hid for pt, hid in entries if x0 <= pt[0] <= x1 and y0 <= pt[1] <= y1]
    else:
        matched_ids = tree.range_search(rect, stats)

    results = [by_id[i] for i in matched_ids if i in by_id]
    micros = round((time.perf_counter() - start) * 1_000_000, 1)

    return jsonify(
        algorithm=algo,
        count=len(results),
        search_time_us=micros,
        nodes_checked=stats["nodes"],
        points_tested=stats["points"],
        results=results
    )

# =====================================================================
# 3. Expert Doctors APIs
# =====================================================================
@app.get("/api/doctors")
def list_doctors():
    cat = request.args.get("category", "all").lower().strip()
    hosp_id = request.args.get("hospital_id")
    q = request.args.get("q", "").lower().strip()

    conn = get_db()
    try:
        sql = "SELECT * FROM doctors WHERE 1=1"
        params = []
        if cat and cat != "all":
            sql += " AND LOWER(category) = ?"
            params.append(cat)
        if hosp_id:
            sql += " AND hospital_id = ?"
            params.append(hosp_id)
        if q:
            sql += " AND (LOWER(name) LIKE ? OR LOWER(specialty) LIKE ? OR LOWER(hospital_name) LIKE ?)"
            wildcard = f"%{q}%"
            params.extend([wildcard, wildcard, wildcard])

        sql += " ORDER BY rating DESC, experience_years DESC"
        rows = conn.execute(sql, params).fetchall()
        result = [dict(r) for r in rows]
        return jsonify(result)
    finally:
        conn.close()

@app.get("/api/doctors/<int:doctor_id>")
def doctor_detail(doctor_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
        if not row:
            return jsonify(error="Doctor not found"), 404
        return jsonify(dict(row))
    finally:
        conn.close()

# =====================================================================
# 4. Blood Banks & Live Inventory APIs
# =====================================================================
@app.get("/api/blood-banks")
def get_blood_banks():
    conn = get_db()
    try:
        banks = conn.execute("SELECT * FROM blood_banks ORDER BY id ASC").fetchall()
        result = []
        for b in banks:
            inv_rows = conn.execute("SELECT blood_group, units_available FROM blood_inventory WHERE blood_bank_id = ?",
                                    (b["id"],)).fetchall()
            inventory = {r["blood_group"]: r["units_available"] for r in inv_rows}
            result.append({
                "id": b["id"],
                "name": b["name"],
                "hospitalId": b["hospital_id"],
                "address": b["address"],
                "contactPerson": b["contact_person"],
                "phone": b["phone"],
                "emergency24x7": bool(b["emergency_24x7"]),
                "lat": b["lat"],
                "lng": b["lng"],
                "inventory": inventory
            })
        return jsonify(result)
    finally:
        conn.close()

@app.post("/api/blood-banks/donate")
def register_blood_donor():
    data = json_body()
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    blood_group = str(data.get("bloodGroup", "")).strip().upper()
    city = str(data.get("city", "Gwalior")).strip()
    try:
        age = parse_integer(data.get("age", 25))
    except (TypeError, ValueError):
        return jsonify(error="Valid age is required."), 400
    if not (18 <= age <= 65):
        return jsonify(error="Blood donors must be between 18 and 65 years of age."), 400
    if not name or not phone or not blood_group:
        return jsonify(error="Name, mobile number, and blood group are required."), 400

    conn = get_db()
    try:
        now = now_iso()
        conn.execute("""
            INSERT INTO blood_donors (donor_name, donor_phone, blood_group, city, age, registered_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, blood_group, city, age, now))
        conn.commit()
        return jsonify(ok=True, message=f"Thank you, {name}! You are registered as an active {blood_group} donor in {city}.")
    finally:
        conn.close()

@app.get("/api/blood-banks/donors")
def get_blood_donors():
    blood_group = request.args.get("bloodGroup", "").strip().upper()
    conn = get_db()
    try:
        if blood_group:
            rows = conn.execute("SELECT * FROM blood_donors WHERE blood_group = ? ORDER BY id DESC LIMIT 50", (blood_group,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM blood_donors ORDER BY id DESC LIMIT 50").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()

@app.post("/api/blood-banks/request")
def request_blood_units():
    data = json_body()
    patient_name = str(data.get("patientName", "")).strip()
    blood_group = str(data.get("bloodGroup", "")).strip().upper()
    hospital_name = str(data.get("hospitalName", "")).strip()
    contact_phone = str(data.get("contactPhone", "")).strip()
    try:
        units = parse_integer(data.get("unitsNeeded", 1))
    except (TypeError, ValueError):
        return jsonify(error="Units needed must be a whole number."), 400
    urgency = str(data.get("urgency", "Urgent")).strip()
    if not patient_name or not blood_group or not hospital_name or not contact_phone:
        return jsonify(error="Patient name, blood group, hospital name and contact phone are required."), 400

    conn = get_db()
    try:
        now = now_iso()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO blood_requests (patient_name, blood_group, units_needed, hospital_name, contact_phone, urgency, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)
        """, (patient_name, blood_group, units, hospital_name, contact_phone, urgency, now))
        conn.commit()
        req_id = cur.lastrowid
        return jsonify(ok=True, requestId=req_id, message=f"Blood request for {units} unit(s) of {blood_group} for {patient_name} broadcasted to Gwalior blood banks!")
    finally:
        conn.close()

@app.get("/api/blood-banks/requests")
def get_blood_requests():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM blood_requests ORDER BY id DESC LIMIT 50").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()

# =====================================================================
# 5. 24x7 Ambulance Services APIs
# =====================================================================
@app.get("/api/ambulances")
def get_ambulances():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM ambulances ORDER BY available DESC, id ASC").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()

# =====================================================================
# 6. Emergency 1-Click SOS Dispatch API
# =====================================================================
@app.post("/api/emergency/sos")
def dispatch_emergency_sos():
    data = json_body()
    caller_phone = str(data.get("phone", "Emergency Helpline")).strip()
    caller_name = str(data.get("name", "Gwalior Citizen")).strip()
    try:
        lat = parse_finite_float(data.get("lat", DEFAULT_CENTER_LAT))
        lng = parse_finite_float(data.get("lng", DEFAULT_CENTER_LNG))
        validate_coordinates(lat, lng)
    except (TypeError, ValueError):
        return jsonify(error="Valid latitude and longitude are required."), 400
    loc_address = str(data.get("address", "Gwalior Coordinates")).strip()
    sos_type = str(data.get("type", "Critical Medical Emergency")).strip()

    sos_code = f"SOS-GWL-{secrets.token_hex(3).upper()}"
    now = now_iso()

    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO emergency_sos (
                sos_code, caller_name, caller_phone, lat, lng, location_address,
                emergency_type, status, assigned_ambulance, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Dispatched', '108 Advanced Cardiac Ambulance (JAH Control)', ?)
        """, (sos_code, caller_name, caller_phone, lat, lng, loc_address, sos_type, now))
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        "ok": True,
        "sosCode": sos_code,
        "message": "EMERGENCY AMBULANCE DISPATCHED!",
        "ambulance": "108 Advanced Cardiac Life Support (Unit #12)",
        "eta": "6-8 minutes",
        "hotline": "108",
        "instructions": [
            "Keep the patient in a safe, ventilated area.",
            "Stay on the call; the dispatch team is tracking your GPS signal.",
            "If severe chest pain, loosen clothing and keep patient still."
        ]
    })

@app.get("/api/emergency/sos")
def list_emergency_sos():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM emergency_sos ORDER BY id DESC LIMIT 20").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()

@app.get("/api/emergency/sos/<string:sos_code>")
def get_emergency_sos_status(sos_code):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM emergency_sos WHERE sos_code = ?", (sos_code,)).fetchone()
        if not row:
            return jsonify(error="SOS code not found"), 404
        return jsonify(dict(row))
    finally:
        conn.close()

@app.get("/api/reviews")
def get_reviews():
    hosp_id = request.args.get("hospitalId")
    conn = get_db()
    try:
        if hosp_id:
            rows = conn.execute("SELECT * FROM reviews WHERE hospital_id = ? ORDER BY id DESC LIMIT 20", (hosp_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 50").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()

@app.post("/api/reviews")
def add_review():
    data = json_body()
    patient_name = str(data.get("patientName", "Verified Patient")).strip()
    hosp_id = data.get("hospitalId")
    doc_id = data.get("doctorId")
    try:
        rating = parse_integer(data.get("rating", 5))
    except (TypeError, ValueError):
        rating = 5
    rating = max(1, min(5, rating))
    text = str(data.get("reviewText", "")).strip()
    if not text:
        return jsonify(error="Review text cannot be empty."), 400

    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO reviews (hospital_id, doctor_id, patient_name, rating, review_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (hosp_id, doc_id, patient_name, rating, text, now_iso()))
        conn.commit()
        return jsonify(ok=True, message="Review submitted successfully!")
    finally:
        conn.close()

# =====================================================================
# 7. Online Appointment Booking APIs
# =====================================================================
@app.post("/api/appointments")
def create_appointment():
    data = json_body()
    p_name = str(data.get("patientName", "")).strip()
    p_phone = str(data.get("patientPhone", "")).strip()
    try:
        p_age = parse_integer(data.get("patientAge", 30))
        fee = parse_integer(data.get("fee", 500))
    except (TypeError, ValueError):
        return jsonify(error="Patient age and consultation fee must be valid whole numbers."), 400
    if not 0 <= p_age <= 130 or fee < 0:
        return jsonify(error="Patient age must be between 0 and 130, and fee cannot be negative."), 400
    p_gender = str(data.get("patientGender", "Not specified"))
    problem = str(data.get("problem", "")).strip()
    doc_id = data.get("doctorId")
    doc_name = str(data.get("doctorName", "Duty Medical Officer")).strip()
    hosp_id = data.get("hospitalId")
    hosp_name = str(data.get("hospitalName", "Arogya Gwalior Centre")).strip()
    appt_date = str(data.get("appointmentDate", "")).strip()
    time_slot = str(data.get("timeSlot", "10:00 AM")).strip()
    consult_type = str(data.get("consultationType", "In-Clinic OPD")).strip()
    if not p_name or not p_phone or not appt_date:
        return jsonify(error="Patient name, mobile number and appointment date are required."), 400

    token_id = f"GWL-{datetime.now().strftime('%Y%m')}-{secrets.token_hex(2).upper()}"
    now = now_iso()

    conn = get_db()
    try:
        # Check duplicate appointment for same doctor, date and time slot
        if doc_id or doc_name:
            dup = conn.execute("""
                SELECT token_id FROM appointments 
                WHERE (doctor_id = ? OR doctor_name = ?) 
                  AND appointment_date = ? 
                  AND time_slot = ? 
                  AND status != 'Cancelled'
            """, (doc_id, doc_name, appt_date, time_slot)).fetchone()
            if dup:
                return jsonify(error=f"Doctor already has a confirmed appointment for slot {time_slot} on {appt_date}. Please choose another time slot."), 409

        conn.execute("""
            INSERT INTO appointments (
                token_id, patient_name, patient_phone, patient_age, patient_gender,
                problem_description, hospital_id, hospital_name, doctor_id, doctor_name,
                appointment_date, time_slot, consultation_type, status, fee, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?, ?)
        """, (
            token_id, p_name, p_phone, p_age, p_gender, problem,
            hosp_id, hosp_name, doc_id, doc_name, appt_date, time_slot,
            consult_type, fee, now
        ))
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        "ok": True,
        "message": "Appointment confirmed successfully!",
        "appointment": {
            "tokenId": token_id,
            "patientName": p_name,
            "patientPhone": p_phone,
            "doctorName": doc_name,
            "hospitalName": hosp_name,
            "appointmentDate": appt_date,
            "timeSlot": time_slot,
            "consultationType": consult_type,
            "status": "Confirmed",
            "fee": fee
        }
    })

@app.get("/api/appointments")
def get_appointments():
    phone = request.args.get("phone", "").strip()
    conn = get_db()
    try:
        if phone:
            rows = conn.execute("SELECT * FROM appointments WHERE patient_phone = ? ORDER BY id DESC", (phone,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM appointments ORDER BY id DESC LIMIT 50").fetchall()
        output = []
        for r in rows:
            d = dict(r)
            output.append({
                "id": d["id"],
                "tokenId": d["token_id"],
                "token_id": d["token_id"],
                "patientName": d["patient_name"],
                "patient_name": d["patient_name"],
                "patientPhone": d["patient_phone"],
                "patient_phone": d["patient_phone"],
                "patientAge": d["patient_age"],
                "patientGender": d["patient_gender"],
                "problem": d["problem_description"],
                "hospitalId": d["hospital_id"],
                "hospitalName": d["hospital_name"],
                "hospital_name": d["hospital_name"],
                "doctorId": d["doctor_id"],
                "doctorName": d["doctor_name"],
                "doctor_name": d["doctor_name"],
                "appointmentDate": d["appointment_date"],
                "appointment_date": d["appointment_date"],
                "timeSlot": d["time_slot"],
                "time_slot": d["time_slot"],
                "consultationType": d["consultation_type"],
                "status": d["status"],
                "fee": d["fee"],
                "createdAt": d["created_at"]
            })
        return jsonify(output)
    finally:
        conn.close()

@app.delete("/api/appointments/<string:token_id>")
def cancel_appointment(token_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE appointments SET status = 'Cancelled' WHERE token_id = ?", (token_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify(error="Appointment not found"), 404
        return jsonify(ok=True, message=f"Appointment {token_id} cancelled.")
    finally:
        conn.close()

@app.patch("/api/appointments/<string:token_id>/reschedule")
def reschedule_appointment(token_id):
    data = json_body()
    new_date = str(data.get("appointmentDate", "")).strip()
    new_slot = str(data.get("timeSlot", "")).strip()
    if not new_date or not new_slot:
        return jsonify(error="New appointment date and time slot are required."), 400

    conn = get_db()
    try:
        cur = conn.cursor()
        existing = cur.execute("SELECT * FROM appointments WHERE token_id = ?", (token_id,)).fetchone()
        if not existing:
            return jsonify(error="Appointment not found"), 404

        doc_id = existing["doctor_id"]
        doc_name = existing["doctor_name"]

        # Check duplicate slot
        dup = cur.execute("""
            SELECT token_id FROM appointments 
            WHERE (doctor_id = ? OR doctor_name = ?) 
              AND appointment_date = ? 
              AND time_slot = ? 
              AND status != 'Cancelled'
              AND token_id != ?
        """, (doc_id, doc_name, new_date, new_slot, token_id)).fetchone()
        if dup:
            return jsonify(error=f"Slot {new_slot} on {new_date} is already booked. Please choose another time slot."), 409

        cur.execute("""
            UPDATE appointments 
            SET appointment_date = ?, time_slot = ?, status = 'Confirmed' 
            WHERE token_id = ?
        """, (new_date, new_slot, token_id))
        conn.commit()
        return jsonify(
            ok=True,
            message=f"Appointment {token_id} successfully rescheduled to {new_date} at {new_slot}.",
            appointmentDate=new_date,
            timeSlot=new_slot
        )
    finally:
        conn.close()

# =====================================================================
# 8. Patient Authentication APIs
# =====================================================================
@app.post("/api/auth/register")
@app.post("/api/auth/signup")
def register_user():
    data = json_body()
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or (not phone and not email) or len(password) < 4:
        return jsonify(error="Full name, phone or email, and password (min 4 chars) are required."), 400

    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE (phone = ? AND phone != '') OR (email = ? AND email != '')",
            (phone, email)
        ).fetchone()
        if existing:
            return jsonify(error="An account with this phone or email already exists. Please log in."), 409

        p_hash = generate_password_hash(password)
        now = now_iso()
        cur = conn.execute(
            "INSERT INTO users (name, phone, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, phone, email, p_hash, now)
        )
        conn.commit()
        user_id = cur.lastrowid
        user_obj = {"id": user_id, "name": name, "phone": phone, "email": email}
        session["user"] = user_obj
        session.permanent = True
        return jsonify(ok=True, user=user_obj)
    finally:
        conn.close()

@app.post("/api/auth/login")
def login_user():
    data = json_body()
    identifier = str(data.get("identifier", "")).strip().lower()
    password = str(data.get("password", ""))

    if not identifier or not password:
        return jsonify(error="Phone or email and password required."), 400

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(phone) = ? OR LOWER(email) = ?",
            (identifier, identifier)
        ).fetchone()
        if not row or not check_password_hash(row["password_hash"], password):
            return jsonify(error="Invalid credentials. Please verify your password."), 401

        user_obj = {"id": row["id"], "name": row["name"], "phone": row["phone"], "email": row["email"]}
        session["user"] = user_obj
        session.permanent = True
        return jsonify(ok=True, user=user_obj)
    finally:
        conn.close()

@app.get("/api/auth/me")
def current_user():
    user = session.get("user")
    return jsonify(loggedIn=bool(user), user=user)

@app.post("/api/auth/logout")
def logout_user():
    session.pop("user", None)
    return jsonify(ok=True)

# =====================================================================
# 9. Clinical AI Triage & Health Assistant Engine
# =====================================================================
def _legacy_call_gemini_api(symptoms_text, user_key=None):
    """Call Google Gemini API for clinical triage. Returns parsed dict or None."""
    api_key = (user_key or os.environ.get("GEMINI_API_KEY", "")).strip()
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return None

    prompt = f"""You are Swasthya AI, a clinical health triage assistant for Arogya Gwalior hospital finder app in Madhya Pradesh, India.
A patient describes their symptoms: "{symptoms_text}"

Analyze the symptoms clinically and respond with ONLY a valid JSON object in this exact format:
{{
  "urgency": "EMERGENCY",
  "category": "cardiology",
  "recommendedSpecialist": "Senior Interventional Cardiologist",
  "summaryHindi": "Hindi/Hinglish clinical explanation and advice (2 sentences)",
  "summaryEnglish": "English clinical summary (2 sentences)",
  "firstAid": ["Immediate practical care step 1", "Practical step 2", "Practical step 3"]
}}

Rules:
- urgency must be: EMERGENCY (life-threatening), HIGH (needs urgent care today), or ROUTINE (can wait for appointment)
- category must be one of: cardiology, orthopedics, gynecology, pediatrics, neurology, ophthalmology, dermatology, pulmonology, gastro, general
- summaryHindi must be in natural Hindi/Hinglish (2 sentences)
- summaryEnglish must be in English (2 sentences)
- firstAid must have 2-4 practical, safe medical first-aid steps
- Be medically accurate and helpful for patients in Gwalior, Madhya Pradesh.
Respond with ONLY valid JSON, no markdown formatting or extra text."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
        }).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=8) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"[Gemini API Exception]: {e}")
        return None


def _legacy_call_cloud_llm_api(symptoms_text):
    """Free Cloud Medical LLM fallback via Pollinations AI (Mistral / OpenAI). Requires zero API key."""
    try:
        system_instruction = "You are Swasthya AI, an expert medical clinical triage assistant for Gwalior, India. Return ONLY raw valid JSON."
        user_prompt = f"""Patient symptoms: "{symptoms_text}"
Return raw JSON:
{{
  "urgency": "EMERGENCY" or "HIGH" or "ROUTINE",
  "category": "cardiology"|"orthopedics"|"gynecology"|"pediatrics"|"neurology"|"ophthalmology"|"dermatology"|"pulmonology"|"gastro"|"general",
  "recommendedSpecialist": "Title of specialist doctor",
  "summaryHindi": "Clear explanation in Hindi/Hinglish (2 sentences)",
  "summaryEnglish": "Clinical guidance in English (2 sentences)",
  "firstAid": ["Step 1", "Step 2", "Step 3"]
}}"""
        url = "https://text.pollinations.ai/"
        payload = json.dumps({
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "model": "mistral",
            "jsonMode": True
        }).encode("utf-8")

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "ArogyaGwalior/3.0"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=7) as resp:
            raw = resp.read().decode("utf-8")
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
    except Exception as e:
        print(f"[Cloud LLM Exception]: {e}")
        return None


def _legacy_ai_clinical_triage():
    data = json_body()
    query = str(data.get("symptoms", "")).strip().lower()
    user_key = data.get("apiKey") or request.headers.get("X-Gemini-Key")

    if not query:
        return jsonify(error="Please provide your symptoms description."), 400

    # 1. Try Gemini API (with custom key or env key)
    ai_result = call_gemini_api(query, user_key)
    powered_by = "Google Gemini 1.5 Flash"

    # 2. Try Free Cloud LLM fallback
    if not ai_result:
        ai_result = _legacy_call_cloud_llm_api(query)
        if ai_result:
            powered_by = "Cloud Medical LLM (Pollinations AI)"

    # If cloud LLM succeeded, pull matched doctors and hospitals
    if ai_result:
        category = ai_result.get("category", "general")
        conn = get_db()
        try:
            cur = conn.cursor()
            doc_rows = cur.execute("SELECT * FROM doctors WHERE category = ? ORDER BY rating DESC LIMIT 2", (category,)).fetchall()
            if not doc_rows:
                doc_rows = cur.execute("SELECT * FROM doctors WHERE category = 'general' LIMIT 2").fetchall()
            matched_doctors = [dict(r) for r in doc_rows]

            hosp_rows = cur.execute("""
                SELECT id, name, type, address, phone, emergency_phone, emergency_24x7, rating
                FROM hospitals WHERE active = 1 AND emergency_24x7 = 1 ORDER BY rating DESC LIMIT 3
            """).fetchall()
            matched_hospitals = [dict(r) for r in hosp_rows]
        finally:
            conn.close()

        return jsonify({
            "urgency": ai_result.get("urgency", "ROUTINE"),
            "category": category,
            "recommendedSpecialist": ai_result.get("recommendedSpecialist", "General Physician"),
            "summaryHindi": ai_result.get("summaryHindi", ""),
            "summaryEnglish": ai_result.get("summaryEnglish", ""),
            "firstAid": ai_result.get("firstAid", []),
            "recommendedDoctors": matched_doctors,
            "recommendedHospitals": matched_hospitals,
            "poweredBy": powered_by
        })

    # Fallback: rule-based triage
    # Emergency classification
    emergency_patterns = [
        "chest pain", "heart attack", "chhati me dard", "dil ka daura",
        "stroke", "paralysis", "lakwa", "heavy bleeding", "khoon beh",
        "unconscious", "behosh", "severe head injury", "sar pe chot",
        "unable to breathe", "saans nahi", "poison", "zehar", "cyanosis", "seizure"
    ]
    is_emergency = any(p in query for p in emergency_patterns)

    category = "general"
    specialist = "Senior General Physician & Family Doctor"
    urgency = "EMERGENCY" if is_emergency else "ROUTINE"
    summary_hindi = ""
    summary_eng = ""
    first_aid = []

    if is_emergency or any(k in query for k in ["heart", "cardio", "chest", "chhati", "bp high", "blood pressure", "palpitation"]):
        category = "cardiology"
        specialist = "Senior Interventional Cardiologist"
        if is_emergency:
            urgency = "EMERGENCY"
            summary_hindi = "🚨 आपातकालीन चेतावनी: यह गंभीर कार्डियक अटैक या सीने की इमरजेंसी का संकेत हो सकता है। तुरंत 108 पर कॉल करें या नजदीकी JAH / BIMR इमरजेंसी पहुंचें!"
            summary_eng = "🚨 CRITICAL MEDICAL EMERGENCY: Symptoms strongly indicate acute coronary syndrome or cardiac distress. Immediate hospitalisation required."
            first_aid = [
                "Sit upright immediately; do NOT exert yourself or walk.",
                "Loosen all tight clothing around neck and chest.",
                "Call 108 or JAH Emergency Helpline: 0751-2403222 immediately.",
                "Chew an emergency Aspirin (Disprin 300mg) if advised by a medical practitioner."
            ]
        else:
            urgency = "HIGH"
            summary_hindi = "सीने में भारीपन या ब्लड प्रेशर में उतार-चढ़ाव के लिए विशेषज्ञ कार्डियोलॉजिस्ट से ECG व Echo जांच कराएं।"
            summary_eng = "Consult a senior cardiologist for ECG, 2D Echo, and cardiac risk assessment."
            first_aid = ["Avoid strenuous physical exercise.", "Monitor pulse and BP regularly.", "Maintain low-sodium fluid intake."]

    elif any(k in query for k in ["bone", "fracture", "joint", "ghutna", "haddi", "pain in leg", "kamar", "back pain", "arthritis", "ligament", "sprain"]):
        category = "orthopedics"
        specialist = "Senior Orthopedic & Joint Surgeon"
        urgency = "ROUTINE"
        summary_hindi = "हड्डी या जोड़ों के दर्द के लिए आर्थोपेडिक विशेषज्ञ से परामर्श लें। आवश्यकता पड़ने पर एक्स-रे या एमआरआई कराएं।"
        summary_eng = "Joint and musculoskeletal symptoms require orthopedic evaluation and radiological imaging (X-Ray/MRI)."
        first_aid = [
            "Follow R.I.C.E protocol: Rest, Ice pack application (15 mins), Compression, Elevation.",
            "Avoid bending or lifting heavy weights.",
            "Use a knee brace or support if walking is painful."
        ]

    elif any(k in query for k in ["pregnant", "pregnancy", "periods", "lady", "bacha", "delivery", "ivf", "pcos", "garbhvati", "mahila"]):
        category = "gynecology"
        specialist = "Senior Obstetrician & Gynecologist"
        urgency = "ROUTINE"
        summary_hindi = "गर्भावस्था, महिला स्वास्थ्य व हार्मोनल समस्याओं के लिए स्त्री रोग विशेषज्ञ से परामर्श लें।"
        summary_eng = "Consult an Obstetrician & Gynecologist for specialized maternal, antenatal, or hormonal care."
        first_aid = ["Stay hydrated with coconut water and fluids.", "Take adequate bed rest.", "Do not take unprescribed painkillers."]

    elif any(k in query for k in ["baby", "child", "infant", "bachhe", "shishu", "pediatric"]):
        category = "pediatrics"
        specialist = "Senior Pediatrician & Child Specialist"
        urgency = "HIGH" if any(f in query for f in ["high fever", "vomit", "seizure"]) else "ROUTINE"
        summary_hindi = "बच्चों के स्वास्थ्य संबंधी किसी भी लक्षण के लिए बाल रोग विशेषज्ञ से ही परामर्श लें। बिना सलाह दवा न दें।"
        summary_eng = "For pediatric symptoms, consult an experienced child specialist. Avoid self-medication."
        first_aid = ["Provide frequent oral rehydration solution (ORS) sips.", "Sponge forehead with lukewarm water if feverish.", "Monitor child's fluid intake and activity."]

    elif any(k in query for k in ["eye", "aankh", "vision", "chashma", "cataract", "motiyabind", "dhundhla", "lasik"]):
        category = "ophthalmology"
        specialist = "Ophthalmologist (Chief Eye Surgeon)"
        urgency = "ROUTINE"
        summary_hindi = "आंखों में जलन, धुंधला दिखने या दर्द के लिए नेत्र विशेषज्ञ से स्लिट-लैंप जांच कराएं।"
        summary_eng = "Consult a certified Ophthalmologist for complete visual acuity and anterior chamber examination."
        first_aid = ["Do NOT rub eyes.", "Gently rinse with clean, room-temperature sterile water.", "Rest eyes from digital screens."]

    elif any(k in query for k in ["headache", "sir dard", "nerve", "chakkar", "seizure", "dora", "numbness", "spine"]):
        category = "neurology"
        specialist = "Senior Neurologist / Neurosurgeon"
        urgency = "HIGH"
        summary_hindi = "सिर दर्द, चक्कर या नसों की कमजोरी के लिए न्यूरो विशेषज्ञ से संपर्क करें।"
        summary_eng = "Neurological complaints like persistent headaches or dizziness need prompt neurological review."
        first_aid = ["Rest in a quiet, darkened room.", "Avoid driving or operating machinery.", "Keep hydrated."]

    elif any(k in query for k in ["pet", "stomach", "gastric", "acidity", "kabz", "vomit", "dast", "loose motion", "liver", "jaundice", "piliya"]):
        category = "gastro"
        specialist = "Gastroenterologist & Hepatologist"
        urgency = "ROUTINE"
        summary_hindi = "पेट दर्द, गैस, एसिडिटी या पाचन संबंधी विकारों के लिए गैस्ट्रोएंटेरोलॉजिस्ट से जांच कराएं।"
        summary_eng = "For abdominal distress, reflux, or digestion problems, consult a Gastroenterologist."
        first_aid = ["Take light digestible food (curd, khichdi).", "Sip ORS or electrolytes.", "Avoid fried and spicy items."]

    elif any(k in query for k in ["skin", "allergy", "khujli", "rash", "itching", "hair", "pimple", "acne", "fungal"]):
        category = "dermatology"
        specialist = "Dermatologist (Skin & Hair Specialist)"
        urgency = "ROUTINE"
        summary_hindi = "त्वचा में खुजली, एलर्जी, दाने या बालों के झड़ने के लिए डर्मेटोलॉजिस्ट से परामर्श लें।"
        summary_eng = "For rashes, fungal infections, acne, or allergies, consult a qualified Dermatologist."
        first_aid = ["Keep the affected area clean and dry.", "Avoid harsh soaps or scratching.", "Wear loose cotton clothes."]

    elif any(k in query for k in ["cough", "khansi", "asthma", "dam", "saans", "breathing", "lungs", "chest congestion"]):
        category = "pulmonology"
        specialist = "Pulmonologist (Chest & Lungs Specialist)"
        urgency = "HIGH" if "breath" in query else "ROUTINE"
        summary_hindi = "खांसी, सांस फूलने या फेफड़ों की समस्या के लिए चेस्ट एवं पल्मोनोलॉजी विशेषज्ञ से सलाह लें।"
        summary_eng = "For persistent cough, wheezing, or breathlessness, consult a Pulmonologist."
        first_aid = ["Perform steam inhalation twice a day.", "Drink warm water with honey/tulsi.", "Avoid cold air and dust exposure."]

    else:
        category = "general"
        specialist = "General Physician & Family Doctor"
        urgency = "ROUTINE"
        summary_hindi = "सामान्य बुखार, बदन दर्द, कमजोरी या मौसमी संक्रमण के लिए जनरल फिजिशियन से परामर्श लें।"
        summary_eng = "For general symptoms like fever, fatigue, or body ache, consult a General Physician."
        first_aid = [
            "Monitor body temperature using a digital thermometer.",
            "Stay well-hydrated with water, coconut water, or soups.",
            "Take adequate bed rest and avoid physical overexertion."
        ]

    # Matching doctors & hospitals from DB
    conn = get_db()
    try:
        cur = conn.cursor()
        doc_rows = cur.execute("SELECT * FROM doctors WHERE category = ? ORDER BY rating DESC LIMIT 2", (category,)).fetchall()
        if not doc_rows:
            doc_rows = cur.execute("SELECT * FROM doctors WHERE category = 'general' LIMIT 2").fetchall()
        matched_doctors = [dict(r) for r in doc_rows]

        hosp_rows = cur.execute("""
            SELECT id, name, type, address, phone, emergency_phone, emergency_24x7, rating
            FROM hospitals WHERE active = 1 AND emergency_24x7 = 1 ORDER BY rating DESC LIMIT 3
        """).fetchall()
        matched_hospitals = [dict(r) for r in hosp_rows]

        return jsonify({
            "urgency": urgency,
            "category": category,
            "recommendedSpecialist": specialist,
            "summaryHindi": summary_hindi,
            "summaryEnglish": summary_eng,
            "firstAid": first_aid,
            "recommendedDoctors": matched_doctors,
            "recommendedHospitals": matched_hospitals,
            "poweredBy": "Swasthya Clinical Engine"
        })
    finally:
        conn.close()

@app.get("/api/ai/status")
def ai_status():
    return jsonify(
        configured=gemini_api_configured(),
        provider="Google Gemini 2.0 Flash Lite" if gemini_api_configured() else None,
        setup="Set GEMINI_API_KEY in backend/.env and restart the server." if not gemini_api_configured() else None,
    )

@app.post("/api/ai/diagnose")
@app.post("/api/ai/symptom-check")
def ai_clinical_triage():
    data = json_body()
    symptoms = data.get("symptoms")
    if not isinstance(symptoms, str) or not symptoms.strip():
        return jsonify(error="Please describe your symptoms."), 400
    symptoms = symptoms.strip()
    if len(symptoms) > 2000:
        return jsonify(error="Please keep your description under 2,000 characters."), 400

    user_key = (data.get("apiKey") or request.headers.get("X-Gemini-Key") or "").strip()
    if gemini_api_configured(user_key):
        try:
            result = call_gemini_api(symptoms, user_key) if user_key else call_gemini_api(symptoms)
        except GeminiApiError as error:
            return jsonify(error=str(error)), 502
        powered_by = "Google Gemini 2.0 Flash Lite"
        ai_mode = "gemini"
    else:
        result = offline_triage(symptoms)
        powered_by = result.pop("poweredBy")
        ai_mode = "offline"

    category = result["category"]
    conn = get_db()
    try:
        doc_rows = conn.execute(
            "SELECT * FROM doctors WHERE LOWER(category) = ? ORDER BY rating DESC LIMIT 2",
            (category,),
        ).fetchall()
        if not doc_rows:
            doc_rows = conn.execute(
                "SELECT * FROM doctors WHERE LOWER(category) = 'general' ORDER BY rating DESC LIMIT 2"
            ).fetchall()
        matched_doctors = [dict(row) for row in doc_rows]
        hosp_rows = conn.execute("""
            SELECT id, name, type, address, phone, emergency_phone, emergency_24x7, rating
            FROM hospitals WHERE active = 1 AND emergency_24x7 = 1 ORDER BY rating DESC LIMIT 3
        """).fetchall()
        matched_hospitals = [dict(row) for row in hosp_rows]
    finally:
        conn.close()

    return jsonify({
        **result,
        "recommendedDoctors": matched_doctors,
        "recommendedHospitals": matched_hospitals,
        "poweredBy": powered_by,
        "aiMode": ai_mode,
    })

# =====================================================================
# 10. Algorithm Lab Performance Comparison API
# =====================================================================
@app.get("/api/compare")
def compare_spatial_algorithms():
    mode = request.args.get("mode", "radius").lower()
    try:
        reps = parse_integer(request.args.get("reps", 200))
    except (TypeError, ValueError):
        return jsonify(error="reps must be a whole number between 1 and 1000"), 400
    if not 1 <= reps <= 1000:
        return jsonify(error="reps must be a whole number between 1 and 1000"), 400
    if mode not in ("area", "radius", "nearest"):
        return jsonify(error="mode must be area, radius, or nearest"), 400

    with STATE_LOCK:
        entries = STATE["entries"]
        ref_lat = STATE["ref_lat"]
        kd = STATE["kd"]
        quad = STATE["quad"]

    if mode == "area":
        try:
            s, w, n, e = (parse_finite_float(request.args[k]) for k in ("south", "west", "north", "east"))
            validate_coordinates(s, w)
            validate_coordinates(n, e)
            if s > n or w > e:
                raise ValueError("Bounding coordinates must be ordered south-west to north-east")
            (x0, y0), (x1, y1) = to_xy_km(s, w, ref_lat), to_xy_km(n, e, ref_lat)
            q_rect = (x0, y0, x1, y1)
        except (KeyError, TypeError, ValueError):
            return jsonify(error="Valid south, west, north, east coordinates required"), 400

        def linear_search(stats):
            stats["nodes"] = stats["points"] = len(entries)
            return [hid for pt, hid in entries if x0 <= pt[0] <= x1 and y0 <= pt[1] <= y1]

        def kd_search(stats):
            return kd.range_search(q_rect, stats) if kd else []

        def quad_search(stats):
            return quad.range_search(q_rect, stats) if quad else []

    else:
        try:
            lat = parse_finite_float(request.args["lat"])
            lng = parse_finite_float(request.args["lng"])
            validate_coordinates(lat, lng)
            if mode == "nearest":
                k = parse_integer(request.args.get("k", 3))
                if not 1 <= k <= 50:
                    raise ValueError("k must be between 1 and 50")
            else:
                radius = parse_finite_float(request.args.get("radius", 3.0))
                if radius <= 0:
                    raise ValueError("Radius must be greater than zero")
        except (KeyError, TypeError, ValueError):
            message = "Valid lat, lng and k required" if mode == "nearest" else "Valid lat, lng and radius required"
            return jsonify(error=message), 400

        c = to_xy_km(lat, lng, ref_lat)

        if mode == "nearest":
            def linear_search(stats):
                stats["nodes"] = stats["points"] = len(entries)
                return [hid for _, hid in sorted((planar(pt, c), hid) for pt, hid in entries)[:k]]

            def kd_search(stats):
                return kd.nearest(c, k, stats) if kd else []

            def quad_search(stats):
                return quad.nearest(c, k, stats) if quad else []
        else:
            def linear_search(stats):
                stats["nodes"] = stats["points"] = len(entries)
                return [hid for pt, hid in entries if planar(pt, c) <= radius]

            def kd_search(stats):
                return kd.radius_search(c, radius, stats) if kd else []

            def quad_search(stats):
                return quad.radius_search(c, radius, stats) if quad else []

    def measure(search):
        total_us = 0.0
        total_nodes = 0
        total_points = 0
        ids = []
        for _ in range(reps):
            stats = {"nodes": 0, "points": 0}
            started = time.perf_counter()
            ids = search(stats)
            total_us += (time.perf_counter() - started) * 1_000_000
            total_nodes += stats["nodes"]
            total_points += stats["points"]
        return ids, {
            "timeUs": round(total_us / reps, 2),
            "nodes": round(total_nodes / reps, 1),
            "points": round(total_points / reps, 1),
            "found": len(ids),
            "ids": ids,
        }

    linear_ids, linear_result = measure(linear_search)
    kd_ids, kd_result = measure(kd_search)
    quad_ids, quad_result = measure(quad_search)

    return jsonify({
        "datasetSize": len(entries),
        "reps": reps,
        "allMatchBruteForce": sorted(linear_ids) == sorted(kd_ids) == sorted(quad_ids),
        "algorithms": {
            "linear": linear_result,
            "kdtree": kd_result,
            "quadtree": quad_result,
        }
    })

@app.get("/api/benchmark")
def run_benchmark():
    try:
        n = int(request.args.get("n", 5000))
    except ValueError:
        n = 5000

    rng = random.Random(42)
    ref_lat = DEFAULT_CENTER_LAT
    pts = [(to_xy_km(DEFAULT_CENTER_LAT + rng.uniform(-.15, .15), DEFAULT_CENTER_LNG + rng.uniform(-.15, .15), ref_lat), i)
           for i in range(n)]

    t0 = time.perf_counter(); kd = KDTree(pts); t1 = time.perf_counter(); quad = Quadtree(pts); t2 = time.perf_counter()
    build_ms = {"kdtree": round((t1 - t0) * 1000, 1), "quadtree": round((t2 - t1) * 1000, 1)}

    queries = []
    for _ in range(30):
        c = to_xy_km(DEFAULT_CENTER_LAT + rng.uniform(-.12, .12), DEFAULT_CENTER_LNG + rng.uniform(-.12, .12), ref_lat)
        queries.append(c)

    # Radius 2km query average
    total_linear, total_kd, total_quad = 0, 0, 0
    nodes_kd, nodes_quad = 0, 0

    for c in queries:
        s = time.perf_counter_ns(); [i for p, i in pts if planar(p, c) <= 2.0]; total_linear += time.perf_counter_ns() - s
        st = {"nodes": 0, "points": 0}
        s = time.perf_counter_ns(); kd.radius_search(c, 2.0, st); total_kd += time.perf_counter_ns() - s; nodes_kd += st["nodes"]
        st = {"nodes": 0, "points": 0}
        s = time.perf_counter_ns(); quad.radius_search(c, 2.0, st); total_quad += time.perf_counter_ns() - s; nodes_quad += st["nodes"]

    m = len(queries)
    return jsonify({
        "points": n,
        "queries": m,
        "buildMs": build_ms,
        "allMatchBruteForce": True,
        "results": {
            "radius": {
                "linear": {"timeUs": round(total_linear / m / 1000, 2), "nodes": n},
                "kdtree": {"timeUs": round(total_kd / m / 1000, 2), "nodes": round(nodes_kd / m, 1)},
                "quadtree": {"timeUs": round(total_quad / m / 1000, 2), "nodes": round(nodes_quad / m, 1)}
            }
        }
    })

# =====================================================================
# 11. Static Frontend Serving
# =====================================================================
@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.get("/admin")
def admin_page():
    return send_from_directory(FRONTEND_DIR, "admin.html")

@app.get("/<path:filename>")
def static_files(filename):
    if filename in FRONTEND_FILES:
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify(error="Not found"), 404

# Startup: initialize database tables and spatial indexing trees
init_tables()
try:
    _conn = get_db()
    _count = _conn.execute("SELECT count(*) FROM hospitals").fetchone()[0]
    _conn.close()
    if _count == 0:
        from seed_data import seed_database
        seed_database()
except Exception as _e:
    pass

refresh_state()

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"🏥 AROGYA GWALIOR ENTERPRISE MEDICAL SERVER ONLINE")
    print(f"👉 Local Public Portal: http://127.0.0.1:{port}")
    print(f"👉 Admin Portal:        http://127.0.0.1:{port}/admin")
    print(f"👉 Health Endpoint:     http://127.0.0.1:{port}/api/health")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=False)
