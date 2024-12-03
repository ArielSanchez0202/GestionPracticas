// Obtener elementos del DOM
const modal = document.getElementById("editNoteModal");
const closeModal = document.querySelector(".close");
const studentNameElem = document.getElementById("modal-student-name");
const practicaIdInput = document.getElementById("modal-practica-id");
const noteInput = document.getElementById("modal-note-input");

// Función para abrir el modal
function openEditModal(practicaId, studentName, nota) {
    // Convertir el separador decimal de punto a coma para mostrarlo en el modal
    const formattedNote = nota && nota !== "Pendiente" ? nota.replace('.', ',') : "";

    // Asignar valores al modal
    practicaIdInput.value = practicaId;
    studentNameElem.textContent = "Estudiante: " + studentName;
    noteInput.value = formattedNote;

    // Mostrar el modal
    modal.style.display = "block";
}

// Función para cerrar el modal al hacer clic en la "x"
closeModal.onclick = function () {
    modal.style.display = "none";
};

// Función para cerrar el modal al hacer clic fuera del contenido
window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
};

// Manejar la conversión al enviar el formulario
document.getElementById("editNoteForm").addEventListener("submit", function (e) {
    const noteValue = noteInput.value.trim();

    // Expresión regular para validar el formato de la nota
    const regex = /^\d+([,\.]\d+)?$/;

    if (!regex.test(noteValue)) {
        alert("Por favor, ingresa una nota válida (por ejemplo, 5,5 o 6.5)");
        e.preventDefault(); // Evita el envío del formulario si la nota no es válida
    } else {
        // Convertir coma a punto antes de enviar el formulario
        noteInput.value = noteValue.replace(',', '.');
    }
});
