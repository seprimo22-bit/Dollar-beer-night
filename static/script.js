let map;
let markers = [];
let userLocation = { lat: 41.0998, lng: -80.6495 }; // fallback
let barData = [];
let selectedDay = null;

const daysOfWeek = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

function initDayBubbles() {
  const container = document.getElementById("day-bubbles");
  container.innerHTML = "";
  daysOfWeek.forEach(day => {
    const bubble = document.createElement("button");
    bubble.className = "day-bubble";
    bubble.innerText = day.slice(0,3);
    bubble.addEventListener("click", () => selectDay(day));
    container.appendChild(bubble);
  });
  // auto-select today
  const today = new Date();
  const todayName = daysOfWeek[today.getDay() === 0 ? 6 : today.getDay()-1];
  selectDay(todayName);
}

function selectDay(day) {
  selectedDay = day;
  document.querySelectorAll(".day-bubble").forEach(b => {
    b.classList.toggle("active", b.innerText === day.slice(0,3));
  });
  loadDeals();
}

async function loadBarsFromDatabase() {
  try {
    const res = await fetch('/get-bars');
    if(!res.ok) throw new Error("Failed fetching bars");
    barData = await res.json();
    initDayBubbles(); // triggers render
  } catch(err) {
    console.error(err);
    document.getElementById("deals-list").innerText = "Failed to load deals.";
  }
}

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: userLocation,
    zoom: 13
  });
  loadBarsFromDatabase();
}

function loadDeals() {
  if(!selectedDay) return;
  clearMarkers();
  const filtered = barData.filter(bar => bar.deals[selectedDay]);
  filtered.forEach(bar => {
    const marker = new google.maps.Marker({
      position: { lat: bar.lat, lng: bar.lng },
      map: map,
      title: bar.bar
    });
    marker.addListener("click", () => renderDeals([bar]));
    markers.push(marker);
  });
  renderDeals(filtered);
}

function renderDeals(bars) {
  const list = document.getElementById("deals-list");
  list.innerHTML = "";
  bars.forEach(bar => {
    const div = document.createElement("div");
    div.className = "deal";
    div.innerHTML = `<h3>${bar.bar}</h3>
                     <p><strong>${selectedDay}:</strong> ${bar.deals[selectedDay]}</p>`;
    list.appendChild(div);
  });
}

function clearMarkers() {
  markers.forEach(m => m.setMap(null));
  markers = [];
}

document.getElementById("nearMeBtn").addEventListener("click", () => {
  if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(pos => {
      userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      map.setCenter(userLocation);
      new google.maps.Marker({ position: userLocation, map: map, title: "You are here" });
    }, () => alert("Could not get location."));
  } else alert("Geolocation not supported.");
});
