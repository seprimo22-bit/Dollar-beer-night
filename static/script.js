let map, userLocation, geocoder;
let markers = [];
let tempPin = null;

function initMap() {
    geocoder = new google.maps.Geocoder();
    const defaultCenter = { lat: 41.1030, lng: -80.6514 }; // Youngstown
    
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: defaultCenter,
        disableDefaultUI: true
    });

    // 1. GET CURRENT LOCATION
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((pos) => {
            userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
            map.setCenter(userLocation);
            loadBars(new Date().toLocaleDateString('en-US', { weekday: 'Long' }));
        });
    }

    // 2. DROP PIN LOGIC: Click map to get address automatically
    map.addListener("click", (mapsMouseEvent) => {
        const clickedPos = mapsMouseEvent.latLng;
        
        // Remove old temp pin
        if (tempPin) tempPin.setMap(null);
        
        tempPin = new google.maps.Marker({ position: clickedPos, map: map, icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png' });
        
        // Use Geocoder to find the address of that pin
        geocoder.geocode({ location: clickedPos }, (results, status) => {
            if (status === "OK" && results[0]) {
                openAddModal();
                document.getElementById("manual-address").value = results[0].formatted_address;
            }
        });
    });
}

// 3. NAVIGATION: Click list item to pan map to that bar
function goToBar(lat, lng) {
    const pos = { lat: parseFloat(lat), lng: parseFloat(lng) };
    map.setCenter(pos);
    map.setZoom(17);
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    const res = await fetch(`/api/specials?day=${day}`);
    const data = await res.json();
    
    list.innerHTML = "";
    markers.forEach(m => m.setMap(null));

    data.forEach(bar => {
        const card = document.createElement("div");
        card.className = "card";
        // Click to move map to bar
        card.onclick = () => goToBar(bar.lat, bar.lng);
        card.innerHTML = `<span class="price">${bar.special}</span><strong>${bar.name}</strong><br><small>${bar.address}</small>`;
        list.appendChild(card);

        const marker = new google.maps.Marker({
            position: { lat: bar.lat, lng: bar.lng },
            map: map,
            title: bar.name
        });
        markers.push(marker);
    });
}

function openAddModal() { document.getElementById("add-modal").style.display = "block"; }
function closeModal() { document.getElementById("add-modal").style.display = "none"; }

async function submitManualBar() {
    const name = document.getElementById("manual-name").value;
    const addr = document.getElementById("manual-address").value;
    const spec = document.getElementById("manual-special").value;

    // Use geocoder one last time to get exact Lat/Lng for the DB
    geocoder.geocode({ address: addr }, async (results, status) => {
        if (status === "OK") {
            const loc = results[0].geometry.location;
            await fetch('/api/add-bar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name, address: addr,
                    lat: loc.lat(), lng: loc.lng(),
                    special: spec, day: "Friday" // You can add day picker logic here
                })
            });
            closeModal();
            loadBars("Friday");
        }
    });
}
