async function validateForm() {
    const nombre = document.getElementById('nombre').value.trim();
    const apellido = document.getElementById('apellido').value.trim();
    const rut = document.getElementById('rut').value.trim();
    const domicilio = document.getElementById('domicilio').value.trim();
    const telefono = document.getElementById('telefono').value.trim();
    const email = document.getElementById('email').value.trim();
    const carrera = document.getElementById('carrera').value.trim();

    const rutPattern = /^[0-9]{7,8}-[0-9kK]{1}$/; // RUT pattern
    const telefonoPattern = /^[0-9]{9}$/; // 9 digits phone number
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Simple email pattern

    if (!nombre || !apellido || !domicilio || !carrera) {
        alert('Por favor, complete todos los campos requeridos.');
        return false;
    }

    if (!rutPattern.test(rut)) {
        alert('El RUT debe seguir el formato: 12345678-9 o 12345678-k');
        return false;
    }

    // Verifica si el RUT ya existe
    const rutExists = await checkRutExists(rut);
    if (rutExists) {
        alert('El RUT ya está registrado.');
        return false;
    }

    if (!telefonoPattern.test(telefono)) {
        alert('El teléfono debe contener 9 dígitos.');
        return false;
    }

    if (!emailPattern.test(email)) {
        alert('Por favor, ingrese un correo electrónico válido.');
        return false;
    }

    return true; // All validations passed
}

document.addEventListener('DOMContentLoaded', function() {
    const rutInput = document.getElementById('rut');
    const form = document.querySelector('form');
    const rutError = document.createElement('div'); // Crea un elemento para el mensaje de error
    rutError.className = 'error-message';
    rutInput.parentNode.appendChild(rutError); // Agrega el mensaje de error en el DOM

    if (rutInput) {
        rutInput.addEventListener('blur', function() {
            const rutValue = rutInput.value.trim();
            console.log("RUT ingresado:", rutValue); // Mensaje de depuración

            if (rutValue) {
                fetch(`/coordinador/verificar_rut/?rut=${encodeURIComponent(rutValue)}`)
                    .then(response => {
                        console.log("Respuesta de la solicitud:", response);
                        return response.json();
                    })
                    .then(data => {
                        console.log("Datos de verificación del RUT:", data); // Muestra los datos devueltos
                        if (data.existe) {
                            rutError.textContent = "Este RUT ya está registrado."; // Muestra el mensaje de error
                            rutInput.classList.add('input-error');
                            form.onsubmit = () => false; // Bloquea el envío del formulario si el RUT ya existe
                        } else {
                            rutError.textContent = ""; // Limpia el mensaje de error si el RUT es nuevo
                            rutInput.classList.remove('input-error');
                            form.onsubmit = () => true; // Permite el envío del formulario si el RUT es nuevo
                        }
                    })
                    .catch(error => console.error('Error al verificar el RUT:', error));
            }
        });
    } else {
        console.error("No se encontró el elemento con ID 'rut'.");
    }
});
