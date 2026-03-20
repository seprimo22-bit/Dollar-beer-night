let userLoc = null;
let map;
let longPressTimeout;

window.onload = () => {
    setTimeout(() => {
        document.getElementById('splash').classList.add('hidden');
        document.getElementById('auth').classList.remove('hidden');
    }, 2000);
    navigator.geolocation.getCurrentPosition(p => {
        userLoc = {lat: p.coords.latitude, lng: p.coords.longitude};
    }, () => { userLoc = {lat: 41.10, lng: -80.65}; });
};

function showCodeInput() { document.getElementById('code-section').classList.remove('hidden'); }

async function verifyCode() {
    if (document.getElementById('code').value === '0000') {
        document.getElementById('auth').classList.add('hidden');
        document.getElementById('main').classList.remove('hidden');
        initApp();
    }
}

async function initApp() {
    const res = await fetch(`/api/bars?lat=${userLoc?.lat || ''}&lng=${userLoc?.lng || ''}`);
    const bars = await res.json();
    const list = document.getElementById('bar-list');
    list.innerHTML = '';

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12, center: userLoc, disableDefaultUI: true,
        styles: [{ featureType: "poi", stylers: [{ visibility: "off" }] }]
    });

    // Blue Angel Long-Press
    map.addListener("mousedown", (e) => {
        longPressTimeout = setTimeout(() => {
            const name = prompt("Bar Name:");
            const deal = prompt("Deal:");
            if (name && deal) submitBar(name, deal, e.latLng.lat(), e.latLng.lng());
        }, 1000);
    });
    map.addListener("mouseup", () => clearTimeout(longPressTimeout));

    bars.forEach(bar => {
        const card = document.createElement('div');
        card.className = 'bar-card';
        card.innerHTML = `<div><h3>${bar.name}</h3><p>${bar.deal}</p></div><strong>${bar.dist} mi</strong>`;
        
        const marker = new google.maps.Marker({ position: {lat: bar.lat, lng: bar.lng}, map: map });
        
        card.onclick = () => { map.panTo(marker.getPosition()); map.setZoom(16); };
        marker.addListener('click', () => {
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`);
        });
        list.appendChild(card);
    });
}

async function submitBar(name, deal, lat, lng) {
    await fetch('/api/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name, deal, lat, lng, day_of_week: "friday", address: "Pinned Location" })
    });
    location.reload();
}
