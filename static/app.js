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
            alert(res.message || "Save failed.");
            return;
        }

        alert("Saved!");

        // CLEAR INPUTS
        document.getElementById("bar").value = "";
        document.getElementById("address").value = "";
        document.getElementById("deal").value = "";
        document.getElementById("day").value = "";

        // REFRESH DAY RESULTS + MAP
        loadDay(day);

    })
    .catch(() => alert("Server error."));
}
