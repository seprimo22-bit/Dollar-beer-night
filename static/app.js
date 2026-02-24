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
                li.innerText = `${item.bar_name} — ${item.deal}`;
                list.appendChild(li);

                // If map exists, add marker
                if (window.map && item.latitude && item.longitude) {
                    L.marker([item.latitude, item.longitude])
                        .addTo(window.map)
                        .bindPopup(`<b>${item.bar_name}</b><br>${item.deal}`);
                }
            });
        });
}


function addSpecial() {

    const bar_name = document.getElementById("bar").value.trim();
    const address = document.getElementById("address").value.trim();
    const deal = document.getElementById("deal").value.trim();
    const day = document.getElementById("day").value.trim();

    if (!bar_name || !deal || !day) {
        alert("Please fill required fields.");
        return;
    }

    fetch("/add_special", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({bar_name, address, deal, day})
    })
    .then(res => res.json())
    .then(res => {
        if(res.success){
            alert("Saved!");
            loadSpecials(day);   // refresh immediately
        } else {
            alert("Save failed.");
        }
    })
    .catch(() => alert("Server error."));
}
