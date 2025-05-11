document.addEventListener('DOMContentLoaded', function () {
    let currentChartType = 'incomes';

    const ctx = document.getElementById('chart');
    let chart;

    function renderChart(type) {
        if (!ctx) {
            console.warn("Элемент chart не найден.");
            return;
        }

        const data = type === 'expenses' ? expensesData : incomesData;
        const labels = Object.keys(data);
        const values = Object.values(data);

        if (chart) {
            chart.destroy();
        }

        if (labels.length === 0) {
            document.getElementById('chartTitle').innerText = "Нет данных для отображения";
            return;
        }

        chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: type === 'expenses' ? 'Расходы по категориям' : 'Доходы по категориям',
                    data: values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }


    const showExpensesButton = document.getElementById('showExpenses');
    const showIncomesButton = document.getElementById('showIncomes');

    if (showExpensesButton) {
        showExpensesButton.addEventListener('click', function () {
            currentChartType = 'expenses';
            document.getElementById('chartTitle').innerText = "Расходы по категориям";
            renderChart(currentChartType);
        });
    }

    if (showIncomesButton) {
        showIncomesButton.addEventListener('click', function () {
            currentChartType = 'incomes';
            document.getElementById('chartTitle').innerText = "Доходы по категориям";
            renderChart(currentChartType);
        });
    }


    if (Object.keys(incomesData).length > 0) {
        currentChartType = 'incomes';
        document.getElementById('chartTitle').innerText = "Доходы по категориям";
    } else if (Object.keys(expensesData).length > 0) {
        currentChartType = 'expenses';
        document.getElementById('chartTitle').innerText = "Расходы по категориям";
    } else {
        document.getElementById('chartTitle').innerText = "Нет данных для отображения";
        return;
    }

    renderChart(currentChartType);


});