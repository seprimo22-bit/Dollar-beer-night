let map, markers = [];

// This makes the list load IMMEDIATELY when the page opens
document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today);
});

function initMap() {
    try {
        const centerPoint = { lat: 41.0664, lng: -80.6273 }; // Center on Boardman/Youngstown
        map = new google.maps.Map(document.getElementById("map"), {
            zoom: 12,
            center: centerPoint,
            disableDefaultUI: false
        });
    } catch (e) {
        console.log("Map API delayed or offline.");
    }
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    list.innerHTML = `<p style="text-align:center;">Searching ${day} specials...</p>`;
    
    try {
        // Pointing to the root where your file is
        const response = await fetch('/specials.json');
        if (!response.ok) throw new Error("File not found");
        
        const allSpecials = await response.json();
        const dailyDeals = allSpecials.filter(item => item.day === day);
        
        list.innerHTML = ""; 
        markers.forEach(m => m.setMap(null));
        markers = [];

        if (dailyDeals.length === 0) {
            list.innerHTML = `<p style="text-align:center; padding:20px;">No specials listed for ${day}.</p>`;
            return;
        }

        dailyDeals.forEach(bar => {
            const card = document.createElement("div");
            card.className = "card";
            card.onclick = () => {
                if (map) {
                    map.setCenter({ lat: bar.lat, lng: bar.lng });
                    map.setZoom(16);
                    document.getElementById('map').scrollIntoView({ behavior: 'smooth' });
                }
            };

            card.innerHTML = `
                <span class="price">${bar.special}</span>
                <strong>${bar.name}</strong><br>
                <small>${bar.address}</small>
            `;
            list.appendChild(card);

            if (map) {
                const marker = new google.maps.Marker({
                    position: { lat: bar.lat, lng: bar.lng },
                    map: map,
                    title: bar.name
                });
                markers.push(marker);
            }
        });
    } catch (err) {
        // If it still fails, it tells you exactly why
        list.innerHTML = `<p style="text-align:center; color:red;">Could not find specials.json in the main folder.</p>`;
    }
}
