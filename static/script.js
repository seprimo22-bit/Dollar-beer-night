// Add this variable at the top of your script.js
let userLocation = null;
let geocoder; // For turning addresses into map pins

// 1. Get User's Location on load
function initMap() {
    geocoder = new google.maps.Geocoder();
    
    // Default map to Youngstown roughly, but will update when user allows location
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: { lat: 41.099, lng: -80.649 }, // Youngstown center
    });

    // Ask browser for location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(userLocation);
                // Now that we have their location, re-sort the bars!
                renderBars(getSelectedDay());
            },
            () => console.log("User denied location")
        );
    }
}

// 2. Sort the bars by distance!
function renderBars(day) {
    const list = document.getElementById("bar-list");
    list.innerHTML = "";

    // If we have the user's location, sort bars by who is closest
    if (userLocation && bars.length > 0) {
        bars.forEach(bar => {
            bar.distance = calculateDistance(userLocation.lat, userLocation.lng, bar.lat, bar.lng);
        });
        
        // Filter to within 45 miles, then sort closest first
        bars = bars.filter(bar => bar.distance <= 45)
                   .sort((a, b) => a.distance - b.distance);
    }

    bars.forEach(bar => {
        const div = document.createElement("div");
        div.className = "bar-item";
        
        // Add the Verification Checkmark if verified
        const checkmark = bar.verified ? `<span style="color: blue;">✓</span>` : '';
        const distText = bar.distance ? `<br><small>${bar.distance.toFixed(1)} miles away</small>` : '';

        div.innerHTML = `<strong>${bar.name} ${checkmark}</strong> - ${bar.special} <br><em>${bar.address}</em> ${distText}`;
        
        // Click the bar -> pinpoints map
        div.addEventListener("click", () => focusMarker(bar));
        list.appendChild(div);
    });

    updateMarkers(day);
}

// 3. The New "Add Bar" (No Lat/Lng prompts!)
document.getElementById("add-bar-btn").addEventListener("click", () => {
    const name = prompt("Bar Name (e.g., Lonnie's):");
    if (!name) return;
    const address = prompt("Address or City (e.g., 123 Main St, Youngstown):");
    const special = prompt("What's the special? (e.g., $2 bottles):");
    const day = prompt("Day of the week:", getSelectedDay());

    if (name && address && special && day) {
        // Use Google Maps to magically find the Lat/Lng
        geocoder.geocode({ address: address }, async (results, status) => {
            if (status === "OK") {
                const lat = results[0].geometry.location.lat();
                const lng = results[0].geometry.location.lng();

                const newBar = { name, address, special, day, lat, lng, verified: false };
                
                // Send to your Python Database
                await fetch('/api/specials', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newBar)
                });
                
                alert("Bar added! It will show up after you refresh the list.");
                fetchBars(getSelectedDay());
            } else {
                alert("Couldn't find that address. Please try adding the city name.");
            }
        });
    }
});

// Math formula to calculate miles between two Lat/Lng coordinates
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 3958.8; // Radius of earth in miles
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}
