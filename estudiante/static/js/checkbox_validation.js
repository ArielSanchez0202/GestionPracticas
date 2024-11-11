document.addEventListener('DOMContentLoaded', function () {
    const practica1Checkbox = document.getElementById('practica1');
    const practica2Checkbox = document.getElementById('practica2');

    // Verificar si ya se ha registrado "Práctica I" o "Práctica II" para el estudiante
    fetch('/estudiante/api/verificar_practica1/')
        .then(response => response.json())
        .then(data => {
            const practica1Existente = data.existe_practica1;
            const practica2Existente = data.existe_practica2;

            // Si ya tiene "Práctica I", deshabilitar el checkbox de "Práctica I"
            if (practica1Existente) {
                practica1Checkbox.disabled = true;
                practica1Checkbox.checked = true; // Preseleccionar si ya existe
            }

            // Si ya tiene "Práctica II", deshabilitar el checkbox de "Práctica II"
            if (practica2Existente) {
                practica2Checkbox.disabled = true;
                practica2Checkbox.checked = true; // Preseleccionar si ya existe
            }

            // Si no tiene "Práctica I", deshabilitar "Práctica II"
            if (!practica1Existente) {
                practica2Checkbox.disabled = true;
            }
        });

    // Lógica para manejar el cambio de "Práctica I"
    practica1Checkbox.addEventListener('change', function () {
        if (this.checked) {
            practica2Checkbox.disabled = false;  // Habilitar "Práctica II"
        } else {
            practica2Checkbox.checked = false;
            practica2Checkbox.disabled = true;  // Deshabilitar "Práctica II" si "Práctica I" no está seleccionada
        }
    });

    // Lógica para manejar el cambio de "Práctica II"
    practica2Checkbox.addEventListener('change', function () {
        if (this.checked) {
            if (!practica1Checkbox.checked) {
                alert("Debes inscribir una 'Práctica I' antes de inscribir una 'Práctica II'.");
                this.checked = false;  // Desmarcar "Práctica II" si "Práctica I" no está seleccionada
            }
        }
    });z
});
