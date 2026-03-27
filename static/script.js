// Global variables
let map;
let markers = [];
let bars = []; // Example bar data, normally fetched from server

// Master override codes
const MASTER_CODES = ["999-000", "1616"];

// Sample bars
bars = [
    { name: "TJ's Brickhouse Tavern", special: "$2 bottles", address: "123 Main St", day: "Thursday", lat: 39.999, lng: -80.600, verified: true },
    { name: "Still City", special: "$2 bottles", address: "456 Oak St", day: "Thursday", lat: 40.001, lng: -80.602, verified: false }
];

// Splash Page Logic
document.getElementById("enter-btn").addEventListener("click", () => {
    const phone = document.getElementById("phone").value.trim();
    const code = document.getElementById("code").value.trim();

    if (!phone || !code) {
        document.getElementById("splash-error").innerText = "Enter both phone number and code.";
        return;
    }

    // Master override
    if (MASTER_CODES.includes(code)) {
        showMainApp();
        return;
    }

    // TODO: Implement sending/validating real code here
    showMainApp();
});

// Show main app
function showMainApp() {
    document.getElementById("splash-page").classList.add("hidden");
    document.getElementById("main-app").classList.remove("hidden");
    highlightCurrentDay();
    populateBars();
}

// Day highlighting
function highlightCurrentDay() {
    const dayBtns = document.querySelectorAll(".day-btn");
    const now = new Date();
    let dayIndex = now.getDay(); // Sunday=0
    const hours = now.getHours();
    const minutes = now.getMinutes();
    if (hours < 2 || (hours === 2 && minutes < 30)) dayIndex -= 1; // day logic until 2:30 am
    if (dayIndex < 0) dayIndex = 6; // Sunday wrap
    dayBtns[dayIndex].classList.add("active");
}

// Populate bars
function populateBars(day = null) {
    const list = document.getElementById("bar-list");
    list.innerHTML = "";

    const selectedDay = day || getSelectedDay() || getCurrentDayName();

    bars.forEach(bar => {
        if (bar.day === selectedDay) {
            const div = document.createElement("div");
            div.className = "bar-item";
            div.innerHTML = `<strong>${bar.name}</strong> - ${bar.special} <br><em>${bar.address}</em>`;
            div.addEventListener("click", () => focusMarker(bar));
            list.appendChild(div);
        }
    });

    updateMarkers(selectedDay);
}

// Get selected day from active button
function getSelectedDay() {
    const active = document.querySelector(".day-btn.active");
    return active ? active.dataset.day : null;
}

// Get current day name
function getCurrentDayName() {
    return ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"][new Date().getDay()];
}

// Day button clicks
document.querySelectorAll(".day-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".day-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        populateBars(btn.dataset.day);
    });
});

// Google Map
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: { lat: 39.999, lng: -80.600 }, // default center
    });

    updateMarkers(getCurrentDayName());
}

// Update markers
function updateMarkers(day) {
    // Clear previous markers
    markers.forEach(m => m.setMap(null));
    markers = [];

    bars.filter(bar => bar.day === day).forEach(bar => {
        const marker = new google.maps.Marker({
            position: { lat: bar.lat, lng: bar.lng },
            map: map,
            title: bar.name
        });
        marker.addListener("click", () => {
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`, "_blank");
        });
        markers.push(marker);
    });
}

// Focus marker when clicking list
function focusMarker(bar) {
    const found = markers.find(m => m.getTitle() === bar.name);
    if (found) map.panTo(found.getPosition());
}

// Floating Add Bar Button
document.getElementById("add-bar-btn").addEventListener("click", () => {
    const name = prompt("Bar Name:");
    const address = prompt("Bar Address:");
    const special = prompt("Special:");
    const day = prompt("Day of the Special (Monday-Sunday):");
    const lat = parseFloat(prompt("Latitude:"));
    const lng = parseFloat(prompt("Longitude:"));
    if (name && address && special && day && !isNaN(lat) && !isNaN(lng)) {
        bars.push({ name, address, special, day, lat, lng, verified: false });
        populateBars(getSelectedDay());
    }
});
