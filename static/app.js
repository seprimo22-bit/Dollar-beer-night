let map;
let markers = [];
let currentDay = getToday();
const apiBase = "/";

function initMap() {
    // Default center: Youngstown, OH
    const defaultLoc = { lat: 41.0998, lng: -80.6495 };

    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLoc,
        zoom: 12,
    });

    // Try to get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                map.setCenter(loc);
                loadBars(currentDay, loc);
            },
            () => loadBars(currentDay, defaultLoc)
        );
    } else {
        loadBars(currentDay, defaultLoc);
    }

    // Click to add bar
    map.addListener("click", (e) => {
        openForm(e.latLng);
    });

    setupDayButtons();
}

function setupDayButtons() {
    const buttons = document.querySelectorAll("#days button");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            currentDay = btn.dataset.day;
            clearMarkers();
            loadBars(currentDay);
        });
    });
}

function getToday() {
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const today = new Date().getDay();
    return days[today];
}

function loadBars(day, loc=null) {
    fetch(`${apiBase}get_bars/${day}`)
        .then(res => res.json())
        .then(data => {
            displayBars(data);
            placeMarkers(data);
        });
}

function displayBars(bars) {
    const list = document.getElementById("bar-list");
    list.innerHTML = "";
    bars.forEach(b => {
        const div = document.createElement("div");
        div.innerHTML = `<strong>${b.name}</strong> - ${b.deal}`;
        if (b.highlighted) div.style.color = "red";
        list.appendChild(div);
    });
}

function placeMarkers(bars) {
    clearMarkers();
    bars.forEach(b => {
        if (b.lat && b.lng) {
            const marker = new google.maps.Marker({
                position: { lat: b.lat, lng: b.lng },
                map: map,
                title: `${b.name} - ${b.deal}`,
            });
            const infowindow = new google.maps.InfoWindow({
                content: `<strong>${b.name}</strong><br>${b.deal}`
            });
            marker.addListener("click", () => infowindow.open(map, marker));
            markers.push(marker);
        }
    });
}

function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

// ----------------------
// Add Bar Form Functions
// ----------------------
function openForm(latLng) {
    const formDiv = document.getElementById("add-bar-form");
    formDiv.style.display = "block";
    const form = document.getElementById("new-bar-form");
    form.lat.value = latLng.lat();
    form.lng.value = latLng.lng();
}

function closeForm() {
    document.getElementById("add-bar-form").style.display = "none";
}

document.getElementById("new-bar-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const jsonData = {};
    formData.forEach((value, key) => { jsonData[key] = value; });

    fetch(`${apiBase}add_bar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jsonData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Bar added!");
            closeForm();
            loadBars(currentDay);
        } else {
            alert("Error: " + data.error);
        }
    });
});

// Initialize map on page load
window.onload = initMap;
