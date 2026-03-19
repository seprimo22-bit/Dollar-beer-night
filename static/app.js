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
        body: JSON.stringify({
            bar_name: bar,
            address: address,
            deal: deal,
            day: day
        })
    })
    .then(res => res.json())
    .then(res => {

        if (!res.success) {
            alert("Save failed.");
            return;
        }

        alert("Saved!");

        loadDay(day); // 🔥 THIS is what makes buttons + map work together
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
                div.innerHTML = `<b>${bar.bar_name}</b><br>${bar.deal}<hr>`;
                results.appendChild(div);

            });

            // 🔥 ALSO update map
            if (window.loadBars) {
                loadBars(day);
            }

        });
}
