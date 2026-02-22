const API = "/api/specials";

async function addSpecial() {
    const bar = document.getElementById("bar").value;
    const deal = document.getElementById("deal").value;
    const location = document.getElementById("location").value;
    const day = document.getElementById("day").value;

    await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bar, deal, location, day })
    });

    loadSpecials();
}

async function loadSpecials() {
    const day = document.getElementById("day").value;

    const res = await fetch(`${API}?day=${day}`);
    const specials = await res.json();

    const list = document.getElementById("specialsList");
    list.innerHTML = "";

    specials.forEach(s => {
        list.innerHTML += `
            <div>
                <strong>${s.bar}</strong> — ${s.deal}<br>
                ${s.location}
            </div>
        `;
    });
}

document.getElementById("addBtn").onclick = addSpecial;
document.getElementById("findBtn").onclick = loadSpecials;
