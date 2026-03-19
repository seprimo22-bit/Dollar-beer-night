let map, vectorSource, vectorLayer, popupOverlay;

// Initialize the map
function initMap() {
    vectorSource = new ol.source.Vector({});
    vectorLayer = new ol.layer.Vector({ source: vectorSource });

    // Popup container
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
        positioning: 'bottom-center',
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
            const name = feature.get("name");
            const deal = feature.get("deal");
            const address = feature.get("address");

            popupOverlay.setPosition(coords);
            container.innerHTML = `<b>${name}</b><br>${deal}<br>
                <a href="https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(address)}" target="_blank">
                Navigate</a>`;
            container.style.display = "block";
        } else {
            container.style.display = "none";
        }
    });
}

// Load bars for a day
function loadBars(bars) {
    vectorSource.clear();

    bars.forEach(bar => {
        if (bar.lat && bar.lng) {
            const feature = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([bar.lng, bar.lat])),
                name: bar.bar_name,
                deal: bar.deal,
                address: bar.address || bar.bar_name
            });

            const style = new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 8,
                    fill: new ol.style.Fill({ color: '#1976d2' }),
                    stroke: new ol.style.Stroke({ color: '#fff', width: 2 })
                })
            });

            feature.setStyle(style);
            vectorSource.addFeature(feature);
        }
    });
}

// Focus map on a bar
function focusBar(bar) {
    if (bar.lat && bar.lng) {
        const view = map.getView();
        view.animate({ center: ol.proj.fromLonLat([bar.lng, bar.lat]), zoom: 14, duration: 500 });
    }
}

// Bind functions globally
window.loadBars = loadBars;
window.focusBar = focusBar;

initMap();

// Load today on start
document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleString('en-US', { weekday: 'long' });
    loadDay(today);
});

// Add new bar
function addSpecial() {
    const bar = document.getElementById("bar").value.trim();
    const address = document.getElementById("address").value.trim();
    const deal = document.getElementById("deal").value.trim();
    const day = document.getElementById("day").value.trim();

    if (!bar || !deal || !day) {
        alert("Bar, deal, and day required.");
        return;
    }

    fetch("/add_special", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bar_name: bar, address, deal, day })
    })
    .then(res => res.json())
    .then(res => {
        if (!res.success) {
            alert("Save failed.");
            return;
        }
        alert("Saved!");
        loadDay(day);
    });
}

// Load bars by day
function loadDay(day) {
    fetch(`/get_specials/${day}`)
        .then(res => res.json())
        .then(data => {
            const results = document.getElementById("results");
            results.innerHTML = "";

            data.forEach(bar => {
                const div = document.createElement("div");
                div.innerHTML = `<b>${bar.bar_name}</b> - ${bar.deal}`;
                div.onclick = () => {
                    if (window.focusBar) window.focusBar(bar);
                };
                results.appendChild(div);
            });

            if (window.loadBars) window.loadBars(data);
        });
}
