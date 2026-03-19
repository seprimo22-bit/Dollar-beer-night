// Current day default
document.addEventListener("DOMContentLoaded", () => {
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    const today = new Date();
    const dayName = days[today.getDay()];
    document.getElementById("day-notice").innerText = `Today is ${dayName}`;
    loadDay(dayName);
});

function addSpecial() {
    const bar = document.getElementById("bar").value.trim();
    const address = document.getElementById("address").value.trim();
    const deal = document.getElementById("deal").value.trim();
    const day = document.getElementById("day").value.trim();

    if (!bar || !deal || !day) {
        alert("Bar, deal, and day required.");
        return;
    }

    fetch("/add_special", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bar_name: bar, address: address, deal: deal, day: day })
    })
    .then(res => res.json())
    .then(res => {
        if (!res.success) {
            alert("Save failed.");
            return;
        }
        alert("Saved!");
        loadDay(day);
    });
}

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
