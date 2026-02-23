function loadSpecials(day) {
    fetch(`/get_specials/${day}`)
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("results");
            list.innerHTML = "";

            if (!data.length) {
                list.innerHTML = "<li>No deals found.</li>";
                return;
            }

            data.forEach(item => {
                const li = document.createElement("li");
                const badge = item.verified ? " ✔ Verified" : "";
                li.innerText = `${item.bar_name} — ${item.deal}${badge}`;
                list.appendChild(li);
            });
        });
}


function addSpecial() {
    const bar_name = document.getElementById("bar_name").value;
    const deal = document.getElementById("deal").value;
    const day = document.getElementById("day").value;

    fetch("/add_special", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({bar_name, deal, day})
    })
    .then(() => alert("Added! Pending verification."));
}
