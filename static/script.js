function submitBar() {
    const data = {
        name: document.getElementById('bar-name').value,
        lat: document.getElementById('bar-lat').value,
        lng: document.getElementById('bar-lng').value,
        description: document.getElementById('bar-desc').value
    };

    fetch('/add_bar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json())
      .then(resp => {
        if (resp.status === 'success') alert('Bar submitted!');
        else alert('Error submitting bar');
      });
}

function verifyBar(barId) {
    fetch(`/verify_bar/${barId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code: '1616'})
    }).then(res => res.json())
      .then(resp => {
        if (resp.status === 'verified') {
            alert('Bar verified!');
            location.reload();
        } else alert('Verification failed');
      });
}
