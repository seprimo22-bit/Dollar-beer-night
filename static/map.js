let map = L.map('map').setView([41.0998, -80.6495], 12);
let markers = [];
let currentDay = null;

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

function clearMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
}

function loadDay(day) {
    currentDay = day;

    fetch(`/get_specials/${day}`)
        .then(r => r.json())
        .then(data => {
            clearMarkers();
            const results = document.getElementById("results");
            results.innerHTML = "";

            if (!data.length) {
                results.innerHTML = "<p>No deals yet.</p>";
                return;
            }

            data.forEach(s => {

                results.innerHTML += `
                    <div class="deal-card">
                        <b>${s.bar_name}</b><br>
                        ${s.deal}<br>
                        ${s.address || ""}
                    </div>
                `;

                if (s.latitude && s.longitude) {
                    let marker = L.marker([s.latitude, s.longitude])
                        .addTo(map)
                        .bindPopup(`<b>${s.bar_name}</b><br>${s.deal}`);

                    markers.push(marker);
                }
            });

            if (markers.length) {
                let group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds(), { padding: [40,40] });
            }
        });
}

function addSpecial() {
    fetch("/add_special", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            bar_name: bar.value,
            address: address.value,
            deal: deal.value,
            day: day.value
        })
    })
    .then(r => r.json())
    .then(() => {
        alert("Saved!");
        if (currentDay) loadDay(currentDay);
    });
}
