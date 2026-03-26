let map, markers = [], barData = [], selectedDay = null, pinMarker = null;
const userLocation = { lat: 41.0998, lng: -80.6495 };
const daysOfWeek = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: userLocation,
        zoom: 13
    });

    // Click to drop a pin
    map.addListener("click", e => {
        if(pinMarker) pinMarker.setMap(null);
        pinMarker = new google.maps.Marker({
            position: e.latLng,
            map: map,
            title: "New Bar Pin"
        });
    });

    loadBarsFromDatabase();
}

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

    // Auto-select today
    const today = new Date();
    const todayName = daysOfWeek[today.getDay() === 0 ? 6 : today.getDay()-1];
    selectDay(todayName);
}

function selectDay(day) {
    selectedDay = day;
    document.querySelectorAll(".day-bubble").forEach(b => b.classList.toggle("active", b.innerText === day.slice(0,3)));
    renderBars();
}

async function loadBarsFromDatabase() {
    try {
        const res = await fetch("/get-bars");
        if(!res.ok) throw new Error("Failed fetching bars");
        barData = await res.json();
        initDayBubbles();
        initAddBarForm();
    } catch(err) {
        console.error(err);
        document.getElementById("deals-list").innerText = "Failed to load deals.";
    }
}

function renderBars() {
    clearMarkers();
    const list = document.getElementById("deals-list");
    list.innerHTML = "";

    barData.forEach(bar => {
        if(bar.deals[selectedDay]){
            const marker = new google.maps.Marker({
                position: { lat: bar.lat, lng: bar.lng },
                map: map,
                title: bar.bar
            });
            markers.push(marker);

            marker.addListener("click", () => {
                list.innerHTML = `<div class="deal"><h3>${bar.bar}</h3><p><strong>${selectedDay}:</strong> ${bar.deals[selectedDay]}</p></div>`;
            });

            // Add to list below map
            const div = document.createElement("div");
            div.className = "deal";
            div.innerHTML = `<h3>${bar.bar}</h3><p><strong>${selectedDay}:</strong> ${bar.deals[selectedDay]}</p>`;
            list.appendChild(div);
        }
    });
}

function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

document.getElementById("nearMeBtn").addEventListener("click", () => {
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(pos => {
            const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
            map.setCenter(loc);
            new google.maps.Marker({ position: loc, map: map, title: "You are here" });
        }, () => alert("Could not get location."));
    } else alert("Geolocation not supported.");
});

function initAddBarForm() {
    const dealDiv = document.getElementById("dealInputs");
    dealDiv.innerHTML = "";
    daysOfWeek.forEach(day => {
        const input = document.createElement("input");
        input.type = "text";
        input.placeholder = `${day} deal`;
        input.id = `deal-${day}`;
        dealDiv.appendChild(input);
    });

    document.getElementById("addBarForm").addEventListener("submit", async e => {
        e.preventDefault();
        const bar = document.getElementById("barName").value;
        const address = document.getElementById("address").value.trim();
        let lat, lng;

        if(pinMarker){
            lat = pinMarker.getPosition().lat();
            lng = pinMarker.getPosition().lng();
        } else if(address){
            // Geocode the address
            const geocoder = new google.maps.Geocoder();
            const res = await new Promise((resolve, reject) => {
                geocoder.geocode({ address }, (results, status) => {
                    if(status === "OK" && results[0]){
                        resolve(results[0].geometry.location);
                    } else reject(status);
                });
            }).catch(err => { alert("Failed to locate address: "+err); return null; });

            if(!res) return;
            lat = res.lat();
            lng = res.lng();
        } else {
            alert("Please provide an address or drop a pin.");
            return;
        }

        const deals = {};
        daysOfWeek.forEach(day => {
            const val = document.getElementById(`deal-${day}`).value.trim();
            if(val) deals[day] = val;
        });
        if(!bar || !lat || !lng || Object.keys(deals).length === 0){
            alert("Fill bar name, coordinates, and at least one deal.");
            return;
        }

        try{
            const response = await fetch("/add-bar", {
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body: JSON.stringify({bar,lat,lng,deals})
            });
            const data = await response.json();
            if(data.success){
                barData.push({bar,lat,lng,deals});
                renderBars();
                document.getElementById("addBarForm").reset();
                if(pinMarker){ pinMarker.setMap(null); pinMarker = null; }
                alert("Bar added! Visible immediately.");
            } else alert("Failed to add bar: "+data.error);
        } catch(err){
            console.error(err);
            alert("Error adding bar");
        }
    });
}
