let map, markers = [];

// FAIL-SAFE: Load bars immediately when the page structure is ready
document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today);
});

function initMap() {
    // This runs in the background. If it fails, the list above still works.
    const centerPoint = { lat: 41.0664, lng: -80.6273 }; // Youngstown/Boardman area
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: centerPoint,
        disableDefaultUI: true
    });
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    
    try {
        // Fetch from your specials.json in the root or static folder
        const response = await fetch('/specials.json'); 
        const allSpecials = await response.json();
        
        // Filter for the selected day
        const dailyDeals = allSpecials.filter(item => item.day === day);
        
        list.innerHTML = ""; // Remove the "Loading" message
        
        if (dailyDeals.length === 0) {
            list.innerHTML = `<p style="text-align:center; padding:20px;">No specials listed for ${day}.</p>`;
            return;
        }

        dailyDeals.forEach(bar => {
            // Create the Card
            const card = document.createElement("div");
            card.className = "card";
            card.onclick = () => {
                if(map) {
                    map.setCenter({ lat: bar.lat, lng: bar.lng });
                    map.setZoom(16);
                }
            };
            card.innerHTML = `
                <span class="price">${bar.special}</span>
                <strong>${bar.name}</strong><br>
                <small>${bar.address}</small>
            `;
            list.appendChild(card);

            // Add Pin if map is ready
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
        console.error("Data error:", err);
        list.innerHTML = `<p style="text-align:center; color:red;">Could not load specials.json. Make sure the file exists in your main folder.</p>`;
    }
}
