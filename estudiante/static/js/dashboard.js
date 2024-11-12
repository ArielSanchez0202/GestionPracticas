// Seleccionar el elemento canvas y obtener los datos de los atributos data-*
const estadoChartCanvas = document.getElementById('estadoChart');
const aprobadas = parseInt(estadoChartCanvas.dataset.aprobadas);
const rechazadas = parseInt(estadoChartCanvas.dataset.rechazadas);
const pendientes = parseInt(estadoChartCanvas.dataset.pendientes);

// Gráfico de "Solicitudes por Estado"
var ctx1 = estadoChartCanvas.getContext('2d');
var estadoChart = new Chart(ctx1, {
    type: 'pie',
    data: {
        labels: ['Aprobadas', 'Rechazadas', 'Pendientes'],
        datasets: [{
            label: 'Solicitudes por Estado',
            data: [aprobadas, rechazadas, pendientes],
            backgroundColor: ['#4caf50', '#f44336', '#ffeb3b']
        }]
    }
});
