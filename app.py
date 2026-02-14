<!DOCTYPE html>
<html>
<head>
    <title>Dollar Beer Night</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial;
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background: #fafafa;
        }

        input, textarea {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            border: 1px solid #ccc;
        }

        button {
            padding: 12px;
            background: #2e7dff;
            color: white;
            border: none;
            border-radius: 6px;
            margin-top: 10px;
        }

        .card {
            background: #f4f4f4;
            padding: 12px;
            margin-top: 12px;
            border-radius: 8px;
        }
    </style>
</head>

<body>

<h2>🍺 Dollar Beer Night</h2>

<form action="/add" method="POST">
    <input name="bar" placeholder="Bar Name" required>
    <input name="price" placeholder="Price ($1.50 etc)" required>
    <input name="day" placeholder="Day (Saturday etc)" required>
    <textarea name="notes" placeholder="Notes"></textarea>

    <button>Add Special</button>
</form>

<hr>

<button type="button" onclick="findSpecials()">
    Find Specials Near Me
</button>

<div id="results"></div>


<script>
async function findSpecials() {
    const res = await fetch("/specials");
    const data = await res.json();

    let html = "";

    if (data.length === 0) {
        html = "<p>No specials yet.</p>";
    } else {
        data.forEach(d => {
            html += `
            <div class="card">
                <b>${d[0]}</b><br>
                Price: ${d[1]}<br>
                Day: ${d[2]}<br>
                Notes: ${d[3]}
            </div>
            `;
        });
    }

    document.getElementById("results").innerHTML = html;
}
</script>

</body>
</html>
