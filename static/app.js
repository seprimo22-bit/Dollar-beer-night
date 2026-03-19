let map;
let markers = [];
let currentDay = new Date().toLocaleDateString('en-US', { weekday: 'long' });
let newMarker = null;

function initApp() {
    document.getElementById('splash').style.display = 'block';
    setTimeout(() => {
        document.getElementById('splash').style.display = 'none';
        document.getElementById('main-app').style.display = 'block';
        initMap();
        loadBars(currentDay);
        setupDayButtons();
    }, 1500);
}

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 41.1, lng: -80.65 },
        zoom: 12
    });

    map.addListener('click', (e) => {
        placeNewMarker(e.latLng);
    });
}

function placeNewMarker(latLng) {
    if (newMarker) newMarker.setMap(null);
    newMarker = new google.maps.Marker({
        position: latLng,
        map: map,
        draggable: true
    });
    document.getElementById('add-bar-form').style.display = 'block';
    document.querySelector('input[name="lat"]').value = latLng.lat();
    document.querySelector('input[name="lng"]').value = latLng.lng();
}

function setupDayButtons() {
    document.querySelectorAll('#days button').forEach(btn => {
        btn.addEventListener('click', () => {
            currentDay = btn.getAttribute('data-day');
            loadBars(currentDay);
        });
    });
}

function loadBars(day) {
    fetch(`/get_bars?day=${day}`)
        .then(res => res.json())
        .then(data => {
            clearMarkers();
            const barList = document.getElementById('bar-list');
            barList.innerHTML = '';
            data.forEach(bar => {
                const marker = new google.maps.Marker({
                    position: { lat: bar.lat, lng: bar.lng },
                    map: map,
                    title: bar.name
                });
                markers.push(marker);
                barList.innerHTML += `<div class="bar-item">${bar.name} - ${bar.deal}</div>`;
            });
        });
}

function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

document.getElementById('new-bar-form').addEventListener('submit', function(e){
    e.preventDefault();
    const formData = {
        name: this.name.value,
        address: this.address.value,
        deal: this.deal.value,
        day: this.day.value,
        lat: parseFloat(this.lat.value),
        lng: parseFloat(this.lng.value)
    };
    fetch('/add_bar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    }).then(res => res.json())
      .then(() => {
        document.getElementById('add-bar-form').style.display = 'none';
        loadBars(currentDay);
        if(newMarker) newMarker.setMap(null);
      });
});

function closeForm() {
    document.getElementById('add-bar-form').style.display = 'none';
    if (newMarker) newMarker.setMap(null);
}

window.onload = initApp;
