let map, autocomplete, selectedPlace, userLocation;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: { lat: 41.1030, lng: -80.6514 }, // Youngstown
        disableDefaultUI: true
    });

    // Get User GPS
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
            map.setCenter(userLocation);
        });
    }

    // MAP CLICK TO ADD
    map.addListener("click", (e) => {
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: e.latLng }, (results, status) => {
            if (status === "OK" && results[0]) {
                selectedPlace = {
                    name: "New Spot",
                    address: results[0].formatted_address,
                    lat: e.latLng.lat(),
                    lng: e.latLng.lng()
                };
                document.getElementById("bar-search").value = results[0].formatted_address;
                openModal();
            }
        });
    });

    const input = document.getElementById("bar-search");
    autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        selectedPlace = {
            name: place.name,
            address: place.formatted_address,
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
        };
    });
}

// NAVIGATION FUNCTION
function navigateTo(lat, lng) {
    window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`, '_blank');
}

async function loadBars(day) {
    const res = await fetch(`/api/specials?day=${day}`);
    const data = await res.json();
    const list = document.getElementById("specialsList");
    list.innerHTML = "";
    
    markers.forEach(m => m.setMap(null));
    markers = [];

    data.forEach(bar => {
        // Radius Filter (Roughly 45 miles)
        const distance = getDistance(userLocation, {lat: bar.lat, lng: bar.lng});
        if (distance > 45) return; 

        const card = document.createElement("div");
        card.className = "card";
        card.onclick = () => navigateTo(bar.lat, bar.lng);
        card.innerHTML = `
            <strong>${bar.name}</strong>
            <span class="price">${bar.special}</span><br>
            <small class="address">${bar.address}</small>
            <button style="margin-top:5px; background:#2196F3; color:white; border:none; border-radius:4px; padding:5px;">Navigate</button>
        `;
        list.appendChild(card);

        const marker = new google.maps.Marker({
            position: { lat: bar.lat, lng: bar.lng },
            map: map,
            title: bar.name
        });
        markers.push(marker);
    });
}

// Distance Helper
function getDistance(p1, p2) {
    if (!p1) return 0;
    const R = 3958.8; // Radius of Earth in miles
    const dLat = (p2.lat - p1.lat) * Math.PI / 180;
    const dLon = (p2.lng - p1.lng) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(p1.lat * Math.PI / 180) * Math.cos(p2.lat * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));
}
