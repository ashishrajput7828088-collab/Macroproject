# Arogya Gwalior - Enterprise Healthcare Network & Hospital Finder

> **A production-ready, international-standard healthcare & emergency medical platform for Gwalior, Madhya Pradesh inspired by Apollo 24/7 and Practo.**

---

## 🌟 Architecture & Features

### 1. 🏥 Gwalior Hospital Directory
- The current database contains **22 authentic Gwalior hospital listings** (JAH Group, GRMC, BIMR, Cancer Hospital & Research Institute CHRI, Scindia Devraj Hospital, Gwalior Mansik Arogyashala, K.D. Super Speciality, Navjeevan Hospital, Chirayu Children Hospital & NICU, Shri Ram Hospital, Apollo Clinic, Civil Hospital Morar, and more).
- Hospital cards include verified contact numbers, GPS locations, facility tags, and 4-tier bed availability (Total, ICU, Ventilator, Oxygen).

### 2. 👨‍⚕️ Doctor Directory
- The current database contains **18 specialist doctor profile records** across Cardiology, Neurology, Orthopedics, Gastroenterology, Pulmonology, Pediatrics, Gynecology, Oncology, and Ophthalmology.
- Verified fees, OPD timings, patient rating, and direct instant booking.

### 3. 📅 Digital Appointment Booking & OPD Pass Token System
- Book OPD or Online Video consultations directly from home.
- Real-time date selector (Today, Tomorrow, next 5 days) + morning/afternoon/evening time slots.
- Instant **Digital OPD Pass & Token ID Generation** (e.g. `GWL-202610-A9F2`) with printable slip.
- **"My Bookings" Dashboard**: Manage upcoming consultations and cancel appointments anytime.

### 4. 🩸 24x7 Blood Banks Directory with Live Blood Group Inventory
- Real Gwalior blood banks (JAH Blood Bank, Red Cross Society, BIMR Blood Bank, Cancer Hospital Blood Bank, Rotary Blood Bank).
- Live stock counts for **A+, A-, B+, B-, O+, O-, AB+, AB-**.
- 1-click filter by blood group and 24x7 emergency helpline dialing.

### 5. 🚑 24x7 Emergency Ambulance Dispatch System
- Fleet tracking for **Advanced Cardiac Life Support (ALS)**, **Basic Life Support (BLS)**, and **Janani Express**.
- Real base hubs (JAH Trauma, BIMR Morar, Phoolbagh Central, Morar Civil, Thatipur, Hazira).
- Equipment breakdown (Defibrillator, Ventilator, Suction, Oxygen).
- Direct one-click ambulance dispatch telephone dialer.

### 6. 🚨 1-Click Emergency SOS GPS Ambulance Dispatch
- Prominent floating SOS beacon button with concentric pulse wave animation.
- Automatic GPS latitude and longitude capture.
- Immediate dispatch code generation (e.g. `SOS-GWL-76291`) with 6-8 minute ETA assignment.
- Emergency hotlines: **National Ambulance 108**, **Emergency 112**, **JAH Trauma 0751-2403222**.

### 7. 🤖 Swasthya AI Clinical Health Assistant (Dr. Arogya)
- Conversational medical triage assistant supporting **Hindi, English, and Hinglish**.
- Detects emergency red flags (**cardiac arrest/chest pain, stroke, breathing distress, severe trauma**) and triggers high-priority alerts with emergency contact links.
- Evaluates fever, viral infection, pediatric distress, joint pain, abdominal pain, etc.
- Automatically recommends the exact specialist doctor and hospital in Gwalior with a direct booking button!

### 8. 🗺️ Interactive Map
- Defaults to keyless **Esri World Street Map**, with **Esri World Imagery**, **OpenStreetMap**, and optional Mapbox Streets/Satellite styles.
- Map tiles are refreshed on layout changes, with alternate tile providers attempted if the selected provider fails. High zoom levels reuse each provider's highest native tile zoom to avoid blank maps. Map style changes apply immediately and are remembered in the browser.
- Hospital markers in the visible map area are fetched through the backend's **K-D Tree** or **Quadtree** radius search. Choose the index in the Map search selector; panning and zooming refresh the visible marker set.
- **OSRM driving routes** with turn-by-turn steps, estimated distance and travel time; Google Maps can launch navigation using the device's current location.
- Pulsing emergency hospital markers with color-coded classification.

### 9. ⚡ Spatial Data Structures & Algorithm Lab (DSA)
- Live side-by-side performance comparison:
  - **Brute Force Spatial Search: O(N)**
  - **K-D Tree Spatial Index: O(log N)**
  - **Quadtree Spatial Partitioning: O(log N)**
- Scaling test on 1,000 to 20,000 synthetic spatial coordinates.

---

## 🚀 How to Run the Project in VS Code

### Quick Start (Full Stack with Flask & SQLite)
1. Open the project folder in **Visual Studio Code**:
   ```bash
   code "d:\VS Code\gwalior-hospital-finder-v3"
   ```
2. Open the built-in terminal (`Ctrl + \`` or `Terminal -> New Terminal`).
3. (Optional) Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   ```
4. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
5. Configure the health assistant:
   - Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Open `backend/.env` and replace the `GEMINI_API_KEY` placeholder with your key.
   - Keep the key private; it is used by the Flask backend and is never saved in browser storage.
   - Restart the Flask server after changing the key.
6. Start the Flask server:
   ```bash
   cd backend
   python app.py
   ```
7. Open your browser:
   - **User Application**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - **Admin Management Portal**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin) (Default Login: `admin` / `admin123`)

---

## 🔑 Mapbox Public Token Configuration

The default map uses Esri World Street Map tiles; Esri World Imagery is also available without a Mapbox token. To enable Mapbox Streets and Satellite, set `MAPBOX_ACCESS_TOKEN=pk...` in `backend/.env` and restart Flask. The `/api/config` endpoint supplies the public token to the map client. Mapbox public tokens are visible in browser requests: restrict the token to your site URL and rotate any token previously committed in client code.

You can also enter a public token from Map Settings; that override is saved only in the current browser.

## 🏥 Hospital and Doctor Directory Management

Open `/admin`, sign in, and add hospital or doctor listings. The admin page can also import hospital locations from OpenStreetMap. Imported records have no verified bed counts, and must be reviewed before marking details verified. Hospital photos can be added with an HTTPS URL and a photo credit; the slideshow does not use stock images as if they belonged to a facility.

---

## 📡 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health status and database connectivity check |
| `GET` | `/api/config` | Public configuration (Mapbox token, map center) |
| `GET` | `/api/hospitals` | Fetch active hospital listings, services and verification status |
| `GET` | `/api/hospitals/nearby?lat=...&lng=...&radius=3` | Spatial search using K-D Tree / Quadtree |
| `GET` | `/api/doctors` | List doctor profiles (filter by `category`) |
| `GET` | `/api/admin/hospitals` | List all hospital records (admin session required) |
| `POST` | `/api/admin/osm/import` | Import hospital locations from OpenStreetMap (admin session required) |
| `GET` | `/api/admin/doctors` | List doctor records (admin session required) |
| `GET` | `/api/blood-banks` | 5 verified blood banks with live inventory (A+, B+, O+, AB+) |
| `GET` | `/api/ambulances` | 24x7 emergency ambulances with base hubs and equipment |
| `POST` | `/api/emergency/sos` | 1-Click SOS emergency ambulance dispatch |
| `POST` | `/api/appointments` | Book OPD consultation and get a digital token slip |
| `GET` | `/api/appointments?phone=...` | Retrieve patient appointments |
| `DELETE`| `/api/appointments/<token_id>` | Cancel an appointment |
| `GET` | `/api/ai/status` | Check whether the server-side Gemini integration is configured |
| `POST` | `/api/ai/diagnose` | Gemini-powered general health information and Gwalior care recommendations |
| `POST` | `/api/auth/register` | User signup with secure SHA-256 password hashing |
| `POST` | `/api/auth/login` | User authentication & session establishment |
| `GET` | `/api/compare?mode=radius\|nearest\|area` | Compare Brute-Force, K-D Tree, and Quadtree results and average query time across repetitions |

---

## 🛡️ Enterprise Offline Fallback Capability

Arogya Gwalior is engineered with **Zero Single Point of Failure (Zero SPoF)**. If the Python Flask backend is stopped, the entire frontend (`index.html`) automatically falls back to `config.js` and `hospitals-data.js`, ensuring:
- All 16 hospitals and 12 doctors remain fully visible.
- Blood bank stock and ambulances remain accessible.
- Appointment passes and AI triage continue working in the browser via offline clinical heuristics.

---

## 👥 Authors & License
Created for Gwalior citizens and healthcare providers. MIT Licensed.
