const map = L.map('map').setView([41.0998, -80.6495], 11);
let markers = [];

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'© OpenStreetMap'
}).addTo(map);

function clearMarkers(){
    markers.forEach(m=>map.removeLayer(m));
    markers=[];
}

function loadDay(day){
    fetch(`/get_specials/${day}`)
    .then(r=>r.json())
    .then(data=>{
        clearMarkers();
        const results=document.getElementById("results");
        results.innerHTML="";

        data.forEach(s=>{
            results.innerHTML += `
                <div class="deal-card">
                    <b>${s.bar_name}</b><br>
                    ${s.deal}
                </div>
            `;

            if(s.latitude && s.longitude){
                const m=L.marker([s.latitude,s.longitude])
                    .addTo(map)
                    .bindPopup(`<b>${s.bar_name}</b><br>${s.deal}`);
                markers.push(m);
            }
        });

        if(markers.length){
            const group=new L.featureGroup(markers);
            map.fitBounds(group.getBounds(),{padding:[40,40]});
        }
    });
}
