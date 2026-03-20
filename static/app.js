let userLoc = null;
let map;
let markers = {};

window.onload = () => {
    // 2-second Splash Anchor
    setTimeout(() => {
        document.getElementById('splash').classList.add('hidden');
        document.getElementById('auth').classList.remove('hidden');
    }, 2000);

    navigator.geolocation.getCurrentPosition(p => {
        userLoc = {lat: p.coords.latitude, lng: p.coords.longitude};
    });
};

async function verifyCode() {
    const code = document.getElementById('code').value;
    const res = await fetch('/api/verify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code})
    });
    if (res.ok) {
        document.getElementById('auth').classList.add('hidden');
        document.getElementById('main').classList.remove('hidden');
        loadDashboard();
    } else {
        alert("Invalid Access Code");
    }
}

async function loadDashboard() {
    const res = await fetch(`/api/bars?lat=${userLoc?.lat || ''}&lng=${userLoc?.lng || ''}`);
    const bars = await res.json();
    
    const list = document.getElementById('bar-list');
    list.innerHTML = '';
    
    // Initialize Map centered on user or Youngstown
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: userLoc || {lat: 41.10, lng: -80.65},
        disableDefaultUI: true
    });

    bars.forEach(bar => {
        // Create Card
        const card = document.createElement('div');
        card.className = 'bar-card';
        card.innerHTML = `<div><h3>${bar.name}</h3><p>${bar.deal}</p></div><strong>${bar.dist} mi</strong>`;
        
        // Marker Logic
        const marker = new google.maps.Marker({
            position: {lat: bar.lat, lng: bar.lng},
            map: map,
            title: bar.name
        });

        // Click Card -> Center Map on Pin
        card.onclick = () => {
            map.panTo(marker.getPosition());
            map.setZoom(15);
        };

        // Click Marker -> Open Navigation
        marker.addListener('click', () => {
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`);
        });

        list.appendChild(card);
    });
}
