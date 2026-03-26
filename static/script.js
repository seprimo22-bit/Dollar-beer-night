let map;
let markers = [];
let selectedDay;
let userLocation = { lat: 41.0998, lng: -80.6495 }; // fallback

// Splash verification
document.getElementById("sendCode").addEventListener("click", async () => {
  const number = document.getElementById("phone").value;
  const res = await fetch("/api/send_code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ number })
  });
  const data = await res.json();
  alert(`Code sent: ${data.code}`);
});

document.getElementById("verifyCode").addEventListener("click", () => {
  const code = document.getElementById("codeInput").value;
  if (MASTER_CODES.includes(code) || code === "123456") {
    document.getElementById("splash").style.display = "none";
    document.getElementById("app").style.display = "block";
    autoSelectDay();
    loadBars(selectedDay);
  } else {
    alert("Invalid code");
  }
});

// Day buttons
document.querySelectorAll(".dayBtn").forEach(btn => {
  btn.addEventListener("click", () => {
    selectedDay = btn.dataset.day;
    highlightSelectedDay();
    loadBars(selectedDay);
  });
});

function autoSelectDay() {
  const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
  const today = days[new Date().getDay()];
  selectedDay = today;
  highlightSelectedDay();
}

function highlightSelectedDay() {
  document.querySelectorAll(".dayBtn").forEach(btn => {
    btn.classList.toggle("selected", btn.dataset.day === selectedDay);
  });
}

// Load bars
async function loadBars(day) {
  const res = await fetch(`/api/bars?day=${day}`);
  const bars = await res.json();
  renderBars(bars);
  renderMap(bars);
}

function renderBars(bars) {
  const container = document.getElementById("bars-list");
  container.innerHTML = "";
  bars.forEach(bar => {
    const div = document.createElement("div");
    div.className = "bar";
    div.innerHTML = `<h3>${bar.name}</h3><p>${bar.special || "No deal today"}</p>`;
    div.addEventListener("click", () => {
      if (bar.lat && bar.lng) map.setCenter({ lat: bar.lat, lng: bar.lng });
    });
    container.appendChild(div);
  });
}

function renderMap(bars) {
  if (!map) return;
  markers.forEach(m => m.setMap(null));
  markers = [];
  bars.forEach(bar => {
    if (bar.lat && bar.lng) {
      const marker = new google.maps.Marker({
        position: { lat: bar.lat, lng: bar.lng },
        map,
        title: bar.name
      });
      marker.addListener("click", () => {
        window.open(`https://www.google.com/maps/dir/?api=1&destination=${bar.lat},${bar.lng}`);
      });
      markers.push(marker);
    }
  });
}

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: userLocation,
    zoom: 13
  });
}

// Add bar
document.getElementById("addBarBtn").addEventListener("click", () => {
  document.getElementById("addBarForm").style.display = "block";
});

document.getElementById("submitBar").addEventListener("click", async () => {
  const name = document.getElementById("barName").value;
  const address = document.getElementById("barAddress").value;
  const specials = JSON.parse(document.getElementById("barSpecials").value);

  const res = await fetch("/api/bars", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, address, specials })
  });
  const data = await res.json();
  if (data.success) {
    alert("Bar added!");
    loadBars(selectedDay);
  } else {
    alert("Error adding bar");
  }
});
