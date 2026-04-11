let map, markers = [];

document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today);
});

function initMap() {
    const centerPoint = { lat: 41.0664, lng: -80.6273 };
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: centerPoint,
        gestureHandling: "greedy", // Makes map immediately responsive to touch
        mapTypeControl: false,
        streetViewControl: true,
        fullscreenControl: false
    });
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    list.innerHTML = `<p style="text-align:center;">Finding ${day} deals...</p>`;
    
    try {
        const jsonResponse = await fetch('/get_json_bars');
        const jsonBars = await jsonResponse.json();
        
        const dbResponse = await fetch(`/get_db_bars?day=${day}`);
        const dbBars = dbResponse.ok ? await dbResponse.json() : [];

        const filteredJson = jsonBars.filter(item => item.day === day);
        const allBars = [...filteredJson, ...dbBars];
        
        list.innerHTML = ""; 
        markers.forEach(m => m.setMap(null));
        markers = [];

        if (allBars.length === 0) {
            list.innerHTML = `<p style="text-align:center; padding:20px;">No deals for ${day}.</p>`;
            return;
        }

        allBars.forEach(bar => {
            const card = document.createElement("div");
            card.className = "card";
            card.onclick = () => {
                if (map) {
                    map.setCenter({ lat: bar.lat, lng: bar.lng });
                    map.setZoom(17);
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
                    title: bar.name,
                    clickable: true
                });

                // When user clicks the pin, it shows the "Navigate" button natively
                marker.addListener("click", () => {
                    map.setCenter(marker.getPosition());
                    map.setZoom(17);
                });

                markers.push(marker);
            }
        });
    } catch (err) {
        list.innerHTML = `<p style="text-align:center; color:red;">Error loading bars from specials.json.</p>`;
    }
                }
