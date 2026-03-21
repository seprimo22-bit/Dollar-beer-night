const saveBtn = document.getElementById("saveBtn");
const saveMsg = document.getElementById("saveMsg");

saveBtn.addEventListener("click", () => {
  const bar = document.getElementById("barName").value;
  const deal = document.getElementById("deal").value;
  const location = document.getElementById("location").value;

  if (!bar || !deal || !location) {
    saveMsg.textContent = "Fill everything out.";
    return;
  }

  saveBtn.disabled = true;
  saveMsg.textContent = "Saving...";

  // Temporary local simulation
  setTimeout(() => {
    saveMsg.textContent = "Saved ✔ (backend next step)";
    saveBtn.disabled = false;

    document.getElementById("barName").value = "";
    document.getElementById("deal").value = "";
    document.getElementById("location").value = "";
  }, 800);
});
