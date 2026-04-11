let map, autocomplete, selectedPlace;
let markers = [];
let userPos = { lat: 41.099, lng: -80.649 };

function initApp() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13, center: userPos, disableDefaultUI: true
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            userPos = { lat: position.coords.latitude, lng: position.coords.longitude };
            map.setCenter(userPos);
            loadBars();
        });
    }

    const input = document.getElementById("autocomplete");
    autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.addListener("place_changed", () => { selectedPlace = autocomplete.getPlace(); });

    // Handle Login Override if on splash
    const verifyBtn = document.getElementById("verify-code-btn");
    verifyBtn?.addEventListener("click", async () => {
        const code = document.getElementById("code").value.trim();
        const res = await fetch("/api/verify-code", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: code })
        });
        if (res.ok) {
            sessionStorage.setItem("authorized", "true");
            window.location.href = "/main";
        } else {
            alert("Wrong code! Try 1616.");
        }
    });

    loadBars();
}

async function loadBars(day = "") {
    const res = await fetch(`/api/specials?day=${day}`);
    const bars = await res.json();
    const list = document.getElementById("bar-list");
    list.innerHTML = "";
    
    markers.forEach(m => m.setMap(null));
    markers = [];

    bars.sort((a, b) => getDistance(userPos.lat, userPos.lng, a.lat, a.lng) - getDistance(userPos.lat, userPos.lng, b.lat, b.lng));

    bars.forEach(bar => {
        const card = document.createElement("div");
        card.className = "card";
        const dist = getDistance(userPos.lat, userPos.lng, bar.lat, bar.lng).toFixed(1);
        card.innerHTML = `<strong>${bar.name}</strong><br><span style="color:#2e7d32; font-weight:bold;">${bar.special}</span><br><small>${bar.address} (${dist} mi)</small>`;
        card.onclick = () => {
            map.panTo({lat: bar.lat, lng: bar.lng});
            map.setZoom(16);
        };
        list.appendChild(card);

        const marker = new google.maps.Marker({
            position: {lat: bar.lat, lng: bar.lng},
            map: map,
            title: bar.name
        });
        markers.push(marker);
    });
}

function getDistance(lat1, lon1, lat2, lon2) {
    const R = 3958.8; 
    const dLat = (lat2-lat1) * Math.PI/180;
    const dLon = (lon2-lon1) * Math.PI/180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) * Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

async function saveBar() {
    const special = document.getElementById("special-input").value;
    if (!selectedPlace || !special) return alert("Select a bar from the list and enter the special!");
    
    const data = {
        name: selectedPlace.name,
        address: selectedPlace.formatted_address,
        lat: selectedPlace.geometry.location.lat(),
        lng: selectedPlace.geometry.location.lng(),
        special: special,
        day: document.getElementById("day-input").value
    };

    await fetch('/api/add-bar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    closeModal();
    loadBars(data.day);
}

function filterDay(day) {
    document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`btn-${day}`).classList.add('active');
    loadBars(day);
}

function openModal() { document.getElementById("add-modal").style.display = "flex"; }
function closeModal() { document.getElementById("add-modal").style.display = "none"; }

window.onload = initApp;
