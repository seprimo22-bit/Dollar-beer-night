<!DOCTYPE html>
<html>
<head>
    <title>Dollar Beer Night</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Leaflet Map -->
    <link rel="stylesheet"
      href="https://unpkg.com/leaflet/dist/leaflet.css"/>

    <style>
        body {
            font-family: Arial;
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }

        input, textarea {
            width: 100%;
            padding: 10px;
            margin: 6px 0;
        }

        button {
            padding: 12px;
            background: #2e7dff;
            color: white;
            border: none;
            border-radius: 6px;
            margin-top: 10px;
        }

        #map {
            height: 300px;
            margin-top: 20px;
        }

        .card {
            background: #f4f4f4;
            padding: 10px;
            margin-top: 10px;
            border-radius: 8px;
        }
    </style>
</head>

<body>

<h2>🍺 Dollar Beer Night</h2>

<form action="/add" method="POST">
    <input name="bar" placeholder="Bar Name" required>
    <input name="price" placeholder="Price ($1.50)" required>
    <input name="day" placeholder="Day (Friday etc)" required>
    <textarea name="notes" placeholder="Notes"></textarea>
    <button>Add Special</button>
</form>

<hr>

<button onclick="findSpecials()">Find Specials Near Me</button>

<div id="map"></div>
<div id="results"></div>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<script>
let map;

function initMap(lat, lon) {
    map = L.map('map').setView([lat, lon], 13);

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    ).addTo(map);

    L.marker([lat, lon]).addTo(map)
      .bindPopup("You are here")
      .openPopup();
}

async function findSpecials() {

    navigator.geolocation.getCurrentPosition(async position => {

        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        initMap(lat, lon);

        const res = await fetch("/specials");
        const data = await res.json();

        let html = "";

        if (data.length === 0) {
            html = "<h3>No specials today near you.</h3>";
        } else {
            data.forEach(d => {
                html += `
                <div class="card">
                    <b>${d[0]}</b><br>
                    Price: ${d[1]}<br>
                    Day: ${d[2]}<br>
                    Notes: ${d[3]}
                </div>`;
            });
        }

        document.getElementById("results").innerHTML = html;
    });
}
</script>

</body>
</html>
