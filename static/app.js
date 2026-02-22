function loadSpecials(day) {
    fetch(`/get_specials/${day}`)
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById("results");
            list.innerHTML = "";

            data.forEach(item => {
                const li = document.createElement("li");
                li.innerText = `${item.bar_name} - ${item.deal}`;
                list.appendChild(li);
            });
        });
}
