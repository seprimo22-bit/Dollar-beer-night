// ===============================
// BEER DOLLARS - script.js (FULL WORKING VERSION)
// ===============================

let map;
let markers = [];
let infoWindow;
let selectedDay = null;

const MAP_DEFAULT_CENTER = { lat: 41.1009, lng: -80.6495 };

function initBeerDollars() {
    console.log("System Initializing with GOOGLE_MAPS_API_KEY...");

    const mapElement = document.getElementById("map");
    
    // IF WE ARE ON THE MAP PAGE
    if (mapElement) {
        map = new google.maps.Map(mapElement, {
            center: MAP_DEFAULT_CENTER,
            zoom: 12,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false
        });

        infoWindow = new google.maps.InfoWindow();

        map.addListener("click", (e) => {
            openAddModal(e.latLng.lat(), e.latLng.lng());
        });

        const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
        selectedDay = days[new Date().getDay()];
        loadSpecials();
    }

    // --- THE MASTER OVERRIDE TRIGGER ---
    // This looks for the input box and the enter button on your splash screen
    const loginBtn = document.getElementById('login-button');
    const codeInput = document.getElementById('code-input');

    if (loginBtn && codeInput) {
        loginBtn.addEventListener('click', function() {
            const enteredCode = codeInput.value.trim();
            
            if (enteredCode === '9999') {
                console.log("Master Override Accepted.");
                window.location.href = '/9999'; // Kicks you to the override route in app.py
            } else {
                alert("Use the Master Override code to enter.");
            }
        });

        // Makes it so hitting the actual 'Enter' key on your keyboard works too
        codeInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                loginBtn.click();
            }
        });
    }
}

window.initBeerDollars = initBeerDollars;

async function loadSpecials() {
    try {
        const response = await fetch('/api/specials');
        const specials = await response.json();
        renderMarkers(specials);
    } catch (err) {
        console.error("Failed to load specials with GOOGLE_MAPS_API_KEY active:", err);
    }
}

function renderMarkers(specials) {
    markers.forEach(m => m.setMap(null));
    markers = [];

    specials.forEach(special => {
        if (special.day === selectedDay) {
            const marker = new google.maps.Marker({
                position: { lat: parseFloat(special.lat), lng: parseFloat(special.lng) },
                map: map,
                title: special.name,
                animation: google.maps.Animation.DROP
            });

            marker.addListener("click", () => {
                const content = `
                    <div style="color: #333; padding: 10px;">
                        <strong>${special.name}</strong><br>
                        <span style="color: #1B6FFC;">${special.deal}</span><br>
                        <small>${special.address || ''}</small>
                    </div>
                `;
                infoWindow.setContent(content);
                infoWindow.open(map, marker);
            });
            markers.push(marker);
        }
    });
}

function openAddModal(lat, lng) {
    const modal = document.getElementById('add-modal');
    if (modal) {
        window.pendingLat = lat;
        window.pendingLng = lng;
        modal.classList.add('visible');
    }
}

