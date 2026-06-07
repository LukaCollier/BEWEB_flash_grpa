const labels = Object.keys(data);
const values = Object.values(data);

const camembert = new Chart(document.getElementById("camembert"), {
    type: "doughnut",
    data: {
        labels: labels,
        datasets: [{
            data: values
        }]
    },
    options: {
        plugins: {
            legend: {
                position: "bottom"
            }
        }
    }
});