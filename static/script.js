let map, autocomplete, selectedPlace;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 14,
        center: { lat: 41.1030, lng: -80.6514 }, // Centered on Youngstown
        disableDefaultUI: true
    });

    // MAP CLICK: Reverse geocode tap into an address
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

    // AUTOCOMPLETE: Search for bar names
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
    
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    loadBars(days[new Date().getDay()]);
}

async function saveBar() {
    const spec = document.getElementById("special-input").value;
    const day = document.getElementById("day-input").value;

    if (!selectedPlace || !spec) {
        alert("Search for a bar or tap the map first!");
        return;
    }

    const res = await fetch('/api/add-bar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: selectedPlace.name,
            address: selectedPlace.address,
            lat: selectedPlace.lat,
            lng: selectedPlace.lng,
            special: spec,
            day: day
        })
    });

    if (res.ok) {
        closeModal();
        loadBars(day);
    }
}

async function loadBars(day) {
    const res = await fetch(`/api/specials?day=${day}`);
    const data = await res.json();
    const list = document.getElementById("specialsList");
    list.innerHTML = "";
    
    markers.forEach(m => m.setMap(null));
    markers = [];

    data.forEach(bar => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<strong>${bar.name}</strong><span class="price">${bar.special}</span><br><small class="address">${bar.address}</small>`;
        list.appendChild(card);

        const marker = new google.maps.Marker({
            position: { lat: bar.lat, lng: bar.lng },
            map: map,
            title: bar.name
        });
        markers.push(marker);
    });
}
