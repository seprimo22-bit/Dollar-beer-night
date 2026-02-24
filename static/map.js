const map = L.map('map').setView([41.0998, -80.6495], 11);
let markers = {};
let markerGroup = [];

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'© OpenStreetMap'
}).addTo(map);

function clearMarkers(){
    markerGroup.forEach(m => map.removeLayer(m));
    markerGroup = [];
    markers = {};
}

function loadDay(day){
    fetch(`/get_specials/${day}`)
    .then(r => r.json())
    .then(data => {

        clearMarkers();
        const results = document.getElementById("results");
        results.innerHTML = "";

        const grouped = {};

        // Group by lat/lon
        data.forEach(s => {
            if(!s.latitude || !s.longitude) return;

            const key = `${s.latitude.toFixed(5)},${s.longitude.toFixed(5)}`;

            if(!grouped[key]){
                grouped[key] = {
                    bar_name: s.bar_name,
                    latitude: s.latitude,
                    longitude: s.longitude,
                    deals: []
                };
            }

            grouped[key].deals.push(s.deal);
        });

        Object.values(grouped).forEach(bar => {

            // Create marker
            const marker = L.marker([bar.latitude, bar.longitude])
                .addTo(map)
                .bindPopup(`
                    <b>${bar.bar_name}</b><br>
                    ${bar.deals.join("<br>")}<br><br>
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${bar.latitude},${bar.longitude}"
                       target="_blank">
                       🧭 Navigate Here
                    </a>
                `);

            markerGroup.push(marker);

            const card = document.createElement("div");
            card.className = "deal-card";
            card.innerHTML = `
                <b>${bar.bar_name}</b><br>
                ${bar.deals.join("<br>")}
            `;

            card.onclick = function(){
                map.flyTo([bar.latitude, bar.longitude], 15);
                marker.openPopup();
            };

            results.appendChild(card);
        });

        if(markerGroup.length){
            const group = new L.featureGroup(markerGroup);
            map.fitBounds(group.getBounds(), { padding:[40,40] });
        }
    });
}
