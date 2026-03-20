let map, vectorSource, vectorLayer, popupOverlay, dropPinFeature;

function initMap() {
    vectorSource = new ol.source.Vector({});
    vectorLayer = new ol.layer.Vector({ source: vectorSource });

    const container = document.createElement("div");
    container.id = "popup";
    container.style.backgroundColor = "white";
    container.style.padding = "6px";
    container.style.border = "1px solid black";
    container.style.borderRadius = "4px";
    container.style.minWidth = "160px";
    container.style.position = "absolute";
    container.style.display = "none";
    document.body.appendChild(container);

    popupOverlay = new ol.Overlay({
        element: container,
        positioning: "bottom-center",
        stopEvent: true,
        offset: [0, -12]
    });

    map = new ol.Map({
        target: "map",
        layers: [
            new ol.layer.Tile({ source: new ol.source.OSM() }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([-84.5555, 41.0379]),
            zoom: 10
        }),
        overlays: [popupOverlay]
    });

    // Click marker → popup
    map.on("singleclick", function (evt) {
        const feature = map.forEachFeatureAtPixel(evt.pixel, f => f);
        if (feature && feature !== dropPinFeature) {
            const coords = feature.getGeometry().getCoordinates();
            const name = feature.get("name");
            const deal = feature.get("deal");
            const address = feature.get("address");
            const paid = feature.get("paid");

            popupOverlay.setPosition(coords);
            container.innerHTML = `
                <b>${name}</b><br>${deal}<br>
                ${paid ? "<span style='color:gold;'>★ Featured</span><br>" : ""}
                <a href="https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(address)}" target="_blank">Navigate</a>
            `;
            container.style.display = "block";
        } else {
            container.style.display = "none";
        }
    });

    // Double-click map → drop pin for new bar
    map.on("dblclick", function (evt) {
        const coords = evt.coordinate;
        if (dropPinFeature) vectorSource.removeFeature(dropPinFeature);

        dropPinFeature = new ol.Feature({
            geometry: new ol.geom.Point(coords),
            name: "New Bar",
            deal: "",
            address: ""
        });

        dropPinFeature.setStyle(new ol.style.Style({
            image: new ol.style.Icon({
                color: "#ff5722",
                crossOrigin: "anonymous",
                src: "https://openlayers.org/en/v7.5.0/examples/data/dot.png",
                scale: 1.2
            })
        }));

        vectorSource.addFeature(dropPinFeature);

        const [lng, lat] = ol.proj.toLonLat(coords);

        // Fill hidden lat/lng fields for backend
        document.querySelector("input[name='lat']").value = lat;
        document.querySelector("input[name='lng']").value = lng;

        alert("Pin dropped! Enter bar name, address, deal, and click Add.");
    });
}

// Load bars from backend
function loadBars(bars) {
    vectorSource.clear();

    bars.forEach(bar => {
        if (bar.lat && bar.lng) {
            const feature = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([bar.lng, bar.lat])),
                name: bar.name,
                deal: bar.deal,
                address: bar.address || bar.name,
                paid: bar.paid
            });

            const style = new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 8,
                    fill: new ol.style.Fill({ color: bar.paid ? "#f1c40f" : "#1976d2" }),
                    stroke: new ol.style.Stroke({ color: "#fff", width: 2 })
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
        view.animate({
            center: ol.proj.fromLonLat([bar.lng, bar.lat]),
            zoom: 14,
            duration: 500
        });
    }
}

window.loadBars = loadBars;
window.focusBar = focusBar;

initMap();
