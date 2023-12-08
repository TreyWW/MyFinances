// Generate random values
var days = [];
var incomeData = [];
var expensesData = [];

for (var i = 1; i <= 30; i++) {
    days.push('Day ' + i);
    incomeData.push(Math.floor(Math.random() * 1000) + 1000); // Random income between 1000 and 2000
    expensesData.push(Math.floor(Math.random() * 500) + 500); // Random expenses between 500 and 1000
}

// Chart.js configuration
var ctx = document.getElementById('incomeExpensesChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: days,
        datasets: [
            {
                label: 'Income',
                data: incomeData,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            },
            {
                label: 'Expenses',
                data: expensesData,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }
        ]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});