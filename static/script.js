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
        console.error("Error loading specials:", err);
    }
}
