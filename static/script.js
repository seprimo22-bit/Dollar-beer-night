let map;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 40.4406, lng: -79.9959}, // default: Pittsburgh
        zoom: 12
    });
    loadSpecials(getToday());
}

function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

function loadSpecials(day) {
    fetch(`/get_specials?day=${day}`)
        .then(res => res.json())
        .then(data => {
            const barList = document.getElementById('bar-list');
            barList.innerHTML = '';
            clearMarkers();
            data.forEach(bar => {
                const div = document.createElement('div');
                div.className = 'bar-item';
                div.innerHTML = `<strong>${bar.name}</strong> - ${bar.deal} - ${bar.address}`;
                div.onclick = () => {
                    map.setCenter({lat: parseFloat(bar.lat), lng: parseFloat(bar.lng)});
                    map.setZoom(15);
                };
                barList.appendChild(div);

                const marker = new google.maps.Marker({
                    position: {lat: parseFloat(bar.lat), lng: parseFloat(bar.lng)},
                    map: map,
                    title: bar.name
                });
                marker.addListener('click', () => {
                    window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`);
                });
                markers.push(marker);
            });
        });
}

function getToday() {
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    return days[new Date().getDay()];
}

document.addEventListener('DOMContentLoaded', () => {
    initMap();

    // Day selector buttons
    document.querySelectorAll('.day-selector button').forEach(btn => {
        btn.addEventListener('click', () => {
            loadSpecials(btn.getAttribute('data-day'));
        });
    });

    // Manual bar entry
    document.getElementById('manual-form').addEventListener('submit', e => {
        e.preventDefault();
        alert('Manual bar addition not yet connected to backend. Admin panel can be used.');
    });
});
