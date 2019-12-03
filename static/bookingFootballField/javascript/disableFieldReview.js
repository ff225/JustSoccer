function DisableField() {
    document.getElementById("id_utente").disabled = true;
}

window.onload = DisableField

function enableField() {
    document.getElementById("id_utente").disabled = false;
}