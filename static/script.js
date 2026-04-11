let map, markers = [];

document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today);
});

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    list.innerHTML = `<p style="text-align:center;">Loading ${day} deals...</p>`;
    
    try {
        // 1. Fetch the verified bars from your moved JSON file
        const jsonResponse = await fetch('/static/specials.json');
        const jsonBars = await jsonResponse.json();
        
        // 2. Fetch user-added bars from your PostgreSQL (via app.py)
        // Note: You must have a route in app.py for '/get_bars'
        const dbResponse = await fetch(`/get_bars?day=${day}`);
        const dbBars = dbResponse.ok ? await dbResponse.json() : [];

        // Combine both lists
        const allBars = [...jsonBars.filter(b => b.day === day), ...dbBars];
        
        list.innerHTML = ""; 
        markers.forEach(m => m.setMap(null));
        markers = [];

        if (allBars.length === 0) {
            list.innerHTML = `<p style="text-align:center;">No deals today.</p>`;
            return;
        }

        allBars.forEach(bar => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `<span class="price">${bar.special}</span><strong>${bar.name}</strong><br><small>${bar.address}</small>`;
            card.onclick = () => {
                if (map) { map.setCenter({ lat: bar.lat, lng: bar.lng }); map.setZoom(16); }
            };
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
        list.innerHTML = `<p style="color:red; text-align:center;">Make sure specials.json is in the STATIC folder!</p>`;
    }
}
