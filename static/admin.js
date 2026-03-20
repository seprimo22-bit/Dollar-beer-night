async function loadAdminBars() {
    const res = await fetch('/api/bars'); 
    const bars = await res.json();
    const tbody = document.getElementById('admin-bars-table').querySelector('tbody');
    tbody.innerHTML = '';

    bars.forEach(bar => {
        tbody.innerHTML += `
            <tr>
                <td>${bar.id || 'N/A'}</td>
                <td>${bar.name}</td>
                <td>${bar.deal}</td>
                <td>${bar.day}</td>
                <td>${bar.address}</td>
                <td><button onclick="deleteBar(${bar.id})">Delete</button></td>
            </tr>`;
    });
}

async function addNewBar() {
    const data = {
        name: document.getElementById('admin-name').value,
        deal: document.getElementById('admin-deal').value,
        day: document.getElementById('admin-day').value,
        address: document.getElementById('admin-address').value
    };

    await fetch('/api/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    location.reload();
}

window.onload = loadAdminBars;
