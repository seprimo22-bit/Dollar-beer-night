let map, vectorSource, vectorLayer, popupOverlay;

function initMap() {
    vectorSource = new ol.source.Vector({});
    vectorLayer = new ol.layer.Vector({ source: vectorSource });

    // Popup div
    const container = document.createElement("div");
    container.id = "popup";
    container.style.backgroundColor = "white";
    container.style.padding = "6px";
    container.style.border = "1px solid black";
    container.style.borderRadius = "4px";
    container.style.position = "absolute";
    container.style.display = "none";
    container.style.minWidth = "120px";
    document.body.appendChild(container);

    popupOverlay = new ol.Overlay({
        element: container,
        positioning: 'bottom-center',
        stopEvent: true,
        offset: [0, -10]
    });

    map = new ol.Map({
        target: "map",
        layers: [
            new ol.layer.Tile({ source: new ol.source.OSM() }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([-84.5555, 41.0379]), // default center
            zoom: 10
        }),
        overlays: [popupOverlay]
    });

    // Click on marker to show popup
    map.on("singleclick", function(evt) {
        const feature = map.forEachFeatureAtPixel(evt.pixel, f => f);
        if (feature) {
            const coords = feature.getGeometry().getCoordinates();
            popupOverlay.setPosition(coords);
            const name = feature.get("name");
            const deal = feature.get("deal");
            container.innerHTML = `<b>${name}</b><br>${deal}`;
            container.style.display = "block";
        } else {
            container.style.display = "none";
        }
    });
}

function loadBars(bars) {
    vectorSource.clear();
    bars.forEach(bar => {
        if (bar.lat && bar.lng) {
            const feature = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([bar.lng, bar.lat])),
                name: bar.bar_name,
                deal: bar.deal
            });

            const style = new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 8,
                    fill: new ol.style.Fill({ color: '#ff0000' }),
                    stroke: new ol.style.Stroke({ color: '#fff', width: 2 })
                })
            });

            feature.setStyle(style);
            vectorSource.addFeature(feature);
        }
    });
}

function focusBar(bar) {
    if (bar.lat && bar.lng) {
        const view = map.getView();
        view.animate({ center: ol.proj.fromLonLat([bar.lng, bar.lat]), zoom: 14, duration: 500 });
    }
}

window.loadBars = loadBars;
window.focusBar = focusBar;

// Initialize map
initMap();
