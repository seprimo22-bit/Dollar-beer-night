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
        center: ol.proj.fromLonLat([-98.5795, 39.8283]), // Center USA
        zoom: 4
    })
});

// ===============================
// VECTOR LAYER TO HOLD PINS
// ===============================
let barLayer = new ol.layer.Vector({
    source: new ol.source.Vector()
});
map.addLayer(barLayer);

// ===============================
// TEMP PIN ON CLICK
// ===============================
let tempPin = null;
map.on("click", function(evt) {
    const coords = ol.proj.toLonLat(evt.coordinate);

    // Remove previous temp pin
    if (tempPin) {
        barLayer.getSource().removeFeature(tempPin);
    }

    tempPin = new ol.Feature({
        geometry: new ol.geom.Point(evt.coordinate)
    });

    barLayer.getSource().addFeature(tempPin);

    // Autofill form
    const latField = document.getElementById("lat");
    const lngField = document.getElementById("lng");

    if (latField && lngField) {
        latField.value = coords[1];
        lngField.value = coords[0];
    }
});

// ===============================
// LOAD BARS FOR GIVEN DAY
// ===============================
async function loadBars(day) {
    try {
        const res = await fetch(`/get_specials/${day}`);
        const bars = await res.json();

        // Clear previous pins
        barLayer.getSource().clear();

        bars.forEach(bar => {
            if (!bar.lat || !bar.lng) return;

            const feature = new ol.Feature({
                geometry: new ol.geom.Point(
                    ol.proj.fromLonLat([bar.lng, bar.lat])
                ),
                name: bar.bar_name,
                deal: bar.deal
            });

            barLayer.getSource().addFeature(feature);
        });

        // Zoom map to fit all pins
        const features = barLayer.getSource().getFeatures();
        if (features.length > 0) {
            const extent = ol.extent.createEmpty();
            features.forEach(f => ol.extent.extend(extent, f.getGeometry().getExtent()));
            map.getView().fit(extent, { padding: [50, 50, 50, 50], maxZoom: 15 });
        }

    } catch (err) {
        console.error("Error loading bars:", err);
    }
}

// ===============================
// EXPORT FUNCTION FOR APP.JS
// ===============================
window.loadBars = loadBars;
