let map, autocomplete, selectedPlace, userLocation;
let markers = [];

function initMap() {
    // Default center (Youngstown area) if GPS is unavailable
    const defaultCenter = { lat: 41.1030, lng: -80.6514 };
    
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: defaultCenter,
        disableDefaultUI: true,
        zoomControl: true
    });

    // 1. Get User Location & Center Map
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(userLocation);
                // Add a small blue dot for the user
                new google.maps.Marker({
                    position: userLocation,
                    map: map,
                    icon: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                });
                loadBars(new Date().toLocaleDateString('en-US', { weekday: 'Long' }));
            },
            () => {
                console.log("Location access denied.");
                loadBars("Monday"); 
            }
        );
    }

    // 2. Setup Google Places Autocomplete for the "Add Special" modal
    const input = document.getElementById("bar-search");
    autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;
        selectedPlace = {
            name: place.name,
            address: place.formatted_address,
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
        };
    });
}

// 3. Navigation Launch Function
function launchNavigation(lat, lng) {
    // This triggers the native Google Maps app for turn-by-turn directions
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}&travelmode=driving`;
    window.open(url, '_blank');
}

// 4. Load and Filter Bars (45 Mile Radius)
async function loadBars(day) {
    const list = document.getElementById("specialsList");
    const res = await fetch(`/api/specials?day=${day}`);
    const data = await res.json();
    
    list.innerHTML = "";
    markers.forEach(m => m.setMap(null));
    markers = [];

    if (data.length === 0) {
        list.innerHTML = `<p style="text-align:center; padding:20px;">No specials found for ${day}.</p>`;
        return;
    }

    data.forEach(bar => {
        const barPos = { lat: bar.lat, lng: bar.lng };
        const distance = calculateDistance(userLocation, barPos);

        // Filter: Only show bars within 45 miles
        if (userLocation && distance > 45) return;

        const card = document.createElement("div");
        card.className = "card";
        // One-tap navigation on the card
        card.onclick = () => launchNavigation(bar.lat, bar.lng);
        
        card.innerHTML = `
            <span class="price">${bar.special}</span>
            <strong>${bar.name}</strong><br>
            <small>${bar.address}</small>
            <div class="nav-hint">📍 Tap to Navigate (${distance.toFixed(1)} miles away)</div>
        `;
        list.appendChild(card);

        const marker = new google.maps.Marker({
            position: barPos,
            map: map,
            title: bar.name
        });
        markers.push(marker);
    });
}

// 5. Submit New Bar to Database
async function submitBar() {
    const special = document.getElementById("special-desc").value;
    const day = document.getElementById("special-day").value;

    if (!selectedPlace || !special) {
        alert("Please search for a bar and enter the special first!");
        return;
    }

    const response = await fetch('/api/add-bar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: selectedPlace.name,
            address: selectedPlace.address,
            lat: selectedPlace.lat,
            lng: selectedPlace.lng,
            special: special,
            day: day
        })
    });

    if (response.ok) {
        alert("Special added successfully!");
        document.getElementById('add-modal').style.display = 'none';
        loadBars(day);
    }
}

// Helper: Haversine distance formula
function calculateDistance(p1, p2) {
    if (!p1 || !p2) return 0;
    const R = 3958.8; // Radius of Earth in miles
    const dLat = (p2.lat - p1.lat) * Math.PI / 180;
    const dLon = (p2.lng - p1.lng) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(p1.lat * Math.PI / 180) * Math.cos(p2.lat * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}
