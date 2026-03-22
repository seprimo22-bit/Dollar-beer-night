// ===============================
// BEER DOLLARS - script.js
// ===============================

// ------- CONFIG -------
const API_GET_SPECIALS = "/get_specials";      // Flask route: returns JSON list of specials
const API_ADD_SPECIAL  = "/add_special";       // Flask route: accepts JSON body, returns success
const MAP_DEFAULT_ZOOM = 11;
const MAP_DEFAULT_CENTER = { lat: 40.75, lng: -80.75 }; // fallback center (set to your region)
const SEARCH_RADIUS_MILES = 45;

// ------- GLOBAL STATE -------
let map;
let markers = [];
let specials = [];
let selectedDay = null;
let infoWindow = null;

// HTML elements (set in initDOMRefs)
let listContainer;
let dayTabsContainer;
let greetingBanner;
let addButton;
let addModal;
let addForm;
let addCloseBtn;

// ===============================
// DAY / TIME LOGIC
// ===============================

function getBeerDollarsDay() {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();

    // If it's after midnight but before 2:30 AM, treat it as "yesterday"
    if (hour < 2 || (hour === 2 && minute <= 30)) {
        now.setDate(now.getDate() - 1);
    }

    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    return days[now.getDay()];
}

const greetings = {
    "Monday": "Another Monday — Grab a Beer!",
    "Tuesday": "Two-Dollar Tuesday!",
    "Wednesday": "Hump Day — Time for a Cold One!",
    "Thursday": "Thirsty Thursday — You Earned It!",
    "Friday": "TGIF — Time for a Beer!",
    "Saturday": "Saturdays Are for Drinking!",
    "Sunday": "Sunday Funday — One More Round!"
};

function showGreeting(day) {
    if (!greetingBanner) return;
    greetingBanner.innerText = greetings[day] || "Stretch Your Beer Money!";
    greetingBanner.classList.add("pop-animation");
}

// ===============================
// MAP INIT
// ===============================

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: MAP_DEFAULT_CENTER,
        zoom: MAP_DEFAULT_ZOOM,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false
    });

    infoWindow = new google.maps.InfoWindow();

    // Click on map to add a bar at that location
    map.addListener("click", (e) => {
        openAddModalWithLocation(e.latLng.lat(), e.latLng.lng());
    });
}

// ===============================
// DOM REFERENCES & EVENTS
// ===============================

function initDOMRefs() {
    listContainer     = document.getElementById("bar-list");
    dayTabsContainer  = document.getElementById("day-tabs");
    greetingBanner    = document.getElementById("greeting");
    addButton         = document.getElementById("add-special-btn");
    addModal          = document.getElementById("add-modal");
    addForm           = document.getElementById("add-form");
    addCloseBtn       = document.getElementById("add-close");

    if (addButton) {
        addButton.addEventListener("click", () => openAddModalWithLocation(null, null));
    }

    if (addCloseBtn) {
        addCloseBtn.addEventListener("click", closeAddModal);
    }

    if (addForm) {
        addForm.addEventListener("submit", handleAddFormSubmit);
    }

    initDayTabs();
}

function initDayTabs() {
    if (!dayTabsContainer) return;
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    dayTabsContainer.innerHTML = "";

    days.forEach(day => {
        const btn = document.createElement("button");
        btn.className = "day-tab";
        btn.innerText = day.slice(0,3); // Sun, Mon, etc.
        btn.dataset.day = day;
        btn.addEventListener("click", () => {
            setSelectedDay(day);
        });
        dayTabsContainer.appendChild(btn);
    });
}

// ===============================
// DAY SELECTION
// ===============================

function setSelectedDay(day) {
    selectedDay = day;
    highlightSelectedDayTab();
    renderSpecials();
}

function highlightSelectedDayTab() {
    if (!dayTabsContainer) return;
    const buttons = dayTabsContainer.querySelectorAll(".day-tab");
    buttons.forEach(btn => {
        if (btn.dataset.day === selectedDay) {
            btn.classList.add("active-day");
        } else {
            btn.classList.remove("active-day");
        }
    });
}

// ===============================
// FETCH SPECIALS
// ===============================

async function loadSpecials() {
    try {
        const res = await fetch(API_GET_SPECIALS);
        if (!res.ok) throw new Error("Failed to load specials");
        specials = await res.json();
        renderSpecials();
    } catch (err) {
        console.error("Error loading specials:", err);
    }
}

// ===============================
// RENDER SPECIALS (LIST + MAP)
// ===============================

function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

function renderSpecials() {
    if (!map || !listContainer) return;
    clearMarkers();
    listContainer.innerHTML = "";

    const filtered = specials.filter(s => s.day === selectedDay);

    filtered.forEach((special, index) => {
        // Create marker
        const marker = new google.maps.Marker({
            position: { lat: special.lat, lng: special.lng },
            map,
            title: special.name
        });

        marker.addListener("click", () => {
            openInfoWindowForSpecial(marker, special);
        });

        markers.push(marker);

        // Create list item
        const item = document.createElement("div");
        item.className = "bar-item";
        item.innerHTML = `
            <div class="bar-name">${special.name}</div>
            <div class="bar-deal">${special.deal}</div>
            <div class="bar-address">${special.address}</div>
        `;
        item.addEventListener("click", () => {
            map.panTo(marker.getPosition());
            map.setZoom(14);
            openInfoWindowForSpecial(marker, special);
        });

        listContainer.appendChild(item);
    });
}

function openInfoWindowForSpecial(marker, special) {
    const content = `
        <div class="info-window">
            <div class="info-name">${special.name}</div>
            <div class="info-deal">${special.deal}</div>
            <div class="info-address">${special.address}</div>
            <button class="nav-btn" onclick="openNavigation(${special.lat}, ${special.lng})">
                Navigate
            </button>
        </div>
    `;
    infoWindow.setContent(content);
    infoWindow.open(map, marker);
}

// ===============================
// NAVIGATION
// ===============================

function openNavigation(lat, lng) {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    window.open(url, "_blank");
}

// Make it accessible from inline onclick
window.openNavigation = openNavigation;

// ===============================
// ADD SPECIAL MODAL
// ===============================

let pendingLat = null;
let pendingLng = null;

function openAddModalWithLocation(lat, lng) {
    pendingLat = lat;
    pendingLng = lng;
    if (!addModal) return;
    addModal.classList.add("visible");
}

function closeAddModal() {
    if (!addModal) return;
    addModal.classList.remove("visible");
    pendingLat = null;
    pendingLng = null;
    if (addForm) addForm.reset();
}

async function handleAddFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(addForm);

    const name    = formData.get("name")?.toString().trim();
    const address = formData.get("address")?.toString().trim();
    const deal    = formData.get("deal")?.toString().trim();
    const day     = formData.get("day")?.toString().trim();

    if (!name || !deal || !day) {
        alert("Please fill in at least name, deal, and day.");
        return;
    }

    // If no lat/lng from map click, backend can geocode from address
    const payload = {
        name,
        address,
        deal,
        day,
        lat: pendingLat,
        lng: pendingLng
    };

    try {
        const res = await fetch(API_ADD_SPECIAL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Failed to add special");

        // Reload specials after successful add
        await loadSpecials();
        closeAddModal();
    } catch (err) {
        console.error("Error adding special:", err);
        alert("Could not add special. Try again.");
    }
}

// ===============================
// INITIALIZATION
// ===============================

async function initBeerDollars() {
    initDOMRefs();
    initMap();

    const today = getBeerDollarsDay();
    setSelectedDay(today);
    showGreeting(today);

    await loadSpecials();
}

// Run when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    // Google Maps callback should call initBeerDollars,
    // or you can call it here if Maps is already loaded.
    // If you use the script tag with callback, set:
    // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY&callback=initBeerDollars" async defer></script>
});

// Expose init for Google Maps callback
window.initBeerDollars = initBeerDollars;
