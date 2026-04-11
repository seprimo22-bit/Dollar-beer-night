let map;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: { lat: 41.0998, lng: -80.6495 }, // Youngstown
        disableDefaultUI: true
    });
    loadBars();
}

async function loadBars(day = "") {
    const res = await fetch(`/api/specials?day=${day}`);
    const data = await res.json();
    const list = document.getElementById("specialsList");
    list.innerHTML = "";

    // Clear old markers
    markers.forEach(m => m.setMap(null));
    markers = [];

    data.forEach(bar => {
        // Add to List
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<strong>${bar.name}</strong><br><span style="color:green;">${bar.special}</span><br><small>${bar.address}</small>`;
        list.appendChild(card);

        // Add to Map
        const marker = new google.maps.Marker({
            position: { lat: bar.lat, lng: bar.lng },
            map: map,
            title: bar.name
        });
        markers.push(marker);
    });
}

