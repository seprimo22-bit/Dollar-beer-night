let map;
let markers = [];
let lastTapTime = 0;
let holdTimer = null;

// Initialize Google Map
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 41.0998, lng: -80.6495 }, // Youngstown default
        zoom: 11,
        disableDoubleClickZoom: true,
        gestureHandling: "greedy"
    });

    setupLongPress();
    loadBars("Monday"); // default
}

// Load bars for selected day
function loadBars(day) {
    fetch(`/api/bars/${day}`)
        .then(res => res.json())
        .then(bars => {
            clearMarkers();
            renderBarList(bars);
            bars.forEach(bar => addMarker(bar));
        });
}

// Add marker with tap/double‑tap behavior
function addMarker(bar) {
    const marker = new google.maps.Marker({
        position: { lat: bar.lat, lng: bar.lng },
        map: map,
        title: bar.name
    });

    let lastTap = 0;

    marker.addListener("click", () => {
        const now = Date.now();
        const timeSince = now - lastTap;

        if (timeSince < 300) {
            openInMaps(bar.lat, bar.lng);
        } else {
            selectBar(bar);
            map.panTo({ lat: bar.lat, lng: bar.lng });
        }

        lastTap = now;
    });

    markers.push(marker);
}

// Highlight bar in list
function selectBar(bar) {
    document.querySelectorAll(".bar").forEach(el => el.classList.remove("selected"));
    const el = document.getElementById(`bar-${bar.id}`);
    if (el) el.classList.add("selected");
}

// Open native Maps app
function openInMaps(lat, lng) {
    const url = `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
    window.open(url, "_blank");
}

// Render bar list
function renderBarList(bars) {
    const list = document.getElementById("bar-list");
    list.innerHTML = "";

    bars.forEach(bar => {
        const div = document.createElement("div");
        div.className = "bar" + (bar.paid ? " paid" : "");
        div.id = `bar-${bar.id}`;
        div.innerHTML = `
            <strong>${bar.name}</strong><br>
            ${bar.deal}<br>
            <small>${bar.address}</small>
        `;

        div.onclick = () => {
            map.panTo({ lat: bar.lat, lng: bar.lng });
            selectBar(bar);
        };

        list.appendChild(div);
    });
}

// Clear markers
function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

// Long‑press to drop a pin
function setupLongPress() {
    map.addListener("mousedown", (e) => {
        holdTimer = setTimeout(() => {
            dropPin(e.latLng);
        }, 600);
    });

    map.addListener("mouseup", () => {
        clearTimeout(holdTimer);
    });
}

// Drop pin + auto‑fill form
function dropPin(latLng) {
    new google.maps.Marker({
        position: latLng,
        map: map
    });

    document.getElementById("bar-lat").value = latLng.lat();
    document.getElementById("bar-lng").value = latLng.lng();
}

// Day button switching
document.querySelectorAll("#days button").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll("#days button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        loadBars(btn.innerText);
    });
});
