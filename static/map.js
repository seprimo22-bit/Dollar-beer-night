// --------------------------
// MAP INITIALIZATION
// --------------------------
const map = L.map('map').setView([41.0998, -80.6495], 12);
let markers = [];
let currentDay = null;

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);


// --------------------------
// CLEAR MARKERS
// --------------------------
function clearMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
}


// --------------------------
// LOAD SPECIALS FOR DAY
// --------------------------
function loadDay(day) {

    if (!day) return;

    currentDay = day;

    fetch(`/get_specials/${day}`)
        .then(res => res.json())
        .then(data => {

            clearMarkers();

            const results = document.getElementById("results");
            results.innerHTML = "";

            if (!data.length) {
                results.innerHTML = "<p>No deals yet.</p>";
                return;
            }

            data.forEach(s => {

                // Deal list display
                results.innerHTML += `
                    <div class="deal-card">
                        <b>${s.bar_name}</b><br>
                        ${s.deal}<br>
                        ${s.address || ""}
                    </div>
                `;

                // Map markers
                if (s.latitude && s.longitude) {
                    const marker = L.marker([s.latitude, s.longitude])
                        .addTo(map)
                        .bindPopup(`<b>${s.bar_name}</b><br>${s.deal}`);

                    markers.push(marker);
                }
            });

            // Fit map bounds if markers exist
            if (markers.length) {
                const group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds(), { padding: [40, 40] });
            }
        })
        .catch(err => {
            console.error("Load error:", err);
        });
}


// --------------------------
// ADD SPECIAL
// --------------------------
function addSpecial() {

    const barName = document.getElementById("bar").value.trim();
    const addressVal = document.getElementById("address").value.trim();
    const dealVal = document.getElementById("deal").value.trim();
    const dayVal = document.getElementById("day").value.trim();

    if (!barName || !dealVal || !dayVal) {
        alert("Bar name, deal, and day are required.");
        return;
    }

    fetch("/add_special", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bar_name: barName,
            address: addressVal,
            deal: dealVal,
            day: dayVal
        })
    })
    .then(res => res.json())
    .then(res => {

        if (!res.success) {
            alert("Save failed.");
            return;
        }

        alert("Saved!");

        // Clear form
        document.getElementById("bar").value = "";
        document.getElementById("address").value = "";
        document.getElementById("deal").value = "";
        document.getElementById("day").value = "";

        // Refresh map immediately
        loadDay(dayVal);
    })
    .catch(err => {
        console.error("Save error:", err);
        alert("Server error.");
    });
}
