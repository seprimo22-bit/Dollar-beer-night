const API = "/api/specials";
let map;
let markers = [];

// ---------------------
// ADD SPECIAL
// ---------------------
async function addSpecial() {
    const bar = document.getElementById("bar").value;
    const deal = document.getElementById("deal").value;
    const location = document.getElementById("location").value;
    const day = document.getElementById("day").value;

    if (!bar || !deal || !location || !day) {
        alert("Fill everything out.");
        return;
    }

    const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bar, deal, location, day })
    });

    const result = await res.json();

    if (result.status === "duplicate") {
        alert("Already listed.");
    } else {
        alert("Special added.");
        loadSpecials();
    }
}

// ---------------------
// LOAD SPECIALS
// ---------------------
async function loadSpecials() {
    const res = await fetch(API);
    const specials = await res.json();

    const list = document.getElementById("specialsList");
    list.innerHTML = "";

    markers.forEach(m => map.removeLayer(m));
    markers = [];

    specials.forEach(s => {
        list.innerHTML += `
            <p>
                <b>${s.bar}</b><br>
                ${s.deal}<br>
                ${s.location} — ${s.day}
            </p>
        `;

        // Basic fake coordinates for demo
        const lat = 41.10 + Math.random() * 0.05;
        const lng = -80.65 + Math.random() * 0.05;

        const marker = L.marker([lat, lng])
            .addTo(map)
            .bindPopup(`${s.bar}<br>${s.deal}`);

        markers.push(marker);
    });
}

// ---------------------
// MAP INIT
// ---------------------
function initMap() {
    map = L.map("map").setView([41.10, -80.65], 12);

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        { attribution: "© OpenStreetMap" }
    ).addTo(map);

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            map.setView([lat, lng], 13);

            L.marker([lat, lng])
                .addTo(map)
                .bindPopup("You are here")
                .openPopup();
        });
    }
}

initMap();
loadSpecials();
