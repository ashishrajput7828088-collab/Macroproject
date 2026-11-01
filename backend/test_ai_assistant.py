import os
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ai_assistant
import app as backend_app


class AiAssistantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = backend_app.app.test_client()

    def test_offline_guidance_is_explicit_and_symptom_aware(self):
        fever = ai_assistant.offline_triage("I have a fever")
        breathing = ai_assistant.offline_triage("Chest me heavy pain and saans lene me dikkat")

        self.assertEqual(fever["aiMode"], "offline")
        self.assertIn("cannot reliably assess", fever["summaryEnglish"])
        self.assertEqual(breathing["urgency"], "EMERGENCY")
        self.assertIn("108", breathing["summaryEnglish"])

    def test_status_reports_missing_gemini_configuration(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "YOUR_GEMINI_API_KEY_HERE"}):
            response = self.client.get("/api/ai/status")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["configured"])

    def test_configured_gemini_result_is_returned_with_recommendations(self):
        result = {
            "urgency": "HIGH",
            "category": "cardiology",
            "recommendedSpecialist": "Cardiologist",
            "summaryHindi": "Hindi response",
            "summaryEnglish": "English response",
            "firstAid": ["Contact a qualified clinician."],
        }
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch.object(backend_app, "call_gemini_api", return_value=result) as generate:
                response = self.client.post("/api/ai/diagnose", json={"symptoms": "chest discomfort"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["poweredBy"], "Google Gemini 2.0 Flash Lite")
        self.assertEqual(response.get_json()["summaryEnglish"], "English response")
        generate.assert_called_once_with("chest discomfort")

    def test_gemini_failure_is_not_replaced_by_a_generic_triage(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch.object(backend_app, "call_gemini_api", side_effect=ai_assistant.GeminiApiError("Gemini unavailable")):
                response = self.client.post("/api/ai/diagnose", json={"symptoms": "rash on my arm"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.get_json()["error"], "Gemini unavailable")

    def test_symptom_input_is_validated(self):
        for payload, expected in (({}, 400), ({"symptoms": "  "}, 400), ({"symptoms": "x" * 2001}, 400)):
            with self.subTest(payload_length=len(payload.get("symptoms", ""))):
                self.assertEqual(self.client.post("/api/ai/diagnose", json=payload).status_code, expected)

    def test_gemini_response_is_normalized(self):
        result = ai_assistant._parse_json_response(
            '{"urgency":"unknown","category":"unknown","recommendedSpecialist":"Doctor",'
            '"summaryHindi":"हिंदी","summaryEnglish":"English","firstAid":["step"]}'
        )

        self.assertEqual(result["urgency"], "HIGH")
        self.assertEqual(result["category"], "general")
        self.assertEqual(result["firstAid"], ["step"])

    def test_gemini_request_keeps_api_key_out_of_url(self):
        response_json = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "urgency": "ROUTINE",
                            "category": "general",
                            "recommendedSpecialist": "General physician",
                            "summaryHindi": "Hindi",
                            "summaryEnglish": "English",
                            "firstAid": ["Contact a clinician."],
                        })
                    }]
                }
            }]
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return json.dumps(response_json).encode("utf-8")

        with patch.dict(os.environ, {"GEMINI_API_KEY": "private-test-key"}):
            with patch.object(ai_assistant.urllib.request, "urlopen", return_value=FakeResponse()) as urlopen:
                result = ai_assistant.call_gemini_api("headache")

        request = urlopen.call_args.args[0]
        self.assertNotIn("private-test-key", request.full_url)
        self.assertEqual(request.get_header("X-goog-api-key"), "private-test-key")
        self.assertIn("gemini-2.0-flash-lite:generateContent", request.full_url)
        self.assertEqual(result["category"], "general")


if __name__ == "__main__":
    unittest.main()
