// ===============================
// BEER DOLLARS - script.js (FULL WORKING VERSION)
// ===============================

let map;
let markers = [];
let infoWindow;
let selectedDay = null;

// Configuration
const MAP_DEFAULT_CENTER = { lat: 41.1009, lng: -80.6495 }; // Austintown/Youngstown

/**
 * 1. MAP INITIALIZATION
 * This runs when the Google Maps API finishes loading.
 */
function initBeerDollars() {
    console.log("System Initializing with GOOGLE_MAPS_API_KEY...");

    const mapElement = document.getElementById("map");
    
    // Check if we are on the map page (index.html)
    if (mapElement) {
        map = new google.maps.Map(mapElement, {
            center: MAP_DEFAULT_CENTER,
            zoom: 12,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false
        });

        infoWindow = new google.maps.InfoWindow();

        // Map Click Listener to add new spots
        map.addListener("click", (e) => {
            openAddModal(e.latLng.lat(), e.latLng.lng());
        });

        // Set initial day and load data
        const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
        selectedDay = days[new Date().getDay()];
        
        loadSpecials();
    }

    // --- LOGIN / OVERRIDE LOGIC FOR SPLASH PAGE ---
    const loginBtn = document.getElementById('login-button');
    const codeInput = document.getElementById('code-input');

    if (loginBtn && codeInput) {
        loginBtn.addEventListener('click', function() {
            const enteredCode = codeInput.value.trim();
            
            // MASTER OVERRIDE CHECK
            if (enteredCode === '9999') {
                console.log("Master Override Accepted. Redirecting...");
                // This hits the route we added to your app.py
                window.location.href = '/9999';
            } else {
                // If it's not the override, we show the alert
                alert("Invalid Access Code. Please use the Master Override.");
            }
        });

        // Also allow pressing 'Enter' key in the input box
        codeInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                loginBtn.click();
            }
        });
    }
}

// Global scope attachment for Google Maps Callback
window.initBeerDollars = initBeerDollars;

/**
 * 2. DATA FETCHING
 */
async function loadSpecials() {
    try {
        const response = await fetch('/api/specials');
        const specials = await response.json();
        renderMarkers(specials);
    } catch (err) {
        console.error("Failed to load specials with GOOGLE_MAPS_API_KEY active:", err);
    }
}

/**
 * 3. RENDERING MARKERS
 */
function renderMarkers(specials) {
    // Clear old markers
    markers.forEach(m => m.setMap(null));
    markers = [];

    specials.forEach(special => {
        // Only show deals for the selected day
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

/**
 * 4. MODAL UI LOGIC
 */
function openAddModal(lat, lng) {
    const modal = document.getElementById('add-modal');
    if (modal) {
        window.pendingLat = lat;
        window.pendingLng = lng;
        modal.classList.add('visible');
    }
}

// Close Button Logic
const addCloseBtn = document.getElementById('add-close');
if (addCloseBtn) {
    addCloseBtn.onclick = () => {
        document.getElementById('add-modal').classList.remove('visible');
    };
            }
    
