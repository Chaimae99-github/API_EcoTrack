// app/frontend/app.js

let accessToken = null;
let statsChart = null;

const apiBaseUrl = "http://127.0.0.1:8000"; // même domaine que l'API

// Récupère le token depuis localStorage (si déjà connecté)
window.addEventListener("DOMContentLoaded", () => {
  const savedToken = localStorage.getItem("ecotrack_token");
  if (savedToken) {
    accessToken = savedToken;
    setLoginStatus("Connecté (token déjà présent)", true);
  }

  // Attacher les handlers
  document
    .getElementById("login-form")
    .addEventListener("submit", handleLogin);
  document
    .getElementById("logout-btn")
    .addEventListener("click", handleLogout);

  document
    .getElementById("load-zones-btn")
    .addEventListener("click", loadZones);
  document
    .getElementById("load-sources-btn")
    .addEventListener("click", loadSources);
  document
    .getElementById("load-indicators-btn")
    .addEventListener("click", () => loadIndicators(0, 10));

  document
    .getElementById("stats-form")
    .addEventListener("submit", handleStatsSubmit);


 document
    .getElementById("create-indicator-form")
    .addEventListener("submit", handleCreateIndicator);
});

// Helpers UI
function setLoginStatus(message, ok = true) {
  const statusEl = document.getElementById("login-status");
  statusEl.textContent = message;
  statusEl.className = "status " + (ok ? "ok" : "error");
}

function setBasicStatus(message, ok = true) {
  const statusEl = document.getElementById("basic-status");
  statusEl.textContent = message;
  statusEl.className = "status " + (ok ? "ok" : "error");
}

function setStatsStatus(message, ok = true) {
  const statusEl = document.getElementById("stats-status");
  statusEl.textContent = message;
  statusEl.className = "status " + (ok ? "ok" : "error");
}

// Retourne l'en-tête Authorization si token présent
function getAuthHeaders() {
  if (!accessToken) return {};
  return {
    Authorization: "Bearer " + accessToken,
  };
}

// --- LOGIN / LOGOUT ---

async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  // OAuth2PasswordRequestForm -> username/password
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  try {
    const resp = await fetch(`${apiBaseUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    if (!resp.ok) {
      const errData = await resp.json();
      setLoginStatus(
        "Erreur de connexion : " + (errData.detail || resp.status),
        false
      );
      return;
    }

    const data = await resp.json();
    accessToken = data.access_token;
    localStorage.setItem("ecotrack_token", accessToken);
    setLoginStatus("Connecté avec succès", true);
  } catch (error) {
    console.error(error);
    setLoginStatus("Erreur réseau lors du login", false);
  }
}

function handleLogout() {
  accessToken = null;
  localStorage.removeItem("ecotrack_token");
  setLoginStatus("Déconnecté", false);
}

// --- ZONES ---

async function loadZones() {
  if (!accessToken) {
    setBasicStatus("Veuillez vous connecter d'abord.", false);
    return;
  }

  try {
    const resp = await fetch(`${apiBaseUrl}/zones/`, {
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!resp.ok) {
      setBasicStatus("Erreur lors du chargement des zones", false);
      return;
    }

    const zones = await resp.json();
    const listEl = document.getElementById("zones-list");
    listEl.innerHTML = "";
    zones.forEach((z) => {
      const li = document.createElement("li");
      li.textContent = `#${z.id} - ${z.name} (${z.postal_code || "-"})`;
      listEl.appendChild(li);
    });

    setBasicStatus(`Zones chargées (${zones.length})`, true);
  } catch (error) {
    console.error(error);
    setBasicStatus("Erreur réseau lors du chargement des zones", false);
  }
}

// --- SOURCES ---

async function loadSources() {
  if (!accessToken) {
    setBasicStatus("Veuillez vous connecter d'abord.", false);
    return;
  }

  try {
    const resp = await fetch(`${apiBaseUrl}/sources/`, {
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!resp.ok) {
      setBasicStatus("Erreur lors du chargement des sources", false);
      return;
    }

    const sources = await resp.json();
    const listEl = document.getElementById("sources-list");
    listEl.innerHTML = "";
    sources.forEach((s) => {
      const li = document.createElement("li");
      li.textContent = `#${s.id} - ${s.name} (${s.type || "?"})`;
      listEl.appendChild(li);
    });

    setBasicStatus(`Sources chargées (${sources.length})`, true);
  } catch (error) {
    console.error(error);
    setBasicStatus("Erreur réseau lors du chargement des sources", false);
  }
}

// --- INDICATORS ---

async function loadIndicators(skip = 0, limit = 10) {
  if (!accessToken) {
    setBasicStatus("Veuillez vous connecter d'abord.", false);
    return;
  }

  try {
    const url = `${apiBaseUrl}/indicators/?skip=${skip}&limit=${limit}`;
    const resp = await fetch(url, {
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!resp.ok) {
      setBasicStatus("Erreur lors du chargement des indicateurs", false);
      return;
    }

    const indicators = await resp.json();
    const tbody = document.getElementById("indicators-table-body");
    tbody.innerHTML = "";

    indicators.forEach((ind) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${ind.id}</td>
        <td>${ind.type}</td>
        <td>${ind.value}</td>
        <td>${ind.unit}</td>
        <td>${ind.zone_id}</td>
        <td>${ind.source_id}</td>
        <td>${ind.timestamp}</td>
      `;
      tbody.appendChild(tr);
    });

    setBasicStatus(`Indicateurs chargés (${indicators.length})`, true);
  } catch (error) {
    console.error(error);
    setBasicStatus("Erreur réseau lors du chargement des indicateurs", false);
  }
}

// --- STATS / TIMESERIES ---

async function handleStatsSubmit(event) {
  event.preventDefault();

  if (!accessToken) {
    setStatsStatus("Veuillez vous connecter d'abord.", false);
    return;
  }

  const indicatorType = document.getElementById("stat-indicator-type").value;
  const groupBy = document.getElementById("stat-group-by").value;
  const zoneIdStr = document.getElementById("stat-zone-id").value;
  const fromDateStr = document.getElementById("stat-from-date").value;
  const toDateStr = document.getElementById("stat-to-date").value;

  const params = new URLSearchParams();
  params.append("indicator_type", indicatorType);
  params.append("group_by", groupBy);

  if (zoneIdStr) {
    params.append("zone_id", zoneIdStr);
  }
  if (fromDateStr) {
    // datetime-local => "2025-11-21T10:00"
    params.append("from_date", new Date(fromDateStr).toISOString());
  }
  if (toDateStr) {
    params.append("to_date", new Date(toDateStr).toISOString());
  }

  try {
    const resp = await fetch(`${apiBaseUrl}/stats/timeseries?` + params.toString(), {
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      setStatsStatus(
        "Erreur stats: " + (errData.detail || resp.status),
        false
      );
      return;
    }

    const data = await resp.json();
    updateChart(data.labels, data.series[0].data, data.series[0].name);
    setStatsStatus("Série chargée", true);
  } catch (error) {
    console.error(error);
    setStatsStatus("Erreur réseau lors de la récupération des stats", false);
  }
}

function updateChart(labels, values, labelName) {
  const ctx = document.getElementById("stats-chart").getContext("2d");

  if (statsChart) {
    statsChart.destroy();
  }

  statsChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: labelName,
          data: values,
          fill: false,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 0,
          },
        },
        y: {
          beginAtZero: false,
        },
      },
    },
  });
}


// --- CREATION D'INDICATOR ---

function setCreateIndicatorStatus(message, ok = true) {
  const el = document.getElementById("create-indicator-status");
  el.textContent = message;
  el.className = "status " + (ok ? "ok" : "error");
}

async function handleCreateIndicator(event) {
  event.preventDefault();

  if (!accessToken) {
    setCreateIndicatorStatus("Veuillez vous connecter d'abord.", false);
    return;
  }

  const type = document.getElementById("ci-type").value;
  const value = parseFloat(document.getElementById("ci-value").value);
  const unit = document.getElementById("ci-unit").value;
  const zoneId = parseInt(document.getElementById("ci-zone-id").value, 10);
  const sourceId = parseInt(document.getElementById("ci-source-id").value, 10);
  const tsStr = document.getElementById("ci-timestamp").value;
  const extraStr = document.getElementById("ci-extra").value;

  let timestamp;
  try {
    timestamp = new Date(tsStr).toISOString();
  } catch {
    setCreateIndicatorStatus("Timestamp invalide.", false);
    return;
  }

  let extraData = null;
  if (extraStr.trim() !== "") {
    try {
      extraData = JSON.parse(extraStr);
    } catch (e) {
      setCreateIndicatorStatus("Extra data doit être un JSON valide.", false);
      return;
    }
  }

  const payload = {
    type,
    value,
    unit,
    timestamp,
    zone_id: zoneId,
    source_id: sourceId,
    extra_data: extraData,
  };

  try {
    const resp = await fetch(`${apiBaseUrl}/indicators/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      setCreateIndicatorStatus(
        "Erreur API: " + (errData.detail || resp.status),
        false
      );
      return;
    }

    const created = await resp.json();
    setCreateIndicatorStatus(
      `Indicateur créé (id=${created.id})`,
      true
    );

    // Rafraîchir la liste des indicateurs
    loadIndicators(0, 10);
  } catch (error) {
    console.error(error);
    setCreateIndicatorStatus(
      "Erreur réseau lors de la création de l'indicateur",
      false
    );
  }
}
