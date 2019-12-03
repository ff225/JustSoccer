function DisableField() {
    document.getElementById("id_campo").disabled = true;
    document.getElementById("id_cliente").disabled = true;
    document.getElementById("id_data").readOnly = true;
    document.getElementById("id_ora").readOnly = true;
}

window.onload = DisableField()

function enableField() {
    document.getElementById("id_campo").disabled = false;
    document.getElementById("id_cliente").disabled = false;
}
