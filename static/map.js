let map = L.map('map').setView([41.0998, -80.6495], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let markers = [];

function clearMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
}

function loadDay(day) {
    fetch(`/get_specials/${day}`)
        .then(r => r.json())
        .then(data => {

            let html = "";
            clearMarkers();

            data.forEach(s => {
                const badge = s.verified
                    ? "✔ Verified"
                    : "⏳ Pending";

                html += `<p>${s.bar_name} — ${s.deal} <b>${badge}</b></p>`;

                if (s.latitude && s.longitude) {
                    let marker = L.marker([s.latitude, s.longitude])
                        .addTo(map)
                        .bindPopup(`${s.bar_name}<br>${s.deal}`);

                    markers.push(marker);
                }
            });

            document.getElementById("results").innerHTML =
                html || "No deals yet.";
        });
}

function addSpecial() {
    fetch("/add_special", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            bar_name: bar.value,
            deal: deal.value,
            day: day.value
        })
    })
    .then(r => r.json())
    .then(res => alert(res.status));
}
