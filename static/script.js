let map, autocomplete, selectedPlace;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13, center: { lat: 41.099, lng: -80.649 }
    });

    // Auto-search for adding bars
    const input = document.getElementById("bar-search");
    if (input) {
        autocomplete = new google.maps.places.Autocomplete(input);
        autocomplete.addListener("place_changed", () => {
            selectedPlace = autocomplete.getPlace();
        });
    }
    loadBars();
}

async function loadBars(day = "") {
    const res = await fetch(`/api/specials?day=${day}`);
    const bars = await res.json();
    const list = document.getElementById("specialsList");
    list.innerHTML = "";

    bars.forEach(bar => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `<strong>${bar.name}</strong><br><span style="color:green;">${bar.special}</span><br><small>${bar.address}</small>`;
        list.appendChild(div);
        
        new google.maps.Marker({
            position: { lat: bar.lat, lng: bar.lng },
            map: map,
            title: bar.name
        });
    });
}
