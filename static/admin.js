async function loadAdminBars() {
  try {
    const res = await fetch("/api/admin/bars");
    const data = await res.json();
    if (!data.success) return;

    const tbody = document.querySelector("#admin-bars-table tbody");
    tbody.innerHTML = "";

    data.bars.forEach((b) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${b.id}</td>
        <td>${b.name}</td>
        <td>${b.deal}</td>
        <td>${b.day_of_week}</td>
        <td>${b.address}</td>
        <td>${b.city || ""}</td>
        <td>${b.state || ""}</td>
        <td>${b.zip_code || ""}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
  }
}

document.addEventListener("DOMContentLoaded", loadAdminBars);
