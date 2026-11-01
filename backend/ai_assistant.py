"""Server-side Gemini integration and a safe, clearly labelled offline fallback."""
import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file securely
_env_file = Path(__file__).resolve().parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()

LOGGER = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-2.0-flash-lite"
CATEGORIES = {
    "cardiology", "orthopedics", "gynecology", "pediatrics", "neurology",
    "ophthalmology", "dermatology", "pulmonology", "gastro", "general",
}
URGENCIES = {"EMERGENCY", "HIGH", "ROUTINE"}


class GeminiApiError(Exception):
    """A safe-to-display Gemini service failure."""


def get_effective_gemini_key(user_key=None):
    if user_key and user_key.strip():
        return user_key.strip()
    env_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not env_key or env_key.startswith("YOUR_"):
        return ""
    return env_key


def gemini_api_configured(user_key=None):
    key = get_effective_gemini_key(user_key)
    return bool(key and not key.startswith("YOUR_"))


def _parse_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError("Gemini response must be a JSON object")

    urgency = str(result.get("urgency", "ROUTINE")).upper()
    category = str(result.get("category", "general")).lower()
    first_aid = result.get("firstAid")
    if urgency not in URGENCIES:
        urgency = "HIGH"
    if category not in CATEGORIES:
        category = "general"
    if not isinstance(first_aid, list):
        first_aid = []

    return {
        "urgency": urgency,
        "category": category,
        "recommendedSpecialist": str(result.get("recommendedSpecialist", "General Physician"))[:120],
        "summaryHindi": str(result.get("summaryHindi", ""))[:1200],
        "summaryEnglish": str(result.get("summaryEnglish", ""))[:1200],
        "firstAid": [str(step)[:240] for step in first_aid[:4] if isinstance(step, str)][:4],
    }


def call_gemini_api(symptoms_text, _user_key=None):
    api_key = get_effective_gemini_key(_user_key)
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        raise GeminiApiError("Gemini is not configured. Add GEMINI_API_KEY to backend/.env and restart the server.")

    prompt = f"""You are Swasthya, a cautious health information and triage assistant for Gwalior, India.
The user describes: {json.dumps(symptoms_text, ensure_ascii=False)}

Respond in the JSON schema provided. Give general information, not a diagnosis. Do not prescribe medicines, doses, or treatment plans. Ask for missing details when the description is vague. Tailor the response to the user's actual words; do not reuse a generic answer. Use the user's language where possible (Hindi/Hinglish or English). For possible emergencies, advise calling India's emergency number 112 or ambulance 108 immediately. Give only low-risk immediate safety steps and make uncertainty clear."""

    schema = {
        "type": "OBJECT",
        "properties": {
            "urgency": {"type": "STRING", "enum": sorted(URGENCIES)},
            "category": {"type": "STRING", "enum": sorted(CATEGORIES)},
            "recommendedSpecialist": {"type": "STRING"},
            "summaryHindi": {"type": "STRING"},
            "summaryEnglish": {"type": "STRING"},
            "firstAid": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": [
            "urgency", "category", "recommendedSpecialist", "summaryHindi",
            "summaryEnglish", "firstAid",
        ],
    }
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.55,
            "maxOutputTokens": 1200,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_json_response(text)
    except urllib.error.HTTPError as error:
        LOGGER.warning("Gemini API returned HTTP %s", error.code)
        if error.code in (400, 401, 403):
            raise GeminiApiError("Gemini rejected the API key or request. Check the key and Gemini API access in Google AI Studio.") from error
        raise GeminiApiError("Gemini is temporarily unavailable. Please try again shortly.") from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        LOGGER.warning("Could not connect to Gemini: %s", error)
        raise GeminiApiError("Could not connect to Gemini. Check the server's internet connection and try again.") from error
    except (KeyError, IndexError, TypeError, ValueError) as error:
        LOGGER.warning("Gemini returned an invalid response: %s", error)
        raise GeminiApiError("Gemini returned an unreadable response. Please try again.") from error


def offline_triage(symptoms_text):
    query = symptoms_text.casefold()
    emergency_terms = (
        "chest pain", "chest tightness", "heavy chest", "chest me", "heart attack",
        "chhati", "dil ka daura", "stroke", "paralysis", "face droop",
        "heavy bleeding", "unconscious", "behosh", "can't breathe", "cant breathe",
        "cannot breathe", "unable to breathe", "breathing difficulty",
        "shortness of breath", "breathlessness", "saans nahi", "saans lene me dikkat",
        "seizure", "poison", "zehar",
    )
    category_terms = {
        "cardiology": ("heart", "cardiac", "chest", "chhati", "dil", "bp", "blood pressure", "palpitation", "dhadkan"),
        "orthopedics": ("bone", "fracture", "joint", "ghutna", "haddi", "back pain", "kamar dard", "kamar", "sprain", "mote", "moch", "jod"),
        "gynecology": ("pregnan", "period", "delivery", "pcos", "garbh", "mahila", "maternity"),
        "pediatrics": ("baby", "child", "infant", "bach", "shishu", "kid"),
        "neurology": ("headache", "migraine", "chakkar", "numb", "seizure", "dora", "sir dard", "sar dard", "sir me", "sar me"),
        "ophthalmology": ("eye", "aankh", "vision", "dhundhla", "motiyabind"),
        "dermatology": ("skin", "rash", "itch", "khujli", "acne", "pimple", "fungal", "daan", "dad"),
        "pulmonology": ("cough", "khansi", "asthma", "breath", "saans", "lungs", "dama", "balgam", "fephde"),
        "gastro": ("stomach", "pet dard", "acidity", "vomit", "ulti", "diarrhea", "dast", "gas", "pet me", "kabz", "constipation", "loose motion"),
    }
    specialists = {
        "cardiology": "Cardiologist",
        "orthopedics": "Orthopedic specialist",
        "gynecology": "Gynecologist",
        "pediatrics": "Pediatrician",
        "neurology": "Neurologist",
        "ophthalmology": "Eye specialist",
        "dermatology": "Dermatologist",
        "pulmonology": "Pulmonologist",
        "gastro": "Gastroenterologist",
        "general": "General physician",
    }
    category = next(
        (name for name, terms in category_terms.items() if any(term in query for term in terms)),
        "general",
    )
    emergency = any(term in query for term in emergency_terms)

    if emergency:
        summary_hindi = "आपके लक्षणों में आपातकालीन चेतावनी संकेत (Emergency signs) मौजूद हैं। तुरंत 108 एम्बुलेंस या 112 पर कॉल करें अथवा नजदीकी JAH / BIMR इमरजेंसी पहुंचें।"
        summary_english = "Your message includes possible emergency warning signs. This is not a diagnosis—call 112 or ambulance 108 now and do not wait for an AI response."
        first_aid = [
            "Call 112 or ambulance 108 immediately and stay on line with dispatcher.",
            "Stay with the patient and move away from immediate danger if safe.",
            "Do not give food, drink, or unprescribed medicines to anyone unconscious.",
            "Proceed immediately to JAH Emergency Trauma or nearest 24x7 hospital."
        ]
        urgency = "EMERGENCY"
    else:
        category_advice_hi = {
            "cardiology": "हार्ट या छाती से जुड़े लक्षणों के लिए कार्डियोलॉजिस्ट (हृदय रोग विशेषज्ञ) से जांच कराएं। ब्लड प्रेशर व ईसीजी की जांच कराएं।",
            "orthopedics": "हड्डी या जोड़ों के दर्द के लिए ऑर्थोपेडिक सर्जन से संपर्क करें। प्रभावित हिस्से पर बर्फ का सेक करें और भारी वजन उठाने से बचें।",
            "neurology": "सिरदर्द, चक्कर या नसों से संबंधित परेशानी के लिए न्यूरोलॉजिस्ट से परामर्श लें। शांत अंधेरे कमरे में आराम करें।",
            "pulmonology": "खांसी या सांस की तकलीफ के लिए पल्मोनोलॉजिस्ट (फेफड़ा रोग विशेषज्ञ) को दिखाएं। भाप (steam) लें और गर्म पानी पिएं।",
            "gastro": "पेट दर्द, गैस या उल्टी-दस्त के लिए गैस्ट्रोएंटेरोलॉजिस्ट से संपर्क करें। ओआरएस (ORS) घोल पिएं और हल्का भोजन लें।",
            "dermatology": "त्वचा पर खुजli या रैश के लिए डर्मेटोलॉजिस्ट से सलाह लें। त्वचा को साफ व सूखा रखें, बिना पर्चे की क्रीम न लगाएं।",
            "pediatrics": "बच्चों के स्वास्थ्य व बुखार के लिए तुरंत पीडियाट्रिशियन (शिशु रोग विशेषज्ञ) से परामर्श लें।",
            "gynecology": "गर्भावस्था या महिलाओं की स्वास्थ्य समस्याओं के लिए गाइनेकोलॉजिस्ट से जांच कराएं।",
            "ophthalmology": "आंखों में दर्द या दृष्टि संबंधी समस्या के लिए नेत्र रोग विशेषज्ञ (Eye Specialist) से संपर्क करें।",
            "general": "बुखार, सर्दी या सामान्य कमजोरी के लिए जनरल फिजिशियन से परामर्श लें। तापमान मापें और पर्याप्त आराम करें।",
        }
        first_aid_map = {
            "gastro": [
                "Drink ORS electrolyte solution frequently to prevent dehydration.",
                "Eat soft, easily digestible food like curd-rice or khichdi.",
                "Avoid oily, spicy foods and outside street food."
            ],
            "pulmonology": [
                "Inhale warm steam for 10-15 minutes.",
                "Sip warm water, ginger tea, or clear soup.",
                "Avoid cold beverages, dust, and smoke exposure."
            ],
            "orthopedics": [
                "Rest the affected joint or limb (avoid weight-bearing).",
                "Apply an ice pack wrapped in a towel for 15 minutes.",
                "Use an elastic support bandage gently if sprained."
            ],
            "neurology": [
                "Rest in a quiet, dark and well-ventilated room.",
                "Drink a glass of water and stay hydrated.",
                "Avoid mobile or computer screen glare and loud noise."
            ],
            "general": [
                "Drink plenty of warm fluids and stay well-hydrated.",
                "Monitor body temperature with a thermometer every 4 hours.",
                "Rest adequately and avoid strenuous physical exertion."
            ]
        }

        summary_hindi = category_advice_hi.get(category, "स्वास्थ्य संबंधी परेशानी के लिए योग्य डॉक्टर से परामर्श लें।")
        summary_english = f"Automated clinical triage for suspected {category} symptoms (Recommended: {specialists[category]}). Note: An automated system cannot reliably assess your condition or replace a clinical examination by a qualified doctor."
        first_aid = first_aid_map.get(category, [
            "This offline response cannot diagnose your condition.",
            "Seek advice from a qualified clinician, especially if symptoms worsen.",
            "In case of severe discomfort, visit nearest hospital casualty."
        ])
        urgency = "ROUTINE"

    return {
        "urgency": urgency,
        "category": category,
        "recommendedSpecialist": specialists[category],
        "summaryHindi": summary_hindi,
        "summaryEnglish": summary_english,
        "firstAid": first_aid,
        "poweredBy": "Swasthya Emergency Triage Engine" if emergency else "Swasthya Clinical Health Engine",
        "aiMode": "offline",
    }
