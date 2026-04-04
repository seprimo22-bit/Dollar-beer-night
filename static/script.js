// ========================================
// Beer Dollars Unified Frontend Script
// Handles Splash Page + Main App + Maps
// ========================================

let userLocation = null;
let geocoder;
let map;
let bars = [];
let selectedDay = null;
let markers = [];

// -----------------------------
// 1. Initialize Google Map
// -----------------------------
function initMap() {
    geocoder = new google.maps.Geocoder();

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: { lat: 41.099, lng: -80.649 }, // Default Youngstown
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
// 2. Splash Page: Send Code / Verify Code
// -----------------------------
const sendBtn = document.getElementById("send-code-btn");
const verifyBtn = document.getElementById("verify-code-btn");
const errorMsg = document.getElementById("splash-error");

sendBtn?.addEventListener("click", async () => {
    const phone = document.getElementById("phone").value.trim();
    if (!phone) {
        showError("Enter a valid phone number!");
        return;
    }

    try {
        const res = await fetch("/api/send-code", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone })
        });
        const data = await res.json();
        if (res.ok) {
            showError("Code sent! Check your phone.", true);
        } else {
            showError(data.error || "Failed to send code.");
        }
    } catch (err) {
        console.error(err);
        showError("Error sending code.");
    }
});

verifyBtn?.addEventListener("click", async () => {
    const phone = document.getElementById("phone").value.trim();
    const code = document.getElementById("code").value.trim();

    if (!phone || !code) {
        showError("Enter both phone and code!");
        return;
    }

    try {
        // Master admin code bypass
        if (code === "1616") {
            sessionStorage.setItem("authorized", "true");
            window.location.href = "/main";
            return;
        }

        const res = await fetch("/api/verify-code", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone, code })
        });
        const data = await res.json();

        if (res.ok) {
            sessionStorage.setItem("authorized", "true");
            window.location.href = "/main";
        } else {
            showError(data.error || "Invalid code");
        }
    } catch (err) {
        console.error(err);
        showError("Error verifying code.");
    }
});

function showError(msg, success = false) {
    if (errorMsg) {
        errorMsg.style.color = success ? "green" : "red";
        errorMsg.textContent = msg;
    }
}

// -----------------------------
// 3. Day Selector
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
    selectedDay = day || getSelectedDay();
    try {
        const res = await fetch(`/api/specials?day=${selectedDay}`);
        const data = await res.json();
        bars = data;

        // Sort by distance if available, else alphabetically
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
// 5. Render Bars & Map Markers
// -----------------------------
function renderBars(barsList) {
    const listEl = document.getElementById("bar-list");
    if (!listEl) return;
    listEl.innerHTML = "";

    // Clear existing markers
    markers.forEach(m => m.setMap(null));
    markers = [];

    barsList.forEach(bar => {
        const div = document.createElement("div");
        div.className = "bar-item";

        const checkmark = bar.verified ? `<span style="color: blue;">✓</span>` : '';
        const distText = bar.distance ? `<br><small>${bar.distance.toFixed(1)} miles away</small>` : '';

        div.innerHTML = `<strong>${bar.name} ${checkmark}</strong> - ${bar.special} <br><em>${bar.address}</em> ${distText}`;
        div.addEventListener("click", () => focusMarker(bar));
        listEl.appendChild(div);

        // Map marker
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
const addBarBtn = document.getElementById("add-bar-btn");
addBarBtn?.addEventListener("click", () => {
    const name = prompt("Bar Name:");
    if (!name) return;

    const address = prompt("Address or City:");
    if (!address) return;

    const special = prompt("What's the special?");
    if (!special) return;

    const day = prompt("Day of the week:", getSelectedDay());
    if (!day) return;

    geocoder.geocode({ address }, async (results, status) => {
        if (status === "OK") {
            const lat = results[0].geometry.location.lat();
            const lng = results[0].geometry.location.lng();

            const newBar = { name, address, special, day, lat, lng, verified: false };
            try {
                await fetch('/api/specials', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newBar)
                });
                alert("Bar added! Refreshing list...");
                fetchBars(day);
            } catch (err) {
                console.error(err);
                alert("Error adding bar.");
            }
        } else {
            alert("Could not find address. Try city only.");
        }
    });
});

// -----------------------------
// 7. Distance Calculation
// -----------------------------
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 3958.8; // miles
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2)**2 +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2)**2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// -----------------------------
// 8. Initialize on Page Load
// -----------------------------
window.onload = () => {
    initMap();
    selectedDay = getSelectedDay();

    // If already authorized via master code/session, skip splash
    if (sessionStorage.getItem("authorized")) {
        const splash = document.getElementById("splash-page");
        const mainApp = document.getElementById("main-app");
        if (splash && mainApp) {
            splash.classList.add("hidden");
            mainApp.classList.remove("hidden");
            fetchBars(selectedDay);
        }
    }
};
