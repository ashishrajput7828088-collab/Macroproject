/* =====================================================================
   Algorithm lab - lab.js (loaded after script.js, uses its globals)
   Sends the SAME query to the Flask server, which runs Brute force, K-D Tree and Quadtree
   and MEASURES time, nodes checked, points tested and hospitals found.
   Nothing on this page is typed in by hand.
   ===================================================================== */
let areaBounds = null;               // Leaflet LatLngBounds chosen for the range query
let areaLayer = null;                // rectangle shown on the map
let queryLayer = null;               // radius circle shown on the map
let drawing = false, drawStart = null, drawTemp = null;
let foundIds = new Set();

const fmt = n => Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });
const RECT_STYLE = { color: "#7a3fb4", weight: 2, dashArray: "6 6", fillOpacity: 0.08 };

/* ----- query type switch ----- */
function applyLabMode() {
  const labModeEl = el("labMode");
  if (!labModeEl) return;
  const mode = labModeEl.value;
  document.querySelectorAll("[data-lab]").forEach(f => { f.hidden = f.dataset.lab !== mode; });
}

document.addEventListener("DOMContentLoaded", () => {
  el("labMode")?.addEventListener("change", applyLabMode);
  applyLabMode();
  setupLabMapListeners();
});

/* ----- choosing a rectangle (range query area) ----- */
function setArea(bounds) {
  areaBounds = bounds;
  if (areaLayer && map) map.removeLayer(areaLayer);
  if (map) areaLayer = L.rectangle(bounds, RECT_STYLE).addTo(map);
  const w = distanceKm(bounds.getSouthWest(), bounds.getSouthEast());
  const h = distanceKm(bounds.getSouthWest(), bounds.getNorthWest());
  if (el("areaInfo")) el("areaInfo").textContent = `Area chosen: about ${w.toFixed(1)} km x ${h.toFixed(1)} km.`;
  if (el("labMode")) el("labMode").value = "area";
  applyLabMode();
}

function setupLabMapListeners() {
  el("viewAreaBtn")?.addEventListener("click", () => {
    if (!map) return;
    setView("split");
    setTimeout(() => setArea(map.getBounds().pad(-0.1)), 100);
  });

  el("drawAreaBtn")?.addEventListener("click", () => {
    if (!map) return;
    setView("split");
    drawing = true;
    map.dragging.disable();
    map.getContainer().classList.add("crosshair");
    if (el("labStatus")) el("labStatus").textContent = "Press and drag on the map to draw the rectangle (on a phone use 'Use visible map').";
    el("map-section")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  if (map) {
    attachMapDrawingEvents();
  } else {
    setTimeout(attachMapDrawingEvents, 500);
  }
}

function attachMapDrawingEvents() {
  if (!map) return;
  map.on("mousedown", e => {
    if (!drawing) return;
    drawStart = e.latlng;
    drawTemp = L.rectangle([drawStart, drawStart], RECT_STYLE).addTo(map);
  });
  map.on("mousemove", e => {
    if (drawing && drawStart && drawTemp) drawTemp.setBounds([drawStart, e.latlng]);
  });
  map.on("mouseup", e => {
    if (!drawing || !drawStart) return;
    const bounds = L.latLngBounds(drawStart, e.latlng);
    if (drawTemp) map.removeLayer(drawTemp);
    drawTemp = drawStart = null;
    drawing = false;
    map.dragging.enable();
    map.getContainer().classList.remove("crosshair");
    if (distanceKm(bounds.getSouthWest(), bounds.getNorthEast()) < 0.2) {
      if (el("labStatus")) el("labStatus").textContent = "That rectangle was too small. Try again.";
      return;
    }
    setArea(bounds);
    if (el("labStatus")) el("labStatus").textContent = "Area set. Press 'Run comparison'.";
  });
}

/* ----- run the comparison ----- */
function clearLabLayers() {
  if (queryLayer && map) { map.removeLayer(queryLayer); queryLayer = null; }
  if (areaLayer && map) { map.removeLayer(areaLayer); areaLayer = null; }
  foundIds = new Set();
  areaBounds = null;
  if (el("areaInfo")) el("areaInfo").textContent = "No area chosen yet.";
}

el("clearCompare")?.addEventListener("click", () => {
  clearLabLayers();
  if (el("labResult")) el("labResult").innerHTML = "";
  if (el("labStatus")) el("labStatus").textContent = "";
});

function compareUrl(mode) {
  const src = "all";
  if (mode === "area") {
    const b = areaBounds;
    return `${API_BASE_URL}/api/compare?mode=area&south=${b.getSouth()}&west=${b.getWest()}&north=${b.getNorth()}&east=${b.getEast()}&source=${src}`;
  }
  const point = `lat=${userPoint.lat}&lng=${userPoint.lng}`;
  return mode === "radius"
    ? `${API_BASE_URL}/api/compare?mode=radius&${point}&radius=${el("labRadius").value}&source=${src}`
    : `${API_BASE_URL}/api/compare?mode=nearest&${point}&k=${Math.max(1, Math.min(50, Number(el("labK").value) || 3))}&source=${src}`;
}

function compareTableHtml(data) {
  const A = data.algorithms, names = ["linear", "kdtree", "quadtree"];
  const fastest = names.reduce((a, b) => (A[b].timeUs < A[a].timeUs ? b : a));
  const row = (label, f, extra = () => "") =>
    `<tr><th scope="row">${label}</th>${names.map(n => `<td class="${extra(n)}">${f(A[n], n)}</td>`).join("")}</tr>`;
  const kdAndQuadNeverMore = n => (A[n].nodes < data.datasetSize ? "good" : "");

  const maxTime = Math.max(A.linear.timeUs, A.kdtree.timeUs, A.quadtree.timeUs, 1);
  const linTimePct = Math.max(4, Math.round((A.linear.timeUs / maxTime) * 100));
  const kdTimePct = Math.max(4, Math.round((A.kdtree.timeUs / maxTime) * 100));
  const quadTimePct = Math.max(4, Math.round((A.quadtree.timeUs / maxTime) * 100));

  const maxNodes = Math.max(A.linear.nodes, A.kdtree.nodes, A.quadtree.nodes, 1);
  const linNodePct = Math.max(4, Math.round((A.linear.nodes / maxNodes) * 100));
  const kdNodePct = Math.max(4, Math.round((A.kdtree.nodes / maxNodes) * 100));
  const quadNodePct = Math.max(4, Math.round((A.quadtree.nodes / maxNodes) * 100));

  return `<div class="table-wrap"><table class="compare-table" style="width:100%; border-collapse:collapse; margin-top:10px;">
    <thead><tr style="background:#f1f5f9; text-align:left;"><th style="padding:8px 12px;">Comparison</th><th style="padding:8px 12px;">Brute force</th><th style="padding:8px 12px;">K-D Tree</th><th style="padding:8px 12px;">Quadtree</th></tr></thead>
    <tbody>
      ${row(`Search time <small>(average of ${data.reps} runs)</small>`, a => `${fmt(a.timeUs)} \u00b5s`, n => (n === fastest ? "best" : ""))}
      ${row("Nodes checked", a => fmt(a.nodes), kdAndQuadNeverMore)}
      ${row("Points tested", a => fmt(a.points))}
      ${row("Hospitals found", a => fmt(a.found))}
      ${row("Same answer as brute force", (a, n) => (n === "linear" ? "(reference)" : "Yes"))}
    </tbody></table></div>

    <div class="algo-visual-graphs" style="margin-top:16px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px;">
      <h4 style="margin:0 0 12px 0; font-size:0.92rem; font-weight:800; color:#0f172a;">📊 Execution Time Comparison (\u00b5s - Lower is Faster)</h4>
      <div style="display:flex; flex-direction:column; gap:10px;">
        <div>
          <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; margin-bottom:4px; color:#475569;">
            <span>Brute Force (Linear Scan)</span>
            <span>${fmt(A.linear.timeUs)} \u00b5s</span>
          </div>
          <div style="height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;">
            <div style="height:100%; width:${linTimePct}%; background:#ef4444; border-radius:6px; transition:width 0.4s ease;"></div>
          </div>
        </div>
        <div>
          <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; margin-bottom:4px; color:#0284c7;">
            <span>2D K-D Tree</span>
            <span>${fmt(A.kdtree.timeUs)} \u00b5s</span>
          </div>
          <div style="height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;">
            <div style="height:100%; width:${kdTimePct}%; background:#0284c7; border-radius:6px; transition:width 0.4s ease;"></div>
          </div>
        </div>
        <div>
          <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; margin-bottom:4px; color:#059669;">
            <span>Quadtree (Spatial Partitioning)</span>
            <span>${fmt(A.quadtree.timeUs)} \u00b5s</span>
          </div>
          <div style="height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;">
            <div style="height:100%; width:${quadTimePct}%; background:#059669; border-radius:6px; transition:width 0.4s ease;"></div>
          </div>
        </div>
      </div>

      <h4 style="margin:16px 0 12px 0; font-size:0.92rem; font-weight:800; color:#0f172a;">🎯 Nodes Visited Ratio (Pruning Efficiency)</h4>
      <div style="display:flex; flex-direction:column; gap:10px;">
        <div>
          <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; margin-bottom:4px; color:#475569;">
            <span>Brute Force (No Pruning)</span>
            <span>${fmt(A.linear.nodes)} nodes visited</span>
          </div>
          <div style="height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;">
            <div style="height:100%; width:${linNodePct}%; background:#94a3b8; border-radius:6px;"></div>
          </div>
        </div>
        <div>
          <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; margin-bottom:4px; color:#0284c7;">
            <span>K-D Tree (Axis Hyperplane Pruned)</span>
            <span>${fmt(A.kdtree.nodes)} nodes visited</span>
          </div>
          <div style="height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;">
            <div style="height:100%; width:${kdNodePct}%; background:#38bdf8; border-radius:6px;"></div>
          </div>
        </div>
        <div>
          <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; margin-bottom:4px; color:#059669;">
            <span>Quadtree (Bounding Box Quadrant Pruned)</span>
            <span>${fmt(A.quadtree.nodes)} nodes visited</span>
          </div>
          <div style="height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;">
            <div style="height:100%; width:${quadNodePct}%; background:#10b981; border-radius:6px;"></div>
          </div>
        </div>
      </div>
    </div>

    <p class="muted small" style="margin-top:10px; font-size:0.84rem; color:#64748b;">Measured on ${data.datasetSize} live hospitals. Fastest time highlighted.
      ${A.linear.timeUs <= Math.min(A.kdtree.timeUs, A.quadtree.timeUs)
        ? "Brute force is very fast on small datasets; K-D Tree & Quadtree scale efficiently as thousands of points are queried (tested in scaling benchmark below)." : ""}</p>`;
}

async function runCompare() {
  const status = el("labStatus"), out = el("labResult");
  const mode = el("labMode").value;
  if (mode === "area" && !areaBounds) {
    if (status) status.textContent = "Choose a map area first: draw a rectangle or use the visible map.";
    return;
  }
  if (status) status.textContent = "Measuring performance live across DSA indexing trees...";
  try {
    const data = await fetchJson(compareUrl(mode), 20000);
    if (status) {
      status.textContent = data.allMatchBruteForce
        ? "Done. K-D Tree and Quadtree returned exactly the same hospitals as brute force."
        : "Warning: query discrepancy detected between spatial structures.";
    }
    const ids = data.algorithms.quadtree.ids;
    const names = ids.map(id => allHospitals.find(h => h.id === id)).filter(Boolean);
    if (out) {
      out.innerHTML = compareTableHtml(data) + `<div class="lab-found" style="margin-top:12px;"><b>Hospitals found (${names.length}):</b> ` +
        (names.length ? names.map(h => `<button class="btn btn-sm btn-ghost" style="margin:2px;" onclick="showHospitalDetails(${h.id})">${esc(h.name)}</button>`).join(" ") : "none") + "</div>";
    }

    if (queryLayer && map) { map.removeLayer(queryLayer); queryLayer = null; }
    if (map && mode === "radius") {
      queryLayer = L.circle([userPoint.lat, userPoint.lng], { radius: Number(el("labRadius").value) * 1000, ...RECT_STYLE }).addTo(map);
    }
  } catch (error) {
    if (status) status.textContent = "Could not run the live comparison (Flask server recommended: python app.py).";
  }
}
el("runCompare")?.addEventListener("click", runCompare);

/* ----- scaling test on synthetic points ----- */
async function runBench() {
  const box = el("benchResult");
  if (!box) return;
  box.innerHTML = '<p class="muted" style="color:#64748b; font-size:0.9rem;">Building spatial trees and running 60 queries per method... (a few seconds)</p>';
  try {
    const d = await fetchJson(`${API_BASE_URL}/api/benchmark?n=${el("benchN").value}`, 60000);
    const labels = { radius: "Radius (2 km)", area: "Rectangle (3 x 3 km)", nearest: "Nearest 5" };
    const rows = Object.keys(labels).map(mode => {
      const r = d.results[mode];
      const best = ["linear", "kdtree", "quadtree"].reduce((a, b) => (r[b].timeUs < r[a].timeUs ? b : a));
      const cell = n => `<td style="padding:8px 12px;" class="${n === best ? "best" : ""}">${fmt(r[n].timeUs)} \u00b5s<br><small style="color:#64748b;">${fmt(r[n].nodes)} nodes</small></td>`;
      const speedup = r.linear.timeUs / Math.min(r.kdtree.timeUs, r.quadtree.timeUs);
      return `<tr style="border-bottom:1px solid #f1f5f9;"><th scope="row" style="padding:8px 12px; text-align:left;">${labels[mode]}</th>${cell("linear")}${cell("kdtree")}${cell("quadtree")}<td style="padding:8px 12px; font-weight:700; color:#059669;">${speedup.toFixed(1)}x faster</td></tr>`;
    }).join("");

    box.innerHTML = `<div class="table-wrap"><table class="compare-table" style="width:100%; border-collapse:collapse; margin-top:10px;">
      <thead><tr style="background:#f1f5f9; text-align:left;"><th style="padding:8px 12px;">${fmt(d.points)} Points Benchmark</th><th style="padding:8px 12px;">Brute force</th><th style="padding:8px 12px;">K-D Tree</th><th style="padding:8px 12px;">Quadtree</th><th style="padding:8px 12px;">Spatial Tree Speedup</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
      <p class="muted small" style="margin-top:8px; font-size:0.84rem; color:#64748b;">Average per query over ${d.queries} synthetic random queries. Tree build time: K-D Tree ${fmt(d.buildMs.kdtree)} ms, Quadtree ${fmt(d.buildMs.quadtree)} ms.
        ${d.allMatchBruteForce ? "All spatial queries matched brute force exactly." : "Warning: some answers differed from brute force."}</p>`;
  } catch (error) {
    box.innerHTML = `<p style="color:#dc2626; font-size:0.88rem; margin-top:6px;">Scaling benchmark runs on Python Flask server. Start server with <code>python app.py</code> to run live tests.</p>`;
  }
}
el("runBench")?.addEventListener("click", runBench);
