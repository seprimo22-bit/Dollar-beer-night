// ===============================
//   Dollar Beer Night – map.js
// ===============================

// Blue/white tile layer
const tileLayer = L.tileLayer(
  "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
  {
    attribution: "&copy; OpenStreetMap & Carto",
    maxZoom: 19
  }
);

// Initialize map
const map = L.map("map", {
  zoomControl: true,
  scrollWheelZoom: true
});

// Add tile layer
tileLayer.addTo(map);

// Try to center on user location
navigator.geolocation.getCurrentPosition(
  (pos) => {
    const userLat = pos.coords.latitude;
    const userLng = pos.coords.longitude;
    map.setView([userLat, userLng], 12);
    loadBars(userLat, userLng);
  },
  () => {
    // Fallback center (Youngstown)
    map.setView([41.0998, -80.6495], 11);
    loadBars(41.0998, -80.6495);
  }
);

// ===============================
// Load bars from backend
// ===============================
function loadBars(userLat, userLng) {
  fetch(`/get_specials/${currentDay}`)
    .then((res) => res.json())
    .then((bars) => {
      bars.forEach((bar) => {
        // If coordinates exist, use them directly
        if (bar.latitude && bar.longitude) {
          if (withinRadius(userLat, userLng, bar.latitude, bar.longitude, 45)) {
            addMarker(bar);
          }
        } else {
          // Otherwise try geocoding
          geocodeBar(bar, userLat, userLng);
        }
      });
    });
}

// ===============================
// Add marker to map
// ===============================
function addMarker(bar) {
  L.marker([bar.latitude, bar.longitude])
    .addTo(map)
    .bindPopup(`<b>${bar.name}</b><br>${bar.deal}`);
}

// ===============================
// Geocode fallback
// ===============================
function geocodeBar(bar, userLat, userLng) {
  fetch(
    `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
      bar.address
    )}&format=json&limit=1`
  )
    .then((res) => res.json())
    .then((data) => {
      if (data.length > 0) {
        const lat = parseFloat(data[0].lat);
        const lon = parseFloat(data[0].lon);

        if (withinRadius(userLat, userLng, lat, lon, 45)) {
          bar.latitude = lat;
          bar.longitude = lon;
          addMarker(bar);
        }
      }
    })
    .catch(() => {});
}

// ===============================
// Radius filter (miles)
// ===============================
function withinRadius(lat1, lon1, lat2, lon2, miles) {
  const R = 3958.8; // Earth radius in miles
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c <= miles;
}

// ===============================
// Tap-to-drop-pin for adding bars
// ===============================
map.on("click", function (e) {
  const lat = e.latlng.lat.toFixed(6);
  const lon = e.latlng.lng.toFixed(6);

  // Auto-fill the Add Special form
  const latField = document.getElementById("latitude");
  const lonField = document.getElementById("longitude");

  if (latField && lonField) {
    latField.value = lat;
    lonField.value = lon;
  }

  L.marker([lat, lon])
    .addTo(map)
    .bindPopup("New bar location selected.")
    .openPopup();
});
