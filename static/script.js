// ===============================
// BEER DOLLARS - script.js
// ===============================

// ------- CONFIG -------
const API_GET_SPECIALS = "/api/specials"; 
const API_ADD_SPECIAL  = "/api/add_special";
const MAP_DEFAULT_ZOOM = 11;
const MAP_DEFAULT_CENTER = { lat: 41.1009, lng: -80.6495 }; 

// EXACT MATCH TO YOUR RENDER ENVIRONMENT VARIABLE
const GOOGLE_MAPS_API_KEY = "{{ GOOGLE_MAPS_API_KEY }}"; 

// ------- GLOBAL STATE -------
let map;
let markers = [];
let specials = [];
let selectedDay = null;
let infoWindow = null;

// DOM references
let listContainer, dayTabsContainer, greetingBanner, addButton, addModal, addForm, addCloseBtn;

// ===============================
// DAY / TIME LOGIC
// ===============================
function getBeerDollarsDay() {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();

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

// ===============================
// MAIN INITIALIZATION
// ===============================
function initBeerDollars() {
    console.log("System Initializing with GOOGLE_MAPS_API_KEY...");
    
    listContainer     = document.getElementById("bar-list");
    dayTabsContainer  = document.getElementById("day-tabs");
    greetingBanner    = document.getElementById("greeting-text"); 
    addButton         = document.getElementById("add-special-btn");
    addModal          = document.getElementById("add-modal");
    addForm           = document.getElementById("add-form");
    addCloseBtn       = document.getElementById("add-close");

    // Initialize Map using the Google Library
    map = new google.maps.Map(document.getElementById("map"), {
        center: MAP_DEFAULT_CENTER,
        zoom: MAP_DEFAULT_ZOOM,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        styles: [ { "featureType": "poi.business", "stylers": [{ "visibility": "off" }] } ]
    });

    infoWindow = new google.maps.InfoWindow();

    if (addButton) addButton.onclick = () => openAddModalWithLocation(null, null);
    if (addCloseBtn) addCloseBtn.onclick = closeAddModal;
    if (addForm) addForm.onsubmit = handleAddFormSubmit;
    
    map.addListener("click", (e) => {
        openAddModalWithLocation(e.latLng.lat(), e.latLng.lng());
    });

    const today = getBeerDollarsDay();
    initDayTabs();
    setSelectedDay(today);
    
    if (greetingBanner) {
        greetingBanner.innerText = greetings[today] || "Stretch Your Beer Money!";
    }

    loadSpecials();
}

window.initBeerDollars = initBeerDollars;

// ===============================
// RENDER LOGIC
// ===============================
async function loadSpecials() {
    try {
        const res = await fetch(API_GET_SPECIALS);
        specials = await res.json();
        renderSpecials();
    } catch (err) {
        console.error("Error loading specials with GOOGLE_MAPS_API_KEY:", err);
    }
}

function renderSpecials() {
    if (!map || !listContainer) return;
    
    markers.forEach(m => m.setMap(null));
    markers = [];
    listContainer.innerHTML = "";

    const filtered = specials.filter(s => s.day === selectedDay);
    const countBadge = document.getElementById("deal-count");
    if (countBadge) countBadge.innerText = `${filtered.length} deals`;

    filtered.forEach((special) => {
        const marker = new google.maps.Marker({
            position: { lat: parseFloat(special.lat), lng: parseFloat(special.lng) },
            map: map,
            title: special.name,
            animation: google.maps.Animation.DROP
        });

        marker.addListener("click", () => openInfoWindowForSpecial(marker, special));
        markers.push(marker);

        const item = document.createElement("div");
        item.className = "bar-item";
        item.innerHTML = `
            <div class="bar-info">
                <div class="bar-name">${special.name}</div>
                <div class="bar-deal">${special.deal}</div>
                <div class="bar-address">${special.address || ''}</div>
            </div>
        `;
        item.onclick = () => {
            map.panTo(marker.getPosition());
            map.setZoom(15);
            openInfoWindowForSpecial(marker, special);
        };
        listContainer.appendChild(item);
    });
}

function openInfoWindowForSpecial(marker, special) {
    const content = `
        <div style="color: #1a1a2e; padding: 10px;">
            <strong style="font-size: 16px;">${special.name}</strong><br>
            <span style="color: #1B6FFC; font-weight: bold;">${special.deal}</span><br>
            <small>${special.address || ''}</small><br><br>
            <button onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${special.lat},${special.lng}', '_blank')" 
                    style="background: #FFC312; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">
                Get Directions
            </button>
        </div>
    `;
    infoWindow.setContent(content);
    infoWindow.open(map, marker);
}

// ===============================
// TABS & MODAL
// ===============================
function initDayTabs() {
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    if (!dayTabsContainer) return;
    dayTabsContainer.innerHTML = "";
    days.forEach(day => {
        const btn = document.createElement("button");
        btn.className = "day-tab";
        btn.innerText = day.slice(0,3);
        btn.onclick = () => setSelectedDay(day);
        btn.dataset.day = day;
        dayTabsContainer.appendChild(btn);
    });
}

function setSelectedDay(day) {
    selectedDay = day;
    const buttons = document.querySelectorAll(".day-tab");
    buttons.forEach(btn => btn.classList.toggle("active-day", btn.dataset.day === day));
    renderSpecials();
}

function openAddModalWithLocation(lat, lng) {
    window.pendingLat = lat || MAP_DEFAULT_CENTER.lat;
    window.pendingLng = lng || MAP_DEFAULT_CENTER.lng;
    if (addModal) addModal.classList.add("visible");
}

function closeAddModal() {
    if (addModal) addModal.classList.remove("visible");
    if (addForm) addForm.reset();
}

async function handleAddFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(addForm);
    const payload = {
        name: formData.get("name"),
        address: formData.get("address"),
        deal: formData.get("deal"),
        day: formData.get("day"),
        lat: window.pendingLat,
        lng: window.pendingLng
    };

    try {
        const res = await fetch(API_ADD_SPECIAL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            await loadSpecials();
            closeAddModal();
        }
    } catch (err) {
        console.error("Submit error with GOOGLE_MAPS_API_KEY logic:", err);
    }
}
