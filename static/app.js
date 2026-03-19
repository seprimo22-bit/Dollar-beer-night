function addSpecial() {

    const bar = document.getElementById("bar").value;
    const address = document.getElementById("address").value;
    const deal = document.getElementById("deal").value;
    const day = document.getElementById("day").value;

    if (!bar || !deal || !day) {
        alert("Missing fields");
        return;
    }

    fetch("/add_special", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bar_name: bar,
            address: address,
            deal: deal,
            day: day
        })
    })
    .then(res => res.json())
    .then(() => {
        alert("Saved");
        loadDay(day);
    });
}

function loadDay(day) {
    loadBars(day);
}
