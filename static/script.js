const API = "/api/specials";

async function addSpecial() {
    const bar = document.getElementById("bar").value;
    const deal = document.getElementById("deal").value;
    const location = document.getElementById("location").value;
    const day = document.getElementById("day").value;

    if (!bar || !deal || !location || !day) {
        alert("Fill everything out.");
        return;
    }

    const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bar, deal, location, day })
    });

    const result = await res.json();

    if (result.status === "duplicate") {
        alert("Already listed.");
    } else {
        alert("Special added.");
        loadSpecials();
    }
}

async function loadSpecials() {
    const day = document.getElementById("day").value;

    const res = await fetch(`${API}?day=${day}`);
    const specials = await res.json();

    const box = document.getElementById("specialsList");

    if (!specials.length) {
        box.innerHTML = `No specials listed for ${day}.`;
        return;
    }

    box.innerHTML = specials
        .map(s => `
            <div>
                <strong>${s.bar}</strong><br>
                ${s.deal}<br>
                ${s.location}<br><br>
            </div>
        `)
        .join("");
}

document.getElementById("addBtn").onclick = addSpecial;
document.getElementById("findBtn").onclick = loadSpecials;
