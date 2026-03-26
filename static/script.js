let map;
let markers = [];

function initMap(lat=39.0, lng=-77.0) {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: lat, lng: lng },
        zoom: 10
    });
}

function loadBars(day=null) {
    fetch(`/api/bars${day ? '?day=' + day : ''}`)
        .then(res => res.json())
        .then(data => {
            const barList = document.getElementById("bar-list");
            barList.innerHTML = "";
            markers.forEach(m => m.setMap(null));
            markers = [];
            data.forEach(bar => {
                const div = document.createElement("div");
                div.className = "bar-item";
                div.innerHTML = `<strong>${bar.name}</strong> - ${bar.special} <br> ${bar.address}`;
                div.onclick = () => map.panTo({ lat: bar.latitude, lng: bar.longitude });
                barList.appendChild(div);

                const marker = new google.maps.Marker({
                    position: { lat: bar.latitude, lng: bar.longitude },
                    map: map,
                    title: bar.name
                });
                marker.addListener("click", () => window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.latitude},${bar.longitude}`));
                markers.push(marker);
            });
        });
}

// Add bar modal
function showAddBarForm() { document.getElementById("add-bar-form").style.display = "block"; }
function closeAddBarForm() { document.getElementById("add-bar-form").style.display = "none"; }

function submitBar() {
    const data = {
        name: document.getElementById("bar-name").value,
        address: document.getElementById("bar-address").value,
        latitude: document.getElementById("bar-lat").value,
        longitude: document.getElementById("bar-lng").value,
        day: document.getElementById("bar-day").value,
        special: document.getElementById("bar-special").value
    };
    fetch("/api/bars/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    }).then(res => res.json())
      .then(resp => {
          if(resp.status === "success") {
              alert("Bar added!");
              closeAddBarForm();
              loadBars(data.day);
          } else {
              alert("Error: " + resp.message);
          }
      });
}

// Init map with default location
window.onload = () => {
    initMap();
    loadBars(); // load today's bars if needed
};
