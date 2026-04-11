let map;

// RUN IMMEDIATELY
document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'Long' });
    loadBars(today); // Show Papa's, TJ's, etc. right away!
});

function initMap() {
    // This only runs if the Google API actually works
    const centerPoint = { lat: 41.1030, lng: -80.6514 };
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: centerPoint
    });
}

async function loadBars(day) {
    const list = document.getElementById("specialsList");
    
    try {
        const response = await fetch('/static/specials.json');
        const data = await response.json();
        const dailyDeals = data.filter(item => item.day === day);

        list.innerHTML = ""; // Clear the "Loading..." message

        if (dailyDeals.length === 0) {
            list.innerHTML = `<p style="text-align:center;">No specials for ${day}.</p>`;
            return;
        }

        dailyDeals.forEach(bar => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `
                <span class="price">${bar.special}</span>
                <strong>${bar.name}</strong><br>
                <small>${bar.address}</small>
            `;
            list.appendChild(card);
        });
    } catch (e) {
        list.innerHTML = "<p>Error loading bars. Check if specials.json is in the static folder.</p>";
    }
}
