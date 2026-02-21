async function loadSpecials() {
    try {
        const res = await fetch('/api/specials');
        const specials = await res.json();

        const today = new Date().toLocaleString('en-US', {
            weekday: 'long'
        });

        const filtered = specials.filter(s =>
            s.day && s.day.toLowerCase() === today.toLowerCase()
        );

        const list = document.getElementById('specials-list');
        list.innerHTML = '';

        if (!filtered.length) {
            list.innerHTML = `<p>No specials listed for ${today}.</p>`;
            return;
        }

        filtered.forEach(s => {
            const div = document.createElement('div');
            div.innerHTML = `
                <strong>${s.barName}</strong><br>
                ${s.deal}<br>
                <small>${s.location}</small>
            `;
            list.appendChild(div);
        });

    } catch (err) {
        console.error(err);
    }
}


function initMap() {
    const map = L.map('map').setView([41.0998, -80.6495], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;

                map.setView([userLat, userLng], 13);

                L.marker([userLat, userLng])
                    .addTo(map)
                    .bindPopup("You are here")
                    .openPopup();
            },
            function(error) {
                console.log("Geolocation denied:", error);
            }
        );
    }
}


window.onload = () => {
    loadSpecials();
    initMap();
};
document.addEventListener("DOMContentLoaded", () => {
    initMap();
});
