let map, markers = [];

document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today);
});

function initMap() {
    const centerPoint = { lat: 41.0664, lng: -80.6273 }; // Boardman/Youngstown area
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: centerPoint
    });
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    list.innerHTML = `<p style="text-align:center;">Loading ${day} specials...</p>`;
    
    try {
        // Pulling from our new Python route
        const jsonResponse = await fetch('/get_json_bars');
        const jsonBars = await jsonResponse.json();
        
        // Pulling user-added bars from the database
        const dbResponse = await fetch(`/get_db_bars?day=${day}`);
        const dbBars = await dbResponse.ok ? await dbResponse.json() : [];

        const filteredJson = jsonBars.filter(item => item.day === day);
        const allBars = [...filteredJson, ...dbBars];
        
        list.innerHTML = ""; 
        markers.forEach(m => m.setMap(null));
        markers = [];

        if (allBars.length === 0) {
            list.innerHTML = `<p style="text-align:center;">No specials listed for ${day}.</p>`;
            return;
        }

        allBars.forEach(bar => {
            const card = document.createElement("div");
            card.className = "card";
            card.onclick = () => {
                if (map) { map.setCenter({ lat: bar.lat, lng: bar.lng }); map.setZoom(16); }
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
        list.innerHTML = `<p style="text-align:center; color:red;">Could not load bars. Make sure specials.json is in your main folder.</p>`;
    }
}
