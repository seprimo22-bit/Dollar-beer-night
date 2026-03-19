// ===============================
// GLOBAL MAP INITIALIZATION
// ===============================

const map = new ol.Map({
  target: "map",
  layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM({
        url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      })
    })
  ],
  view: new ol.View({
    center: ol.proj.fromLonLat([-98.5795, 39.8283]), // USA center
    zoom: 4
  })
});

// ===============================
// TAP-TO-DROP-PIN FEATURE
// ===============================

let tempPinLayer = null;
let selectedCoords = null;

map.on("click", function (evt) {
  const lonLat = ol.proj.toLonLat(evt.coordinate);
  selectedCoords = lonLat;

  // Remove old temp pin
  if (tempPinLayer) map.removeLayer(tempPinLayer);

  const pin = new ol.Feature({
    geometry: new ol.geom.Point(evt.coordinate)
  });

  tempPinLayer = new ol.layer.Vector({
    source: new ol.source.Vector({
      features: [pin]
    })
  });

  map.addLayer(tempPinLayer);

  // Autofill form fields if they exist
  const latField = document.getElementById("lat");
  const lngField = document.getElementById("lng");

  if (latField && lngField) {
    latField.value = lonLat[1];
    lngField.value = lonLat[0];
  }
});

// ===============================
// LOAD EXISTING BARS FROM BACKEND
// ===============================

async function loadBars() {
  try {
    const res = await fetch("/api/bars");
    const bars = await res.json();

    bars.forEach(bar => {
      if (!bar.lat || !bar.lng) return;

      const marker = new ol.Feature({
        geometry: new ol.geom.Point(
          ol.proj.fromLonLat([bar.lng, bar.lat])
        )
      });

      const layer = new ol.layer.Vector({
        source: new ol.source.Vector({
          features: [marker]
        })
      });

      map.addLayer(layer);

      // Optional: flyTo behavior when clicking cards
      const card = document.getElementById(`bar-${bar.id}`);
      if (card) {
        card.onclick = () => {
          map.getView().animate({
            center: ol.proj.fromLonLat([bar.lng, bar.lat]),
            zoom: 15,
            duration: 600
          });
        };
      }
    });
  } catch (err) {
    console.error("Error loading bars:", err);
  }
}

loadBars();

// ===============================
// EXPORT COORDS FOR SAVE BUTTON
// ===============================

window.getSelectedCoords = () => selectedCoords;
