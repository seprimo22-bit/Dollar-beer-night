let userLoc = null;
let map;

window.onload = () => {
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
        initApp();
    }
}

async function initApp() {
    const res = await fetch(`/api/bars?lat=${userLoc?.lat || ''}&lng=${userLoc?.lng || ''}`);
    const bars = await res.json();
    const list = document.getElementById('bar-list');
    map = new google.maps.Map(document.getElementById('map'), {zoom: 10, center: userLoc || {lat: 41.1, lng: -80.6}});

    bars.forEach(bar => {
        const card = document.createElement('div');
        card.className = 'bar-card';
        card.innerHTML = `<h3>${bar.name}</h3><p>${bar.deal}</p><span>${bar.dist} mi</span>`;
        card.onclick = () => {
            map.setCenter({lat: bar.lat, lng: bar.lng});
            map.setZoom(15);
        };
        list.appendChild(card);
        new google.maps.Marker({position: {lat: bar.lat, lng: bar.lng}, map, title: bar.name});
    });
}

function showAddForm() {
    const name = prompt("Bar Name:");
    const address = prompt("Address:");
    const deal = prompt("Special:");
    const day = "Friday"; 
    fetch('/api/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, address, deal, day, lat: userLoc?.lat, lng: userLoc?.lng})
    }).then(() => alert("Bar Added to Database"));
}
