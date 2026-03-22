let map;
let markers = [];

// INIT MAP
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 41.0814, lng: -81.5190 }, // Akron default
        zoom: 12,
    });

    loadToday();
}

// LOAD TODAY AUTOMATICALLY
function loadToday() {
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    const today = days[new Date().getDay()];
    loadDay(today);
}

// LOAD DATA
function loadDay(day) {
    fetch(`/get_specials?day=${day}`)
        .then(res => res.json())
        .then(data => {
            renderList(data);
            renderMap(data);
        });
}

// RENDER LIST
function renderList(data) {
    const list = document.getElementById("list");
    list.innerHTML = "";

    data.forEach((bar, index) => {
        const div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <strong>${bar.name}</strong><br>
            ${bar.deal}<br>
            <small>${bar.address}</small>
        `;

        div.onclick = () => focusMarker(index);

        list.appendChild(div);
    });
}

// RENDER MAP
function renderMap(data) {
    markers.forEach(m => m.setMap(null));
    markers = [];

    data.forEach((bar, index) => {
        const marker = new google.maps.Marker({
            position: { lat: parseFloat(bar.lat), lng: parseFloat(bar.lng) },
            map: map,
            title: bar.name
        });

        marker.addListener("click", () => {
            window.open(`https://www.google.com/maps/search/?api=1&query=${bar.lat},${bar.lng}`);
        });

        markers.push(marker);
    });
}

// CLICK LIST → FOCUS MAP
function focusMarker(index) {
    const marker = markers[index];
    map.panTo(marker.getPosition());
    map.setZoom(15);
}

// START
window.onload = initMap;
