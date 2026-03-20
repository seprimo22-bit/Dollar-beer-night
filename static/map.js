let map;
let markers = {};
let longPressTimeout = null;

function initMap() {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  // Initializing with Youngstown/Austintown area focus
  map = new google.maps.Map(mapEl, {
    center: { lat: 41.10, lng: -80.65 }, 
    zoom: 11,
    disableDefaultUI: true,
    styles: [{ featureType: "poi", stylers: [{ visibility: "off" }] }]
  });

  // Long press to "Drop a Pin" (The Blue Angel Solution)
  map.addListener("mousedown", (e) => {
    longPressTimeout = setTimeout(() => {
      const lat = e.latLng.lat();
      const lng = e.latLng.lng();
      if (confirm(`Add a new bar at these coordinates?`)) {
          showAddForm(lat, lng); 
      }
    }, 800);
  });

  map.addListener("mouseup", () => { clearTimeout(longPressTimeout); });
}

function updateMapMarkers(bars) {
  Object.values(markers).forEach((m) => m.setMap(null));
  markers = {};

  bars.forEach((bar) => {
    const marker = new google.maps.Marker({
      position: { lat: bar.lat, lng: bar.lng },
      map,
      icon: bar.premium ? 'http://maps.google.com/mapfiles/ms/icons/gold-pushpin.png' : null
    });

    marker.addListener("click", () => {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`;
      window.open(url, "_blank");
    });
    markers[bar.id] = marker;
  });
}
