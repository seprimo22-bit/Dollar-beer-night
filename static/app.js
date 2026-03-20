// Handle Add Bar form submission
document.getElementById("new-bar-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};

    formData.forEach((v, k) => {
        data[k] = isNaN(v) ? v : parseFloat(v);
    });

    fetch("/api/add_bar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(() => {
        // Clear form
        this.reset();

        // Reload bars for the current day
        const activeDay = document.querySelector("#days .active")?.dataset.day || "Monday";
        loadBars(activeDay);
    });
});
