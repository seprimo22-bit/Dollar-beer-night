
let map;
let markers = [];
let userLocation = { lat: 41.0998, lng: -80.6495 }; // fallback Youngstown
let barData = [];

window.gm_authFailure = function() {
  document.getElementById("map-error").innerText =
    "Google Maps failed to load. Check your API key or API settings.";
};

async function loadBarsFromDatabase() {
  try {
    const response = await fetch('/get-bars');
    if (!response.ok) throw new Error("Network response not ok");
    barData = await response.json();
    loadDeals();
  } catch (err) {
    console.error("Failed to load bar data:", err);
    document.getElementById("deals-list").innerText = "Failed to load deals.";
  }
}

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: userLocation,
    zoom: 13
  });
  loadBarsFromDatabase();
}

function loadDeals(selectedDay = null) {
  const day = selectedDay || document.getElementById("daySelect").value;
  clearMarkers();

  barData.forEach(bar => {
    const marker = new google.maps.Marker({
      position: { lat: bar.lat, lng: bar.lng },
      map: map,
      title: bar.bar
    });

    marker.addListener("click", () => {
      renderDeals([bar], day);
    });

    markers.push(marker);
  });

  renderDeals(barData, day);
}

function renderDeals(bars, day) {
  const list = document.getElementById("deals-list");
  list.innerHTML = "";

  bars.forEach(bar => {
    const div = document.createElement("div");
    div.className = "deal";
    div.innerHTML = `
      <h3>${bar.bar}</h3>
      <p><strong>${day}:</strong> ${bar.deals[day] || "No deal"}</p>
    `;
    list.appendChild(div);
  });
}

function clearMarkers() {
  markers.forEach(m => m.setMap(null));
  markers = [];
}

document.getElementById("nearMeBtn").addEventListener("click", () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      map.setCenter(userLocation);

      new google.maps.Marker({
        position: userLocation,
        map: map,
        title: "You are here"
      });
    }, () => alert("Could not get your location."));
  } else {
    alert("Geolocation is not supported by your browser.");
  }
});

document.getElementById("daySelect").addEventListener("change", function() {
  loadDeals(this.value);
});
