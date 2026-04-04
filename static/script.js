// -----------------------------
// Beer Dollars Frontend Script
// -----------------------------

let userLocation = null;
let geocoder;
let map;
let bars = [];
let selectedDay = null;

// -----------------------------
// 1. Initialize Google Map
// -----------------------------
function initMap() {
    geocoder = new google.maps.Geocoder();

    // Default map center (Youngstown)
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: { lat: 41.099, lng: -80.649 },
    });

    // Ask for user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(userLocation);
                if (selectedDay) fetchBars(selectedDay);
            },
            () => console.log("User denied location")
        );
    }
}

// -----------------------------
// 2. Splash Page Login Handling
// -----------------------------
const splashEnterBtn = document.getElementById("enter-btn");
const splashError = document.getElementById("splash-error");

splashEnterBtn.addEventListener("click", async () => {
    const phoneInput = document.getElementById("phone").value.trim();
    const codeInput = document.getElementById("code").value.trim();

    if (!phoneInput || !codeInput) {
        splashError.textContent = "Enter phone and code!";
        return;
    }

    try {
        // Master admin code bypass
        if (codeInput === "1616") {
            sessionStorage.setItem("authorized", "true");
            showMainApp();
            return;
        }

        const res = await fetch("/api/verify-code", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone: phoneInput, code: codeInput })
        });
        const data = await res.json();

        if (res.ok) {
            sessionStorage.setItem("authorized", "true");
            showMainApp();
        } else {
            splashError.textContent = data.error || "Invalid code";
        }
    } catch (err) {
        splashError.textContent = "Error verifying code.";
        console.error(err);
    }
});

function showMainApp() {
    document.getElementById("splash-page").classList.add("hidden");
    document.getElementById("main-app").classList.remove("hidden");
    selectedDay = getSelectedDay();
    fetchBars(selectedDay);
}

// -----------------------------
// 3. Day Selector Handling
// -----------------------------
const dayButtons = document.querySelectorAll(".day-btn");
dayButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        selectedDay = btn.dataset.day;
        fetchBars(selectedDay);
    });
});

function getSelectedDay() {
    const today = new Date();
    return today.toLocaleString("en-US", { weekday: "long" });
}

// -----------------------------
// 4. Fetch Bars from Backend
// -----------------------------
async function fetchBars(day) {
    try {
        const res = await fetch(`/api/specials?day=${day}`);
        const data = await res.json();
        bars = data;

        // Sort bars by distance if user location exists, else by name
        if (userLocation) {
            bars.forEach(bar => {
                bar.distance = calculateDistance(userLocation.lat, userLocation.lng, bar.lat, bar.lng);
            });
            bars = bars
                .filter(bar => bar.distance <= 45)
                .sort((a, b) => a.distance - b.distance);
        } else {
            bars.sort((a, b) => a.name.localeCompare(b.name));
        }

        renderBars(bars);
    } catch (err) {
        console.error("Error fetching bars:", err);
    }
}

// -----------------------------
// 5. Render Bars to UI & Map
// -----------------------------
let markers = [];

function renderBars(barsList) {
    const listEl = document.getElementById("bar-list");
    listEl.innerHTML = "";

    // Clear previous map markers
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    barsList.forEach(bar => {
        const div = document.createElement("div");
        div.className = "bar-item";

        const checkmark = bar.verified ? `<span style="color: blue;">✓</span>` : '';
        const distText = bar.distance ? `<br><small>${bar.distance.toFixed(1)} miles away</small>` : '';

        div.innerHTML = `<strong>${bar.name} ${checkmark}</strong> - ${bar.special} <br><em>${bar.address}</em> ${distText}`;
        div.addEventListener("click", () => focusMarker(bar));
        listEl.appendChild(div);

        // Add marker to map
        const marker = new google.maps.Marker({
            position: { lat: bar.lat, lng: bar.lng },
            map: map,
            title: bar.name
        });
        markers.push(marker);
    });
}

function focusMarker(bar) {
    map.setCenter({ lat: bar.lat, lng: bar.lng });
    map.setZoom(15);
}

// -----------------------------
// 6. Add Bar Button
// -----------------------------
document.getElementById("add-bar-btn").addEventListener("click", () => {
    const name = prompt("Bar Name:");
    if (!name) return;

    const address = prompt("Address or City:");
    if (!address) return;

    const special = prompt("What's the special?");
    if (!special) return;

    const
