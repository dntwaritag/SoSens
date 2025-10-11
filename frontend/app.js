/* app.js — dynamic form builder, responsive behavior, robust fetch + UI state */
const API_BASE = "http://localhost:8000"; // adjust if different
const FEATURE_ENDPOINT = `${API_BASE}/feature-names`; // try to fetch; server may not have this
const FALLBACK_FEATURES = [
  "Ph","K","P","N","Zn","S","QV2M-W","QV2M-Sp","QV2M-Su",
  "QV2M-Au","T2M_MIN-W","T2M_MIN-Sp","WD10M","PRECTOTCORR-W"
];

const fieldsContainer = document.getElementById("fields");
const form = document.getElementById("inputForm");
const resultDiv = document.getElementById("result");
const submitBtn = document.getElementById("predictBtn");
const statusEl = document.getElementById("status");

let featureNames = [];

// Utility: show a short toast/inline status
function setStatus(msg, isError=false){
  statusEl.textContent = msg;
  statusEl.style.color = isError ? "var(--danger)" : "var(--muted)";
}

// Build the form given feature names (array of strings)
function buildFormUI(features){
  featureNames = features;
  fieldsContainer.innerHTML = "";
  features.forEach(f => {
    const id = "f_" + f.replace(/[^a-zA-Z0-9]/g,"_");
    const wrapper = document.createElement("div");
    wrapper.className = "field";
    wrapper.innerHTML = `
      <label for="${id}">${f}</label>
      <input inputmode="decimal" step="any" type="number" id="${id}" name="${f}" placeholder="enter ${f}" required />
    `;
    fieldsContainer.appendChild(wrapper);
  });
  // store last used values if available
  const last = JSON.parse(localStorage.getItem("last_inputs") || "{}");
  features.forEach(f => {
    const id = "f_" + f.replace(/[^a-zA-Z0-9]/g,"_");
    const el = document.getElementById(id);
    if (last[f] !== undefined) el.value = last[f];
  });
}

// Try to fetch feature names from server; fallback to hardcoded
async function loadFeatureNames(){
  try {
    const resp = await fetch(FEATURE_ENDPOINT, {method: "GET"});
    if (resp.ok) {
      const data = await resp.json();
      if (Array.isArray(data.feature_names) && data.feature_names.length){
        buildFormUI(data.feature_names);
        setStatus("Using feature names from server");
        return;
      }
    }
    throw new Error("No feature names from server");
  } catch (err){
    console.warn("Feature names fetch failed:", err);
    buildFormUI(FALLBACK_FEATURES);
    setStatus("Using fallback feature list (edit if needed)");
  }
}

// Called when user submits
async function handleSubmit(ev){
  ev.preventDefault();
  submitBtn.disabled = true;
  const spinner = document.createElement("span"); spinner.className = "spinner";
  submitBtn.appendChild(spinner);
  setStatus("Predicting...");
  // gather payload
  const payload = {};
  let valid = true;
  featureNames.forEach(f => {
    const id = "f_" + f.replace(/[^a-zA-Z0-9]/g,"_");
    const v = parseFloat(document.getElementById(id).value);
    if (Number.isNaN(v)) valid = false;
    payload[f] = v;
  });
  if (!valid){
    setStatus("Please fill numeric values for every field", true);
    submitBtn.disabled = false;
    spinner.remove();
    return;
  }
  // save last inputs
  localStorage.setItem("last_inputs", JSON.stringify(payload));

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    if (!res.ok){
      const text = await res.text();
      throw new Error(text || `HTTP ${res.status}`);
    }
    const data = await res.json();
    renderResult(data);
    setStatus("Prediction returned");
  } catch (err){
    console.error("Prediction error:", err);
    setStatus("Error calling API: " + (err.message||err), true);
    resultDiv.style.display = "none";
  } finally {
    submitBtn.disabled = false;
    spinner.remove();
  }
}

// Render the API response
function renderResult(data){
  resultDiv.style.display = "block";
  const top3 = data.top3 || [];
  const topList = top3.map(t => `<li>${t.label} — ${(t.prob*100).toFixed(1)}%</li>`).join("");
  resultDiv.innerHTML = `
    <h3>Prediction</h3>
    <p><strong>${data.predicted_label}</strong></p>
    <p class="small">Confidence: ${data.confidence ? (data.confidence*100).toFixed(1)+"%" : "N/A"}</p>
    ${top3.length ? `<div class="small"><strong>Top 3:</strong><ul class="toplist">${topList}</ul></div>` : ""}
    <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
      <button id="copyBtn" class="btn secondary">Copy SMS</button>
      <button id="openMaps" class="btn">Save & Share</button>
    </div>
  `;
  // wire copy button
  document.getElementById("copyBtn").addEventListener("click", () => {
    const sms = `${data.predicted_label} recommended (confidence ${(data.confidence*100).toFixed(0)}%).`;
    navigator.clipboard.writeText(sms).then(()=> alert("Copied SMS text"));
  });
  // example Save & Share: store result to localStorage and open share if available
  document.getElementById("openMaps").addEventListener("click", () => {
    const history = JSON.parse(localStorage.getItem("pred_history") || "[]");
    history.unshift({ts:Date.now(), result: data});
    localStorage.setItem("pred_history", JSON.stringify(history.slice(0,50)));
    alert("Saved to local history");
  });
}

// bootstrap
document.addEventListener("DOMContentLoaded", () => {
  loadFeatureNames();
  form.addEventListener("submit", handleSubmit);
});
