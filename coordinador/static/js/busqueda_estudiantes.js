document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.querySelector(".search-container input");
    const studentCards = document.querySelectorAll(".card");

    searchInput.addEventListener("input", () => {
        const filter = searchInput.value.toLowerCase();

        studentCards.forEach((card) => {
            const nombre = card.querySelector("h2").textContent.toLowerCase();
            const correo = card.querySelector("p:nth-of-type(1)").textContent.toLowerCase();
            const rut = card.querySelector("p:nth-of-type(2)").textContent.toLowerCase();
            const domicilio = card.querySelector("p:nth-of-type(3)").textContent.toLowerCase();
            const carrera = card.querySelector("p:nth-of-type(4)").textContent.toLowerCase();

            if (
                nombre.includes(filter) ||
                correo.includes(filter) ||
                rut.includes(filter) ||
                domicilio.includes(filter) ||
                carrera.includes(filter)
            ) {
                card.style.display = "flex";  // Mostrar tarjeta
            } else {
                card.style.display = "none";  // Ocultar tarjeta
            }
        });
    });
});
