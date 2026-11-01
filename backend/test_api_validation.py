import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app as backend_app
from config import DEFAULT_CENTER_LAT, DEFAULT_CENTER_LNG


class APIValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = backend_app.app.test_client()

    def test_sos_rejects_invalid_coordinates(self):
        for payload in ({"lat": "not-a-number"}, {"lat": 91, "lng": 0}, {"lat": 0, "lng": float("inf")}):
            with self.subTest(payload=payload):
                response = self.client.post("/api/emergency/sos", json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_appointment_rejects_invalid_numbers(self):
        base = {
            "patientName": "Test Patient",
            "patientPhone": "1234567890",
            "appointmentDate": "2026-10-25",
        }
        for field, value in (
            ("patientAge", "invalid"),
            ("patientAge", 131),
            ("patientAge", float("inf")),
            ("fee", "invalid"),
            ("fee", 10.5),
            ("fee", -1),
        ):
            with self.subTest(field=field, value=value):
                response = self.client.post("/api/appointments", json={**base, field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_spatial_endpoints_reject_invalid_queries(self):
        paths = (
            "/api/hospitals/nearby?lat=NaN&lng=0",
            "/api/hospitals/nearby?lat=26&lng=78&radius=-1",
            "/api/hospitals/nearby?lat=26&lng=78&algorithm=unknown",
            "/api/hospitals/nearest?lat=26&lng=78&k=-1",
            "/api/hospitals/area?south=27&west=78&north=26&east=79",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 400)

    def test_compare_nearest_returns_k_closest(self):
        response = self.client.get(
            f"/api/compare?mode=nearest&lat={DEFAULT_CENTER_LAT}&lng={DEFAULT_CENTER_LNG}&k=2&reps=2"
        )
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertTrue(result["allMatchBruteForce"])
        self.assertEqual(result["reps"], 2)
        for algorithm in result["algorithms"].values():
            self.assertEqual(algorithm["found"], min(2, result["datasetSize"]))

    def test_compare_radius_and_area_results_match(self):
        queries = (
            f"/api/compare?mode=radius&lat={DEFAULT_CENTER_LAT}&lng={DEFAULT_CENTER_LNG}&radius=5&reps=2",
            f"/api/compare?mode=area&south={DEFAULT_CENTER_LAT - 0.1}&west={DEFAULT_CENTER_LNG - 0.1}"
            f"&north={DEFAULT_CENTER_LAT + 0.1}&east={DEFAULT_CENTER_LNG + 0.1}&reps=2",
        )
        for path in queries:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.get_json()["allMatchBruteForce"])

    def test_compare_rejects_invalid_mode_and_repetitions(self):
        queries = (
            f"/api/compare?mode=unsupported&lat={DEFAULT_CENTER_LAT}&lng={DEFAULT_CENTER_LNG}",
            f"/api/compare?mode=nearest&lat={DEFAULT_CENTER_LAT}&lng={DEFAULT_CENTER_LNG}&k=2&reps=0",
        )
        for path in queries:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 400)

    def test_appointment_duplicate_and_reschedule(self):
        import secrets
        uid = secrets.token_hex(4)
        rand_day1 = secrets.randbelow(20) + 1
        rand_day2 = secrets.randbelow(20) + 1
        rand_year = 2030 + secrets.randbelow(50)
        date1 = f"{rand_year}-01-{rand_day1:02d}"
        date2 = f"{rand_year}-02-{rand_day2:02d}"
        payload = {
            "patientName": f"Test Patient {uid}",
            "patientPhone": "9876543210",
            "appointmentDate": date1,
            "timeSlot": "11:30 AM",
            "doctorId": 1,
            "doctorName": "Dr. Pradeep Kashyap"
        }
        res1 = self.client.post("/api/appointments", json=payload)
        self.assertEqual(res1.status_code, 200)
        token_id = res1.get_json()["appointment"]["tokenId"]

        try:
            # Duplicate should return 409
            res_dup = self.client.post("/api/appointments", json=payload)
            self.assertEqual(res_dup.status_code, 409)

            # Reschedule to free slot
            res_resched = self.client.patch(f"/api/appointments/{token_id}/reschedule", json={
                "appointmentDate": date2,
                "timeSlot": "04:00 PM"
            })
            self.assertEqual(res_resched.status_code, 200)
            self.assertTrue(res_resched.get_json()["ok"])
        finally:
            self.client.delete(f"/api/appointments/{token_id}")

    def test_blood_donor_and_request_apis(self):
        donor_res = self.client.post("/api/blood-banks/donate", json={
            "name": "Rahul Sharma",
            "phone": "9826012345",
            "bloodGroup": "O+",
            "city": "Gwalior",
            "age": 28
        })
        self.assertEqual(donor_res.status_code, 200)
        self.assertTrue(donor_res.get_json()["ok"])

        # Blood request
        req_res = self.client.post("/api/blood-banks/request", json={
            "patientName": "Aman Gupta",
            "bloodGroup": "O+",
            "unitsNeeded": 2,
            "hospitalName": "JA Hospital Gwalior",
            "contactPhone": "9826054321",
            "urgency": "Immediate Emergency"
        })
        self.assertEqual(req_res.status_code, 200)
        self.assertTrue(req_res.get_json()["ok"])


if __name__ == "__main__":
    unittest.main()
