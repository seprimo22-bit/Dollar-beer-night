let map, vectorSource, vectorLayer, popupOverlay;

function initMap() {
    // Create a vector source and layer for bar markers
    vectorSource = new ol.source.Vector({});
    vectorLayer = new ol.layer.Vector({ source: vectorSource });

    // Create popup overlay
    const container = document.createElement("div");
    container.id = "popup";
    container.style.backgroundColor = "white";
    container.style.padding = "8px";
    container.style.border = "1px solid black";
    container.style.borderRadius = "6px";
    container.style.minWidth = "150px";
    container.style.position = "absolute";
    container.style.display = "none";
    document.body.appendChild(container);

    popupOverlay = new ol.Overlay({
        element: container,
        positioning: 'bottom-center',
        stopEvent: true,
        offset: [0, -12]
    });

    // Initialize the map
    map = new ol.Map({
        target: "map",
        layers: [
            new ol.layer.Tile({ source: new ol.source.OSM() }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([-84.5555, 41.0379]), // Default center
            zoom: 10
        }),
        overlays: [popupOverlay]
    });

    // Click on marker to show popup with Navigate link
    map.on("singleclick", function(evt) {
        const feature = map.forEachFeatureAtPixel(evt.pixel, f => f);
        if (feature) {
            const coords = feature.getGeometry().getCoordinates();
            popupOverlay.setPosition(coords);

            const name = feature.get("name");
            const deal = feature.get("deal");
            const lat = feature.get("lat");
            const lng = feature.get("lng");

            const navUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;

            container.innerHTML = `<b>${name}</b><br>${deal}<br><a href="${navUrl}" target="_blank">Navigate</a>`;
            container.style.display = "block";
        } else {
            container.style.display = "none";
        }
    });
}

// Load bars for a given day and add markers
function loadBars(bars) {
    vectorSource.clear();

    bars.forEach(bar => {
        if (bar.lat && bar.lng) {
            const feature = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([bar.lng, bar.lat])),
                name: bar.bar_name,
                deal: bar.deal,
                lat: bar.lat,
                lng: bar.lng
            });

            // Use a standard pin icon instead of a circle
            const iconStyle = new ol.style.Style({
                image: new ol.style.Icon({
                    anchor: [0.5, 1],
                    src: "https://cdn-icons-png.flaticon.com/512/684/684908.png",
                    scale: 0.05
                })
            });

            feature.setStyle(iconStyle);
            vectorSource.addFeature(feature);
        }
    });

    // Optionally auto-zoom to fit all markers
    if (vectorSource.getFeatures().length > 0) {
        const extent = vectorSource.getExtent();
        map.getView().fit(extent, { padding: [50, 50, 50, 50], maxZoom: 14 });
    }
}

// Focus map on a specific bar when clicking the list
function focusBar(bar) {
    if (bar.lat && bar.lng) {
        const coords = ol.proj.fromLonLat([bar.lng, bar.lat]);
        map.getView().animate({ center: coords, zoom: 14, duration: 500 });

        // Trigger popup for that bar
        const feature = vectorSource.getFeatures().find(f => f.get("name") === bar.bar_name && f.get("deal") === bar.deal);
        if (feature) {
            popupOverlay.setPosition(feature.getGeometry().getCoordinates());
            const navUrl = `https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`;
            document.getElementById("popup").innerHTML = `<b>${bar.bar_name}</b><br>${bar.deal}<br><a href="${navUrl}" target="_blank">Navigate</a>`;
            document.getElementById("popup").style.display = "block";
        }
    }
}

// Expose functions globally for index.html
window.loadBars = loadBars;
window.focusBar = focusBar;

// Initialize map
initMap();
