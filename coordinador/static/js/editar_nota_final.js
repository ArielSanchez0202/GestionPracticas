// Obtener elementos del DOM
const modal = document.getElementById("editNoteModal");
const closeModal = document.querySelector(".close");
const studentNameElem = document.getElementById("modal-student-name");
const practicaIdInput = document.getElementById("modal-practica-id");
const noteInput = document.getElementById("modal-note-input");

// Función para abrir el modal
function openEditModal(practicaId, studentName, nota) {
    const formattedNote = nota && nota !== "Pendiente" ? nota.replace('.', ',') : "";

    // Asignar valores al modal
    practicaIdInput.value = practicaId;
    studentNameElem.textContent = "Estudiante: " + studentName;
    noteInput.value = formattedNote;

    modal.style.display = "block";
}

// Función para cerrar el modal
closeModal.onclick = function () {
    modal.style.display = "none";
};

window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
};

// Validación del formulario antes de enviar
document.getElementById("editNoteForm").addEventListener("submit", function (e) {
    const noteValue = noteInput.value.trim();
    const regex = /^\d+([,\.]\d+)?$/;

    if (!regex.test(noteValue)) {
        alert("Por favor, ingresa una nota válida (por ejemplo, 5,5 o 6.5)");
        e.preventDefault();
    } else {
        noteInput.value = noteValue.replace(',', '.');
    }
});
