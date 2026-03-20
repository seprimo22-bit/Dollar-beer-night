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
    if (code === '0000') {
        document.getElementById('auth').classList.add('hidden');
        document.getElementById('main').classList.remove('hidden');
        initApp();
    }
}

async function initApp() {
    const res = await fetch(`/api/bars?lat=${userLoc?.lat || ''}&lng=${userLoc?.lng || ''}`);
    const bars = await res.json();
    const list = document.getElementById('bar-list');
    map = new google.maps.Map(document.getElementById('map'), {zoom: 11, center: userLoc || {lat: 41.1, lng: -80.6}});

    bars.forEach(bar => {
        const card = document.createElement('div');
        card.className = 'bar-card';
        card.innerHTML = `<div><h3>${bar.name}</h3><p>${bar.deal}</p></div><strong>${bar.dist} mi</strong>`;
        card.onclick = () => {
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`);
        };
        list.appendChild(card);
        new google.maps.Marker({position: {lat: bar.lat, lng: bar.lng}, map, title: bar.name});
    });
}
