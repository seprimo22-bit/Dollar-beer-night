function addSpecial(){

    const payload={
        bar_name:document.getElementById("bar").value,
        address:document.getElementById("address").value,
        deal:document.getElementById("deal").value,
        day:document.getElementById("day").value
    };

    fetch("/add_special",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
    })
    .then(r=>r.json())
    .then(res=>{
        if(res.success){
            alert("Saved!");
            loadDay(payload.day);
        }else{
            alert("Save failed");
        }
    });
}
