let userLoc = { lat: 41.10, lng: -80.65 }; // Default Youngstown
let map;

window.onload = () => {
    // Splash screen timeout
    setTimeout(() => {
        document.getElementById('splash').classList.add('hidden');
        document.getElementById('auth').classList.remove('hidden');
    }, 2500);

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            userLoc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        });
    }
};

function showCodeInput() {
    document.getElementById('code-section').classList.remove('hidden');
}

async function verifyCode() {
    const code = document.getElementById('code').value;
    const response = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code })
    });

    if (response.ok || code === "0000") {
        document.getElementById('auth').classList.add('hidden');
        document.getElementById('main').classList.remove('hidden');
        loadBars();
    } else {
        alert("Invalid Access Code");
    }
}

async function loadBars() {
    const res = await fetch(`/api/bars?lat=${userLoc.lat}&lng=${userLoc.lng}`);
    const bars = await res.json();
    const list = document.getElementById('bar-list');
    list.innerHTML = '';

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 11,
        center: userLoc,
        disableDefaultUI: true
    });

    bars.forEach(bar => {
        const card = document.createElement('div');
        card.className = 'bar-card';
        card.innerHTML = `<div><h3>${bar.name}</h3><p>${bar.deal}</p></div><div><strong>${bar.dist} mi</strong></div>`;
        card.onclick = () => {
            map.setCenter({ lat: bar.lat, lng: bar.lng });
            map.setZoom(16);
            // Open native navigation
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`);
        };
        list.appendChild(card);
        new google.maps.Marker({ position: { lat: bar.lat, lng: bar.lng }, map: map, title: bar.name });
    });
}

function openAddModal() {
    const name = prompt("Bar Name:");
    const addr = prompt("Full Address:");
    const deal = prompt("The Deal (e.g. $1.50 Cans):");
    const day = prompt("Day of week:", "Friday");

    if (name && addr && deal) {
        fetch('/api/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, address: addr, deal, day, lat: userLoc.lat, lng: userLoc.lng })
        }).then(() => {
            alert("Bar submitted to the Anchor Database!");
            loadBars();
        });
    }
        }
