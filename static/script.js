async function loadSpecials() {

    try {

        const res = await fetch('/api/specials');

        const specials = await res.json();

        const today = new Date()

            .toLocaleDateString('en-US', { weekday: 'long' })

            .trim()

            .toLowerCase();

        const list = document.getElementById('specials-list');

        list.innerHTML = '';

        const filtered = specials.filter(s =>

            s.day && s.day.trim().toLowerCase() === today

        );

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

        body: JSON.stringify({

            barName,

            deal,

            location,

            day: new Date().toLocaleDateString('en-US', { weekday: 'long' })

        })

    });

    loadSpecials();

    document.getElementById('barName').value = '';

    document.getElementById('deal').value = '';

    document.getElementById('location').value = '';

}

window.onload = loadSpecials;