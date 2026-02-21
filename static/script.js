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

    } function initMap() {
    const map = L.map('map').setView([41.0998, -80.6495], 11); // Youngstown area

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

window.onload = () => {
    loadSpecials();
    initMap();
};
