/* =====================================================================
   Admin dashboard - admin.js
   Talks to the authenticated Flask admin API for hospital directory data.
   Open it from the Flask server:  http://127.0.0.1:5000/admin
   ===================================================================== */
const BED_LABELS = {
  general: "General Ward", icu: "ICU", emergency: "Emergency",
  oxygen: "Oxygen-supported", ventilator: "Ventilator-supported",
};
const BED_TYPES = Object.keys(BED_LABELS);
const COMMON_SERVICES = ["Ambulance", "Blood bank", "Pharmacy", "Trauma care", "Cardiology", "Paediatrics"];
const DEMO_CENTER = { lat: 26.2183, lng: 78.1828 };

const el = id => document.getElementById(id);
const esc = text => String(text).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let hospitals = [];
let doctors = [];
let editingId = null;            // null = adding a new hospital
let editingDoctorId = null;

/* ---------- API helper ---------- */
async function api(path, method = "GET", body) {
  let response;
  try {
    response = await fetch(path, {
      method, credentials: "same-origin", cache: "no-store",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (error) {
    throw new Error("Cannot reach the Flask server. Start it with: python app.py  and open http://127.0.0.1:5000/admin");
  }
  let data = {};
  try { data = await response.json(); } catch (error) { /* no JSON body */ }
  if (response.status === 401 && path !== "/api/admin/login") showLogin();
  if (!response.ok) throw new Error(data.error || `Server error (${response.status})`);
  return data;
}

/* ---------- Views ---------- */
function showLogin() {
  el("dashView").hidden = true;
  el("loginView").hidden = false;
}

function showDashboard() {
  el("loginView").hidden = true;
  el("dashView").hidden = false;
}

function showServerError(message) {
  el("serverError").hidden = !message;
  el("serverError").textContent = message || "";
}

function flash(message) {
  el("flash").textContent = message;
  if (message) setTimeout(() => { if (el("flash").textContent === message) el("flash").textContent = ""; }, 9000);
}

/* ---------- Helpers ---------- */
function availableOf(h, type) {
  const [total, occupied] = (h.beds && h.beds[type]) || [0, 0];
  return Math.max(0, total - occupied);
}
function totalAvailable(h) { return BED_TYPES.reduce((s, t) => s + availableOf(h, t), 0); }
function ago(iso) {
  const t = new Date(iso).getTime();
  if (!iso || Number.isNaN(t)) return "unknown";
  const m = Math.max(0, Math.round((Date.now() - t) / 60000));
  if (m < 1) return "just now";
  if (m < 60) return `${m} min ago`;
  if (m < 1440) return `${Math.round(m / 60)} hr ago`;
  return `${Math.round(m / 1440)} day(s) ago`;
}

const SOURCE_TEXT = { real: "Directory", demo: "Demo", osm: "OpenStreetMap", manual: "Added by admin" };

/* ---------- Table ---------- */
function renderStats() {
  const active = hospitals.filter(h => h.active);
  const listed = hospitals.filter(h => h.source !== "demo").length;
  const verified = hospitals.filter(h => h.source !== "demo" && h.verified).length;
  const freeBeds = active.filter(h => h.verified).reduce((s, h) => s + totalAvailable(h), 0);
  const freeIcu = active.filter(h => h.verified).reduce((s, h) => s + availableOf(h, "icu"), 0);
  const tile = (value, label, cls = "") => `<div class="admin-stat ${cls}"><b>${value}</b><span>${label}</span></div>`;
  el("adminStats").innerHTML =
    tile(hospitals.length, "Hospitals in database") + tile(active.length, "Active (visible)", "good") +
    tile(listed, "Directory listings") + tile(`${verified} / ${listed}`, "Listings verified", verified === listed ? "good" : "warn") +
    tile(freeBeds, "Free beds (verified, active)") + tile(freeIcu, "Free ICU beds (verified, active)");
}

function renderTable() {
  const active = hospitals.filter(h => h.active).length;
  el("adminSummary").textContent = `${hospitals.length} hospital(s) in the database, ${active} active`;
  renderStats();
  const q = el("adminSearch").value.trim().toLowerCase(), src = el("adminSource").value;
  const shown = hospitals.filter(h =>
    (!q || `${h.name} ${h.address}`.toLowerCase().includes(q)) &&
    (src === "all" || (src === "real" && h.source !== "demo") || (src === "demo" && h.source === "demo") ||
     (src === "unverified" && !h.verified)));
  el("adminRows").innerHTML = shown.map(h => `
    <tr>
      <td><b>${esc(h.name)}</b><br><small>${esc(h.address)}</small></td>
      <td>${esc(h.type)}</td>
      <td>${esc(SOURCE_TEXT[h.source] || h.source)}<br><small class="${h.verified ? "avail-ok" : "avail-none"}">${h.verified ? "verified" : "not verified"}</small></td>
      <td class="${h.verified ? (totalAvailable(h) > 0 ? "avail-ok" : "avail-none") : ""}"><b>${h.verified ? totalAvailable(h) : "-"}</b></td>
      <td class="${h.verified ? (availableOf(h, "icu") > 0 ? "avail-ok" : "avail-none") : ""}"><b>${h.verified ? availableOf(h, "icu") : "-"}</b></td>
      <td><span class="status ${h.active ? "active" : "inactive"}">${h.active ? "Active" : "Inactive"}</span></td>
      <td title="${esc(new Date(h.lastUpdated).toLocaleString())}">${esc(ago(h.lastUpdated))}</td>
      <td><div class="row-actions">
        <button class="btn btn-ghost btn-sm" data-act="edit" data-id="${h.id}" type="button">Edit</button>
        <button class="btn btn-ghost btn-sm" data-act="toggle" data-id="${h.id}" type="button">${h.active ? "Deactivate" : "Activate"}</button>
        <button class="btn btn-danger-outline btn-sm" data-act="delete" data-id="${h.id}" type="button">Delete</button>
      </div></td>
    </tr>`).join("") || '<tr><td colspan="8">No hospitals match. Add a listing or import from OpenStreetMap.</td></tr>';
}

async function loadHospitals() {
  hospitals = await api("/api/admin/hospitals");
  const hospitalSelect = el("dHospitalId");
  if (hospitalSelect) {
    hospitalSelect.replaceChildren(new Option("Standalone clinic / enter manually", ""));
    hospitals.forEach(hospital => {
      const option = new Option(hospital.name, String(hospital.id));
      option.dataset.address = hospital.address;
      hospitalSelect.add(option);
    });
  }
  renderTable();
}

function renderDoctors() {
  el("doctorRows").innerHTML = doctors.map(doctor => `
    <tr>
      <td><b>${esc(doctor.name)}</b><br><small>${esc(doctor.qualification)}</small></td>
      <td>${esc(doctor.specialty)}</td>
      <td>${esc(doctor.hospital_name)}</td>
      <td><small class="${doctor.verified ? "avail-ok" : "avail-none"}">${doctor.verified ? "verified" : "needs verification"}</small></td>
      <td><div class="row-actions">
        <button class="btn btn-ghost btn-sm" data-doctor-act="edit" data-id="${doctor.id}" type="button">Edit</button>
        <button class="btn btn-danger-outline btn-sm" data-doctor-act="delete" data-id="${doctor.id}" type="button">Delete</button>
      </div></td>
    </tr>`).join("") || '<tr><td colspan="5">No doctor profiles in the directory yet.</td></tr>';
}

async function loadDoctors() {
  doctors = await api("/api/admin/doctors");
  renderDoctors();
}

function openDoctorDialog(doctor = null) {
  editingDoctorId = doctor ? doctor.id : null;
  el("doctorDialogTitle").textContent = doctor ? `Edit: ${doctor.name}` : "Add doctor";
  el("doctorDialogError").textContent = "";
  el("dName").value = doctor ? doctor.name : "";
  el("dQualification").value = doctor ? doctor.qualification : "";
  el("dSpecialty").value = doctor ? doctor.specialty : "";
  el("dCategory").value = doctor ? doctor.category : "general";
  el("dExperience").value = doctor ? doctor.experience_years : "";
  el("dHospitalId").value = doctor && doctor.hospital_id ? String(doctor.hospital_id) : "";
  el("dHospital").value = doctor ? doctor.hospital_name : "";
  el("dAddress").value = doctor ? doctor.clinic_address : "";
  el("dPhone").value = doctor ? doctor.phone : "";
  el("dFee").value = doctor ? doctor.fee : "";
  el("dOpd").value = doctor ? doctor.opd_timings : "";
  el("dDays").value = doctor ? doctor.days_available : "Mon - Sat";
  el("dAbout").value = doctor ? doctor.about : "";
  el("dVerified").checked = doctor ? Boolean(doctor.verified) : false;
  el("doctorDialog").showModal();
}

function collectDoctorForm() {
  return {
    name: el("dName").value.trim(),
    qualification: el("dQualification").value.trim(),
    specialty: el("dSpecialty").value.trim(),
    category: el("dCategory").value,
    experienceYears: el("dExperience").value || 0,
    hospitalId: el("dHospitalId").value || null,
    hospitalName: el("dHospital").value.trim(),
    clinicAddress: el("dAddress").value.trim(),
    phone: el("dPhone").value.trim(),
    fee: el("dFee").value || 0,
    opdTimings: el("dOpd").value.trim(),
    daysAvailable: el("dDays").value.trim(),
    about: el("dAbout").value.trim(),
    verified: el("dVerified").checked,
  };
}

async function saveDoctor() {
  el("doctorDialogError").textContent = "";
  el("doctorDialogSave").disabled = true;
  try {
    const body = collectDoctorForm();
    const path = editingDoctorId === null ? "/api/admin/doctors" : `/api/admin/doctors/${editingDoctorId}`;
    await api(path, editingDoctorId === null ? "POST" : "PUT", body);
    el("doctorDialog").close();
    await loadDoctors();
    flash(editingDoctorId === null ? "Doctor profile added." : "Doctor profile updated.");
  } catch (error) {
    el("doctorDialogError").textContent = error.message;
  } finally {
    el("doctorDialogSave").disabled = false;
  }
}

/* ---------- Add / edit dialog ---------- */
function buildFormParts() {
  el("serviceChecks").innerHTML = COMMON_SERVICES.map((s, i) =>
    `<label class="check"><input type="checkbox" data-service="${esc(s)}" id="svc${i}"> ${esc(s)}</label>`).join("");
  el("bedEditRows").innerHTML = BED_TYPES.map(t => `
    <tr>
      <td>${BED_LABELS[t]}</td>
      <td><input type="number" min="0" max="10000" id="bt_${t}" aria-label="${BED_LABELS[t]} total beds"></td>
      <td><input type="number" min="0" max="10000" id="bo_${t}" aria-label="${BED_LABELS[t]} occupied beds"></td>
      <td id="ba_${t}">0</td>
    </tr>`).join("");
  BED_TYPES.forEach(t => {
    ["bt_", "bo_"].forEach(p => el(p + t).addEventListener("input", () => updateAvailable(t)));
  });
}

function updateAvailable(type) {
  const total = Number(el("bt_" + type).value) || 0, occupied = Number(el("bo_" + type).value) || 0;
  const cell = el("ba_" + type);
  cell.textContent = occupied > total ? "check numbers" : Math.max(0, total - occupied);
  cell.className = occupied <= total && total - occupied > 0 ? "avail-ok" : "avail-none";
}

function openDialog(h) {
  editingId = h ? h.id : null;
  el("dialogTitle").textContent = h ? `Edit: ${h.name}` : "Add hospital";
  el("dialogError").textContent = "";
  el("fName").value = h ? h.name : "";
  el("fPhotoUrl").value = h ? (h.photoUrl || h.photo_url || "") : "";
  el("fPhotoCredit").value = h ? (h.photoCredit || h.photo_credit || "") : "";
  el("fType").value = h ? h.type : "Government";
  el("fPhone").value = h ? h.phone : "";
  el("fAddress").value = h ? h.address : "";
  el("fLat").value = h ? h.lat : DEMO_CENTER.lat;
  el("fLng").value = h ? h.lng : DEMO_CENTER.lng;
  el("fEmergency").checked = h ? h.emergency24x7 : false;
  el("fActive").checked = h ? h.active : true;
  el("fVerified").checked = h ? h.verified : true;
  el("fSourceInfo").textContent = h
    ? `Source: ${SOURCE_TEXT[h.source] || h.source}${h.osmId ? " (" + h.osmId + ")" : ""}. ${h.source === "osm" ? "Location, phone and type come from OpenStreetMap; fix them here if they are wrong." : ""}`
    : "New hospitals are marked 'Added by admin'.";
  const services = h ? h.services : [];
  const common = COMMON_SERVICES.map(s => s.toLowerCase());
  document.querySelectorAll("[data-service]").forEach(box => {
    box.checked = services.some(s => s.toLowerCase() === box.dataset.service.toLowerCase());
  });
  el("fOtherServices").value = services.filter(s => !common.includes(s.toLowerCase())).join(", ");
  BED_TYPES.forEach(t => {
    const [total, occupied] = (h && h.beds[t]) || [0, 0];
    el("bt_" + t).value = total;
    el("bo_" + t).value = occupied;
    updateAvailable(t);
  });
  el("hospitalDialog").showModal();
}

function collectForm() {
  const services = [...document.querySelectorAll("[data-service]")].filter(b => b.checked).map(b => b.dataset.service);
  el("fOtherServices").value.split(",").map(s => s.trim()).filter(Boolean).forEach(s => services.push(s));
  const beds = {};
  BED_TYPES.forEach(t => { beds[t] = [Number(el("bt_" + t).value) || 0, Number(el("bo_" + t).value) || 0]; });
  return {
    name: el("fName").value.trim(), type: el("fType").value, phone: el("fPhone").value.trim(),
    photoUrl: el("fPhotoUrl").value.trim(), photoCredit: el("fPhotoCredit").value.trim(),
    address: el("fAddress").value.trim(), lat: el("fLat").value, lng: el("fLng").value,
    emergency24x7: el("fEmergency").checked, active: el("fActive").checked, verified: el("fVerified").checked, services, beds,
  };
}

async function saveHospital() {
  el("dialogError").textContent = "";
  el("dialogSave").disabled = true;
  try {
    const body = collectForm();
    if (editingId === null) await api("/api/admin/hospitals", "POST", body);
    else await api(`/api/admin/hospitals/${editingId}`, "PUT", body);
    el("hospitalDialog").close();
    await loadHospitals();
    flash(editingId === null ? "Hospital added." : "Hospital updated. The website will show it on its next refresh.");
  } catch (error) {
    el("dialogError").textContent = error.message;
  } finally {
    el("dialogSave").disabled = false;
  }
}

/* ---------- Table actions ---------- */
el("adminRows").addEventListener("click", async event => {
  const button = event.target.closest("[data-act]");
  if (!button) return;
  const h = hospitals.find(x => x.id === Number(button.dataset.id));
  if (!h) return;
  try {
    if (button.dataset.act === "edit") openDialog(h);
    else if (button.dataset.act === "toggle") {
      await api(`/api/admin/hospitals/${h.id}`, "PUT", { ...h, active: !h.active });
      await loadHospitals();
      flash(`${h.name} is now ${h.active ? "inactive" : "active"}.`);
    } else if (button.dataset.act === "delete") {
      if (!confirm(`Delete "${h.name}" permanently? This cannot be undone.`)) return;
      await api(`/api/admin/hospitals/${h.id}`, "DELETE");
      await loadHospitals();
      flash("Hospital deleted.");
    }
  } catch (error) {
    flash(error.message);
  }
});

el("doctorRows").addEventListener("click", async event => {
  const button = event.target.closest("[data-doctor-act]");
  if (!button) return;
  const doctor = doctors.find(item => item.id === Number(button.dataset.id));
  if (!doctor) return;
  if (button.dataset.doctorAct === "edit") {
    openDoctorDialog(doctor);
    return;
  }
  if (!confirm(`Delete doctor profile for "${doctor.name}"? This cannot be undone.`)) return;
  try {
    await api(`/api/admin/doctors/${doctor.id}`, "DELETE");
    await loadDoctors();
    flash("Doctor profile deleted.");
  } catch (error) {
    flash(error.message);
  }
});

/* ---------- Login / logout / password ---------- */
async function login() {
  el("loginError").textContent = "";
  try {
    await api("/api/admin/login", "POST", { username: el("loginUser").value, password: el("loginPass").value });
    el("loginPass").value = "";
    await startDashboard();
  } catch (error) {
    el("loginError").textContent = error.message;
  }
}

async function startDashboard() {
  const me = await api("/api/admin/me");
  if (!me.loggedIn) { showLogin(); return; }
  showDashboard();
  el("passwordWarning").hidden = !me.defaultPassword;
  await Promise.all([loadHospitals(), loadDoctors()]);
}

async function savePassword() {
  el("pwError").textContent = "";
  if (el("pwNew").value !== el("pwNew2").value) { el("pwError").textContent = "The two new passwords do not match."; return; }
  try {
    await api("/api/admin/password", "POST", { current: el("pwCurrent").value, new: el("pwNew").value });
    el("pwDialog").close();
    ["pwCurrent", "pwNew", "pwNew2"].forEach(id => { el(id).value = ""; });
    el("passwordWarning").hidden = true;
    flash("Password changed.");
  } catch (error) {
    el("pwError").textContent = error.message;
  }
}

el("loginBtn").addEventListener("click", login);
el("loginPass").addEventListener("keydown", e => { if (e.key === "Enter") login(); });
el("logoutBtn").addEventListener("click", async () => { await api("/api/admin/logout", "POST", {}); showLogin(); });
el("addBtn").addEventListener("click", () => openDialog(null));
el("adminSearch").addEventListener("input", renderTable);
el("adminSource").addEventListener("change", renderTable);

// Import hospital locations from OpenStreetMap.
// Step 1: the SERVER downloads them. Step 2 (if that fails): this BROWSER downloads them and sends them to the server.
const OVERPASS_URLS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"];
function overpassQuery(km) {
  const around = `(around:${km * 1000},${DEMO_CENTER.lat},${DEMO_CENTER.lng})`;
  return `[out:json][timeout:50];(node["amenity"="hospital"]${around};way["amenity"="hospital"]${around};relation["amenity"="hospital"]${around};);out center tags;`;
}

async function downloadInBrowser(km) {
  const problems = [];
  for (const url of OVERPASS_URLS) {
    try {
      const response = await fetch(url, {
        method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "data=" + encodeURIComponent(overpassQuery(km)),
      });
      if (!response.ok) { problems.push(`${new URL(url).host}: HTTP ${response.status}`); continue; }
      const data = await response.json();
      return data.elements || [];
    } catch (error) {
      problems.push(`${new URL(url).host}: ${error.message}`);
    }
  }
  throw new Error("The browser could not reach OpenStreetMap either (" + problems.join("; ") + ")");
}

function osmReport(message, isError) {
  const box = el("osmReport");
  box.hidden = !message;
  box.textContent = message || "";
  box.classList.toggle("is-ok", !isError);
}

el("osmBtn").addEventListener("click", async () => {
  if (!confirm("Download hospitals within 15 km of Gwalior from OpenStreetMap?\n\nOnly names, locations and any contact details listed there are imported. Bed, ICU and ambulance information stays 'not verified' until you verify it.")) return;
  el("osmBtn").disabled = true;
  osmReport("Step 1: the server is contacting OpenStreetMap (can take up to a minute)...", false);
  let result = null, serverProblem = "";
  try {
    result = await api("/api/admin/osm/import", "POST", { radiusKm: 15 });
  } catch (error) {
    serverProblem = error.message;
  }
  if (!result) {
    osmReport("Step 1 failed (" + serverProblem + ")\nStep 2: trying again from your browser...", true);
    try {
      const elements = await downloadInBrowser(15);
      if (!elements.length) throw new Error("OpenStreetMap returned no hospitals for this area.");
      result = await api("/api/admin/osm/import-elements", "POST", { elements });
    } catch (error) {
      osmReport("Import failed.\nServer: " + serverProblem + "\nBrowser: " + error.message +
        "\n\nCheck your internet / VPN / firewall, wait a minute (the OpenStreetMap servers can be busy) and try again.", true);
      el("osmBtn").disabled = false;
      return;
    }
  }
  await loadHospitals();
  osmReport(`Import done: ${result.found} hospitals found - ${result.added} new, ${result.updated} refreshed, ${result.keptVerified} existing records retained, ${result.skippedUnnamed} skipped (no name). ` +
    "The website directory will show active hospital records.", false);
  el("osmBtn").disabled = false;
});
el("dialogCancel").addEventListener("click", () => el("hospitalDialog").close());
el("dialogSave").addEventListener("click", saveHospital);
el("addDoctorBtn").addEventListener("click", () => openDoctorDialog());
el("dHospitalId").addEventListener("change", event => {
  const hospital = hospitals.find(item => item.id === Number(event.target.value));
  if (!hospital) return;
  el("dHospital").value = hospital.name;
  el("dAddress").value = hospital.address;
});
el("doctorDialogSave").addEventListener("click", saveDoctor);
el("doctorDialogCancel").addEventListener("click", () => el("doctorDialog").close());
el("pwBtn").addEventListener("click", () => { el("pwError").textContent = ""; el("pwDialog").showModal(); });
el("pwCancel").addEventListener("click", () => el("pwDialog").close());
el("pwSave").addEventListener("click", savePassword);

/* ---------- Start ---------- */
buildFormParts();
startDashboard().catch(error => {
  showServerError(error.message);
  showLogin();
});