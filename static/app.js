// Load today's specials on page load
document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toLocaleString('en-US', { weekday: 'long' });
    loadDay(today);
});

// Load bars for a specific day
function loadDay(day) {
    fetch(`/get_specials/${day}`)
        .then(res => res.json())
        .then(data => {
            const results = document.getElementById("results");
            results.innerHTML = "";

            data.forEach(bar => {
                const div = document.createElement("div");
                div.innerHTML = `<b>${bar.bar_name}</b> - ${bar.deal}`;
                div.onclick = () => {
                    if (window.focusBar) window.focusBar(bar);
                };
                results.appendChild(div);
            });

            if (window.loadBars) window.loadBars(data);
        });
}

// Add or update a special
function addSpecial() {
    const bar = document.getElementById("bar").value.trim();
    const address = document.getElementById("address").value.trim();
    const deal = document.getElementById("deal").value.trim();
    const day = document.getElementById("day").value.trim();

    if (!bar || !deal || !day) {
        alert("Bar, deal, and day are required.");
        return;
    }

    // Check if the address contains coordinates from map pin
    let lat = null, lng = null;
    const coordMatch = address.match(/Lat:\s*([-+]?\d*\.\d+),\s*Lng:\s*([-+]?\d*\.\d+)/i);
    if (coordMatch) {
        lat = parseFloat(coordMatch[1]);
        lng = parseFloat(coordMatch[2]);
    }

    fetch("/add_special", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bar_name: bar, address, deal, day, lat, lng })
    })
    .then(res => res.json())
    .then(res => {
        if (!res.success) {
            alert("Save failed.");
            return;
        }
        alert("Saved!");
        // Clear form
        document.getElementById("bar").value = "";
        document.getElementById("address").value = "";
        document.getElementById("deal").value = "";
        document.getElementById("day").value = "";

        loadDay(day);
    });
}

// Bind globally
window.loadDay = loadDay;
window.addSpecial = addSpecial;
