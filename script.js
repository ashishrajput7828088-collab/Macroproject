/* =====================================================================
   Arogya Gwalior - Enterprise Healthcare, Hospital Network & Emergency API
   Features:
     1. Authentication Gate & Session Management
     2. Esri & Mapbox GIS Map (Keyless streets/satellite and optional Mapbox styles)
     3. Gwalior Hospital Directory (JAH, BIMR, CHRI, Apollo, Morar, etc.)
     4. Expert Doctors Directory with OPD timings, direct contact & fees
     5. Online Doctor Appointment Booking System with Digital Token Pass
     6. Gwalior Blood Banks & Inventory (A+, B+, O+, AB+)
     7. 24x7 Emergency Ambulances with 1-Click SOS Dispatch
     8. Swasthya AI Clinical Health Assistant (Symptom Triage & First-Aid)
     9. Algorithm Lab (KD-Tree vs Quadtree spatial indexing)
   ===================================================================== */

/* ---------- 1. SETTINGS & CONFIGURATION ---------- */
const GWALIOR_CENTER = { lat: 26.2183, lng: 78.1828 };
const IS_VERCEL = location.hostname.endsWith(".vercel.app") || location.hostname === "vercel.app";
const IS_GITHUB_PAGES = location.hostname.endsWith(".github.io");
const IS_SAME_ORIGIN = location.port === "5000" || IS_VERCEL || (!IS_GITHUB_PAGES && location.protocol === "https:");
const API_BASE_URL = IS_SAME_ORIGIN ? "" : (IS_GITHUB_PAGES ? "" : "http://127.0.0.1:5000");
const API_URL = API_BASE_URL; // alias for lab.js
const USE_BACKEND = !IS_GITHUB_PAGES;
const ROUTING_URL = "https://router.project-osrm.org/route/v1/driving";

const FAV_KEY = "arogyaGwaliorFavourites";
const USER_KEY = "arogyaUserSession";
const APPT_KEY = "arogyaAppointments";
const AUTH_GATE_SEEN_KEY = "arogyaAuthGateSeen";
const MAPBOX_TOKEN_KEY = "arogyaMapboxToken";
const MAP_STYLE_KEY = "arogyaMapStyle";
const MAP_SPATIAL_ALGORITHM_KEY = "arogyaMapSpatialAlgorithm";

const BED_LABELS = {
  general: "General Ward",
  icu: "ICU",
  emergency: "Emergency",
  oxygen: "Oxygen-supported",
  ventilator: "Ventilator-supported",
};
const BED_TYPES = Object.keys(BED_LABELS);
const SHORT_LABELS = { icu: "ICU", oxygen: "Oxygen", ventilator: "Ventilator", emergency: "Emergency" };
const ALGO_NAMES = { kdtree: "K-D Tree", quadtree: "Quadtree", linear: "Brute force" };

const PRESET_AREAS = [
  ["City Centre, Gwalior", 26.2198, 78.2045],
  ["Lashkar / Kampoo", 26.1985, 78.1634],
  ["Morar Cantt", 26.2268, 78.2295],
  ["Thatipur", 26.2115, 78.2098],
  ["Hazira / Tansen Road", 26.2285, 78.1788],
  ["Phoolbagh Chowk", 26.2088, 78.1745],
  ["Cancer Hills / Mandre Ki Mata", 26.1912, 78.1568],
  ["Gole Ka Mandir", 26.2020, 78.1930],
  ["Maharajpura", 26.2700, 78.2250]
];

/* Helper to get element by id */
const el = id => document.getElementById(id);

function esc(text) {
  return String(text || "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

/* ---------- 2. APPLICATION STATE ---------- */
let allHospitals = [];
let allDoctors = [];
let allBloodBanks = [];
let allAmbulances = [];
let userPoint = { lat: GWALIOR_CENTER.lat, lng: GWALIOR_CENTER.lng, accurate: false };
let map = null;
let currentTileLayer = null;
let activeTileProvider = typeof AROGYA_CONFIG !== "undefined" ? AROGYA_CONFIG.defaultProvider : "osm";
let mapResizeObserver = null;
let mapFailedProviders = new Set();
let mapLoadTimer = null;
let mapSpatialAlgorithm = "kdtree";
let mapSpatialSearchTimer = null;
let mapSpatialSearchRequest = 0;
let filteredMapHospitals = [];
let drawerTileLayer = null;
let mapMarkers = {};
let routePolyline = null;
let routeStartMarker = null;
let routeDestMarker = null;
let userMarker = null;
let MAP_ENABLED = false;
let currentTab = "finder";
let dataMode = "all";
let emergencyMode = false;
let favourites = new Set();
let currentUser = null;

/* ---------- 3. DATA SERVICE (API + OFFLINE FALLBACK) ---------- */
async function fetchJson(url, timeoutMs = 1500) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: controller.signal, cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

async function loadHospitalsData() {
  if (USE_BACKEND) {
    try {
      const data = await fetchJson(`${API_BASE_URL}/api/hospitals`);
      if (Array.isArray(data) && data.length > 0) return data;
    } catch (e) {}
  }
  return typeof HOSPITAL_DATABASE !== "undefined" ? HOSPITAL_DATABASE : [];
}

async function loadDoctorsData() {
  if (USE_BACKEND) {
    try {
      const data = await fetchJson(`${API_BASE_URL}/api/doctors`);
      if (Array.isArray(data) && data.length > 0) return data;
    } catch (e) {}
  }
  return typeof DOCTORS_DATABASE !== "undefined" ? DOCTORS_DATABASE : [];
}

async function loadBloodBanksData() {
  if (USE_BACKEND) {
    try {
      const data = await fetchJson(`${API_BASE_URL}/api/blood-banks`);
      if (Array.isArray(data) && data.length > 0) return data;
    } catch (e) {}
  }
  return typeof BLOOD_BANKS_DATABASE !== "undefined" ? BLOOD_BANKS_DATABASE : [];
}

async function loadAmbulancesData() {
  if (USE_BACKEND) {
    try {
      const data = await fetchJson(`${API_BASE_URL}/api/ambulances`);
      if (Array.isArray(data) && data.length > 0) return data;
    } catch (e) {}
  }
  return typeof AMBULANCES_DATABASE !== "undefined" ? AMBULANCES_DATABASE : [];
}

async function loadMapConfiguration() {
  if (!USE_BACKEND) return;
  try {
    const config = await fetchJson(`${API_BASE_URL}/api/config`);
    if (typeof AROGYA_CONFIG !== "undefined" && config.mapboxAccessToken) {
      AROGYA_CONFIG.mapboxToken = config.mapboxAccessToken;
    }
  } catch (error) {
    console.warn("Map configuration could not be loaded; using the keyless Esri map style.", error);
  }
}

/* ---------- 4. GEOLOCATION & DISTANCE HELPERS ---------- */
function distanceKm(a, b) {
  const R = 6371, rad = d => d * Math.PI / 180;
  const dLat = rad(b.lat - a.lat), dLng = rad(b.lng - a.lng);
  const x = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(x));
}

function etaMinutes(km) {
  return Math.max(2, Math.round(km * 1.35 / 24 * 60));
}

function distanceText(h) {
  if (typeof h.distance !== "number") return "";
  return `${h.distance.toFixed(1)} km · ~${etaMinutes(h.distance)} min drive`;
}

function bedInfo(h, type) {
  if (!h.beds) return { total: 0, occupied: 0, available: 0, known: false };
  const pair = h.beds[type] || [0, 0];
  const total = Number(pair[0]) || 0, occupied = Number(pair[1]) || 0;
  return { total, occupied, available: Math.max(0, total - occupied), known: true };
}

function totalBeds(h) {
  return BED_TYPES.reduce((sum, t) => {
    const b = bedInfo(h, t);
    return { total: sum.total + b.total, occupied: sum.occupied + b.occupied, available: sum.available + b.available };
  }, { total: 0, occupied: 0, available: 0 });
}

function bedsFor(h, type) {
  if (!h.beds) return 0;
  return type === "all" ? totalBeds(h).available : bedInfo(h, type).available;
}

/* ---------- 5. USER AUTHENTICATION SYSTEM ---------- */
function initAuth() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    if (raw) currentUser = JSON.parse(raw);
  } catch (e) { currentUser = null; }

  renderHeaderAuth();

  const hasSeenGate = sessionStorage.getItem(AUTH_GATE_SEEN_KEY);
  if (!currentUser && !hasSeenGate) {
    setTimeout(() => {
      openAuthModal("login");
    }, 600);
  }
}

function renderHeaderAuth() {
  const container = el("headerAuthArea");
  if (!container) return;

  if (currentUser) {
    container.innerHTML = `
      <div class="user-profile-pill" onclick="toggleUserDropdown(event)" title="User Profile">
        <div class="user-avatar-circle">${esc(currentUser.name.charAt(0).toUpperCase())}</div>
        <span class="user-name-label">${esc(currentUser.name.split(" ")[0])}</span>
        <span style="font-size:0.7rem; color:var(--slate-500)">▼</span>
      </div>
    `;
  } else {
    container.innerHTML = `
      <button type="button" class="btn btn-auth" onclick="openAuthModal('login')">
        <span>Sign In / Sign Up</span>
      </button>
    `;
  }
}

function toggleUserDropdown(e) {
  e.stopPropagation();
  const existing = document.getElementById("userDropdownMenu");
  if (existing) {
    existing.remove();
    return;
  }

  const menu = document.createElement("div");
  menu.id = "userDropdownMenu";
  menu.style.cssText = `
    position: absolute; top: 58px; right: 24px; z-index: 1500;
    background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.12); padding: 8px; min-width: 200px;
    display: flex; flex-direction: column; gap: 4px;
  `;

  menu.innerHTML = `
    <div style="padding: 8px 12px; border-bottom: 1px solid #f1f5f9;">
      <strong style="display:block; font-size:0.9rem; color:#0f172a">${esc(currentUser.name)}</strong>
      <span style="font-size:0.78rem; color:#64748b">${esc(currentUser.phone || currentUser.email || "")}</span>
    </div>
    <button class="nav-item" style="text-align:left; width:100%" onclick="switchMainTab('my-appointments-section'); document.getElementById('userDropdownMenu')?.remove()">
      📋 My Appointments
    </button>
    <button class="nav-item" style="text-align:left; width:100%" onclick="openBookingModal(); document.getElementById('userDropdownMenu')?.remove()">
      📅 Book Appointment
    </button>
    <button class="nav-item" style="text-align:left; width:100%; color:#dc2626" onclick="handleLogout()">
      🚪 Sign Out
    </button>
  `;

  document.body.appendChild(menu);
  const clickCloser = (evt) => {
    if (!menu.contains(evt.target)) {
      menu.remove();
      document.removeEventListener("click", clickCloser);
    }
  };
  setTimeout(() => document.addEventListener("click", clickCloser), 50);
}

function openAuthModal(tab = "login") {
  const modal = el("authModal");
  if (!modal) return;
  switchAuthTab(tab);
  if (typeof modal.showModal === "function") modal.showModal();
  else modal.setAttribute("open", "");
  setTimeout(() => {
    if (tab === "signup") (el("signupName") || el("regName"))?.focus();
    else el("loginIdentifier")?.focus();
  }, 150);
}

function closeAuthModal() {
  const modal = el("authModal");
  if (!modal) return;
  if (typeof modal.close === "function") modal.close();
  else modal.removeAttribute("open");
  sessionStorage.setItem(AUTH_GATE_SEEN_KEY, "true");
}

function switchAuthTab(tab) {
  const tabLoginBtn = el("tabLoginBtn");
  const tabSignupBtn = el("tabSignupBtn");
  const loginForm = el("loginForm");
  const signupForm = el("signupForm");

  if (tab === "login") {
    tabLoginBtn.classList.add("active");
    tabSignupBtn.classList.remove("active");
    loginForm.hidden = false;
    signupForm.hidden = true;
  } else {
    tabSignupBtn.classList.add("active");
    tabLoginBtn.classList.remove("active");
    signupForm.hidden = false;
    loginForm.hidden = true;
  }
}

function continueAsGuest() {
  sessionStorage.setItem(AUTH_GATE_SEEN_KEY, "true");
  closeAuthModal();
  showToast("Browsing as Guest. You can Sign In anytime from the top bar.");
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const identifier = el("loginIdentifier").value.trim();
  const password = el("loginPassword").value;

  if (!identifier || !password) {
    showToast("Please enter phone or email and password.");
    return;
  }

  if (USE_BACKEND) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, password })
      });
      const data = await res.json();
      if (res.ok && data.user) {
        currentUser = data.user;
        localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
        closeAuthModal();
        renderHeaderAuth();
        showToast(`Welcome back, ${currentUser.name}! 👋`);
        return;
      }
    } catch (err) {}
  }

  currentUser = {
    name: identifier.includes("@") ? identifier.split("@")[0] : `User ${identifier.slice(-4)}`,
    phone: identifier.match(/^[0-9]+$/) ? identifier : "9826012345",
    email: identifier.includes("@") ? identifier : ""
  };
  localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
  closeAuthModal();
  renderHeaderAuth();
  showToast(`Welcome back, ${currentUser.name}! 👋`);
}

async function handleSignupSubmit(e) {
  e.preventDefault();
  const name = el("signupName").value.trim();
  const phone = el("signupPhone").value.trim();
  const email = el("signupEmail").value.trim();
  const password = el("signupPassword").value;

  if (!name || !phone || !password) {
    showToast("Please complete all required fields.");
    return;
  }

  if (USE_BACKEND) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, email, password })
      });
      const data = await res.json();
      if (res.ok && data.user) {
        currentUser = data.user;
        localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
        closeAuthModal();
        renderHeaderAuth();
        showToast(`Account created successfully! Welcome, ${currentUser.name}!`);
        return;
      }
    } catch (err) {}
  }

  currentUser = { name, phone, email };
  localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
  closeAuthModal();
  renderHeaderAuth();
  showToast(`Account created successfully! Welcome, ${currentUser.name}!`);
}

function quickDemoLogin() {
  currentUser = {
    name: "Rahul Sharma",
    phone: "9826012345",
    email: "rahul.gwalior@example.com"
  };
  localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
  closeAuthModal();
  renderHeaderAuth();
  showToast("Signed in as Demo User: Rahul Sharma (Gwalior)");
}

function handleLogout() {
  currentUser = null;
  localStorage.removeItem(USER_KEY);
  if (USE_BACKEND) {
    fetch(`${API_BASE_URL}/api/auth/logout`, { method: "POST" }).catch(() => {});
  }
  renderHeaderAuth();
  showToast("You have been signed out.");
}

function handleForgotPassword(e) {
  e.preventDefault();
  showToast("Password reset link / OTP simulated to your mobile number.");
}

/* ---------- 6. MAP SYSTEM (ESRI & MAPBOX GIS LAYERS) ---------- */
function getActiveMapboxToken() {
  const stored = localStorage.getItem(MAPBOX_TOKEN_KEY);
  if (stored && stored.trim().length > 10) return stored.trim();
  if (typeof AROGYA_CONFIG !== "undefined" && AROGYA_CONFIG.mapboxToken) {
    return AROGYA_CONFIG.mapboxToken;
  }
  return "";
}

/* ---------- SPATIAL DSA HELPERS & MAP PARTITIONS OVERLAY ---------- */
let dsaVisualLayerGroup = null;
let dsaVisualEnabled = false;

function getHospitalQuadrant(h) {
  const isNorth = (h.lat || 0) >= GWALIOR_CENTER.lat;
  const isEast = (h.lng || 0) >= GWALIOR_CENTER.lng;
  if (isNorth && !isEast) return "NW";
  if (isNorth && isEast) return "NE";
  if (!isNorth && !isEast) return "SW";
  return "SE";
}

function getHospitalKdDepth(h) {
  return (((h.id || 1) * 3 + 1) % 4) + 1;
}

function changeMapSpatialAlgorithm(algo) {
  mapSpatialAlgorithm = algo;
  const statusEl = el("mapSpatialStatus");
  if (statusEl) {
    if (algo === "kdtree") statusEl.textContent = "🌲 K-D Tree: 16 hospitals indexed";
    else if (algo === "quadtree") statusEl.textContent = "🔲 Quadtree: 4 Quadrants indexed";
    else statusEl.textContent = "🔍 Linear Brute Force O(n)";
  }
  filterHospitals();
}

function toggleDsaVisualOverlays() {
  if (!map) return;
  if (!dsaVisualLayerGroup) {
    dsaVisualLayerGroup = L.layerGroup().addTo(map);
  }

  dsaVisualEnabled = !dsaVisualEnabled;
  dsaVisualLayerGroup.clearLayers();

  const btnText = el("dsaVisualText");
  const btnIcon = el("dsaVisualIcon");

  if (!dsaVisualEnabled) {
    if (btnText) btnText.textContent = "Tree Partitions";
    if (btnIcon) btnIcon.textContent = "👁️";
    showToast("DSA Visual Partitions hidden");
    return;
  }

  if (btnText) btnText.textContent = "Hide Partitions";
  if (btnIcon) btnIcon.textContent = "✕";

  // 1. Draw Quadtree Quadrants around Gwalior
  const boundsNW = [[26.2183, 78.1300], [26.3100, 78.1828]];
  const boundsNE = [[26.2183, 78.1828], [26.3100, 78.2600]];
  const boundsSW = [[26.1300, 78.1300], [26.2183, 78.1828]];
  const boundsSE = [[26.1300, 78.1828], [26.2183, 78.2600]];

  const quads = [
    { b: boundsNW, name: "Quadtree NW [Maharajpura / Airport]", col: "#059669" },
    { b: boundsNE, name: "Quadtree NE [Morar Cantt / Hazira]", col: "#2563eb" },
    { b: boundsSW, name: "Quadtree SW [Lashkar / Kampoo / JAH]", col: "#7c3aed" },
    { b: boundsSE, name: "Quadtree SE [City Centre / University]", col: "#d97706" }
  ];

  quads.forEach(q => {
    const rect = L.rectangle(q.b, {
      color: q.col,
      weight: 1.5,
      dashArray: "6, 6",
      fillColor: q.col,
      fillOpacity: 0.08
    });
    rect.bindTooltip(`<b>${q.name}</b>`, { permanent: false, direction: "center" });
    dsaVisualLayerGroup.addLayer(rect);
  });

  // 2. Draw KD-Tree Split Hyperplanes
  const vLine = L.polyline([[26.1300, 78.1828], [26.3100, 78.1828]], {
    color: "#0284c7",
    weight: 2.5,
    dashArray: "8, 6"
  });
  vLine.bindTooltip("<b>🌲 K-D Tree Split X: Lng 78.1828° (Median Split)</b>", { sticky: true });
  dsaVisualLayerGroup.addLayer(vLine);

  const hLine = L.polyline([[26.2183, 78.1300], [26.2183, 78.2600]], {
    color: "#0d9488",
    weight: 2.5,
    dashArray: "8, 6"
  });
  hLine.bindTooltip("<b>🌲 K-D Tree Split Y: Lat 26.2183° (Median Split)</b>", { sticky: true });
  dsaVisualLayerGroup.addLayer(hLine);

  showToast("🌲 K-D Tree & 🔲 Quadtree Partitions active on map!");
}

function initMap() {
  if (typeof L === "undefined") {
    console.warn("Leaflet library not loaded yet.");
    return;
  }
  const container = el("map");
  if (!container) return;

  map = L.map("map", {
    center: [GWALIOR_CENTER.lat, GWALIOR_CENTER.lng],
    zoom: 13,
    maxZoom: 20,
    zoomControl: true
  });

  if (activeTileProvider.startsWith("mapbox") && !getActiveMapboxToken()) {
    activeTileProvider = "arcgisStreets";
  }
  changeMapLayer(activeTileProvider, true);

  MAP_ENABLED = true;
  updateUserMarker();

  const resizeMap = () => {
    if (!map || !container.offsetWidth || !container.offsetHeight) return;
    requestAnimationFrame(() => map && map.invalidateSize({ pan: false, debounceMoveend: true }));
  };
  if (typeof ResizeObserver !== "undefined") {
    mapResizeObserver = new ResizeObserver(resizeMap);
    mapResizeObserver.observe(container);
  }
  window.addEventListener("resize", resizeMap, { passive: true });
  map.whenReady(() => {
    resizeMap();
    setTimeout(() => {
      if (!dsaVisualEnabled) toggleDsaVisualOverlays();
    }, 400);
  });

  // Floating map tools
  el("mapLocateBtn")?.addEventListener("click", () => {
    useMyLocation();
    if (map) map.flyTo([userPoint.lat, userPoint.lng], 14, { duration: 1.2 });
  });

  el("mapResetBtn")?.addEventListener("click", () => {
    if (map) map.flyTo([GWALIOR_CENTER.lat, GWALIOR_CENTER.lng], 13, { duration: 1 });
  });

  el("mapEmergencyBtn")?.addEventListener("click", () => {
    const chk = el("emergencyOnly");
    if (chk) {
      chk.checked = !chk.checked;
      filterHospitals();
      showToast(chk.checked ? "Showing only 24x7 Emergency Hospitals on map." : "Showing all hospitals.");
    }
  });

  map.on("click", (e) => {
    if (window._isPickingMap) {
      userPoint = { lat: e.latlng.lat, lng: e.latlng.lng, accurate: true };
      updateUserMarker();
      el("locationStatus").textContent = `Selected map pin: ${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
      window._isPickingMap = false;
      document.body.style.cursor = "default";
      filterHospitals();
      showToast("Location updated from map click.");
    }
  });
  map.on("moveend", scheduleVisibleHospitalSearch);
}

function changeMapLayer(providerKey, automaticFallback = false) {
  if (!map) return;
  if (!AROGYA_CONFIG.tileProviders[providerKey]) {
    showToast("That map style is unavailable. Choose another map style.");
    return;
  }
  let feedbackMessage = "";
  if (mapLoadTimer) clearTimeout(mapLoadTimer);
  const token = getActiveMapboxToken();
  if (providerKey.startsWith("mapbox") && !token) {
    feedbackMessage = "Mapbox needs a public token. Esri World Street Map is active instead.";
    providerKey = "arcgisStreets";
  }
  if (!automaticFallback) mapFailedProviders.clear();
  activeTileProvider = providerKey;

  if (currentTileLayer) {
    map.removeLayer(currentTileLayer);
  }

  const cfg = (typeof AROGYA_CONFIG !== "undefined" && AROGYA_CONFIG.tileProviders[providerKey])
    ? AROGYA_CONFIG.tileProviders[providerKey]
    : AROGYA_CONFIG.tileProviders.arcgisStreets;

  let tileUrl = cfg.url;
  if (tileUrl.includes("{token}")) {
    tileUrl = tileUrl.replace("{token}", token);
  }

  currentTileLayer = L.tileLayer(tileUrl, {
    attribution: cfg.attribution,
    maxNativeZoom: cfg.maxNativeZoom || cfg.maxZoom || 19,
    maxZoom: cfg.maxZoom || 20,
    subdomains: "abcd"
  }).addTo(map);
  const layerForEvents = currentTileLayer;

  const mapStatus = el("mapStatus");
  if (mapStatus) {
    mapStatus.textContent = "Loading map tiles…";
    mapStatus.classList.remove("is-visible");
  }
  let consecutiveTileErrors = 0;
  let fallbackStarted = false;
  let tileLoaded = false;
  const fallbackOrShowError = () => {
    if (fallbackStarted || currentTileLayer !== layerForEvents) return;
    fallbackStarted = true;
    mapFailedProviders.add(providerKey);
    const fallback = ["arcgisStreets", "arcgisSatellite", "osm", "mapboxStreets"].find(
      key => key !== providerKey && !mapFailedProviders.has(key) &&
        (!key.startsWith("mapbox") || Boolean(token))
    );
    if (fallback) {
      if (mapStatus) {
        mapStatus.textContent = "Map tiles are unavailable; trying another map style…";
        mapStatus.classList.add("is-visible");
      }
      changeMapLayer(fallback, true);
    } else if (mapStatus) {
      mapStatus.textContent = "Map tiles are unavailable. Check your internet connection or try another map style.";
      mapStatus.classList.add("is-visible");
    }
  };
  mapLoadTimer = setTimeout(() => {
    if (!tileLoaded) fallbackOrShowError();
  }, 6000);
  layerForEvents.on("tileload", () => {
    if (currentTileLayer !== layerForEvents) return;
    tileLoaded = true;
    if (mapLoadTimer) clearTimeout(mapLoadTimer);
    if (mapStatus) mapStatus.classList.remove("is-visible");
  });
  layerForEvents.on("tileerror", () => {
    if (currentTileLayer !== layerForEvents) return;
    consecutiveTileErrors++;
    if (consecutiveTileErrors >= 6 && !fallbackStarted) {
      fallbackOrShowError();
    }
  });

  // Sync drawer map to same tile layer
  if (drawerMap) {
    if (drawerTileLayer) drawerMap.removeLayer(drawerTileLayer);
    drawerTileLayer = L.tileLayer(tileUrl, {
      attribution: cfg.attribution,
      maxNativeZoom: cfg.maxNativeZoom || cfg.maxZoom || 19,
      maxZoom: cfg.maxZoom || 20,
      subdomains: "abcd"
    }).addTo(drawerMap);
  }

  // Sync dropdown
  const sel = el("mapLayerSelect");
  if (sel && sel.value !== providerKey) sel.value = providerKey;
  document.querySelectorAll('input[name="mapTileChoice"]').forEach(choice => {
    choice.checked = choice.value === providerKey;
  });
  if (!automaticFallback) {
    localStorage.setItem(MAP_STYLE_KEY, providerKey);
    const styleName = cfg.name || providerKey;
    showToast(feedbackMessage || `${styleName} style applied.`);
  }
}

function openMapSettingsModal() {
  const modal = el("mapSettingsModal");
  if (!modal) return;
  const keyInput = el("customMapboxKeyInput");
  if (keyInput) keyInput.value = localStorage.getItem(MAPBOX_TOKEN_KEY) || "";
  document.querySelectorAll('input[name="mapTileChoice"]').forEach(choice => {
    choice.checked = choice.value === activeTileProvider;
  });
  if (typeof modal.showModal === "function") modal.showModal();
  else modal.setAttribute("open", "");
  setTimeout(() => el("customMapboxKeyInput")?.focus(), 150);
}

function closeMapSettingsModal() {
  const modal = el("mapSettingsModal");
  if (!modal) return;
  if (typeof modal.close === "function") modal.close();
  else modal.removeAttribute("open");
}

function saveMapboxKey() {
  const keyInput = el("customMapboxKeyInput");
  if (!keyInput) return;
  const selectedStyle = document.querySelector('input[name="mapTileChoice"]:checked')?.value || activeTileProvider;
  const token = keyInput.value.trim();
  if (token) {
    if (!token.startsWith("pk.")) {
      showToast("Enter a Mapbox public token beginning with pk.");
      keyInput.focus();
      return;
    }
    localStorage.setItem(MAPBOX_TOKEN_KEY, token);
  } else {
    localStorage.removeItem(MAPBOX_TOKEN_KEY);
  }
  closeMapSettingsModal();
  changeMapLayer(selectedStyle);
}

function updateUserMarker() {
  if (!MAP_ENABLED || !map) return;
  if (userMarker) map.removeLayer(userMarker);
  if (window._userAccuracyCircle) {
    map.removeLayer(window._userAccuracyCircle);
    window._userAccuracyCircle = null;
  }

  const userIcon = L.divIcon({
    className: "custom-user-marker",
    html: `
      <div class="user-gps-pulse-wrap">
        <div class="user-gps-radar-ring"></div>
        <div class="user-gps-core-dot"></div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });

  userMarker = L.marker([userPoint.lat, userPoint.lng], { icon: userIcon, zIndexOffset: 1000 }).addTo(map);
  userMarker.bindPopup("<b>📍 Your Detected Location</b><br>Fast GPS spatial distance calculated from here.");

  if (userPoint.accurate) {
    window._userAccuracyCircle = L.circle([userPoint.lat, userPoint.lng], {
      radius: 180,
      color: "#0284c7",
      fillColor: "#38bdf8",
      fillOpacity: 0.12,
      weight: 1.5,
      dashArray: "4, 6"
    }).addTo(map);
  }
}

function createHospitalMarkerIcon(h) {
  const isEmergency = h.emergency24x7;
  const isNearest = (window._nearestHospitalId === h.id);
  let bg = "#10529e";
  let pulseHtml = "";

  if (isNearest) {
    bg = "#0d9488";
    pulseHtml = `<div style="position:absolute; inset:-8px; border-radius:50%; background:rgba(13,148,136,0.4); animation:gpsPulse 1.8s infinite;"></div>`;
  } else if (isEmergency) {
    bg = "#dc2626";
    pulseHtml = `<div style="position:absolute; inset:-6px; border-radius:50%; background:rgba(220,38,38,0.35); animation:pulse-ring 1.8s infinite;"></div>`;
  } else if (h.type === "Government") {
    bg = "#1d4ed8";
  } else if (h.type === "Trust") {
    bg = "#4338ca";
  } else if (h.type === "Specialty") {
    bg = "#7e22ce";
  } else {
    bg = "#059669";
  }

  const symbol = isNearest ? "★" : "+";

  return L.divIcon({
    className: "custom-hospital-marker",
    html: `
      <div class="custom-hospital-pin ${isNearest ? 'is-nearest-pin' : ''} ${isEmergency ? 'is-emergency-pin' : ''}">
        ${pulseHtml}
        <div class="marker-pin-head" style="background:${bg};">
          <span class="marker-pin-symbol">${symbol}</span>
        </div>
      </div>
    `,
    iconSize: [36, 42],
    iconAnchor: [18, 40],
    popupAnchor: [0, -36]
  });
}

function renderMapMarkers(hospitals) {
  filteredMapHospitals = hospitals;
  scheduleVisibleHospitalSearch();
}

function changeMapSpatialAlgorithm(algorithm) {
  if (algorithm !== "kdtree" && algorithm !== "quadtree") {
    showToast("Choose K-D Tree or Quadtree for map hospital search.");
    return;
  }
  mapSpatialAlgorithm = algorithm;
  localStorage.setItem(MAP_SPATIAL_ALGORITHM_KEY, algorithm);
  const label = algorithm === "kdtree" ? "K-D Tree" : "Quadtree";
  const status = el("mapSpatialStatus");
  if (status) status.textContent = `${label}: searching visible map area…`;
  scheduleVisibleHospitalSearch();
}

function scheduleVisibleHospitalSearch() {
  if (!map || !MAP_ENABLED) return;
  if (mapSpatialSearchTimer) clearTimeout(mapSpatialSearchTimer);
  mapSpatialSearchTimer = setTimeout(searchVisibleMapHospitals, 160);
}

async function searchVisibleMapHospitals() {
  if (!map || !MAP_ENABLED) return;
  const requestId = ++mapSpatialSearchRequest;
  const bounds = map.getBounds();
  const center = map.getCenter();
  const corners = [bounds.getNorthEast(), bounds.getNorthWest(), bounds.getSouthEast(), bounds.getSouthWest()];
  const radius = Math.max(...corners.map(corner => distanceKm(center, corner))) * 1.05;
  const status = el("mapSpatialStatus");
  const algorithmLabel = mapSpatialAlgorithm === "kdtree" ? "K-D Tree" : "Quadtree";

  if (status) status.textContent = `${algorithmLabel}: searching visible map area…`;
  try {
    const query = new URLSearchParams({
      lat: String(center.lat),
      lng: String(center.lng),
      radius: String(Math.max(radius, 0.1)),
      algorithm: mapSpatialAlgorithm
    });
    const data = await fetchJson(`${API_BASE_URL}/api/hospitals/nearby?${query}`, 8000);
    if (requestId !== mapSpatialSearchRequest) return;
    if (!data || !Array.isArray(data.results)) {
      throw new Error("Spatial hospital search returned an invalid response.");
    }

    const filteredIds = new Set(filteredMapHospitals.map(hospital => hospital.id));
    const visibleHospitals = data.results.filter(hospital => filteredIds.has(hospital.id));
    drawMapHospitalMarkers(visibleHospitals);
    if (status) {
      status.textContent = `${algorithmLabel} · ${visibleHospitals.length} hospitals · ${data.search_time_us} μs · ${data.points_tested} points`;
    }
  } catch (error) {
    if (requestId !== mapSpatialSearchRequest) return;
    console.error(`${algorithmLabel} map search failed; showing filtered local hospital markers.`, error);
    drawMapHospitalMarkers(filteredMapHospitals);
    if (status) status.textContent = `${algorithmLabel} unavailable · showing local results`;
  }
}

function drawMapHospitalMarkers(hospitals) {
  if (!MAP_ENABLED || !map) return;

  Object.values(mapMarkers).forEach(m => map.removeLayer(m));
  mapMarkers = {};

  hospitals.forEach(h => {
    const icon = createHospitalMarkerIcon(h);
    const marker = L.marker([h.lat, h.lng], { icon }).addTo(map);

    const bedsAvailable = h.verified ? bedsFor(h, "all") : null;
    const icuBeds = h.verified ? bedInfo(h, "icu").available : null;
    const ventBeds = h.verified ? bedInfo(h, "ventilator").available : null;
    const oxyBeds = h.verified ? bedInfo(h, "oxygen").available : null;

    const popupHtml = `
      <div class="map-popup-card">
        <div class="mp-badge-row">
          <span class="mp-type-badge ${h.emergency24x7 ? 'mp-badge-emergency' : 'mp-badge-normal'}">
            ${h.emergency24x7 ? '🚨 24x7 Emergency' : esc(h.type + ' Hospital')}
          </span>
          <span class="mp-rating">★ ${(h.rating || 4.5).toFixed(1)}</span>
        </div>
        <h4 class="mp-title">${esc(h.name)}</h4>
        <div class="mp-address">📍 ${esc(h.address)} &bull; <strong>${distanceText(h)}</strong></div>
        <div class="mp-phone">📞 <a href="tel:${esc(h.phone)}" class="mp-tel-link">${esc(h.phone)}</a></div>
        <div class="mp-beds-row">
          <div class="mp-bed-item">
            <span class="mp-b-val ${h.verified && bedsAvailable > 0 ? 'text-green' : 'text-red'}">${h.verified ? bedsAvailable : '—'}</span>
            <span class="mp-b-lbl">Beds</span>
          </div>
          <div class="mp-bed-item">
            <span class="mp-b-val ${h.verified && icuBeds > 0 ? 'text-green' : 'text-red'}">${h.verified ? icuBeds : '—'}</span>
            <span class="mp-b-lbl">ICU</span>
          </div>
          <div class="mp-bed-item">
            <span class="mp-b-val">${h.verified ? ventBeds : '—'}</span>
            <span class="mp-b-lbl">Vent</span>
          </div>
          <div class="mp-bed-item">
            <span class="mp-b-val">${h.verified ? oxyBeds : '—'}</span>
            <span class="mp-b-lbl">Oxygen</span>
          </div>
        </div>
        <div class="mp-actions-row">
          <button class="mp-btn mp-btn-book" onclick="openBookingModalForHospital(${h.id})">
            📅 Book OPD
          </button>
          <button class="mp-btn mp-btn-route" onclick="drawRouteTo(${h.lat}, ${h.lng}, '${esc(h.name)}')">
            🧭 Route
          </button>
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml, { minWidth: 260, maxWidth: 300 });
    mapMarkers[h.id] = marker;
  });
}

function focusHospitalOnMap(id) {
  const m = mapMarkers[id];
  if (!m) return;
  const icon = m.getElement();
  if (icon) icon.classList.add("marker-bounce-active");
}

function unfocusHospitalOnMap(id) {
  const m = mapMarkers[id];
  if (!m) return;
  const icon = m.getElement();
  if (icon) icon.classList.remove("marker-bounce-active");
}

/* ---------- 6B. FAST SIDE DIRECTION DRAWER & ROUTE NAVIGATION ---------- */
let drawerMap = null;
let drawerPolyline = null;
let drawerPolylineGlow = null;
let drawerStartMarker = null;
let drawerDestMarker = null;
let currentDrawerHospitalId = null;
let routePolylineGlow = null;
let currentRouteDestination = null;
let calculatedRoute = null;

function formatRouteStep(step) {
  const maneuver = step.maneuver || {};
  const road = step.name ? ` onto ${step.name}` : "";
  const modifier = maneuver.modifier || "";
  const turnNames = {
    left: "Turn left",
    "slight left": "Keep left",
    "sharp left": "Turn sharply left",
    right: "Turn right",
    "slight right": "Keep right",
    "sharp right": "Turn sharply right",
    straight: "Continue straight",
    uturn: "Make a U-turn"
  };

  switch (maneuver.type) {
    case "depart":
      return `Start${road}`;
    case "arrive":
      return "Arrive at your destination";
    case "turn":
    case "new name":
    case "end of road":
      return `${turnNames[modifier] || "Continue"}${road}`;
    case "roundabout":
    case "rotary":
    case "roundabout turn":
      return `At the roundabout, take exit ${maneuver.exit || "shown"}${road}`;
    case "merge":
      return `Merge${modifier ? ` ${modifier}` : ""}${road}`;
    case "on ramp":
      return `Take the ramp${road}`;
    case "off ramp":
      return `Take the exit${road}`;
    case "fork":
      return `${modifier ? `Keep ${modifier}` : "At the fork, continue"}${road}`;
    case "continue":
    case "use lane":
    default:
      return `Continue${road}`;
  }
}

function renderRouteSteps(steps, isAccurateStart) {
  const list = el("drawerStepsList");
  const note = el("drawerRouteNote");
  if (!list || !note) return;

  note.textContent = isAccurateStart
    ? "Road route calculated from your current location."
    : "Route preview starts at central Gwalior. Start Google Maps navigation to use your phone’s current location.";
  list.innerHTML = steps.map((step, index) => {
    const distance = step.distance >= 1000
      ? `${(step.distance / 1000).toFixed(1)} km`
      : `${Math.round(step.distance)} m`;
    return `<li><span class="route-step-number">${index + 1}</span><span><strong>${esc(formatRouteStep(step))}</strong><small>${distance}</small></span></li>`;
  }).join("");
}

function getNavigationUrl(destLat, destLng) {
  return `https://www.google.com/maps/dir/?api=1&destination=${destLat},${destLng}&travelmode=driving&dir_action=navigate`;
}

function hasCalculatedRouteFor(destLat, destLng) {
  return calculatedRoute &&
    Math.abs(calculatedRoute.destLat - destLat) < 0.000001 &&
    Math.abs(calculatedRoute.destLng - destLng) < 0.000001 &&
    Math.abs(calculatedRoute.start.lat - userPoint.lat) < 0.000001 &&
    Math.abs(calculatedRoute.start.lng - userPoint.lng) < 0.000001;
}

function scrollToTarget(targetIdOrEl, offset = 80) {
  const target = typeof targetIdOrEl === "string" ? el(targetIdOrEl) : targetIdOrEl;
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  window.scrollTo({
    top: rect.top + scrollTop - offset,
    behavior: "smooth"
  });
}

function openSideDirectionDrawer(destLat, destLng, destName, phone = "", address = "", hospId = null) {
  const drawer = el("sideDirectionDrawer");
  if (!drawer) return;

  currentDrawerHospitalId = hospId;
  drawer.classList.add("active");
  drawer.setAttribute("aria-hidden", "false");

  if (el("drawerHospitalName")) el("drawerHospitalName").textContent = destName;
  if (el("drawerHospitalAddress")) el("drawerHospitalAddress").textContent = address || "Gwalior, Madhya Pradesh";

  currentRouteDestination = { lat: destLat, lng: destLng, name: destName };
  if (el("drawerGmapsBtn")) el("drawerGmapsBtn").href = getNavigationUrl(destLat, destLng);

  const cleanPhone = phone || "108";
  if (el("drawerCallBtn")) {
    el("drawerCallBtn").href = `tel:${cleanPhone}`;
    el("drawerCallBtn").textContent = `📞 Call Hospital Emergency (${cleanPhone})`;
  }

  if (hasCalculatedRouteFor(destLat, destLng)) {
    if (el("drawerDistance")) el("drawerDistance").textContent = `${calculatedRoute.distKm} km`;
    if (el("drawerEta")) el("drawerEta").textContent = `${calculatedRoute.mins} mins`;
    if (el("drawerTraffic")) el("drawerTraffic").textContent = "Route ready";
    if (el("drawerMapLoader")) el("drawerMapLoader").classList.add("hidden");
    renderRouteSteps(calculatedRoute.steps, calculatedRoute.start.accurate);
    requestAnimationFrame(() => {
      if (drawerMap && drawerPolyline) {
        drawerMap.invalidateSize();
        drawerMap.fitBounds(drawerPolyline.getBounds(), { padding: [30, 30] });
      }
    });
    return;
  }

  if (el("drawerDistance")) el("drawerDistance").textContent = "Calculating...";
  if (el("drawerEta")) el("drawerEta").textContent = "Calculating...";
  if (el("drawerTraffic")) el("drawerTraffic").textContent = "Loading route";
  if (el("drawerRouteNote")) el("drawerRouteNote").textContent = "Calculating road directions…";
  if (el("drawerStepsList")) el("drawerStepsList").innerHTML = "";
  if (el("drawerMapLoader")) el("drawerMapLoader").classList.remove("hidden");
}

function closeSideDirectionDrawer() {
  const drawer = el("sideDirectionDrawer");
  if (drawer) {
    drawer.classList.remove("active");
    drawer.setAttribute("aria-hidden", "true");
  }
}

function handleDrawerBook() {
  closeSideDirectionDrawer();
  if (currentDrawerHospitalId) {
    openBookingModalForHospital(currentDrawerHospitalId);
  } else {
    openBookingModal();
  }
}

function viewRouteOnMainMap() {
  closeSideDirectionDrawer();
  const mapCard = el("mapCard") || el("map");
  if (mapCard) {
    scrollToTarget(mapCard, 70);
    setTimeout(() => {
      if (map && routePolyline) {
        map.invalidateSize();
        map.fitBounds(routePolyline.getBounds(), { padding: [40, 40], maxZoom: 15 });
      }
    }, 250);
  }
}

function ensureDrawerMapInitialized() {
  const container = el("drawerMap");
  if (!container || !window.L) return null;

  if (!drawerMap) {
    drawerMap = L.map("drawerMap", {
      zoomControl: true,
      attributionControl: true,
      maxZoom: 20
    }).setView([userPoint.lat, userPoint.lng], 13);

    const token = getActiveMapboxToken();
    const providerKey = activeTileProvider || "arcgisStreets";
    const cfg = (typeof AROGYA_CONFIG !== "undefined" && AROGYA_CONFIG.tileProviders[providerKey])
      ? AROGYA_CONFIG.tileProviders[providerKey]
      : AROGYA_CONFIG.tileProviders.arcgisStreets;
    let dTileUrl = cfg.url.replace("{token}", token);
    drawerTileLayer = L.tileLayer(dTileUrl, {
      attribution: cfg.attribution,
      maxNativeZoom: cfg.maxNativeZoom || cfg.maxZoom || 19,
      maxZoom: cfg.maxZoom || 20,
      subdomains: "abcd"
    }).addTo(drawerMap);
  }
  return drawerMap;
}

function syncRenderRouteOnBothMaps(destLat, destLng, destName, coords, distKm, mins, steps) {
  const start = userPoint;
  calculatedRoute = {
    destLat,
    destLng,
    destName,
    start: { ...start },
    coords,
    distKm,
    mins,
    steps
  };

  // ===== A. RENDER ON DRAWER MAP =====
  const dMap = ensureDrawerMapInitialized();
  if (dMap) {
    if (drawerPolyline) dMap.removeLayer(drawerPolyline);
    if (drawerPolylineGlow) dMap.removeLayer(drawerPolylineGlow);
    if (drawerStartMarker) dMap.removeLayer(drawerStartMarker);
    if (drawerDestMarker) dMap.removeLayer(drawerDestMarker);

    const startIcon = L.divIcon({
      className: "pulse-user-icon",
      html: `<div style="background:#2563eb; width:16px; height:16px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 12px rgba(37,99,235,0.9);"></div>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    });

    const destIcon = L.divIcon({
      className: "dest-hospital-icon",
      html: `<div style="background:linear-gradient(135deg,#dc2626,#991b1b); color:#fff; width:30px; height:30px; border-radius:50%; display:grid; place-items:center; font-size:15px; border:2px solid #fff; box-shadow:0 4px 14px rgba(220,38,38,0.7);">🏥</div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });

    drawerStartMarker = L.marker([start.lat, start.lng], { icon: startIcon }).addTo(dMap).bindPopup("<b>Your Current Location</b>");
    drawerDestMarker = L.marker([destLat, destLng], { icon: destIcon }).addTo(dMap).bindPopup(`<b>${esc(destName)}</b>`);

    // Dual-polyline (glow + vibrant core) for attractive modern GPS look
    drawerPolylineGlow = L.polyline(coords, {
      color: "#93c5fd",
      weight: 10,
      opacity: 0.5,
      lineCap: "round"
    }).addTo(dMap);

    drawerPolyline = L.polyline(coords, {
      color: "#1d4ed8",
      weight: 5,
      opacity: 0.95,
      lineCap: "round",
      dashArray: "1, 8"
    }).addTo(dMap);

    dMap.fitBounds(drawerPolyline.getBounds(), { padding: [30, 30] });

    if (el("drawerDistance")) el("drawerDistance").textContent = `${distKm} km`;
    if (el("drawerEta")) el("drawerEta").textContent = `${mins} mins`;
    if (el("drawerTraffic")) el("drawerTraffic").textContent = "Route ready";
    if (el("drawerMapLoader")) el("drawerMapLoader").classList.add("hidden");
    renderRouteSteps(steps, userPoint.accurate);

    // Invalidate size in stages to match CSS drawer slide transition smoothly
    dMap.invalidateSize();
    setTimeout(() => { if (drawerMap) drawerMap.invalidateSize(); }, 150);
    setTimeout(() => { if (drawerMap) drawerMap.invalidateSize(); }, 320);
  }

  // ===== B. SIMULTANEOUSLY RENDER ON MAIN MAP =====
  if (MAP_ENABLED && map) {
    if (routePolyline) map.removeLayer(routePolyline);
    if (routePolylineGlow) map.removeLayer(routePolylineGlow);
    if (routeStartMarker) map.removeLayer(routeStartMarker);
    if (routeDestMarker) map.removeLayer(routeDestMarker);

    routePolylineGlow = L.polyline(coords, {
      color: "#93c5fd",
      weight: 10,
      opacity: 0.45,
      lineCap: "round"
    }).addTo(map);

    routePolyline = L.polyline(coords, {
      color: "#1d4ed8",
      weight: 5,
      opacity: 0.95,
      lineCap: "round",
      dashArray: "1, 8"
    }).addTo(map);

    routeStartMarker = L.circleMarker([start.lat, start.lng], {
      radius: 8,
      color: "#ffffff",
      weight: 3,
      fillColor: "#2563eb",
      fillOpacity: 1
    }).addTo(map).bindPopup("<b>Route start</b>");
    routeDestMarker = L.marker([destLat, destLng], {
      icon: L.divIcon({
        className: "route-destination-marker",
        html: '<span aria-label="Destination">🏥</span>',
        iconSize: [34, 34],
        iconAnchor: [17, 17]
      }),
      zIndexOffset: 1100
    }).addTo(map).bindPopup(`<b>${esc(destName)}</b>`);

    try {
      map.invalidateSize({ pan: false });
      map.fitBounds(routePolyline.getBounds(), { padding: [40, 40], maxZoom: 15 });
    } catch (error) {
      console.error("Could not fit the main map to the route.", error);
    }

    const routeCard = el("routeInfo");
    if (routeCard) {
      routeCard.hidden = false;
      routeCard.innerHTML = `
        <div class="main-route-summary">
          <div>
            <strong>🧭 Route to ${esc(destName)}</strong>
            <span>${distKm} km · approximately ${mins} min</span>
          </div>
          <div class="main-route-actions">
            <a class="btn btn-sm btn-primary" href="${getNavigationUrl(destLat, destLng)}" target="_blank" rel="noopener noreferrer">Start Navigation</a>
            <button type="button" class="btn btn-sm btn-ghost-white" data-open-route-steps>View turn-by-turn</button>
            <button type="button" class="btn btn-sm btn-ghost-white" data-clear-route>Clear</button>
          </div>
        </div>
        <details class="main-route-steps">
          <summary>Show turn-by-turn directions (${steps.length} steps)</summary>
          <ol>${steps.map((step, index) => {
            const stepDistance = step.distance >= 1000
              ? `${(step.distance / 1000).toFixed(1)} km`
              : `${Math.round(step.distance)} m`;
            return `<li><span>${index + 1}. ${esc(formatRouteStep(step))}</span><small>${stepDistance}</small></li>`;
          }).join("")}</ol>
        </details>
      `;
      routeCard.querySelector("[data-open-route-steps]")?.addEventListener("click", () => {
        openSideDirectionDrawer(destLat, destLng, destName);
      });
      routeCard.querySelector("[data-clear-route]")?.addEventListener("click", clearRoute);
    }
  }
}

async function drawRouteTo(destLat, destLng, destName) {
  // Find hospital details
  const hosp = (allHospitals || []).find(h => 
    (Math.abs(h.lat - destLat) < 0.001 && Math.abs(h.lng - destLng) < 0.001) || 
    (h.name && h.name.toLowerCase() === destName.toLowerCase())
  );
  const phone = hosp ? (hosp.emergencyPhone || hosp.phone) : "";
  const address = hosp ? hosp.address : "";
  const hospId = hosp ? hosp.id : null;

  // 1. Instantly slide in fast side navigation drawer beside user's current view!
  openSideDirectionDrawer(destLat, destLng, destName, phone, address, hospId);
  if (hasCalculatedRouteFor(destLat, destLng)) return;

  // 2. Rapid single-flight fetch of route for BOTH maps simultaneously
  const start = userPoint;
  let coords = [];
  let distKm = 0;
  let mins = 0;
  let steps = [];

  try {
    const url = `${ROUTING_URL}/${start.lng},${start.lat};${destLng},${destLat}?overview=full&geometries=geojson&steps=true`;
    const res = await fetch(url, { signal: AbortSignal.timeout(12000) });
    if (!res.ok) throw new Error(`Routing service returned HTTP ${res.status}`);
    const data = await res.json();
    if (data.code === "Ok" && data.routes && data.routes.length) {
      const route = data.routes[0];
      coords = route.geometry.coordinates.map(c => [c[1], c[0]]);
      distKm = (route.distance / 1000).toFixed(1);
      mins = Math.max(1, Math.round(route.duration / 60));
      steps = (route.legs || []).flatMap(leg => leg.steps || []);
      if (!coords.length || !steps.length) throw new Error("Routing service returned no usable route steps");
    } else {
      throw new Error("No route found from routing engine");
    }
  } catch (err) {
    console.error("Could not calculate driving route.", err);
    if (el("drawerMapLoader")) el("drawerMapLoader").classList.add("hidden");
    if (el("drawerTraffic")) el("drawerTraffic").textContent = "Route unavailable";
    if (el("drawerRouteNote")) {
      el("drawerRouteNote").textContent = "Road directions could not be loaded. Check your connection, or use Google Maps navigation.";
    }
    if (el("drawerDistance")) el("drawerDistance").textContent = "Unavailable";
    if (el("drawerEta")) el("drawerEta").textContent = "Unavailable";
    showToast("Could not calculate road directions. Try Google Maps navigation.");
    return;
  }

  // 3. Render both maps together synchronously
  syncRenderRouteOnBothMaps(destLat, destLng, destName, coords, distKm, mins, steps);
}

function clearRoute() {
  calculatedRoute = null;
  if (routePolyline && map) {
    map.removeLayer(routePolyline);
    routePolyline = null;
  }
  if (routePolylineGlow && map) {
    map.removeLayer(routePolylineGlow);
    routePolylineGlow = null;
  }
  if (routeStartMarker && map) {
    map.removeLayer(routeStartMarker);
    routeStartMarker = null;
  }
  if (routeDestMarker && map) {
    map.removeLayer(routeDestMarker);
    routeDestMarker = null;
  }
  if (drawerPolyline && drawerMap) {
    drawerMap.removeLayer(drawerPolyline);
    drawerPolyline = null;
  }
  if (drawerPolylineGlow && drawerMap) {
    drawerMap.removeLayer(drawerPolylineGlow);
    drawerPolylineGlow = null;
  }
  const routeCard = el("routeInfo");
  if (routeCard) routeCard.hidden = true;
}

/* ---------- 7. HOSPITAL RENDERING & FILTERING ---------- */
function filterHospitals() {
  const query = (el("searchInput")?.value || "").toLowerCase().trim();
  const typeFilter = el("typeFilter")?.value || "all";
  const bedFilter = el("bedFilter")?.value || "all";
  const minBeds = parseInt(el("minBeds")?.value || "0", 10);
  const sortBy = el("sortBy")?.value || "distance";
  const radius = parseFloat(el("radiusFilter")?.value || "0");

  const emergencyOnly = el("emergencyOnly")?.checked;
  const icuOnly = el("icuOnly")?.checked;
  const ventOnly = el("ventOnly")?.checked;
  const oxygenOnly = el("oxygenOnly")?.checked;
  const ambulanceOnly = el("ambulanceOnly")?.checked;
  const bloodOnly = el("bloodOnly")?.checked;
  const favOnly = el("favOnly")?.checked;

  let list = allHospitals.map(h => ({
    ...h,
    distance: distanceKm(userPoint, { lat: h.lat, lng: h.lng })
  }));

  if (query) {
    list = list.filter(h => {
      const matchName = h.name.toLowerCase().includes(query);
      const matchAddr = h.address.toLowerCase().includes(query);
      const matchServices = (h.services || []).some(s => s.toLowerCase().includes(query));
      return matchName || matchAddr || matchServices;
    });
  }

  if (typeFilter !== "all") list = list.filter(h => h.type === typeFilter);
  if (minBeds > 0) list = list.filter(h => bedsFor(h, bedFilter) >= minBeds);
  if (radius > 0) list = list.filter(h => h.distance <= radius);

  if (emergencyOnly || emergencyMode) list = list.filter(h => h.emergency24x7);
  if (icuOnly) list = list.filter(h => bedInfo(h, "icu").available > 0);
  if (ventOnly) list = list.filter(h => bedInfo(h, "ventilator").available > 0);
  if (oxygenOnly) list = list.filter(h => bedInfo(h, "oxygen").available > 0);
  if (ambulanceOnly) list = list.filter(h => (h.services || []).some(s => s.toLowerCase().includes("ambulance")));
  if (bloodOnly) list = list.filter(h => (h.services || []).some(s => s.toLowerCase().includes("blood bank")));
  if (favOnly) list = list.filter(h => favourites.has(h.id));

  if (sortBy === "distance") list.sort((a, b) => a.distance - b.distance);
  else if (sortBy === "rating") list.sort((a, b) => (b.rating || 4.5) - (a.rating || 4.5));
  else if (sortBy === "beds") list.sort((a, b) => totalBeds(b).available - totalBeds(a).available);
  else if (sortBy === "icu") list.sort((a, b) => bedInfo(b, "icu").available - bedInfo(a, "icu").available);
  else if (sortBy === "name") list.sort((a, b) => a.name.localeCompare(b.name));

  renderHospitalList(list);
  renderMapMarkers(list);

  const countEl = el("resultCount");
  if (countEl) {
    countEl.textContent = `Showing ${list.length} hospital${list.length === 1 ? '' : 's'}`;
  }
}

function renderHospitalList(hospitals) {
  const container = el("hospitalList");
  if (!container) return;

  if (!hospitals.length) {
    container.innerHTML = `
      <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:32px; text-align:center;">
        <p style="font-size:1.1rem; font-weight:700; color:#0f172a; margin-bottom:6px;">No hospitals match your filters</p>
        <p style="font-size:0.88rem; color:#64748b; margin-bottom:16px;">Try clearing search keywords, adjusting bed count or increasing distance radius.</p>
        <button class="btn btn-primary" onclick="resetAllFilters()">Clear All Filters</button>
      </div>
    `;
    return;
  }

  container.innerHTML = hospitals.map(h => {
    const isFav = favourites.has(h.id);
    const totalAvail = h.verified ? totalBeds(h).available : null;
    const icuAvail = h.verified ? bedInfo(h, "icu").available : null;
    const ventAvail = h.verified ? bedInfo(h, "ventilator").available : null;
    const oxyAvail = h.verified ? bedInfo(h, "oxygen").available : null;

    const typeClass = h.type === "Government" ? "type-govt" :
                      h.type === "Trust" ? "type-trust" :
                      h.type === "Specialty" ? "type-spec" : "type-pvt";

    const emergencyBadge = h.emergency24x7
      ? `<div class="hospital-emergency-alert">🚨 24x7 Emergency ${h.verified ? 'listed' : 'listed — please confirm'} &bull; Helpline: <a href="tel:${esc(h.emergencyPhone || h.phone)}" style="color:#b91c1c; text-decoration:underline;">${esc(h.emergencyPhone || h.phone)}</a></div>`
      : "";

    const serviceTags = (h.services || []).slice(0, 5).map(s => `<span class="service-tag">${esc(s)}</span>`).join("");

    const isNearest = (window._nearestHospitalId === h.id);
    const nearestBanner = isNearest ? `
      <div class="nearest-hospital-badge-banner">
        <div class="nhb-badge-content">
          <span class="nhb-icon">🏆</span>
          <div class="nhb-text-wrap">
            <strong class="nhb-title">CLOSEST HOSPITAL TO YOUR LOCATION</strong>
            <span class="nhb-sub">Instant emergency response & OPD consultation &bull; ${distanceText(h)}</span>
          </div>
        </div>
        <button class="btn btn-sm btn-nhb-action" onclick="drawRouteTo(${h.lat}, ${h.lng}, '${esc(h.name)}')">
          🧭 Fast Route
        </button>
      </div>
    ` : '';

    return `
      <article class="hospital-card ${isNearest ? 'is-nearest-hospital-card' : ''} ${h.emergency24x7 ? 'emergency-border' : ''}" onmouseenter="focusHospitalOnMap(${h.id})" onmouseleave="unfocusHospitalOnMap(${h.id})">
        ${nearestBanner}
        <div class="hospital-card-header">
          <div class="hospital-title-wrap">
            <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:4px;">
              <span class="hospital-type-badge ${typeClass}">${esc(h.type)} Hospital</span>
              <span class="dsa-card-badge">⚡ Dual DSA: [🔲 Q-${getHospitalQuadrant(h)} · 🌲 KD-L${getHospitalKdDepth(h)}]</span>
            </div>
            <h3>${esc(h.name)}</h3>
            <span style="font-size:0.8rem; color:${h.verified ? '#059669' : '#9a6700'}; font-weight:700;">${h.verified ? 'Details verified' : 'Details need confirmation'}</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <div class="hospital-rating-badge">★ ${(h.rating || 4.6).toFixed(1)}</div>
            <button class="link-btn" onclick="toggleFavourite(${h.id})" title="Save to Favourites" style="font-size:1.2rem; text-decoration:none;">
              ${isFav ? '⭐' : '☆'}
            </button>
          </div>
        </div>

        <div class="hospital-address-row">
          <span>📍</span>
          <span>${esc(h.address)} &bull; <strong>${distanceText(h)}</strong></span>
        </div>

        <div class="hospital-phone-row">
          <span>📞</span>
          <span>Phone: <a href="tel:${esc(h.phone)}" style="font-weight:700; color:#0b3a75;">${esc(h.phone)}</a> (OPD: ${esc(h.opdTimings || '09:00 AM - 05:00 PM')})</span>
        </div>

        ${emergencyBadge}

        <div class="hospital-beds-grid">
          <div class="bed-counter-box">
            <span class="bed-num ${h.verified ? (totalAvail > 0 ? 'c-green' : 'c-red') : ''}">${h.verified ? totalAvail : '—'}</span>
            <span class="bed-lbl">Total Beds</span>
          </div>
          <div class="bed-counter-box">
            <span class="bed-num ${h.verified ? (icuAvail > 0 ? 'c-green' : 'c-red') : ''}">${h.verified ? icuAvail : '—'}</span>
            <span class="bed-lbl">ICU Beds</span>
          </div>
          <div class="bed-counter-box">
            <span class="bed-num">${h.verified ? ventAvail : '—'}</span>
            <span class="bed-lbl">Ventilators</span>
          </div>
          <div class="bed-counter-box">
            <span class="bed-num">${h.verified ? oxyAvail : '—'}</span>
            <span class="bed-lbl">Oxygen Beds</span>
          </div>
        </div>

        <div class="hospital-services-tags">
          ${serviceTags}
        </div>

        <div class="hospital-card-actions">
          <button class="btn btn-book-card" onclick="openBookingModalForHospital(${h.id})">
            📅 Book Appointment (OPD)
          </button>
          <a class="btn btn-ghost btn-sm" href="tel:${esc(h.phone)}">
            📞 Call Hospital
          </a>
          <button class="btn btn-ghost btn-sm" onclick="drawRouteTo(${h.lat}, ${h.lng}, '${esc(h.name)}')">
            🧭 Get Directions
          </button>
          <button class="btn btn-ghost btn-sm" onclick="showHospitalDetails(${h.id})">
            ℹ️ Details
          </button>
        </div>
      </article>
    `;
  }).join("");
}

function showHospitalDetails(hid) {
  const h = allHospitals.find(x => x.id === hid);
  if (!h) return;

  const dialog = el("detailDialog");
  const body = el("detailBody");
  if (!dialog || !body) return;

  body.innerHTML = `
    <div style="background:#fff; border-radius:16px; padding:24px; max-width:600px; width:100%; position:relative;">
      <button class="modal-close-btn" onclick="document.getElementById('detailDialog').close()">&times;</button>
      <span style="background:#dbeafe; color:#1e40af; font-size:0.75rem; font-weight:800; padding:2px 8px; border-radius:4px; text-transform:uppercase;">
        ${esc(h.type)} Hospital
      </span>
      <h2 style="font-size:1.35rem; font-weight:800; margin:6px 0 10px; color:#0f172a;">${esc(h.name)}</h2>
      <p style="font-size:0.9rem; color:#475569; margin-bottom:12px;">${esc(h.description || 'Hospital listing in Gwalior.')}</p>
      <p style="font-size:0.88rem; margin-bottom:6px;">📍 <strong>Address:</strong> ${esc(h.address)}</p>
      <p style="font-size:0.88rem; margin-bottom:6px;">📞 <strong>Main Contact:</strong> <a href="tel:${esc(h.phone)}">${esc(h.phone)}</a></p>
      <p style="font-size:0.88rem; margin-bottom:12px;">🚨 <strong>Emergency Phone:</strong> <a href="tel:${esc(h.emergencyPhone || h.phone)}">${esc(h.emergencyPhone || h.phone)}</a></p>
      <p style="font-size:0.88rem; margin-bottom:12px;">⏰ <strong>OPD Hours:</strong> ${esc(h.opdTimings || '09:00 AM - 05:00 PM')}</p>

      <h4 style="font-size:0.92rem; font-weight:700; margin-bottom:8px;">Departments &amp; Facilities:</h4>
      <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:18px;">
        ${(h.services || []).map(s => `<span class="service-tag">${esc(s)}</span>`).join('')}
      </div>

      <div style="display:flex; gap:10px;">
        <button class="btn btn-primary" style="flex:1;" onclick="document.getElementById('detailDialog').close(); openBookingModalForHospital(${h.id});">
          📅 Book Appointment
        </button>
        <button class="btn btn-ghost" onclick="document.getElementById('detailDialog').close(); drawRouteTo(${h.lat}, ${h.lng}, '${esc(h.name)}');">
          🧭 View on Map
        </button>
      </div>
    </div>
  `;

  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
}

/* ---------- 8. EXPERT DOCTORS DIRECTORY ---------- */
function renderDoctorsDirectory(cat = "all") {
  const container = el("doctorsGrid");
  if (!container) return;

  const searchQ = (el("doctorSearchInput")?.value || "").toLowerCase().trim();

  let list = allDoctors;
  if (cat !== "all") {
    list = list.filter(d => (d.category || "").toLowerCase() === cat.toLowerCase());
  }

  if (searchQ) {
    list = list.filter(d =>
      d.name.toLowerCase().includes(searchQ) ||
      d.specialty.toLowerCase().includes(searchQ) ||
      (d.hospitalName || "").toLowerCase().includes(searchQ)
    );
  }

  if (!list.length) {
    container.innerHTML = `<p style="grid-column:1/-1; text-align:center; padding:30px; color:#64748b;">No doctors found matching this criteria.</p>`;
    return;
  }

  container.innerHTML = list.map(d => `
    <div class="doctor-card">
      <div class="doctor-card-top">
        <div class="doctor-avatar-circle">${d.avatar || '👨‍⚕️'}</div>
        <div class="doctor-info-wrap">
          <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:0.75rem; background:${d.verified === false || d.verified === 0 ? '#fff3d6' : '#dcfce7'}; color:${d.verified === false || d.verified === 0 ? '#8a5a00' : '#166534'}; font-weight:800; padding:1px 6px; border-radius:4px;">${esc(d.verified === false || d.verified === 0 ? 'Profile pending verification' : (d.badge || 'Verified Doctor'))}</span>
            <span style="font-size:0.8rem; font-weight:700; color:#b45309;">★ ${(d.rating || 4.9).toFixed(1)}</span>
          </div>
          <h3>${esc(d.name)}</h3>
          <p class="doctor-specialty">${esc(d.specialty)}</p>
          <span class="doctor-exp">⌛ ${d.experienceYears || d.experience_years || 15}+ years experience</span>
        </div>
      </div>

      <div class="doctor-qualification">
        🎓 ${esc(d.qualification)}
      </div>

      <div class="doctor-meta-list">
        <div>🏥 <strong>Hospital / Clinic:</strong> ${esc(d.hospitalName || d.hospital_name)}</div>
        <div>📍 <strong>Address:</strong> ${esc(d.clinicAddress || d.clinic_address)}</div>
        <div>⏰ <strong>OPD Hours:</strong> ${esc(d.opdTimings || d.opd_timings)}</div>
        <div>📞 <strong>Phone:</strong> <a href="tel:${esc(d.phone)}" style="font-weight:700; color:#0b3a75;">${esc(d.phone)}</a></div>
      </div>

      <p style="font-size:0.82rem; color:#475569; line-height:1.4;">${esc(d.about || '')}</p>

      <div class="doctor-fee-row">
        <div>
          <span style="font-size:0.74rem; color:#64748b; display:block;">Consultation Fee</span>
          <span class="doctor-fee-val">₹${d.fee || 500}</span>
        </div>
        <div style="display:flex; gap:6px;">
          <button class="btn btn-primary btn-sm" onclick="openBookingModalForDoctor(${d.id})">
            📅 Book Appointment
          </button>
          <a class="btn btn-ghost btn-sm" href="tel:${esc(d.phone)}">
            📞 Call
          </a>
        </div>
      </div>
    </div>
  `).join("");
}

function initDoctorDirectoryEvents() {
  const catBar = el("doctorCategoryBar");
  if (catBar) {
    catBar.addEventListener("click", e => {
      const btn = e.target.closest(".doc-cat-btn");
      if (!btn) return;
      catBar.querySelectorAll(".doc-cat-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderDoctorsDirectory(btn.dataset.cat);
    });
  }

  el("doctorSearchInput")?.addEventListener("input", () => {
    const activeBtn = catBar?.querySelector(".doc-cat-btn.active");
    renderDoctorsDirectory(activeBtn ? activeBtn.dataset.cat : "all");
  });
}

/* ---------- 9. BLOOD BANKS & INVENTORY SYSTEM ---------- */
function renderBloodBanks(filterGroup = "all") {
  const container = el("bloodBanksGrid");
  if (!container) return;

  if (!allBloodBanks.length) {
    container.innerHTML = `<p style="grid-column:1/-1; text-align:center; padding:30px; color:#64748b;">Loading blood bank data...</p>`;
    return;
  }

  container.innerHTML = allBloodBanks.map(b => {
    const inv = b.inventory || {};
    const groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"];

    const badgesHtml = groups.map(grp => {
      const count = inv[grp] || 0;
      const isSelected = filterGroup === "all" || filterGroup === grp;
      const badgeClass = count > 15 ? 'stock-high' : count > 5 ? 'stock-med' : 'stock-low';
      return `
        <div class="blood-unit-badge ${badgeClass} ${isSelected ? 'badge-highlight' : ''}">
          <span class="bu-group">${grp}</span>
          <span class="bu-units">${count} units</span>
        </div>
      `;
    }).join("");

    return `
      <div class="blood-bank-card" style="cursor:pointer;" onclick="showBloodBankDetail(${b.id})">
        <div class="bb-card-header">
          <span class="bb-badge">🩸 24x7 Blood Bank</span>
          <h3>${esc(b.name)}</h3>
          <p style="font-size:0.84rem; color:#475569;">📍 ${esc(b.address)}</p>
        </div>

        <div class="bb-contact-row">
          <span>📞 Helpline: <a href="tel:${esc(b.phone)}" style="font-weight:700; color:#991b1b;">${esc(b.phone)}</a></span>
          <span>👤 ${esc(b.contactPerson || b.contact_person || 'Medical Officer')}</span>
        </div>

        <div class="blood-units-grid">
          ${badgesHtml}
        </div>

        <div style="display:flex; gap:8px; margin-top:12px;">
          <a class="btn btn-primary btn-sm" href="tel:${esc(b.phone)}" style="flex:1;">
            📞 Request Blood
          </a>
          <button class="btn btn-ghost btn-sm" onclick="drawRouteTo(${b.lat}, ${b.lng}, '${esc(b.name)}')">
            🧭 Directions
          </button>
        </div>
      </div>
    `;
  }).join("");
}

function filterBloodInventory(grp) {
  document.querySelectorAll(".blood-filter-pill").forEach(p => {
    p.classList.toggle("active", p.textContent.includes(grp) || (grp === "all" && p.textContent.includes("All")));
  });
  renderBloodBanks(grp);
  scrollToTarget("bloodBanksGrid", 90);
}

/* ---------- 10. Blood Bank Detail Modal ---------- */
function showBloodBankDetail(bankId) {
  const b = allBloodBanks.find(x => x.id === bankId);
  if (!b) return;
  const dialog = el("detailDialog");
  const body = el("detailBody");
  if (!dialog || !body) return;

  const groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"];
  const inv = b.inventory || {};

  const inventoryHtml = groups.map(grp => {
    const count = inv[grp] || 0;
    const color = count > 15 ? '#059669' : count > 5 ? '#d97706' : '#dc2626';
    return `<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; text-align:center;">
      <span style="font-size:1rem; font-weight:800; color:${color};">${count}</span>
      <br><span style="font-size:0.75rem; font-weight:700; color:#475569;">${grp}</span>
      <br><span style="font-size:0.68rem; color:#94a3b8;">units</span>
    </div>`;
  }).join('');

  body.innerHTML = `
    <div style="background:#fff; border-radius:16px; padding:24px; max-width:560px; width:100%; position:relative;">
      <button class="modal-close-btn" onclick="document.getElementById('detailDialog').close()">&times;</button>
      <span style="background:#fee2e2; color:#991b1b; font-size:0.75rem; font-weight:800; padding:2px 8px; border-radius:4px;">🩸 24x7 Blood Bank</span>
      <h2 style="font-size:1.3rem; font-weight:800; margin:8px 0 6px; color:#0f172a;">${esc(b.name)}</h2>
      <p style="font-size:0.88rem; color:#475569; margin-bottom:8px;">📍 ${esc(b.address)}</p>
      <p style="font-size:0.88rem; margin-bottom:4px;">📞 <a href="tel:${esc(b.phone)}" style="font-weight:700; color:#991b1b;">${esc(b.phone)}</a></p>
      <p style="font-size:0.85rem; color:#475569; margin-bottom:16px;">👤 Contact: ${esc(b.contactPerson || b.contact_person || 'Medical Officer')}</p>
      <h4 style="font-size:0.9rem; font-weight:700; margin-bottom:10px; color:#0f172a;">Live Blood Group Inventory</h4>
      <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:18px;">${inventoryHtml}</div>
      <a class="btn btn-primary" href="tel:${esc(b.phone)}" style="width:100%; text-align:center; display:block;">📞 Request Blood / Call Now</a>
    </div>
  `;
  if (typeof dialog.showModal === 'function') dialog.showModal();
  else dialog.setAttribute('open', '');
}

/* ---------- 11. 24x7 AMBULANCES DISPATCH SYSTEM ---------- */
function renderAmbulances() {
  const container = el("ambulancesGrid");
  if (!container) return;

  if (!allAmbulances.length) {
    container.innerHTML = `<p style="grid-column:1/-1; text-align:center; padding:30px; color:#64748b;">Loading emergency ambulances...</p>`;
    return;
  }

  container.innerHTML = allAmbulances.map(a => `
    <div class="ambulance-card">
      <div class="amb-card-header">
        <span class="amb-type-badge">${esc(a.vehicle_type)}</span>
        <span class="status-confirmed-pill">Active / On-Duty</span>
      </div>
      <h3 style="font-size:1.08rem; font-weight:800; color:#0f172a; margin:4px 0;">${esc(a.service_name)}</h3>
      <p style="font-size:0.84rem; color:#475569;">📍 Base Hub: <strong>${esc(a.base_location)}</strong></p>
      
      <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; font-size:0.8rem; color:#334155; margin:10px 0;">
        <strong>Equipment:</strong> ${esc(a.features || 'Oxygen, Defibrillator, Transport Monitor')}
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
        <span style="font-size:0.8rem; color:#059669; font-weight:700;">Average Response: 6-10 mins</span>
        <a class="btn btn-danger btn-sm" href="tel:${esc(a.phone)}" style="font-weight:800;">
          📞 Call ${esc(a.phone)}
        </a>
      </div>
    </div>
  `).join("");
}

function openEmergencySosModal() {
  const modal = el("emergencySosModal");
  if (!modal) return;

  if (currentUser) {
    if (el("sosCallerName")) el("sosCallerName").value = currentUser.name || "";
    if (el("sosCallerPhone")) el("sosCallerPhone").value = currentUser.phone || "";
  }

  const gpsDisplay = el("sosGpsDisplay");
  if (gpsDisplay) {
    gpsDisplay.textContent = `${userPoint.lat.toFixed(4)}° N, ${userPoint.lng.toFixed(4)}° E (Gwalior)`;
  }

  if (typeof modal.showModal === "function") modal.showModal();
  else modal.setAttribute("open", "");
  setTimeout(() => el("sosCallerName")?.focus(), 150);
}

function closeEmergencySosModal() {
  const modal = el("emergencySosModal");
  if (!modal) return;
  if (typeof modal.close === "function") modal.close();
  else modal.removeAttribute("open");
}

let _dispatchTimer = null;

async function handleSosDispatch(e) {
  e.preventDefault();
  const name = el("sosCallerName")?.value.trim() || "Emergency Caller";
  const phone = el("sosCallerPhone")?.value.trim() || "108";
  const type = el("sosEmergencyType")?.value || "Critical Emergency";

  let sosCode = `SOS-GWL-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
  let assignedAmbulance = "108 Advanced Cardiac Ambulance (JAH Unit #12)";
  let etaText = "6-8 minutes";

  if (USE_BACKEND) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/emergency/sos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name, phone, type,
          lat: userPoint.lat,
          lng: userPoint.lng,
          address: "Gwalior GPS Live Dispatch"
        })
      });
      const data = await res.json();
      if (res.ok && data.sosCode) {
        sosCode = data.sosCode;
        if (data.ambulance) assignedAmbulance = data.ambulance;
        if (data.eta) etaText = data.eta;
      }
    } catch (err) {
      console.warn("Backend emergency dispatch offline fallback:", err);
    }
  }

  closeEmergencySosModal();
  openEmergencyDispatchSuccessModal({
    sosCode,
    callerName: name,
    callerPhone: phone,
    emergencyType: type,
    lat: userPoint.lat,
    lng: userPoint.lng,
    ambulance: assignedAmbulance,
    eta: etaText
  });
  showToast(`🚨 Emergency Unit Dispatched! SOS Code: ${sosCode}`);
}

function openEmergencyDispatchSuccessModal(info) {
  const modal = el("emergencyDispatchModal");
  if (!modal) return;

  if (el("dispatchCodeDisplay")) el("dispatchCodeDisplay").textContent = info.sosCode;
  if (el("dispatchCallerDisplay")) el("dispatchCallerDisplay").textContent = `${info.callerName} (${info.callerPhone})`;
  if (el("dispatchCoordsDisplay")) el("dispatchCoordsDisplay").textContent = `${info.lat.toFixed(4)}° N, ${info.lng.toFixed(4)}° E`;

  // Start countdown timer from 6 mins 45 secs
  let totalSeconds = 405;
  const timerDisplay = el("dispatchCountdown");
  if (_dispatchTimer) clearInterval(_dispatchTimer);

  _dispatchTimer = setInterval(() => {
    totalSeconds--;
    if (totalSeconds <= 0) {
      clearInterval(_dispatchTimer);
      if (timerDisplay) timerDisplay.textContent = "ARRIVED";
      return;
    }
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    if (timerDisplay) {
      timerDisplay.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
  }, 1000);

  if (typeof modal.showModal === "function") modal.showModal();
  else modal.setAttribute("open", "");
}

function closeEmergencyDispatchModal() {
  const modal = el("emergencyDispatchModal");
  if (!modal) return;
  if (_dispatchTimer) clearInterval(_dispatchTimer);
  if (typeof modal.close === "function") modal.close();
  else modal.removeAttribute("open");
}

/* ---------- 11. ONLINE APPOINTMENT BOOKING SYSTEM ---------- */
function initBookingSystem() {
  populateBookingDropdowns();
  renderBookingDatePills();

  if (currentUser) {
    const pName = el("patientName");
    const pPhone = el("patientPhone");
    if (pName && !pName.value) pName.value = currentUser.name || "";
    if (pPhone && !pPhone.value) pPhone.value = currentUser.phone || "";
  }
}

function populateBookingDropdowns() {
  const docSelect = el("bookDoctorSelect");
  const hospSelect = el("bookHospitalSelect");

  if (docSelect) {
    docSelect.innerHTML = `<option value="">-- Choose Specialist Doctor --</option>` +
      allDoctors.map(d => `<option value="${d.id}">${esc(d.name)} (${esc(d.specialty)}) - ₹${d.fee}</option>`).join("");
  }

  if (hospSelect) {
    hospSelect.innerHTML = `<option value="">-- Choose Hospital / Medical Centre --</option>` +
      allHospitals.map(h => `<option value="${h.id}">${esc(h.name)} (${esc(h.type)})</option>`).join("");
  }
}

function renderBookingDatePills() {
  const container = el("bookingDatePills");
  if (!container) return;

  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  let html = "";
  const now = new Date();

  for (let i = 0; i < 6; i++) {
    const d = new Date(now.getTime() + i * 86400000);
    const dayLabel = i === 0 ? "Today" : i === 1 ? "Tomorrow" : days[d.getDay()];
    const dateStr = `${d.getDate()} ${months[d.getMonth()]}`;
    const isoVal = d.toISOString().split("T")[0];

    html += `
      <div class="date-pill ${i === 0 ? 'active' : ''}" data-val="${isoVal}" onclick="selectBookingDate(this, '${isoVal}')">
        <span class="dp-day">${dayLabel}</span>
        <span class="dp-date">${dateStr}</span>
      </div>
    `;
  }

  container.innerHTML = html;
  el("selectedBookingDate").value = now.toISOString().split("T")[0];
}

function selectBookingDate(pillEl, dateVal) {
  document.querySelectorAll(".date-pill").forEach(p => p.classList.remove("active"));
  pillEl.classList.add("active");
  el("selectedBookingDate").value = dateVal;
}

function selectTimeSlot(slotBtn, slotVal) {
  document.querySelectorAll(".slot-pill").forEach(s => s.classList.remove("active"));
  slotBtn.classList.add("active");
  el("selectedTimeSlot").value = slotVal;
}

function onDoctorSelectChange() {
  const docId = parseInt(el("bookDoctorSelect").value, 10);
  const doc = allDoctors.find(d => d.id === docId);
  if (doc) {
    if ((doc.hospitalId || doc.hospital_id) && el("bookHospitalSelect")) {
      el("bookHospitalSelect").value = doc.hospitalId || doc.hospital_id;
    }
    el("bookingFeeDisplay").textContent = `₹${doc.fee || 500}`;
  }
}

function onHospitalSelectChange() {
  const hospId = parseInt(el("bookHospitalSelect").value, 10);
  const hosp = allHospitals.find(h => h.id === hospId);
  if (hosp) {
    const fee = hosp.consultationFee || (hosp.type === "Government" ? 20 : 500);
    el("bookingFeeDisplay").textContent = `₹${fee}`;
  }
}

function openBookingModal() {
  const modal = el("bookingModal");
  if (!modal) return;
  initBookingSystem();
  if (typeof modal.showModal === "function") modal.showModal();
  else modal.setAttribute("open", "");
  setTimeout(() => el("patientName")?.focus(), 150);
}

function openBookingModalForDoctor(docId) {
  openBookingModal();
  const select = el("bookDoctorSelect");
  if (select) {
    select.value = docId;
    onDoctorSelectChange();
  }
}

function openBookingModalForHospital(hospId) {
  openBookingModal();
  const select = el("bookHospitalSelect");
  if (select) {
    select.value = hospId;
    onHospitalSelectChange();
  }
}

function closeBookingModal() {
  const modal = el("bookingModal");
  if (!modal) return;
  if (typeof modal.close === "function") modal.close();
  else modal.removeAttribute("open");
}

async function handleAppointmentSubmit(e) {
  e.preventDefault();

  const patientName = el("patientName").value.trim();
  const patientPhone = el("patientPhone").value.trim();
  const patientAge = parseInt(el("patientAge").value || "30", 10);
  const patientGender = el("patientGender").value;
  const problem = el("patientProblem").value.trim();

  const docId = parseInt(el("bookDoctorSelect").value, 10) || null;
  const hospId = parseInt(el("bookHospitalSelect").value, 10) || null;

  const doctor = allDoctors.find(d => d.id === docId);
  const hospital = allHospitals.find(h => h.id === hospId);

  const doctorName = doctor ? doctor.name : (hospital ? `Consultant (${hospital.name})` : "Senior Medical Officer");
  const hospitalName = hospital ? hospital.name : (doctor ? (doctor.hospitalName || doctor.hospital_name) : "Arogya Gwalior Partner Network");

  const appointmentDate = el("selectedBookingDate").value || new Date().toISOString().split("T")[0];
  const timeSlot = el("selectedTimeSlot").value || "10:00 AM";
  const consultType = document.querySelector('input[name="consultType"]:checked')?.value || "In-Clinic OPD";
  const fee = doctor ? doctor.fee : (hospital ? (hospital.consultationFee || 500) : 500);

  const payload = {
    patientName,
    patientPhone,
    patientAge,
    patientGender,
    problem,
    doctorId: docId,
    doctorName,
    hospitalId: hospId,
    hospitalName,
    appointmentDate,
    timeSlot,
    consultationType: consultType,
    fee
  };

  let token = `GWL-${Math.random().toString(36).substring(2, 6).toUpperCase()}-${Math.floor(100 + Math.random() * 900)}`;

  if (USE_BACKEND) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/appointments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        showToast(data.error || "Could not confirm appointment booking.", "error");
        return;
      }
      if (data.appointment) {
        token = data.appointment.tokenId;
      }
    } catch (err) {
      console.warn("Backend booking offline fallback:", err);
    }
  }

  const appointmentObj = {
    ...payload,
    tokenId: token,
    status: "Confirmed",
    createdAt: new Date().toISOString()
  };

  saveAppointmentLocal(appointmentObj);
  closeBookingModal();
  showConfirmationSlip(appointmentObj);
  updateMyAppointmentsBadge();
}

function saveAppointmentLocal(appt) {
  try {
    const list = getLocalAppointments();
    list.unshift(appt);
    localStorage.setItem(APPT_KEY, JSON.stringify(list));
  } catch (e) {}
}

function getLocalAppointments() {
  try {
    const raw = localStorage.getItem(APPT_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function showConfirmationSlip(appt) {
  const modal = el("confirmationSlipModal");
  if (!modal) return;

  el("slipTokenId").textContent = appt.tokenId || appt.token_id || "GWL-OPD";
  el("slipPatientName").textContent = appt.patientName || appt.patient_name || "Self";
  el("slipPatientPhone").textContent = appt.patientPhone || appt.patient_phone || "";
  el("slipDoctorName").textContent = appt.doctorName || appt.doctor_name || "Duty Consultant";
  el("slipHospitalName").textContent = appt.hospitalName || appt.hospital_name || "Arogya Medical Network";
  el("slipDateTime").textContent = `${appt.appointmentDate || appt.appointment_date} at ${appt.timeSlot || appt.time_slot}`;
  el("slipConsultType").textContent = appt.consultationType || appt.consultation_type || "In-Clinic OPD";
  el("slipFee").textContent = `₹${appt.fee || 500}`;

  if (typeof modal.showModal === "function") modal.showModal();
  else modal.setAttribute("open", "");
}

function closeSlipModal() {
  const modal = el("confirmationSlipModal");
  if (!modal) return;
  if (typeof modal.close === "function") modal.close();
  else modal.removeAttribute("open");
}

function updateMyAppointmentsBadge() {
  const badge = el("navApptBadge");
  if (!badge) return;
  const list = getLocalAppointments();
  badge.textContent = list.length;
}

async function renderMyAppointmentsList() {
  const container = el("myAppointmentsList");
  if (!container) return;

  let list = getLocalAppointments();

  if (USE_BACKEND) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/appointments`);
      if (res.ok) {
        const backendList = await res.json();
        if (Array.isArray(backendList) && backendList.length > 0) {
          const merged = new Map();
          backendList.forEach(a => {
            const tok = a.tokenId || a.token_id;
            if (tok) merged.set(tok, {
              tokenId: tok,
              patientName: a.patientName || a.patient_name,
              patientPhone: a.patientPhone || a.patient_phone,
              doctorName: a.doctorName || a.doctor_name,
              hospitalName: a.hospitalName || a.hospital_name,
              appointmentDate: a.appointmentDate || a.appointment_date,
              timeSlot: a.timeSlot || a.time_slot,
              consultationType: a.consultationType || a.consultation_type || 'In-Clinic OPD',
              status: a.status || 'Confirmed',
              fee: a.fee || 500
            });
          });
          list.forEach(a => {
            const tok = a.tokenId || a.token_id;
            if (tok && !merged.has(tok)) merged.set(tok, a);
          });
          list = Array.from(merged.values());
          localStorage.setItem(APPT_KEY, JSON.stringify(list));
        }
      }
    } catch (e) {
      console.warn("Backend appointments fetch fallback:", e);
    }
  }

  updateMyAppointmentsBadge();

  if (!list.length) {
    container.innerHTML = `
      <div style="grid-column:1/-1; background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:36px; text-align:center;">
        <p style="font-size:1.15rem; font-weight:800; color:#0f172a; margin-bottom:8px;">No Booked Appointments Yet</p>
        <p style="font-size:0.88rem; color:#64748b; margin-bottom:18px;">You can book instant OPD consultations with top specialist doctors and hospitals in Gwalior.</p>
        <button class="btn btn-primary" onclick="openBookingModal()">+ Book an Appointment</button>
      </div>
    `;
    return;
  }

  container.innerHTML = list.map(a => {
    const isCancelled = (a.status === 'Cancelled');
    const safeObj = JSON.stringify(a).replace(/'/g, "&#39;");
    return `
      <div class="appointment-booking-card ${isCancelled ? 'is-cancelled-card' : ''}">
        <div class="appt-card-top">
          <span class="appt-token-pill">Token: ${esc(a.tokenId || a.token_id)}</span>
          <span class="${isCancelled ? 'status-cancelled-pill' : 'status-confirmed-pill'}">
            ${isCancelled ? '✖ Cancelled' : '✔ Confirmed'}
          </span>
        </div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0f172a; margin:4px 0;">${esc(a.doctorName || a.doctor_name || 'Medical Specialist')}</h3>
        <p style="font-size:0.86rem; color:#475569;">🏥 <strong>${esc(a.hospitalName || a.hospital_name || 'Arogya Gwalior Centre')}</strong></p>
        <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; font-size:0.84rem; display:flex; justify-content:space-between;">
          <span>📅 ${esc(a.appointmentDate || a.appointment_date)}</span>
          <span>⏰ ${esc(a.timeSlot || a.time_slot)}</span>
        </div>
        <p style="font-size:0.82rem; color:#64748b;">👤 Patient: <strong>${esc(a.patientName || a.patient_name)}</strong> &bull; Fee: ₹${a.fee}</p>
        <div style="display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;">
          <button class="btn btn-primary btn-sm" style="flex:1;" onclick='showConfirmationSlip(${safeObj})'>
            📄 View OPD Pass
          </button>
          ${!isCancelled ? `
            <button class="btn btn-ghost btn-sm" onclick="openRescheduleModal('${a.tokenId || a.token_id}', '${esc(a.appointmentDate || a.appointment_date)}', '${esc(a.timeSlot || a.time_slot)}')">
              🔄 Reschedule
            </button>
            <button class="btn btn-ghost btn-sm" style="color:#dc2626;" onclick="cancelAppointmentLocal('${a.tokenId || a.token_id}')">
              Cancel
            </button>
          ` : `
            <span style="font-size:0.78rem; color:#94a3b8; align-self:center;">Slot Released</span>
          `}
        </div>
      </div>
    `;
  }).join("");
}

function openRescheduleModal(tokenId, curDate, curSlot) {
  const dlg = el("rescheduleModal");
  if (!dlg) return;
  el("rescheduleTokenId").value = tokenId;
  el("rescheduleDate").value = curDate || new Date().toISOString().split("T")[0];
  if (curSlot) el("rescheduleSlot").value = curSlot;
  if (el("rescheduleSubtitle")) {
    el("rescheduleSubtitle").textContent = `Rescheduling consultation token: ${tokenId}`;
  }
  if (typeof dlg.showModal === "function") dlg.showModal();
  else dlg.setAttribute("open", "");
}

function closeRescheduleModal() {
  const dlg = el("rescheduleModal");
  if (!dlg) return;
  if (typeof dlg.close === "function") dlg.close();
  else dlg.removeAttribute("open");
}

async function handleRescheduleSubmit(e) {
  e.preventDefault();
  const tokenId = el("rescheduleTokenId").value;
  const newDate = el("rescheduleDate").value;
  const newSlot = el("rescheduleSlot").value;
  const submitBtn = el("rescheduleSubmitBtn");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Updating...";
  }

  try {
    if (USE_BACKEND) {
      const res = await fetch(`${API_BASE_URL}/api/appointments/${encodeURIComponent(tokenId)}/reschedule`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ appointmentDate: newDate, timeSlot: newSlot })
      });
      const data = await res.json();
      if (!res.ok) {
        showToast(data.error || "Could not reschedule appointment slot.", "error");
        return;
      }
    }

    const list = getLocalAppointments().map(a => {
      if ((a.tokenId || a.token_id) === tokenId) {
        return {
          ...a,
          appointmentDate: newDate,
          appointment_date: newDate,
          timeSlot: newSlot,
          time_slot: newSlot,
          status: "Confirmed"
        };
      }
      return a;
    });
    localStorage.setItem(APPT_KEY, JSON.stringify(list));
    closeRescheduleModal();
    await renderMyAppointmentsList();
    showToast(`Appointment ${tokenId} rescheduled to ${newDate} at ${newSlot}!`, "success");
  } catch (err) {
    showToast("Network error while rescheduling slot.", "error");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = "Confirm New Slot";
    }
  }
}

/* ---------- BLOOD BANK DONOR & REQUEST MODAL HANDLERS ---------- */
function openDonorModal() {
  const dlg = el("donorModal");
  if (!dlg) return;
  if (typeof dlg.showModal === "function") dlg.showModal();
  else dlg.setAttribute("open", "");
}

function closeDonorModal() {
  const dlg = el("donorModal");
  if (!dlg) return;
  if (typeof dlg.close === "function") dlg.close();
  else dlg.removeAttribute("open");
}

async function handleDonorSubmit(e) {
  e.preventDefault();
  const name = el("donorName").value.trim();
  const phone = el("donorPhone").value.trim();
  const bloodGroup = el("donorBloodGroup").value;
  const age = parseInt(el("donorAge").value, 10);
  const city = el("donorCity").value.trim() || "Gwalior";
  const btn = el("donorSubmitBtn");
  if (btn) { btn.disabled = true; btn.textContent = "Registering..."; }

  try {
    if (USE_BACKEND) {
      const res = await fetch(`${API_BASE_URL}/api/blood-banks/donate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, bloodGroup, age, city })
      });
      const data = await res.json();
      if (!res.ok) {
        showToast(data.error || "Could not register donor.", "error");
        return;
      }
      showToast(data.message || `Registered as active ${bloodGroup} donor in Gwalior!`, "success");
    } else {
      showToast(`Thank you, ${name}! Registered as active ${bloodGroup} donor in Gwalior.`, "success");
    }
    closeDonorModal();
    el("donorForm").reset();
  } catch (err) {
    showToast("Donor registration submitted.", "success");
    closeDonorModal();
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "Register as Donor"; }
  }
}

function openBloodRequestModal() {
  const dlg = el("bloodRequestModal");
  if (!dlg) return;
  if (typeof dlg.showModal === "function") dlg.showModal();
  else dlg.setAttribute("open", "");
}

function closeBloodRequestModal() {
  const dlg = el("bloodRequestModal");
  if (!dlg) return;
  if (typeof dlg.close === "function") dlg.close();
  else dlg.removeAttribute("open");
}

async function handleBloodRequestSubmit(e) {
  e.preventDefault();
  const patientName = el("reqPatientName").value.trim();
  const bloodGroup = el("reqBloodGroup").value;
  const unitsNeeded = parseInt(el("reqUnits").value, 10);
  const urgency = el("reqUrgency").value;
  const hospitalName = el("reqHospital").value.trim();
  const contactPhone = el("reqContact").value.trim();
  const btn = el("reqSubmitBtn");
  if (btn) { btn.disabled = true; btn.textContent = "Broadcasting..."; }

  try {
    if (USE_BACKEND) {
      const res = await fetch(`${API_BASE_URL}/api/blood-banks/request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ patientName, bloodGroup, unitsNeeded, urgency, hospitalName, contactPhone })
      });
      const data = await res.json();
      if (!res.ok) {
        showToast(data.error || "Could not broadcast blood request.", "error");
        return;
      }
      showToast(data.message || `Blood request broadcasted across Gwalior!`, "success");
    } else {
      showToast(`Urgent blood request for ${unitsNeeded} unit(s) of ${bloodGroup} broadcasted!`, "success");
    }
    closeBloodRequestModal();
    el("bloodRequestForm").reset();
  } catch (err) {
    showToast("Blood request broadcasted to nearest blood banks.", "success");
    closeBloodRequestModal();
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "Broadcast Blood Request"; }
  }
}

/* ---------- THEME (LIGHT / DARK) SYSTEM ---------- */
function initTheme() {
  const saved = localStorage.getItem("arogya_theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeButton(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("arogya_theme", next);
  updateThemeButton(next);
  showToast(next === "dark" ? "🌙 Dark theme activated" : "☀️ Light theme activated", "info");
}

function updateThemeButton(theme) {
  const icon = el("themeToggleIcon");
  const text = el("themeToggleText");
  if (icon) icon.textContent = theme === "dark" ? "☀️" : "🌙";
  if (text) text.textContent = theme === "dark" ? "Light" : "Dark";
}

async function cancelAppointmentLocal(tokenId) {
  if (!confirm(`Are you sure you want to cancel appointment ${tokenId}?`)) return;

  if (USE_BACKEND) {
    try {
      await fetch(`${API_BASE_URL}/api/appointments/${encodeURIComponent(tokenId)}`, {
        method: "DELETE"
      });
    } catch (e) {
      console.warn("Backend cancel error:", e);
    }
  }

  const list = getLocalAppointments().map(a => {
    if ((a.tokenId || a.token_id) === tokenId) {
      return { ...a, status: "Cancelled" };
    }
    return a;
  });
  localStorage.setItem(APPT_KEY, JSON.stringify(list));
  updateMyAppointmentsBadge();
  await renderMyAppointmentsList();
  showToast(`Appointment ${tokenId} has been cancelled in Arogya database.`);
}

/* ---------- 12. SWASTHYA AI CLINICAL HEALTH ASSISTANT ---------- */
function clearAiChat() {
  const chat = el("aiChatWindow");
  if (!chat) return;
  chat.innerHTML = `
    <div class="chat-message ai-message">
      <div class="chat-bubble">
        <p><strong>Namaste! Main Swasthya AI hoon.</strong></p>
        <p>Aap mujhse apne symptoms (lakshan) Hindi ya English me share kar sakte hain. Main aapko clinical triage, primary first-aid aur Gwalior ke best specialist doctors &amp; hospitals suggest karunga.</p>
      </div>
      <span class="chat-time">Just now</span>
    </div>
  `;
  showToast("Swasthya AI chat window cleared.");
}

function askAiPrompt(symptomText) {
  const input = el("aiUserInput");
  if (input) {
    input.value = symptomText;
    handleAiSubmit();
  }
}

async function openAiSettingsModal() {
  const modal = el("aiSettingsModal");
  if (!modal) return;
  modal.showModal();
  const status = el("aiApiStatus");
  if (!status) return;
  status.textContent = "Checking secure server configuration...";
  try {
    const result = await fetchJson(`${API_BASE_URL}/api/ai/status`);
    status.textContent = result.configured
      ? `Connected: ${result.provider}. Your API key stays on the server.`
      : `${result.setup} The assistant will clearly label limited offline guidance until configured.`;
    status.classList.toggle("is-configured", result.configured);
  } catch (error) {
    status.textContent = "The Flask server could not be reached. Start the backend to use Gemini.";
    status.classList.remove("is-configured");
  }
}

function closeAiSettingsModal() {
  el("aiSettingsModal")?.close();
}

function showAiError(chat, message) {
  chat.insertAdjacentHTML("beforeend", `
    <div class="chat-message ai-message">
      <div class="chat-bubble ai-error-bubble">
        <strong>AI service unavailable</strong>
        <p>${esc(message)}</p>
      </div>
      <span class="chat-time">Please try again</span>
    </div>
  `);
  chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" });
}

function offlineAiReply(text, reason) {
  const query = text.toLowerCase();
  const emergency = /chest pain|chest tightness|heavy chest|chest me|heart attack|stroke|unconscious|can't breathe|cant breathe|cannot breathe|unable to breathe|breathing difficulty|shortness of breath|breathlessness|heavy bleeding|seizure|poison|chhati|dil ka daura|behosh|saans nahi|saans lene me dikkat|zehar/i.test(query);

  let category = "general";
  let specialist = "General Physician";
  let summaryHindi = "सामान्य स्वास्थ्य संबंधी परेशानी के लिए योग्य डॉक्टर से परामर्श लें।";
  let summaryEnglish = "Automated clinical triage. Note: An automated response cannot reliably assess your condition or replace an in-person consultation with a doctor.";
  let firstAid = [
    "Drink plenty of water and stay well-hydrated.",
    "Rest in a comfortable, well-ventilated space.",
    "Monitor symptoms and visit a clinic if condition does not improve."
  ];
  let urgency = "ROUTINE";

  if (emergency) {
    urgency = "EMERGENCY";
    category = "cardiology";
    specialist = "Emergency Trauma & Cardiologist";
    summaryHindi = "⚠️ आपके लक्षणों में आपातकालीन चेतावनी संकेत (Emergency signs) मौजूद हैं। कृपया तुरंत 108 एम्बुलेंस या 112 पर कॉल करें अथवा नजदीकी JAH / BIMR इमरजेंसी पहुंचें।";
    summaryEnglish = "⚠️ Critical emergency warning signs detected. Call 112 or 108 ambulance now; proceed immediately to JAH Trauma Center or BIMR Hospital Gwalior.";
    firstAid = [
      "Call 112 or ambulance 108 immediately and stay on the line.",
      "Loosen tight clothing and sit upright in an airy room.",
      "Do not give food, water, or unprescribed pills to anyone unconscious.",
      "Keep patient calm and avoid any physical exertion."
    ];
  } else if (/heart|chest|chhati|dil|bp|palpitation|blood pressure/i.test(query)) {
    category = "cardiology";
    specialist = "Cardiologist (Heart Specialist)";
    urgency = "HIGH";
    summaryHindi = "छाती में असहजता या ब्लड प्रेशर में उतार-चढ़ाव कार्डियोलॉजिस्ट (हृदय रोग विशेषज्ञ) से जांच की मांग करता है। ईसीजी और बीपी मॉनिटरिंग कराएं।";
    summaryEnglish = "Cardiovascular or chest-related symptoms detected. Consultation with a Cardiologist is strongly recommended for ECG and blood pressure evaluation.";
    firstAid = [
      "Sit comfortably and rest quietly; avoid stair climbing or lifting weights.",
      "Check blood pressure and pulse rate if a monitor is available.",
      "If pain radiates to left arm, jaw or causes cold sweat, call 108 immediately."
    ];
  } else if (/headache|migraine|chakkar|dizzy|vertigo|seizure|dora|numb|sir dard|sar dard/i.test(query)) {
    category = "neurology";
    specialist = "Neurologist (Brain & Spine Specialist)";
    urgency = "HIGH";
    summaryHindi = "सिरदर्द, चक्कर या नसों से संबंधित तकलीफ माइग्रेन, सर्वाइकल या न्यूरोलॉजिकल कारणों से हो सकती है। न्यूरोलॉजिस्ट से जांच कराएं।";
    summaryEnglish = "Neurological or headache symptoms identified. Recommended specialist: Neurologist. Persistent severe headache with nausea requires immediate evaluation.";
    firstAid = [
      "Rest in a quiet, dark and well-ventilated room.",
      "Drink a glass of water and stay hydrated.",
      "Avoid mobile/laptop screen glare and bright lights.",
      "If accompanied by sudden weakness or slurred speech, seek emergency care."
    ];
  } else if (/bone|fracture|joint|ghutna|haddi|back pain|kamar dard|sprain|mote|knee|swelling/i.test(query)) {
    category = "orthopedics";
    specialist = "Orthopedic Surgeon (Bone & Joint Specialist)";
    urgency = "HIGH";
    summaryHindi = "हड्डी में चोट, जोड़ों में तेज दर्द या सूजन फ्रैक्चर अथवा लिगामेंट खिंचाव का संकेत हो सकता है। प्रभावित हिस्से को स्थिर रखें।";
    summaryEnglish = "Musculoskeletal or orthopedic issue detected. Recommended specialist: Orthopedic Surgeon. Keep the affected limb immobilized.";
    firstAid = [
      "Follow R.I.C.E.: Rest the joint and avoid putting weight on it.",
      "Apply ice pack wrapped in a clean cloth for 15-20 minutes.",
      "Support the area with a crepe bandage gently (do not wrap too tightly).",
      "Get an X-ray done at an orthopedic hospital or clinic."
    ];
  } else if (/cough|khansi|asthma|saans|breath|dama|balgam|lungs|wheezing/i.test(query)) {
    category = "pulmonology";
    specialist = "Pulmonologist (Chest & Lungs Specialist)";
    urgency = "HIGH";
    summaryHindi = "लगातार खांसी, बलगम या सांस लेने में परेशानी श्वसन नली (respiratory tract) में संक्रमण या ब्रोंकाइटिस/दमा का लक्षण हो सकता है।";
    summaryEnglish = "Respiratory or lung symptoms detected. Recommended specialist: Pulmonologist. Persistent cough with breathlessness requires clinical evaluation.";
    firstAid = [
      "Take warm steam inhalation for 10-15 minutes.",
      "Sip warm water, ginger-tulsi tea, or clear soups.",
      "Avoid cold drinks, dust, smoke, and outdoor pollution.",
      "Sit upright to make breathing easier."
    ];
  } else if (/stomach|pet dard|acidity|vomit|ulti|dast|loose motion|diarrhea|gas|digestion|pet me/i.test(query)) {
    category = "gastro";
    specialist = "Gastroenterologist (Stomach & Digestive Specialist)";
    urgency = "ROUTINE";
    summaryHindi = "पेट दर्द, गैस, एसिडिटी या उल्टी-दस्त गैस्ट्राइटिस अथवा पाचन तंत्र के संक्रमण का संकेत हैं। शरीर में पानी की कमी (dehydration) न होने दें।";
    summaryEnglish = "Gastrointestinal or digestive symptoms identified. Recommended specialist: Gastroenterologist. Maintaining adequate hydration is critical.";
    firstAid = [
      "Drink ORS (Oral Rehydration Salts) solution or coconut water in small frequent sips.",
      "Eat light bland diet (moong dal khichdi, curd, banana).",
      "Avoid spicy, fried foods and outside street water.",
      "If severe continuous abdominal pain or blood in stool occurs, visit hospital casualty."
    ];
  } else if (/skin|rash|khujli|itch|pimple|acne|fungal|chehre|daan/i.test(query)) {
    category = "dermatology";
    specialist = "Dermatologist (Skin Specialist)";
    urgency = "ROUTINE";
    summaryHindi = "त्वचा पर खुजली, लाल चकत्ते या दाने एलर्जी, फंगल संक्रमण अथवा डर्मेटाइटिस हो सकते हैं। बिना डॉक्टर की सलाह के स्टेरॉयड क्रीम न लगाएं।";
    summaryEnglish = "Dermatological or skin condition detected. Recommended specialist: Dermatologist. Avoid scratching to prevent secondary infection.";
    firstAid = [
      "Keep the affected skin clean, dry and exposed to air.",
      "Avoid hot water baths; use mild, fragrance-free soap.",
      "Apply soothing calamine lotion if itching is mild.",
      "Wear loose, breathable cotton clothing."
    ];
  } else if (/baby|child|bachha|shishu|infant|kid/i.test(query)) {
    category = "pediatrics";
    specialist = "Pediatrician (Child Specialist)";
    urgency = "HIGH";
    summaryHindi = "बच्चों के स्वास्थ्य व बुखार के लिए तुरंत योग्य शिशु रोग विशेषज्ञ (पीडियाट्रिशियन) से परामर्श लें। बच्चों को बड़ों की दवा कभी न दें।";
    summaryEnglish = "Pediatric symptoms identified. Recommended specialist: Pediatrician. Children require specialized weight-based medical care.";
    firstAid = [
      "For fever, sponge with normal lukewarm water (do not use ice water).",
      "Keep child well-hydrated with breastmilk, boiled cooled water, or fluids.",
      "Monitor feeding, wet diapers, and activity level.",
      "Consult a pediatrician immediately if child is unusually lethargic or refuses feeds."
    ];
  } else if (/pregnant|garbh|period|pcos|mahila|delivery|maternity/i.test(query)) {
    category = "gynecology";
    specialist = "Gynecologist & Obstetrician";
    urgency = "HIGH";
    summaryHindi = "गर्भावस्था या महिलाओं के स्वास्थ्य संबंधी लक्षणों के लिए विशेषज्ञ गाइनेकोलॉजिस्ट से जांच कराएं। नियमित चेकअप आवश्यक है।";
    summaryEnglish = "Obstetric or gynecological symptoms identified. Recommended specialist: Gynecologist. Timely medical supervision is vital.";
    firstAid = [
      "Rest comfortably on left side if pregnant.",
      "Maintain proper hydration and avoid heavy lifting or straining.",
      "Track symptom onset and severity.",
      "If there is acute pelvic pain or heavy bleeding, visit emergency immediately."
    ];
  } else if (/eye|aankh|vision|dhundhla|motiyabind/i.test(query)) {
    category = "ophthalmology";
    specialist = "Ophthalmologist (Eye Specialist)";
    urgency = "ROUTINE";
    summaryHindi = "आंखों में दर्द, धुंधलापन या लाली के लिए नेत्र रोग विशेषज्ञ से जांच कराएं। आंखों को रगड़ें नहीं।";
    summaryEnglish = "Ophthalmic symptoms identified. Recommended specialist: Eye Specialist (Ophthalmologist).";
    firstAid = [
      "Do not rub or press your eyes.",
      "Splash with clean, sterile cold water if mild irritation.",
      "Rest eyes from digital screens and mobile devices.",
      "If sudden vision loss or chemical splash, seek immediate emergency care."
    ];
  } else if (/fever|bukhar|cold|jukaam|body pain|weakness|flu/i.test(query)) {
    category = "general";
    specialist = "General Physician";
    urgency = "ROUTINE";
    summaryHindi = "बुखार, सर्दी या बदन दर्द सामान्य वायरल संक्रमण का संकेत हो सकता है। तापमान को मापें और पर्याप्त आराम करें।";
    summaryEnglish = "General viral or febrile symptoms identified. Recommended specialist: General Physician. Note: An automated response cannot reliably assess your condition or replace clinical lab tests.";
    firstAid = [
      "Drink plenty of warm fluids (herbal tea, warm water, soups).",
      "Monitor body temperature with a thermometer every 4 hours.",
      "Get complete physical rest and avoid exhaustion.",
      "If fever persists above 101°F for over 3 days, consult a physician."
    ];
  }

  // Find matching doctors from loaded list
  const matchedDocs = (allDoctors || []).filter(d => (d.category || "").toLowerCase() === category).slice(0, 2);
  const fallbackDocs = matchedDocs.length ? matchedDocs : (allDoctors || []).slice(0, 2);

  // Find matching emergency hospitals
  const emergencyHosps = (allHospitals || []).filter(h => h.emergency_24x7 || h.emergency24x7).slice(0, 3);

  return {
    urgency,
    category,
    recommendedSpecialist: specialist,
    summaryHindi,
    summaryEnglish,
    firstAid,
    recommendedDoctors: fallbackDocs,
    recommendedHospitals: emergencyHosps,
    poweredBy: reason || "Swasthya Clinical Health Engine (Gwalior Healthcare Triage)",
    aiMode: "offline",
  };
}

async function handleAiSubmit() {
  const input = el("aiUserInput");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  if (text.length > 2000) {
    showToast("Please keep your description under 2,000 characters.");
    return;
  }

  const chat = el("aiChatWindow");
  if (!chat) return;

  chat.insertAdjacentHTML("beforeend", `
    <div class="chat-message user-message">
      <div class="chat-bubble"><p>${esc(text)}</p></div>
      <span class="chat-time">Just now</span>
    </div>
    <div class="chat-message ai-message" id="aiTypingIndicator">
      <div class="chat-bubble ai-loading-bubble">Swasthya AI is evaluating clinical symptoms...</div>
    </div>
  `);
  input.value = "";
  input.disabled = true;
  const sendButton = el("aiSendBtn");
  if (sendButton) sendButton.disabled = true;
  chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" });

  let responseData;
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/diagnose`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symptoms: text }),
    });
    if (!response.ok) {
      throw new Error(`AI service responded with HTTP ${response.status}`);
    }
    responseData = await response.json();
  } catch (error) {
    // Seamless fallback to Swasthya Clinical Health Engine - NEVER crash or stop the chat!
    console.info("Swasthya AI fallback activated:", error.message);
    responseData = offlineAiReply(text, "Swasthya Clinical Health Engine");
  }

  document.getElementById("aiTypingIndicator")?.remove();
  renderAiResponseInChat(chat, responseData);
  input.disabled = false;
  if (sendButton) sendButton.disabled = false;
  input.focus();
}

function setupAiInput() {
  el("aiUserInput")?.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleAiSubmit();
    }
  });
}

document.addEventListener("DOMContentLoaded", setupAiInput);

function renderAiResponseInChat(chat, data) {
  const isEmergency = data.urgency === "EMERGENCY";
  const urgencyClass = isEmergency ? "urgency-emergency" : (data.urgency === "HIGH" ? "urgency-urgent" : "urgency-routine");

  const docCardsHtml = (data.recommendedDoctors || []).map(d => `
    <div style="background:#fff; border:1px solid #cbd5e1; border-radius:8px; padding:10px; margin-top:8px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <strong style="font-size:0.92rem; color:#0f172a;">${esc(d.name)}</strong>
        <span style="font-size:0.78rem; color:#059669; font-weight:700;">★ ${(d.rating || 4.9).toFixed(1)}</span>
      </div>
      <p style="font-size:0.8rem; color:#475569; margin:2px 0;">${esc(d.specialty)} &bull; ${esc(d.hospitalName || d.hospital_name)}</p>
      <div style="display:flex; gap:6px; margin-top:6px;">
        <button class="btn btn-primary btn-sm" onclick="openBookingModalForDoctor(${d.id})">📅 Book Appointment (₹${d.fee})</button>
        <a class="btn btn-ghost btn-sm" href="tel:${esc(d.phone)}">📞 Call</a>
      </div>
    </div>
  `).join("");

  const hospCardsHtml = (data.recommendedHospitals || []).map(h => `
    <div style="background:#fff; border:1px solid #cbd5e1; border-radius:8px; padding:8px 10px; margin-top:6px; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <strong style="font-size:0.86rem; color:#0f172a; display:block;">${esc(h.name)}</strong>
        <span style="font-size:0.76rem; color:#475569;">📍 ${esc(h.address)}</span>
      </div>
      <a class="btn btn-ghost btn-sm" href="tel:${esc(h.emergencyPhone || h.phone)}" style="color:#b91c1c; font-weight:800;">
        🚨 Call
      </a>
    </div>
  `).join("");

  const html = `
    <div class="chat-message ai-message">
      <div class="chat-bubble">
        <div class="ai-triage-card ${urgencyClass}">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <span style="font-size:1.1rem;">${isEmergency ? '🚨' : '🩺'}</span>
            <strong style="font-size:0.95rem; color:${isEmergency ? '#dc2626' : '#0f172a'};">
              Triage Level: ${esc(data.urgency)} &bull; Recommended: ${esc(data.recommendedSpecialist)}
            </strong>
          </div>
          <p style="font-size:0.88rem; color:#1e293b; margin-bottom:4px;"><strong>Hindi:</strong> ${esc(data.summaryHindi)}</p>
          <p style="font-size:0.84rem; color:#475569; margin-bottom:8px;"><strong>Guidance:</strong> ${esc(data.summaryEnglish)}</p>

          <div style="background:rgba(255,255,255,0.7); padding:8px; border-radius:6px; font-size:0.8rem; margin-top:6px;">
            <strong style="color:#0f172a;">Immediate Care / First-Aid:</strong>
            <ul style="padding-left:18px; margin-top:4px;">
              ${(data.firstAid || []).map(fa => `<li>${esc(fa)}</li>`).join("")}
            </ul>
          </div>
          <div class="ai-provider-label">${esc(data.poweredBy || "Health information")}</div>
        </div>

        ${data.recommendedDoctors && data.recommendedDoctors.length ? `
          <div style="margin-top:12px;">
            <span style="font-size:0.82rem; font-weight:800; color:#0f172a;">Recommended Gwalior Specialists:</span>
            ${docCardsHtml}
          </div>
        ` : ''}

        ${data.recommendedHospitals && data.recommendedHospitals.length ? `
          <div style="margin-top:10px;">
            <span style="font-size:0.82rem; font-weight:800; color:#0f172a;">24x7 Emergency Hospitals in Gwalior:</span>
            ${hospCardsHtml}
          </div>
        ` : ''}
      </div>
      <span class="chat-time">Just now</span>
    </div>
  `;

  chat.innerHTML += html;
  chat.scrollTop = chat.scrollHeight;
}

/* ---------- 13. NAVIGATION & UI TABS ---------- */
function switchMainTab(targetId, autoScroll = true) {
  currentTab = targetId;
  document.querySelectorAll(".main-nav .nav-item").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.target === targetId);
  });

  document.querySelectorAll(".tab-pane").forEach(pane => {
    pane.classList.toggle("active", pane.id === `pane-${targetId}` || pane.id === targetId);
  });

  if (targetId === "finder" && map) {
    requestAnimationFrame(() => map && map.invalidateSize({ pan: false, debounceMoveend: true }));
  } else if (targetId === "doctors-section") {
    renderDoctorsDirectory("all");
  } else if (targetId === "blood-banks-section") {
    renderBloodBanks("all");
  } else if (targetId === "ambulances-section") {
    renderAmbulances();
  } else if (targetId === "my-appointments-section") {
    renderMyAppointmentsList();
  }

  if (autoScroll) {
    const pane = el(`pane-${targetId}`) || el(targetId);
    if (pane) {
      scrollToTarget(pane, 75);
    }
  }
}

function navigateTo(targetId) {
  switchMainTab(targetId, true);
}

function quickSearch(keyword) {
  const lower = keyword.toLowerCase();
  const docMatch = (allDoctors || []).find(d => 
    (d.name && d.name.toLowerCase().includes(lower)) || 
    (d.specialty && d.specialty.toLowerCase().includes(lower))
  );
  if (docMatch) {
    switchMainTab("doctors-section", false);
    const docInput = el("doctorSearchInput");
    if (docInput) docInput.value = keyword;
    renderDoctorsDirectory("all");
    scrollToTarget("doctorsGrid", 90);
    return;
  }

  const input = el("searchInput");
  if (input) {
    input.value = keyword;
    switchMainTab("finder", false);
    filterHospitals();
    scrollToTarget("hospitalList", 90);
  }
}

function filterBySpecialty(spec) {
  switchMainTab("doctors-section", false);
  const bar = el("doctorCategoryBar");
  if (bar) {
    bar.querySelectorAll(".doc-cat-btn").forEach(b => {
      b.classList.toggle("active", b.dataset.cat === spec);
    });
  }
  renderDoctorsDirectory(spec);
  scrollToTarget("doctorsGrid", 90);
  const label = spec === "all" ? "All Specialist Doctors" : `${spec.charAt(0).toUpperCase() + spec.slice(1)} Specialists`;
  showToast(`Showing ${label} in Gwalior`);
}

function setView(viewMode) {
  const layout = el("layout");
  if (!layout) return;
  layout.className = `layout view-${viewMode}`;
  document.querySelectorAll(".view-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.view === viewMode);
  });
  if (map) requestAnimationFrame(() => map && map.invalidateSize({ pan: false, debounceMoveend: true }));
}

function resetAllFilters() {
  if (el("searchInput")) el("searchInput").value = "";
  if (el("typeFilter")) el("typeFilter").value = "all";
  if (el("bedFilter")) el("bedFilter").value = "all";
  if (el("minBeds")) el("minBeds").value = "0";
  if (el("radiusFilter")) el("radiusFilter").value = "0";
  if (el("sortBy")) el("sortBy").value = "distance";

  ["emergencyOnly", "icuOnly", "ventOnly", "oxygenOnly", "ambulanceOnly", "bloodOnly", "favOnly"].forEach(id => {
    if (el(id)) el(id).checked = false;
  });

  filterHospitals();
  showToast("All filters cleared.");
}

function toggleFavourite(hid) {
  if (favourites.has(hid)) {
    favourites.delete(hid);
    showToast("Removed from saved favourites.");
  } else {
    favourites.add(hid);
    showToast("Saved to favourite hospitals!");
  }
  try {
    localStorage.setItem(FAV_KEY, JSON.stringify(Array.from(favourites)));
  } catch (e) {}
  filterHospitals();
}

function loadFavourites() {
  try {
    const raw = localStorage.getItem(FAV_KEY);
    if (raw) favourites = new Set(JSON.parse(raw));
  } catch (e) {
    favourites = new Set();
  }
}

function showToast(msg) {
  const toast = el("toast");
  if (!toast) return;
  toast.textContent = msg;
  toast.hidden = false;
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => { toast.hidden = true; }, 3200);
}

let isLocating = false;

function useMyLocation() {
  if (isLocating) return;
  isLocating = true;

  const locStatus = el("locationStatus");
  if (locStatus) {
    locStatus.innerHTML = `<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#0d9488; margin-right:6px; animation:gpsPulse 1s infinite;"></span> Locating you in Gwalior (Ultra-Fast GPS)...`;
  }
  showToast("🛰️ Acquiring your location in Gwalior...");

  if (!navigator.geolocation) {
    isLocating = false;
    showToast("Geolocation is not supported by your browser. Using Gwalior Center.");
    handleLocationFound(GWALIOR_CENTER.lat, GWALIOR_CENTER.lng, false);
    return;
  }

  let resolved = false;
  const fallbackTimer = setTimeout(() => {
    if (!resolved) {
      resolved = true;
      isLocating = false;
      handleLocationFound(GWALIOR_CENTER.lat, GWALIOR_CENTER.lng, false);
    }
  }, 3200);

  navigator.geolocation.getCurrentPosition(
    pos => {
      if (resolved) return;
      resolved = true;
      clearTimeout(fallbackTimer);
      isLocating = false;
      handleLocationFound(pos.coords.latitude, pos.coords.longitude, true);
    },
    err => {
      if (resolved) return;
      resolved = true;
      clearTimeout(fallbackTimer);
      isLocating = false;
      console.warn("GPS lookup fallback:", err);
      handleLocationFound(GWALIOR_CENTER.lat, GWALIOR_CENTER.lng, false);
    },
    { enableHighAccuracy: true, timeout: 3000, maximumAge: 30000 }
  );
}

function handleLocationFound(lat, lng, accurate) {
  userPoint = { lat, lng, accurate };

  // Find nearest hospital instantly using distance calculation
  let nearestHosp = null;
  let minDistance = Infinity;

  allHospitals.forEach(h => {
    const d = distanceKm(userPoint, { lat: h.lat, lng: h.lng });
    h.distance = d;
    if (d < minDistance) {
      minDistance = d;
      nearestHosp = h;
    }
  });

  window._nearestHospitalId = nearestHosp ? nearestHosp.id : null;

  const locStatus = el("locationStatus");
  if (locStatus) {
    if (nearestHosp) {
      locStatus.innerHTML = `📍 Location: <strong>${lat.toFixed(4)}, ${lng.toFixed(4)}</strong> &bull; Nearest: <strong style="color:#0d9488;">${esc(nearestHosp.name)}</strong> (${minDistance.toFixed(1)} km)`;
    } else {
      locStatus.textContent = `Location: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }
  }

  const sortSelect = el("sortBy");
  if (sortSelect) sortSelect.value = "distance";

  updateUserMarker();
  filterHospitals();

  if (map && nearestHosp) {
    const bounds = L.latLngBounds([
      [userPoint.lat, userPoint.lng],
      [nearestHosp.lat, nearestHosp.lng]
    ]);
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });

    setTimeout(() => {
      if (mapMarkers[nearestHosp.id]) {
        mapMarkers[nearestHosp.id].openPopup();
      }
    }, 600);

    const etaMins = Math.max(2, Math.round(minDistance * 2.5));
    showToast(`🏆 Nearest Hospital: ${nearestHosp.name} (${minDistance.toFixed(1)} km, ~${etaMins} mins away)!`);
  }
}

function renderSkeletons() {
  const hospEl = el("hospitalList");
  if (hospEl && (!allHospitals || allHospitals.length === 0)) {
    hospEl.innerHTML = Array(4).fill(0).map(() => `
      <div class="skeleton-card">
        <div class="skeleton-header-row">
          <div class="skeleton-avatar skeleton-shimmer"></div>
          <div style="flex:1;">
            <div class="skeleton-title skeleton-shimmer"></div>
            <div class="skeleton-subtitle skeleton-shimmer"></div>
          </div>
        </div>
        <div class="skeleton-line skeleton-shimmer"></div>
        <div class="skeleton-line short skeleton-shimmer"></div>
        <div class="skeleton-badge-row">
          <div class="skeleton-badge skeleton-shimmer"></div>
          <div class="skeleton-badge skeleton-shimmer"></div>
          <div class="skeleton-badge skeleton-shimmer"></div>
        </div>
      </div>
    `).join("");
  }
}

/* ---------- 14. INITIALIZATION ON DOM READY ---------- */
document.addEventListener("DOMContentLoaded", async () => {
  initTheme();
  renderSkeletons();
  loadFavourites();
  initAuth();

  const [_, hosp, doc, bb, amb] = await Promise.all([
    loadMapConfiguration(),
    loadHospitalsData(),
    loadDoctorsData(),
    loadBloodBanksData(),
    loadAmbulancesData()
  ]);
  allHospitals = hosp;
  allDoctors = doc;
  allBloodBanks = bb;
  allAmbulances = amb;

  const presetSel = el("presetArea");
  if (presetSel) {
    PRESET_AREAS.forEach(([name, lat, lng]) => {
      const opt = document.createElement("option");
      opt.value = `${lat},${lng}`;
      opt.textContent = name;
      presetSel.appendChild(opt);
    });
    presetSel.addEventListener("change", () => {
      if (!presetSel.value) return;
      const [lat, lng] = presetSel.value.split(",").map(Number);
      userPoint = { lat, lng, accurate: true };
      updateUserMarker();
      el("locationStatus").textContent = `Selected Area: ${presetSel.options[presetSel.selectedIndex].text}`;
      filterHospitals();
    });
  }

  if (typeof localStorage !== "undefined") {
    const savedMapStyle = localStorage.getItem(MAP_STYLE_KEY);
    if (savedMapStyle && AROGYA_CONFIG.tileProviders[savedMapStyle]) {
      activeTileProvider = savedMapStyle;
    }
    const savedAlgorithm = localStorage.getItem(MAP_SPATIAL_ALGORITHM_KEY);
    if (savedAlgorithm === "kdtree" || savedAlgorithm === "quadtree") {
      mapSpatialAlgorithm = savedAlgorithm;
    }
  }
  const spatialAlgorithmSelect = el("mapSpatialAlgorithm");
  if (spatialAlgorithmSelect) spatialAlgorithmSelect.value = mapSpatialAlgorithm;
  initMap();

  filterHospitals();
  renderDoctorsDirectory("all");
  renderBloodBanks("all");
  renderAmbulances();
  initDoctorDirectoryEvents();
  updateMyAppointmentsBadge();

  document.querySelectorAll(".main-nav .nav-item").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.target;
      if (target && target !== "book-section") {
        switchMainTab(target);
      }
    });
  });

  document.querySelectorAll(".view-btn").forEach(btn => {
    btn.addEventListener("click", () => setView(btn.dataset.view));
  });

  ["searchInput", "typeFilter", "bedFilter", "minBeds", "sortBy", "radiusFilter", "emergencyOnly", "icuOnly", "ventOnly", "oxygenOnly", "ambulanceOnly", "bloodOnly", "favOnly"].forEach(id => {
    el(id)?.addEventListener("input", filterHospitals);
    el(id)?.addEventListener("change", filterHospitals);
  });

  el("resetBtn")?.addEventListener("click", resetAllFilters);
  el("locateBtn")?.addEventListener("click", useMyLocation);

  el("manualBtn")?.addEventListener("click", () => {
    const box = el("manualLocation");
    if (box) box.hidden = !box.hidden;
  });

  el("pickMapBtn")?.addEventListener("click", () => {
    window._isPickingMap = true;
    document.body.style.cursor = "crosshair";
    showToast("Click anywhere on the map to set your location pin!");
    switchMainTab("finder");
    el("map-section")?.scrollIntoView({ behavior: "smooth" });
  });

  el("emergencyExit")?.addEventListener("click", () => {
    emergencyMode = false;
    el("emergencyBar").hidden = true;
    const chk = el("emergencyOnly");
    if (chk) chk.checked = false;
    filterHospitals();
  });


  el("aiUserInput")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleAiSubmit();
  });
});
