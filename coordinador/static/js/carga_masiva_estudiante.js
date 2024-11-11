const modal = document.getElementById('modalSubirArchivo');
        const btnSubirCarga = document.getElementById('btnSubirCarga');
        const inputFile = document.getElementById('archivo');
        const fileDetails = document.getElementById('fileDetails');
        const fileName = document.getElementById('fileName');
        const deleteFile = document.getElementById('deleteFile');
        const uploadLabel = document.getElementById('uploadLabel');

        btnSubirCarga.onclick = function() {
            modal.style.display = 'flex';
        };

        inputFile.onchange = function(event) {
            const file = event.target.files[0];
            if (file) {
                fileName.textContent = file.name;
                fileDetails.style.display = 'flex';
                uploadLabel.classList.add('active');
            }
        };

        deleteFile.onclick = function() {
            inputFile.value = '';
            fileDetails.style.display = 'none';
            fileName.textContent = '';
            uploadLabel.classList.remove('active');
        };

        // Prevenir que el archivo se descargue y permitir la carga masiva
        uploadLabel.ondragover = function(event) {
            event.preventDefault();
            uploadLabel.classList.add('dragover');
        };

        uploadLabel.ondragleave = function() {
            uploadLabel.classList.remove('dragover');
        };

        uploadLabel.ondrop = function(event) {
            event.preventDefault();
            const file = event.dataTransfer.files[0];
            if (file && file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") {
                inputFile.files = event.dataTransfer.files; // Asigna los archivos arrastrados al input
                fileName.textContent = file.name;
                fileDetails.style.display = 'flex';
                uploadLabel.classList.add('active');
            }
            uploadLabel.classList.remove('dragover');
        };

        // Cerrar el modal al hacer clic fuera del contenido
        window.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };