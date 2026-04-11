let map, markers = [], tempMarker = null;

function initMap() {
    // Center map near Bellaire, OH
    const defaultCenter = { lat: 40.0162, lng: -80.7423 }; 
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: defaultCenter,
        disableDefaultUI: false,
        gestureHandling: "greedy"
    });

    // Tap to drop pin functionality
    map.addListener("click", (e) => {
        if (tempMarker) tempMarker.setMap(null);
        tempMarker = new google.maps.Marker({
            position: e.latLng,
            map: map,
            animation: google.maps.Animation.DROP
        });
        // Captures coordinates from the tap so users don't have to type them
        document.getElementById("lat").value = e.latLng.lat();
        document.getElementById("lng").value = e.latLng.lng();
        document.getElementById("addForm").style.display = "block";
    });
}

async function saveBar() {
    const addressText = document.getElementById("address").value;
    const geocoder = new google.maps.Geocoder();

    // AUTO-LOOKUP: Turns address text into map coordinates automatically
    geocoder.geocode({ address: addressText }, async (results, status) => {
        if (status === "OK") {
            const coords = results[0].geometry.location;
            const data = {
                name: document.getElementById("name").value,
                address: addressText,
                special: document.getElementById("special").value,
                day: document.getElementById("day").value,
                lat: coords.lat(), 
                lng: coords.lng()  
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
        } else {
            alert("Google couldn't find that address. Check your spelling!");
        }
    });
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    try {
        const jsonRes = await fetch('/get_json_bars');
        const jsonBars = await jsonRes.json();
        const dbRes = await fetch(`/get_db_bars?day=${day}`);
        const dbBars = dbRes.ok ? await dbRes.json() : [];

        const allBars = [...jsonBars.filter(b => b.day === day), ...dbBars];
        list.innerHTML = ""; 
        markers.forEach(m => m.setMap(null)); 
        markers = [];

        allBars.forEach(bar => {
            // FIX: HARDCODED OVERRIDE FOR DENNY'S
            // This forces the map to use Bellaire coordinates if the name matches
            if (bar.name.includes("Denny's Blue Angel")) {
                bar.lat = 40.01258;
                bar.lng = -80.74317;
            }

            const card = document.createElement("div");
            card.className = "card";
            
            // NAVIGATION FIX: Use the actual address text for the Rocket Ship
            const destination = encodeURIComponent(`${bar.name} ${bar.address}`);
            const navUrl = `https://www.google.com/maps/dir/?api=1&destination=${destination}`;

            card.innerHTML = `
                <a href="${navUrl}" target="_blank" style="float:right; text-decoration:none; font-size:35px;">🚀</a>
                <span class="price" style="color:#28a745; font-weight:bold;">${bar.special}</span>
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
