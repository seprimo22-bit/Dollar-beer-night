let map, autocomplete, selectedPlace;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 14,
        center: { lat: 41.0998, lng: -80.6495 },
        disableDefaultUI: true
    });

    // NEW: Click the map to add a bar at that location
    map.addListener("click", (mapsMouseEvent) => {
        const latLng = mapsMouseEvent.latLng;
        reverseGeocode(latLng);
    });

    // Fix the Search Box
    const input = document.getElementById("bar-search");
    autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.addListener("place_changed", () => {
        selectedPlace = autocomplete.getPlace();
        // Automatically put the address in the UI so you can see it
        if (selectedPlace.formatted_address) {
            console.log("Found:", selectedPlace.formatted_address);
        }
    });

    loadBars();
}

// Helper to get address when you click the map
function reverseGeocode(latLng) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: latLng }, (results, status) => {
        if (status === "OK" && results[0]) {
            selectedPlace = {
                name: "New Bar", // You can rename this in the input
                formatted_address: results[0].formatted_address,
                geometry: { location: latLng }
            };
            document.getElementById("bar-search").value = results[0].formatted_address;
            openModal();
        }
    });
}

async function saveBar() {
    const special = document.getElementById("special-input").value;
    const day = document.getElementById("day-input").value;

    if (!selectedPlace || !special) {
        alert("Please search for a bar or click the map first!");
        return;
    }

    const barData = {
        name: document.getElementById("bar-search").value || selectedPlace.name,
        address: selectedPlace.formatted_address,
        lat: typeof selectedPlace.geometry.location.lat === 'function' ? selectedPlace.geometry.location.lat() : selectedPlace.geometry.location.lat,
        lng: typeof selectedPlace.geometry.location.lng === 'function' ? selectedPlace.geometry.location.lng() : selectedPlace.geometry.location.lng,
        special: special,
        day: day
    };

    const res = await fetch('/api/add-bar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(barData)
    });

    if (res.ok) {
        closeModal();
        loadBars(day);
    } else {
        alert("Error saving bar. Check your database connection.");
    }
}

async function loadBars(day = "") {
    const res = await fetch(`/api/specials?day=${day}`);
    const bars = await res.json();
    const list = document.getElementById("specialsList");
    list.innerHTML = "";
    
    markers.forEach(m => m.setMap(null));
    markers = [];

    bars.forEach(bar => {
        const card = document.createElement("div");
        card.className = "card";
        // Now showing the address inside the card
        card.innerHTML = `
            <strong>${bar.name}</strong>
            <span class="price">${bar.special}</span>
            <span class="address">${bar.address}</span>
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




