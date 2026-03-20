// Screen management + onboarding + main UI logic

const Screen = {
  LOADING: "screen-loading",
  PHONE: "screen-phone",
  CODE: "screen-code",
  MAIN: "screen-main",
};

let currentPhone = null;
let currentDayKey = null;
let currentLocation = null; // { lat, lng }
let mapReady = false;

// Day messages
const DAY_MESSAGES = {
  monday: "It's Monday again… might as well make it a beer night.",
  tuesday: "Two-for-Tuesday? Check the deals.",
  wednesday: "Hump Day – time for a beer.",
  thursday: "Thirsty Thursday – stretch those beer dollars.",
  friday: "TGI Friday – beer time.",
  saturday: "Saturday night – make it count.",
  sunday: "Sunday Funday – one more round.",
};

const DAY_ORDER = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];

function $(id) {
  return document.getElementById(id);
}

function showScreen(screenId) {
  Object.values(Screen).forEach((sid) => {
    const el = $(sid);
    if (!el) return;
    el.classList.toggle("hidden", sid !== screenId);
  });
}

function fillBeerGlass() {
  const fill = $("beer-fill");
  if (fill) {
    fill.style.height = "65%";
  }
}

function resetBeerGlass() {
  const fill = $("beer-fill");
  if (fill) {
    fill.style.height = "0%";
  }
}

function getCurrentDayKey() {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();

  // If it's after midnight but before 2:30am, treat as previous day
  if (hour < 2 || (hour === 2 && minute < 30)) {
    const prev = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    return DAY_ORDER[prev.getDay()];
  }

  return DAY_ORDER[now.getDay()];
}

function setDayMessage(dayKey) {
  const msg = DAY_MESSAGES[dayKey] || "";
  const el = $("day-message");
  if (el) el.textContent = msg;
}

function buildDaySelector() {
  const container = $("day-selector");
  if (!container) return;
  container.innerHTML = "";

  DAY_ORDER.forEach((dayKey) => {
    const label = dayKey.charAt(0).toUpperCase() + dayKey.slice(1);
    const pill = document.createElement("button");
    pill.className = "day-pill";
    pill.textContent = label;
    pill.dataset.dayKey = dayKey;
    pill.addEventListener("click", () => {
      setActiveDay(dayKey);
    });
    container.appendChild(pill);
  });
}

function setActiveDay(dayKey) {
  currentDayKey = dayKey;
  setDayMessage(dayKey);

  const pills = document.querySelectorAll(".day-pill");
  pills.forEach((pill) => {
    pill.classList.toggle("active", pill.dataset.dayKey === dayKey);
  });

  loadBarsForCurrentState();
}

async function checkSession() {
  try {
    const res = await fetch("/api/session_status");
    const data = await res.json();
    if (data.verified) {
      currentPhone = data.phone;
      return true;
    }
  } catch (e) {
    console.error(e);
  }
  return false;
}

function showInitialFlow() {
  // First: show loading briefly
  showScreen(Screen.LOADING);
  resetBeerGlass();
  setTimeout(() => {
    fillBeerGlass();
  }, 50);

  setTimeout(async () => {
    const verified = await checkSession();
    if (verified) {
      // Already verified: go straight to main
      goToMainWithLoading();
    } else {
      // Not verified: go to phone screen
      showScreen(Screen.PHONE);
    }
  }, 900);
}

function goToMainWithLoading() {
  showScreen(Screen.LOADING);
  resetBeerGlass();
  setTimeout(() => {
    fillBeerGlass();
  }, 50);

  setTimeout(() => {
    showScreen(Screen.MAIN);
    initMainScreen();
  }, 900);
}

// --- Auth actions ---

async function sendCode() {
  const phoneInput = $("phone-input");
  const errorEl = $("phone-error");
  if (!phoneInput) return;

  const phone = phoneInput.value.trim();
  if (!phone) {
    errorEl.textContent = "Please enter your phone number.";
    return;
  }
  errorEl.textContent = "";

  try {
    const res = await fetch("/api/send_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone }),
    });
    const data = await res.json();
    if (!data.success) {
      errorEl.textContent = data.error || "Could not send code.";
      return;
    }
    currentPhone = phone;
    showScreen(Screen.CODE);
  } catch (e) {
    console.error(e);
    errorEl.textContent = "Network error. Try again.";
  }
}

async function verifyCode() {
  const codeInput = $("code-input");
  const errorEl = $("code-error");
  if (!codeInput) return;

  const code = codeInput.value.trim();
  if (!code || code.length !== 4) {
    errorEl.textContent = "Enter the 4-digit code.";
    return;
  }
  if (!currentPhone) {
    errorEl.textContent = "Missing phone. Go back and enter your phone.";
    return;
  }
  errorEl.textContent = "";

  try {
    const res = await fetch("/api/verify_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: currentPhone, code }),
    });
    const data = await res.json();
    if (!data.success) {
      errorEl.textContent = data.error || "Invalid code.";
      return;
    }
    // Verified: show loading then main
    goToMainWithLoading();
  } catch (e) {
    console.error(e);
    errorEl.textContent = "Network error. Try again.";
  }
}

async function resendCode() {
  if (!currentPhone) {
    const errorEl = $("code-error");
    errorEl.textContent = "Missing phone. Go back and enter your phone.";
    return;
  }
  try {
    await fetch("/api/send_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: currentPhone }),
    });
  } catch (e) {
    console.error(e);
  }
}

// --- Main screen logic ---

function initMainScreen() {
  buildDaySelector();
  const todayKey = getCurrentDayKey();
  setActiveDay(todayKey);

  const useLocationBtn = $("use-location-btn");
  if (useLocationBtn) {
    useLocationBtn.addEventListener("click", () => {
      requestCurrentLocation();
    });
  }

  const locationInput = $("location-input");
  if (locationInput) {
    locationInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        geocodeLocationInput();
      }
    });
  }

  const searchInput = $("search-input");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      filterBarListBySearch(searchInput.value.trim());
    });
  }

  const addSpecialBtn = $("add-special-btn");
  if (addSpecialBtn) {
    addSpecialBtn.addEventListener("click", () => {
      openAddBarFlowManual();
    });
  }

  // If map is already ready, load bars now
  if (mapReady) {
    loadBarsForCurrentState();
  }
}

function filterBarListBySearch(query) {
  const cards = document.querySelectorAll(".bar-card");
  const q = query.toLowerCase();
  cards.forEach((card) => {
    const name = card.dataset.name || "";
    const deal = card.dataset.deal || "";
    const combined = (name + " " + deal).toLowerCase();
    card.style.display = combined.includes(q) ? "" : "none";
  });
}

function requestCurrentLocation() {
  if (!navigator.geolocation) {
    alert("Location not supported on this device.");
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      currentLocation = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
      };
      if (typeof setMapCenter === "function") {
        setMapCenter(currentLocation.lat, currentLocation.lng);
      }
      loadBarsForCurrentState();
    },
    (err) => {
      console.error(err);
      alert("Could not get your location.");
    }
  );
}

function geocodeLocationInput() {
  const input = $("location-input");
  if (!input || !input.value.trim()) return;

  if (!window.google || !google.maps || !google.maps.Geocoder) {
    alert("Maps not ready yet.");
    return;
  }

  const geocoder = new google.maps.Geocoder();
  geocoder.geocode({ address: input.value.trim() }, (results, status) => {
    if (status === "OK" && results[0]) {
      const loc = results[0].geometry.location;
      currentLocation = { lat: loc.lat(), lng: loc.lng() };
      if (typeof setMapCenter === "function") {
        setMapCenter(currentLocation.lat, currentLocation.lng);
      }
      loadBarsForCurrentState();
    } else {
      alert("Could not find that location.");
    }
  });
}

async function loadBarsForCurrentState() {
  if (!currentDayKey) return;

  const params = new URLSearchParams();
  params.set("day", currentDayKey);
  if (currentLocation) {
    params.set("lat", currentLocation.lat);
    params.set("lng", currentLocation.lng);
    params.set("radius", 45);
  }

  try {
    const res = await fetch(`/api/bars?${params.toString()}`);
    const data = await res.json();
    if (!data.success) return;
    renderBarList(data.bars);
    if (typeof updateMapMarkers === "function") {
      updateMapMarkers(data.bars);
    }
  } catch (e) {
    console.error(e);
  }
}

function renderBarList(bars) {
  const list = $("bar-list");
  if (!list) return;
  list.innerHTML = "";

  bars.forEach((bar) => {
    const card = document.createElement("div");
    card.className = "bar-card";
    card.dataset.id = bar.id;
    card.dataset.name = bar.name;
    card.dataset.deal = bar.deal;

    const nameEl = document.createElement("div");
    nameEl.className = "bar-name";
    nameEl.textContent = bar.name;

    const dealEl = document.createElement("div");
    dealEl.className = "bar-deal";
    dealEl.textContent = bar.deal;

    const metaEl = document.createElement("div");
    metaEl.className = "bar-meta";
    const distanceText = bar.distance != null ? `${bar.distance.toFixed(1)} mi` : "";
    const cityState = [bar.city, bar.state].filter(Boolean).join(", ");
    metaEl.textContent = [distanceText, cityState].filter(Boolean).join(" • ");

    card.appendChild(nameEl);
    card.appendChild(dealEl);
    card.appendChild(metaEl);

    card.addEventListener("click", () => {
      highlightBarCard(bar.id);
      if (typeof focusMarkerOnBar === "function") {
        focusMarkerOnBar(bar.id);
      }
    });

    list.appendChild(card);
  });
}

function highlightBarCard(barId) {
  const cards = document.querySelectorAll(".bar-card");
  cards.forEach((card) => {
    card.classList.toggle("active", card.dataset.id == barId);
  });
}

// --- Add bar flows ---

function openAddBarFlowManual() {
  const name = prompt("Bar name:");
  if (!name) return;
  const address = prompt("Bar address:");
  if (!address) return;
  const deal = prompt("Deal (e.g., $2 drafts):");
  if (!deal) return;
  const day = prompt("Day of week (e.g., Thursday):", currentDayKey || "thursday");
  if (!day) return;

  if (!window.google || !google.maps || !google.maps.Geocoder) {
    alert("Maps not ready yet for geocoding.");
    return;
  }

  const geocoder = new google.maps.Geocoder();
  geocoder.geocode({ address }, async (results, status) => {
    if (status === "OK" && results[0]) {
      const loc = results[0].geometry.location;
      const components = results[0].address_components || [];
      let city = "";
      let state = "";
      let zip = "";

      components.forEach((c) => {
        if (c.types.includes("locality")) city = c.long_name;
        if (c.types.includes("administrative_area_level_1")) state = c.short_name;
        if (c.types.includes("postal_code")) zip = c.long_name;
      });

      await submitBar({
        name,
        address: results[0].formatted_address,
        deal,
        day_of_week: day,
        lat: loc.lat(),
        lng: loc.lng(),
        city,
        state,
        zip_code: zip,
      });
    } else {
      alert("Could not geocode that address.");
    }
  });
}

async function submitBar(payload) {
  try {
    const res = await fetch("/api/bars", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!data.success) {
      alert(data.error || "Could not add bar.");
      return;
    }
    // Reload bars
    loadBarsForCurrentState();
  } catch (e) {
    console.error(e);
    alert("Network error adding bar.");
  }
}

// Called from map.js when user long-presses map
async function addBarFromMap(lat, lng) {
  const name = prompt("Bar name:");
  if (!name) return;
  const deal = prompt("Deal (e.g., $2 drafts):");
  if (!deal) return;
  const day = prompt("Day of week (e.g., Thursday):", currentDayKey || "thursday");
  if (!day) return;

  let address = "";
  let city = "";
  let state = "";
  let zip = "";

  if (window.google && google.maps && google.maps.Geocoder) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: { lat, lng } }, async (results, status) => {
      if (status === "OK" && results[0]) {
        address = results[0].formatted_address;
        const components = results[0].address_components || [];
        components.forEach((c) => {
          if (c.types.includes("locality")) city = c.long_name;
          if (c.types.includes("administrative_area_level_1")) state = c.short_name;
          if (c.types.includes("postal_code")) zip = c.long_name;
        });
      }
      await submitBar({
        name,
        address: address || "Unknown address",
        deal,
        day_of_week: day,
        lat,
        lng,
        city,
        state,
        zip_code: zip,
      });
    });
  } else {
    await submitBar({
      name,
      address: "Unknown address",
      deal,
      day_of_week: day,
      lat,
      lng,
      city,
      state,
      zip_code: zip,
    });
  }
}

// --- Init ---

document.addEventListener("DOMContentLoaded", () => {
  const sendCodeBtn = $("send-code-btn");
  if (sendCodeBtn) sendCodeBtn.addEventListener("click", sendCode);

  const verifyCodeBtn = $("verify-code-btn");
  if (verifyCodeBtn) verifyCodeBtn.addEventListener("click", verifyCode);

  const resendCodeBtn = $("resend-code-btn");
  if (resendCodeBtn) resendCodeBtn.addEventListener("click", resendCode);

  showInitialFlow();
});

// Called from map.js when map is ready
function onMapReady() {
  mapReady = true;
  if (document.getElementById(Screen.MAIN) && !document.getElementById(Screen.MAIN).classList.contains("hidden")) {
    loadBarsForCurrentState();
  }
        }
