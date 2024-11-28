function enableEditing(element) {
    const notaStatic = element;
    const notaInput = notaStatic.nextElementSibling;

    // Ocultar el texto estático y mostrar el campo de entrada
    notaStatic.style.display = "none";
    notaInput.style.display = "inline";
    notaInput.focus();

    // Eliminar cualquier evento anterior para evitar múltiples listeners
    notaInput.removeEventListener("keydown", handleEnterKey);
    notaInput.addEventListener("keydown", handleEnterKey);
}

function handleEnterKey(event) {
    const notaInput = event.target;
    const notaStatic = notaInput.previousElementSibling;

    // Si la tecla presionada es ENTER
    if (event.key === "Enter") {
        const nota = notaInput.value;
        const autoevaluacionId = notaInput.getAttribute("data-id");

        // Log para verificar el ID y la URL
        console.log(`Guardando nota. ID: ${autoevaluacionId}, URL: /guardar-nota/${autoevaluacionId}/`);

        // Enviar la petición para guardar la nota
        fetch(`/guardar-nota/${autoevaluacionId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ nota }),
        })
        .then((response) => {
            console.log('Respuesta del servidor:', response);
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Error al guardar la nota.");
            }
        })
        .then((data) => {
            // Actualizar la vista con la nueva nota
            notaStatic.textContent = data.nota || "No hay nota";
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("No se pudo guardar la nota. Intente nuevamente.");
        })
        .finally(() => {
            // Restaurar la visualización
            notaInput.style.display = "none";
            notaStatic.style.display = "inline";
        });
    }
}

function getCSRFToken() {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split("=");
        if (name === "csrftoken") {
            return value;
        }
    }
    return null;
}