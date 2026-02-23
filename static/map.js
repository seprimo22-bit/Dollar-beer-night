let map = L.map('map').setView([41.0998, -80.6495], 12);
let markers = [];
let currentDay = null;

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);


// CLEAR MARKERS
function clearMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
}


// LOAD DAY DATA
function loadDay(day) {

    currentDay = day;

    fetch(`/get_specials/${day}`)
        .then(r => r.json())
        .then(data => {

            clearMarkers();

            const results = document.getElementById("results");
            results.innerHTML = "";

            if (data.length === 0) {
                results.innerHTML = "<p>No deals yet.</p>";
                return;
            }

            data.forEach(s => {

                const badge = s.verified
                    ? `<span class="badge">✔ Verified</span>`
                    : `<span class="badge">⏳ Pending</span>`;

                const card = `
                    <div class="deal-card">
                        <div class="bar-name">${s.bar_name} ${badge}</div>
                        <div class="deal-text">${s.deal}</div>
                        <div style="font-size:12px;color:#777;">
                            ${s.address || ""}
                        </div>
                    </div>
                `;

                results.innerHTML += card;

                if (s.latitude && s.longitude) {
                    let marker = L.marker([s.latitude, s.longitude])
                        .addTo(map)
                        .bindPopup(`
                            <b>${s.bar_name}</b><br>
                            ${s.deal}<br>
                            ${s.address || ""}
                        `);

                    marker.on("click", () => {
                        window.open(
                            `https://www.google.com/maps?q=${s.latitude},${s.longitude}`,
                            "_blank"
                        );
                    });

                    markers.push(marker);
                }
            });

            // Auto zoom
            if (markers.length > 0) {
                let group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds(), { padding: [40, 40] });
            }
        });
}


// ADD SPECIAL
function addSpecial() {

    const barName = document.getElementById("bar").value;
    const address = document.getElementById("address").value;
    const dealText = document.getElementById("deal").value;
    const dayText = document.getElementById("day").value;

    fetch("/add_special", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            bar_name: barName,
            address: address,
            deal: dealText,
            day: dayText
        })
    })
    .then(r => r.json())
    .then(res => {

        alert(res.status);

        document.getElementById("bar").value = "";
        document.getElementById("address").value = "";
        document.getElementById("deal").value = "";
        document.getElementById("day").value = "";

        if (currentDay) loadDay(currentDay);
    });
}
