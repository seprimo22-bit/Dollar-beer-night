async function loadAdminBars() {
    const res = await fetch('/api/bars');
    const bars = await res.json();
    const tbody = document.getElementById('admin-tbody');
    tbody.innerHTML = '';

    bars.forEach(bar => {
        tbody.innerHTML += `
            <tr>
                <td>${bar.id}</td>
                <td>${bar.name}</td>
                <td>${bar.deal}</td>
                <td>${bar.day_of_week}</td>
                <td>${bar.address}, ${bar.city}, ${bar.state}</td>
                <td>
                    <button class="delete-btn" onclick="deleteBar(${bar.id})">Remove</button>
                </td>
            </tr>`;
    });
}

async function addNewBar() {
    const data = {
        name: document.getElementById('admin-name').value,
        deal: document.getElementById('admin-deal').value,
        day_of_week: document.getElementById('admin-day').value.toLowerCase(),
        address: document.getElementById('admin-address').value,
        city: document.getElementById('admin-city').value,
        state: document.getElementById('admin-state').value,
        zip_code: document.getElementById('admin-zip').value
    };

    const res = await fetch('/api/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    if (res.ok) {
        alert("Bar added to the Beer Dollars network.");
        location.reload();
    }
}

window.onload = loadAdminBars;

