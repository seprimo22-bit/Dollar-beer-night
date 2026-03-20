// Google Maps integration

let map;
let markers = {};
let longPressTimeout = null;

function initMap() {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  map = new google.maps.Map(mapEl, {
    center: { lat: 39.8283, lng: -98.5795 }, // USA center
    zoom: 4,
    styles: [
      {
        featureType: "poi",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "transit",
        stylers: [{ visibility: "off" }],
      },
    ],
  });

  // Long press to add bar
  map.addListener("mousedown", (e) => {
    longPressTimeout = setTimeout(() => {
      if (typeof addBarFromMap === "function") {
        addBarFromMap(e.latLng.lat(), e.latLng.lng());
      }
    }, 700);
  });

  map.addListener("mouseup", () => {
    if (longPressTimeout) {
      clearTimeout(longPressTimeout);
      longPressTimeout = null;
    }
  });

  onMapReady();
}

function setMapCenter(lat, lng) {
  if (!map) return;
  map.setCenter({ lat, lng });
  map.setZoom(12);
}

function updateMapMarkers(bars) {
  if (!map) return;

  // Clear old markers
  Object.values(markers).forEach((m) => m.setMap(null));
  markers = {};

  bars.forEach((bar) => {
    const marker = new google.maps.Marker({
      position: { lat: bar.lat, lng: bar.lng },
      map,
      title: bar.name,
    });

    const info = new google.maps.InfoWindow({
      content: `
        <div style="font-size: 13px;">
          <strong>${bar.name}</strong><br/>
          ${bar.deal}<br/>
          ${bar.address || ""}
        </div>
      `,
    });

    marker.addListener("click", () => {
      info.open(map, marker);
      if (typeof highlightBarCard === "function") {
        highlightBarCard(bar.id);
      }
      openNavigation(bar.lat, bar.lng);
    });

    markers[bar.id] = marker;
  });
}

function focusMarkerOnBar(barId) {
  const marker = markers[barId];
  if (!marker || !map) return;
  map.panTo(marker.getPosition());
  map.setZoom(15);
}

function openNavigation(lat, lng) {
  const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
  window.open(url, "_blank");
}
