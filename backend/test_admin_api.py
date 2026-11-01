"""Admin directory API tests using a temporary SQLite database."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app as backend_app
import database
from werkzeug.security import generate_password_hash


class AdminDirectoryApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = Path(self.temp_dir.name) / "admin-test.db"
        database.init_tables()
        conn = database.get_db()
        conn.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            ("test-admin", generate_password_hash("safe-test-password")),
        )
        conn.commit()
        conn.close()
        backend_app.refresh_state()
        self.client = backend_app.app.test_client()

    def tearDown(self):
        database.DB_PATH = self.original_db_path
        backend_app.refresh_state()
        self.temp_dir.cleanup()

    def login(self):
        response = self.client.post(
            "/api/admin/login",
            json={"username": "test-admin", "password": "safe-test-password"},
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_routes_require_a_login(self):
        self.assertEqual(self.client.get("/api/admin/hospitals").status_code, 401)
        self.assertEqual(self.client.get("/api/admin/doctors").status_code, 401)
        self.assertEqual(self.client.post("/api/admin/osm/import-elements", json={"elements": []}).status_code, 401)

    def test_hospital_photo_facilities_and_verification_are_saved(self):
        self.login()
        hospital = {
            "name": "Sample Medical Centre",
            "type": "Private",
            "address": "Gwalior",
            "phone": "+91 751 1234567",
            "lat": 26.22,
            "lng": 78.18,
            "photoUrl": "https://example.org/hospital.jpg",
            "photoCredit": "Facility website",
            "services": ["Emergency", "Radiology"],
            "beds": {"general": [20, 5], "icu": [4, 1]},
            "verified": False,
            "active": True,
        }
        created = self.client.post("/api/admin/hospitals", json=hospital)
        self.assertEqual(created.status_code, 201)
        hospital_id = created.get_json()["id"]

        public_record = self.client.get("/api/hospitals").get_json()[0]
        self.assertEqual(public_record["id"], hospital_id)
        self.assertEqual(public_record["photoUrl"], hospital["photoUrl"])
        self.assertEqual(public_record["photoCredit"], hospital["photoCredit"])
        self.assertIn("Radiology", public_record["services"])
        self.assertFalse(public_record["verified"])

        hospital["photoUrl"] = "http://example.org/insecure.jpg"
        invalid_update = self.client.put(f"/api/admin/hospitals/{hospital_id}", json=hospital)
        self.assertEqual(invalid_update.status_code, 400)

    def test_doctor_profile_defaults_to_unverified_and_can_be_updated(self):
        self.login()
        profile = {
            "name": "Dr. Example",
            "qualification": "MBBS",
            "specialty": "General Physician",
            "category": "general",
            "experienceYears": 8,
            "hospitalName": "Sample Clinic",
            "clinicAddress": "Gwalior",
            "phone": "+91 751 1234567",
            "opdTimings": "10 AM - 2 PM",
            "fee": 300,
            "verified": False,
        }
        created = self.client.post("/api/admin/doctors", json=profile)
        self.assertEqual(created.status_code, 201)
        doctor_id = created.get_json()["id"]
        doctor = self.client.get("/api/doctors").get_json()[0]
        self.assertEqual(doctor["id"], doctor_id)
        self.assertFalse(doctor["verified"])
        self.assertEqual(doctor["badge"], "Profile pending verification")

        profile["verified"] = True
        updated = self.client.put(f"/api/admin/doctors/{doctor_id}", json=profile)
        self.assertEqual(updated.status_code, 200)
        doctor = self.client.get("/api/doctors").get_json()[0]
        self.assertTrue(doctor["verified"])

    def test_osm_import_creates_unverified_hospital(self):
        self.login()
        elements = [{
            "type": "node", "id": 90210, "lat": 26.22, "lon": 78.18,
            "tags": {
                "amenity": "hospital", "name": "OSM Community Hospital",
                "operator:type": "public", "healthcare:speciality": "cardiology",
            },
        }]
        response = self.client.post(
            "/api/admin/osm/import-elements",
            json={"elements": elements},
        )
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result["added"], 1)
        public_record = self.client.get("/api/hospitals").get_json()[0]
        self.assertFalse(public_record["verified"])
        self.assertEqual(public_record["source"], "osm")
        self.assertIn("Cardiology", public_record["services"])


if __name__ == "__main__":
    unittest.main()
