async function loadSpecials() {
    try {
        const res = await fetch('/api/specials');
        const specials = await res.json();

        const list = document.getElementById('specials-list');
        list.innerHTML = '';

        if (!specials.length) {
            list.innerHTML = "<p>No specials yet.</p>";
            return;
        }

        specials.forEach(s => {
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

async function submitSpecial() {
    const barName = document.getElementById('barName').value;
    const deal = document.getElementById('deal').value;
    const location = document.getElementById('location').value;

    if (!barName || !deal || !location) {
        alert("Fill all fields.");
        return;
    }

    await fetch('/api/specials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ barName, deal, location })
    });

    loadSpecials();

    document.getElementById('barName').value = '';
    document.getElementById('deal').value = '';
    document.getElementById('location').value = '';
}
