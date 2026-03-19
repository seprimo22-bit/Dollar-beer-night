let map, vectorSource, vectorLayer, currentDay;
let markers = {};

function initMap() {
    vectorSource = new ol.source.Vector({});
    vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });

    map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([-80.65, 40.98]), // default center (Youngstown)
            zoom: 12
        })
    });
}

// Add markers from the specials list
function loadBars(day, specials) {
    vectorSource.clear();
    markers = {};

    specials.forEach(bar => {
        if (bar.lat && bar.lng) {
            const marker = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([bar.lng, bar.lat])),
                name: bar.bar_name,
                deal: bar.deal
            });

            vectorSource.addFeature(marker);
            markers[bar.bar_name] = marker;
        }
    });

    if (specials.length > 0) {
        const first = specials[0];
        if (first.lat && first.lng) {
            map.getView().setCenter(ol.proj.fromLonLat([first.lng, first.lat]));
        }
    }
}

// Click on map features to show bar info
mapClickHandler = function() {
    map.on('singleclick', function(evt) {
        map.forEachFeatureAtPixel(evt.pixel, function(feature) {
            alert(`${feature.get('name')} - ${feature.get('deal')}`);
        });
    });
};

// Initialize map immediately
window.onload = function() {
    initMap();
    mapClickHandler();

    // Default to today
    const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const today = new Date().getDay(); // Sunday=0
    loadDay(days[today]);
};
