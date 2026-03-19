let bars = [];

function loadBars() {
    fetch("/api/bars/Monday") // Load all bars for management, can extend to all days if needed
        .then(response => response.json())
        .then(data => {
            bars = data;
            renderTable();
        });
}

function renderTable() {
    const tbody = document.querySelector("#bars-table tbody");
    tbody.innerHTML = "";
    bars.forEach(bar => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td><input type="text" value="${bar.name}" data-id="${bar.id}" class="edit-name"></td>
            <td><input type="text" value="${bar.address}" data-id="${bar.id}" class="edit-address"></td>
            <td><input type="text" value="${bar.deal}" data-id="${bar.id}" class="edit-deal"></td>
            <td>
                <select data-id="${bar.id}" class="edit-day">
                    <option ${bar.day==='Monday'?'selected':''}>Monday</option>
                    <option ${bar.day==='Tuesday'?'selected':''}>Tuesday</option>
                    <option ${bar.day==='Wednesday'?'selected':''}>Wednesday</option>
                    <option ${bar.day==='Thursday'?'selected':''}>Thursday</option>
                    <option ${bar.day==='Friday'?'selected':''}>Friday</option>
                    <option ${bar.day==='Saturday'?'selected':''}>Saturday</option>
                    <option ${bar.day==='Sunday'?'selected':''}>Sunday</option>
                </select>
            </td>
            <td><input type="checkbox" data-id="${bar.id}" class="edit-paid" ${bar.paid?'checked':''}></td>
            <td>
                <button class="save-btn" data-id="${bar.id}">Save</button>
                <button class="delete-btn" data-id="${bar.id}">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Attach event listeners
    document.querySelectorAll(".save-btn").forEach(btn => {
        btn.addEventListener("click", () => saveBar(btn.dataset.id));
    });

    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", () => deleteBar(btn.dataset.id));
    });
}

function saveBar(id) {
    const bar = {
        id: id,
        name: document.querySelector(`.edit-name[data-id='${id}']`).value,
        address: document.querySelector(`.edit-address[data-id='${id}']`).value,
        deal: document.querySelector(`.edit-deal[data-id='${id}']`).value,
        day: document.querySelector(`.edit-day[data-id='${id}']`).value,
        paid: document.querySelector(`.edit-paid[data-id='${id}']`).checked
    };

    fetch("/api/add_bar", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(bar)
    }).then(() => loadBars());
}

function deleteBar(id) {
    fetch(`/api/delete_bar/${id}`, {method: "DELETE"})
        .then(() => loadBars());
}

document.getElementById("admin-add-bar-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = {};
    formData.forEach((v,k) => data[k] = k==="paid" ? this.elements[k].checked : v);

    fetch("/api/add_bar", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    }).then(() => {
        this.reset();
        loadBars();
    });
});

// Initial load
window.onload = loadBars;
