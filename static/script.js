const API = "/api/specials";

async function addSpecial() {
    const bar = document.getElementById("bar").value;
    const deal = document.getElementById("deal").value;
    const location = document.getElementById("location").value;
    const day = document.getElementById("day").value;

    if (!bar || !deal || !location || !day) {
        alert("Fill everything out.");
        return;
    }

    const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bar, deal, location, day })
    });

    const result = await res.json();

    if (result.status === "duplicate") {
        alert("Already listed.");
    } else {
        alert("Special added.");
        loadSpecials();
    }
}

async function loadSpecials() {
    const day = document.getElementById("day").value;

    const res = await fetch(`${API}?day=${day}`);
    const specials = await res.json();

    const box = document.getElementById("specialsList");

    if (!specials.length) {
        box.innerHTML = `No specials listed for ${day}.`;
        return;
async function loadSpecials() {
    try fetch("/api/add-special")
fetch("/api/specials?day=" + day)

        const today = new Date().toLocaleString('en-US', {
            weekday: 'long'
        });

        const filtered = specials.filter(s =>
            s.day && s.day.toLowerCase() === today.toLowerCase()
        );

        const list = document.getElementById('specials-list');
        list.innerHTML = '';

        if (!filtered.length) {
            list.innerHTML = `<p>No specials listed for ${today}.</p>`;
            return;
        }

        filtered.forEach(s => {
            const div = document.createElement('div');
            div.innerHTML = `
                <strong>${s.barName}</strong><br>
                ${s.deal}<br>
                <small>${s.location}</small>
            `;
            list.appendChild(div);
        });

    } catch (err) {
        console.error(err);
    }
}


function initMap() {
    const map = L.map('map').setView([41.0998, -80.6495], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;

                map.setView([userLat, userLng], 13);

                L.marker([userLat, userLng])
                    .addTo(map)
                    .bindPopup("You are here")
                    .openPopup();
            },
            function(error) {
                console.log("Geolocation denied:", error);
            }
        );
    }
}

    box.innerHTML = specials
        .map(s => `
            <div>
                <strong>${s.bar}</strong><br>
                ${s.deal}<br>
                ${s.location}<br><br>
            </div>
        `)
        .join("");
}

document.getElementById("addBtn").onclick = addSpecial;
document.getElementById("findBtn").onclick = loadSpecials;

window.onload = () => {
    loadSpecials();
    initMap();
};function initMap() {
  if (!navigator.geolocation) return;

  navigator.geolocation.getCurrentPosition(pos => {
    const lat = pos.coords.latitude;
    const lon = pos.coords.longitude;

    const map = L.map('map').setView([lat, lon], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    L.marker([lat, lon])
      .addTo(map)
      .bindPopup("You are here")
      .openPopup();

    fetch('/api/specials')
      .then(r => r.json())
      .then(data => {
        data.forEach(s => {
          if (s.lat && s.lon) {
            L.marker([s.lat, s.lon])
              .addTo(map)
              .bindPopup(`${s.bar}<br>${s.deal}`);
          }
        });
      });
  });
}

window.onload = initMap;
