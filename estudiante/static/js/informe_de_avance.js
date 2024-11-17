window.onload = function () {
    const modal = document.getElementById('modalSubirArchivo');
    const modalFinal = document.getElementById('modalSubirArchivoFinal');
    const btnSubirInformeAvance = document.getElementById('btnSubirInformeAvance');
    const btnSubirInformeFinal = document.getElementById('btnSubirInformeFinal');
    const inputFile = document.getElementById('archivo');
    const fileDetails = document.getElementById('fileDetails');
    const fileName = document.getElementById('fileName');
    const deleteFile = document.getElementById('deleteFile');
    const uploadLabel = document.getElementById('uploadLabel');

    const inputFileFinal = document.getElementById('archivoFinal');
    const fileDetailsFinal = document.getElementById('fileDetailsFinal');
    const fileNameFinal = document.getElementById('fileNameFinal');
    const deleteFileFinal = document.getElementById('deleteFileFinal');
    const uploadLabelFinal = document.getElementById('uploadLabelFinal');
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    // Función para abrir el modal
    function openModal(modalElement) {
        modalElement.style.display = 'flex';
    }

    // Función para cerrar el modal al hacer clic fuera de su contenido
    function closeModalOnClickOutside(modalElement, event) {
        if (event.target === modalElement) {
            modalElement.style.display = 'none';
        }
    }

    // Función para manejar el cambio de archivo
    function handleFileChange(input, fileDetails, fileName, uploadLabel) {
        return function (event) {
            const file = event.target.files[0];
            if (file) {
                if (!validTypes.includes(file.type)) {
                    alert('Solo se permiten archivos PDF o Word (.docx)');
                    input.value = '';
                    return;
                }
                fileName.textContent = file.name;
                fileDetails.style.display = 'flex';
                uploadLabel.classList.add('active');
            }
        };
    }

    // Función para eliminar archivo seleccionado
    function deleteSelectedFile(input, fileDetails, fileName, uploadLabel) {
        return function () {
            input.value = '';
            fileDetails.style.display = 'none';
            fileName.textContent = '';
            uploadLabel.classList.remove('active');
        };
    }

    // Función para manejar drag-and-drop
    function setupDragAndDrop(uploadLabel, input, fileDetails, fileName) {
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
            if (file && validTypes.includes(file.type)) {
                input.files = event.dataTransfer.files;
                fileName.textContent = file.name;
                fileDetails.style.display = 'flex';
                uploadLabel.classList.add('active');
            } else {
                alert('Solo se permiten archivos PDF o Word (.docx)');
            }
            uploadLabel.classList.remove('dragover');
        };
    }

    // Abrir modal de informe de avances
    if (btnSubirInformeAvance) {
        btnSubirInformeAvance.onclick = () => openModal(modal);
    }

    // Abrir modal de informe final
    if (btnSubirInformeFinal) {
        btnSubirInformeFinal.onclick = () => openModal(modalFinal);
    }

    // Manejar selección de archivo para informe de avances
    if (inputFile) {
        inputFile.onchange = handleFileChange(inputFile, fileDetails, fileName, uploadLabel);
    }

    // Manejar selección de archivo para informe final
    if (inputFileFinal) {
        inputFileFinal.onchange = handleFileChange(inputFileFinal, fileDetailsFinal, fileNameFinal, uploadLabelFinal);
    }

    // Eliminar archivo seleccionado en informe de avances
    if (deleteFile) {
        deleteFile.onclick = deleteSelectedFile(inputFile, fileDetails, fileName, uploadLabel);
    }

    // Eliminar archivo seleccionado en informe final
    if (deleteFileFinal) {
        deleteFileFinal.onclick = deleteSelectedFile(inputFileFinal, fileDetailsFinal, fileNameFinal, uploadLabelFinal);
    }

    // Configurar drag-and-drop para informe de avances
    if (uploadLabel) {
        setupDragAndDrop(uploadLabel, inputFile, fileDetails, fileName);
    }

    // Configurar drag-and-drop para informe final
    if (uploadLabelFinal) {
        setupDragAndDrop(uploadLabelFinal, inputFileFinal, fileDetailsFinal, fileNameFinal);
    }

    // Cerrar modales al hacer clic fuera
    window.onclick = (event) => {
        closeModalOnClickOutside(modal, event);
        closeModalOnClickOutside(modalFinal, event);
    };
};
