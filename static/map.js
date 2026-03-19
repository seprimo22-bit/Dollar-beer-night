let map, vectorLayer, vectorSource;

function initMap() {
    vectorSource = new ol.source.Vector({});
    vectorLayer = new ol.layer.Vector({ source: vectorSource });

    map = new ol.Map({
        target: "map",
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([-84.5555, 41.0379]), // default center (Youngstown)
            zoom: 10
        })
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

// Click a bar from list
function focusBar(bar) {
    if (bar.lat && bar.lng) {
        const view = map.getView();
        view.animate({ center: ol.proj.fromLonLat([bar.lng, bar.lat]), zoom: 14, duration: 500 });
    }
}

window.loadBars = loadBars;
window.focusBar = focusBar;

// initialize map when script loads
initMap();
