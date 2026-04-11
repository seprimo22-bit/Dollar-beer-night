let map, markers = [];

// This runs as soon as the page opens, regardless of API status
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
            disableDefaultUI: true
        });
        console.log("Map API loaded successfully.");
    } catch (e) {
        console.log("Map API failed or is offline. Continuing with list only.");
        document.getElementById("map").innerHTML = "<p style='text-align:center; padding:20px;'>Map unavailable offline.</p>";
    }
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    
    try {
        // Pulls from your specials.json
        const response = await fetch('/specials.json');
        const allSpecials = await response.json();
        
        const dailyDeals = allSpecials.filter(item => item.day === day);
        list.innerHTML = ""; 

        if (dailyDeals.length === 0) {
            list.innerHTML = `<p style="text-align:center; padding:20px;">No specials found for ${day}.</p>`;
            return;
        }

        dailyDeals.forEach(bar => {
            const card = document.createElement("div");
            card.className = "card";
            // If map exists, click card to center it. If not, card still works as info.
            card.onclick = () => {
                if (map) {
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

            // Add Pin only if map loaded
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
        list.innerHTML = `<p style="text-align:center; color:red;">Error loading list. Check specials.json location.</p>`;
    }
}
