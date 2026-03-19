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
