let map, markers = [];

// Load data immediately when page opens
document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today);
});

function initMap() {
    try {
        const centerPoint = { lat: 41.0664, lng: -80.6273 }; // Youngstown/Boardman
        map = new google.maps.Map(document.getElementById("map"), {
            zoom: 12,
            center: centerPoint,
            disableDefaultUI: false
        });
    } catch (e) {
        console.error("Map failed to load. List will still function.");
    }
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    list.innerHTML = `<p style="text-align:center;">Searching ${day} specials...</p>`;
    
    try {
        // Fetch from the static folder
        const response = await fetch('/static/specials.json');
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
            
            // Logic: Click bar to center map
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
        list.innerHTML = `<div class="error">Error loading list. Check if specials.json is in the /static folder.</div>`;
    }
}
