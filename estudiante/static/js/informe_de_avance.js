window.onload = function () {
    const modal = document.getElementById('modalSubirArchivo');
    const btnSubirInforme = document.getElementById('btnSubirInforme');
    const inputFile = document.getElementById('archivo');
    const fileDetails = document.getElementById('fileDetails');
    const fileName = document.getElementById('fileName');
    const deleteFile = document.getElementById('deleteFile');
    const uploadLabel = document.getElementById('uploadLabel');

    // Abrir modal al hacer clic en "Subir Informe de Avances"
    btnSubirInforme.onclick = function () {
        modal.style.display = 'flex';
    };

    // Mostrar detalles del archivo seleccionado
    inputFile.onchange = function (event) {
        const file = event.target.files[0];
        if (file) {
            const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            if (!validTypes.includes(file.type)) {
                alert('Solo se permiten archivos PDF o Word (.docx)');
                inputFile.value = '';
                return;
            }
            fileName.textContent = file.name;
            fileDetails.style.display = 'flex';
            uploadLabel.classList.add('active');
        }
    };

    // Eliminar archivo seleccionado
    deleteFile.onclick = function () {
        inputFile.value = '';
        fileDetails.style.display = 'none';
        fileName.textContent = '';
        uploadLabel.classList.remove('active');
    };

    // Drag-and-drop para subir archivos
    uploadLabel.ondragover = function (event) {
        event.preventDefault();
        uploadLabel.classList.add('dragover');
    };

    uploadLabel.ondragleave = function () {
        uploadLabel.classList.remove('dragover');
    };

    uploadLabel.ondrop = function (event) {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (file && (file.type === 'application/pdf' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
            inputFile.files = event.dataTransfer.files;
            fileName.textContent = file.name;
            fileDetails.style.display = 'flex';
            uploadLabel.classList.add('active');
        } else {
            alert('Solo se permiten archivos PDF o Word (.docx)');
        }
        uploadLabel.classList.remove('dragover');
    };

    // Cerrar modal al hacer clic fuera de su contenido
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
};
