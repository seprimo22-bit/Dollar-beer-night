let map;
let markers = [];

function initMap() {
    const center = { lat: 39.8283, lng: -98.5795 }; // USA center default
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: center
    });
    placeMarkers();
}

function placeMarkers() {
    // Clear previous markers
    markers.forEach(m => m.setMap(null));
    markers = [];

    const bars = document.querySelectorAll('.bar-item:visible, .bar-item');
    bars.forEach(bar => {
        const lat = parseFloat(bar.dataset.lat);
        const lng = parseFloat(bar.dataset.lng);
        if (lat && lng) {
            const marker = new google.maps.Marker({
                position: { lat, lng },
                map: map,
                title: bar.querySelector('h3').innerText
            });
            marker.addListener('click', () => {
                window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`);
            });
            markers.push(marker);
        }
    });
}

// Filter bars by day
function filterDay(day) {
    const items = document.querySelectorAll('.bar-item');
    items.forEach(item => {
        if (item.dataset.day === day) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
    document.querySelectorAll('.day-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.day-btn[onclick="filterDay('${day}')"]`).classList.add('active');
    placeMarkers();
}

// Add bar form
function toggleAddBarForm() {
    const form = document.getElementById('add-bar-form');
    form.style.display = form.style.display === 'none' ? 'flex' : 'none';
}

function submitBar() {
    const name = document.getElementById('bar-name').value;
    const address = document.getElementById('bar-address').value;
    const special = document.getElementById('bar-special').value;
    const day = document.getElementById('bar-day').value;

    fetch('/add_bar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, address, special, day, lat:0, lng:0})
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            alert('Bar added!');
            location.reload();
        } else {
            alert('Error adding bar');
        }
    });
}

// Initialize map on page load
window.onload = initMap;
