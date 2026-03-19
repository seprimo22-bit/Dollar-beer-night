let map;
let markers = [];
let currentDay = new Date().toLocaleString("en-US", { weekday: "long" });

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 41.0998, lng: -80.6495 }, // Youngstown default
        zoom: 12
    });

    google.maps.event.addListener(map, "click", function(event) {
        openForm(event.latLng);
    });

    loadBars(currentDay);
    highlightDayButton(currentDay);
}

function loadBars(day) {
    fetch(`/api/bars/${day}`)
        .then(response => response.json())
        .then(data => {
            clearMarkers();
            const barList = document.getElementById("bar-list");
            barList.innerHTML = "";

            data.sort((a,b) => b.paid - a.paid); // Paid bars first

            data.forEach(bar => {
                const marker = new google.maps.Marker({
                    position: { lat: bar.lat, lng: bar.lng },
                    map: map,
                    title: bar.name
                });
                markers.push(marker);

                const barDiv = document.createElement("div");
                barDiv.className = bar.paid ? "bar paid" : "bar";
                barDiv.textContent = `${bar.name} - ${bar.deal}`;
                barList.appendChild(barDiv);

                barDiv.addEventListener("click", () => {
                    map.setCenter(marker.getPosition());
                    map.setZoom(15);
                });
            });
        });
}

function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

document.querySelectorAll("#days button").forEach(button => {
    button.addEventListener("click", () => {
        currentDay = button.dataset.day;
        loadBars(currentDay);
        highlightDayButton(currentDay);
    });
});

function highlightDayButton(day) {
    document.querySelectorAll("#days button").forEach(btn => {
        btn.style.backgroundColor = btn.dataset.day === day ? "#ffcc00" : "";
    });
}

function openForm(latLng) {
    const form = document.getElementById("add-bar-form");
    form.style.display = "block";
    document.querySelector("input[name=lat]").value = latLng.lat();
    document.querySelector("input[name=lng]").value = latLng.lng();
}

function closeForm() {
    document.getElementById("add-bar-form").style.display = "none";
}

document.getElementById("new-bar-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = {};
    formData.forEach((v,k) => data[k] = isNaN(v)? v : parseFloat(v));

    fetch("/api/add_bar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    }).then(() => {
        closeForm();
        loadBars(currentDay);
    });
});

// Initialize Map after DOM load
window.onload = initMap;
