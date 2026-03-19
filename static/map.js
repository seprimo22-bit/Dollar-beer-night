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
// VECTOR LAYER FOR MARKERS
// ===============================

let markerLayer = new ol.layer.Vector({
  source: new ol.source.Vector()
});

map.addLayer(markerLayer);

// ===============================
// LOAD BARS AND SHOW ON MAP
// ===============================

window.loadBars = async function(day) {
  try {
    const res = await fetch(`/get_specials/${day}`);
    const bars = await res.json();

    // Clear old markers
    markerLayer.getSource().clear();

    const features = [];

    bars.forEach(bar => {
      if (!bar.lat || !bar.lng) return;

      const marker = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([bar.lng, bar.lat])),
        name: bar.bar_name,
        deal: bar.deal
      });

      features.push(marker);
    });

    markerLayer.getSource().addFeatures(features);

    // Auto zoom to fit all markers
    if (features.length > 0) {
      const extent = ol.extent.createEmpty();
      features.forEach(f => ol.extent.extend(extent, f.getGeometry().getExtent()));
      map.getView().fit(extent, { padding: [50, 50, 50, 50], maxZoom: 16 });
    }

  } catch (err) {
    console.error("Error loading bars:", err);
  }
};

// ===============================
// CLICK TO ADD TEMP PIN (OPTIONAL)
// ===============================

let tempPinLayer = null;
let selectedCoords = null;

map.on("click", function(evt) {
  const lonLat = ol.proj.toLonLat(evt.coordinate);
  selectedCoords = lonLat;

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

  const latField = document.getElementById("lat");
  const lngField = document.getElementById("lng");

  if (latField && lngField) {
    latField.value = lonLat[1];
    lngField.value = lonLat[0];
  }
});

// ===============================
// EXPORT SELECTED COORDS
// ===============================

window.getSelectedCoords = () => selectedCoords;
