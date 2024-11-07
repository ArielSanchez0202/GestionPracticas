function toggleCheckbox(selectedCheckbox) {
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');

    checkboxes.forEach(checkbox => {
        // Si la checkbox seleccionada es diferente de la actual, la desmarcamos
        if (checkbox !== selectedCheckbox) {
            checkbox.checked = false;
        }
    });
}

// Función para validar que al menos una checkbox esté seleccionada
function validateCheckboxes() {
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');
    const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

    if (!isChecked) {
        alert("Debes seleccionar al menos una práctica.");
        return false; // Evita que el formulario se envíe
    }

    return true; // Permite que el formulario se envíe
}

document.addEventListener('DOMContentLoaded', function () {
    const practica1Checkbox = document.getElementById('practica1');
    const practica2Checkbox = document.getElementById('practica2');

    let practica1Existente = false; // Variable para almacenar si existe la Práctica I

    // Desactivar práctica II inicialmente
    practica2Checkbox.disabled = true;

    // Aquí podrías hacer una solicitud al servidor para verificar si hay registros de "Práctica I"
    fetch('/estudiante/api/verificar_practica1/') // Suponiendo que tienes un endpoint para esto
        .then(response => response.json())
        .then(data => {
            practica1Existente = data.existe_practica1; // Guardamos el resultado de la API

            if (practica1Existente) {
                practica2Checkbox.disabled = false; // Activar práctica II si existe "Práctica I"
            } else {
                practica1Checkbox.checked = true; // Activar "Práctica I" si no existe en la BD
            }
        });

    // Evento para la checkbox de "Práctica I"
    practica1Checkbox.addEventListener('change', function () {
        if (this.checked) {
            practica2Checkbox.disabled = false; // Activar práctica II si "Práctica I" está seleccionada
        } else {
            practica2Checkbox.checked = false; // Desmarcar práctica II si "Práctica I" no está seleccionada
            practica2Checkbox.disabled = true; // Desactivar práctica II
        }
    });

    // Evento para la checkbox de "Práctica II"
    practica2Checkbox.addEventListener('change', function () {
        if (this.checked && !practica1Existente && !practica1Checkbox.checked) {
            this.checked = false; // Desmarcar práctica II si "Práctica I" no está seleccionada
            alert("Debes inscribir una 'Práctica I' antes de inscribir una 'Práctica II'.");
        }
    });
});
