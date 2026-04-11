let map, markers = [], tempMarker = null;

document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today);
});

function initMap() {
    // UPDATED: Centered on Bellaire, OH
    const bellaire = { lat: 40.0162, lng: -80.7423 }; 
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: bellaire,
        disableDefaultUI: false,
        gestureHandling: "greedy"
    });

    // Tap map to drop pin
    map.addListener("click", (e) => {
        if (tempMarker) tempMarker.setMap(null);
        tempMarker = new google.maps.Marker({
            position: e.latLng,
            map: map,
            animation: google.maps.Animation.DROP
        });
        document.getElementById("lat").value = e.latLng.lat();
        document.getElementById("lng").value = e.latLng.lng();
        document.getElementById("addForm").style.display = "block";
    });
}

async function saveBar() {
    const data = {
        name: document.getElementById("name").value,
        address: document.getElementById("address").value,
        special: document.getElementById("special").value,
        day: document.getElementById("day").value,
        lat: parseFloat(document.getElementById("lat").value),
        lng: parseFloat(document.getElementById("lng").value)
    };

    const response = await fetch('/add_bar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    if (response.ok) {
        document.getElementById("addForm").style.display = "none";
        loadBars(data.day);
    }
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    list.innerHTML = `<p style="text-align:center;">Finding ${day} deals...</p>`;
    
    try {
        const jsonRes = await fetch('/get_json_bars');
        const jsonBars = await jsonRes.json();
        const dbRes = await fetch(`/get_db_bars?day=${day}`);
        const dbBars = dbRes.ok ? await dbRes.json() : [];

        const allBars = [...jsonBars.filter(b => b.day === day), ...dbBars];
        list.innerHTML = ""; markers.forEach(m => m.setMap(null)); markers = [];

        allBars.forEach(bar => {
            const card = document.createElement("div");
            card.className = "card";
            
            // This URL opens the ACTUAL Google Maps App
            const navUrl = `https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`;

            card.innerHTML = `
                <a href="${navUrl}" target="_blank" style="float:right; text-decoration:none; font-size:30px;">➡️</a>
                <span class="price">${bar.special}</span>
                <strong>${bar.name}</strong><br>
                <small>${bar.address}</small>
            `;
            
            card.onclick = (e) => {
                if (e.target.tagName !== 'A') {
                    map.setCenter({ lat: bar.lat, lng: bar.lng });
                    map.setZoom(17);
                }
            };
            list.appendChild(card);

            const marker = new google.maps.Marker({ position: { lat: bar.lat, lng: bar.lng }, map: map });
            markers.push(marker);
        });
    } catch (err) { console.error(err); }
}
