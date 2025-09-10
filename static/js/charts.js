// This file contains chart initialization and updating functions

/**
 * Initializes the sales chart with provided data
 * @param {string} elementId - The ID of the canvas element to render the chart
 * @param {Object} data - The data object containing dates and sales values
 */
function initSalesChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Daily Sales ($)',
                data: data.sales,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '$' + context.raw.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initializes the popular items chart with provided data
 * @param {string} elementId - The ID of the canvas element to render the chart
 * @param {Object} data - The data object containing item names and counts
 */
function initPopularItemsChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.items,
            datasets: [{
                label: 'Orders',
                data: data.counts,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            cutout: '65%'
        }
    });
}

/**
 * Initializes the inventory level chart with provided data
 * @param {string} elementId - The ID of the canvas element to render the chart
 * @param {Object} data - The data object containing inventory items, levels and reorder levels
 */
function initInventoryChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.items,
            datasets: [{
                label: 'Current Quantity',
                data: data.levels,
                backgroundColor: 'rgba(75, 192, 192, 0.7)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }, {
                label: 'Reorder Level',
                data: data.reorder_levels,
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                type: 'line'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Updates an existing chart with new data
 * @param {Chart} chart - The Chart.js instance to update
 * @param {Object} data - The new data to display
 */
function updateChart(chart, data) {
    chart.data.labels = data.labels;
    chart.data.datasets.forEach((dataset, i) => {
        dataset.data = data.datasets[i].data;
    });
    chart.update();
}

/**
 * Fetches chart data from the API
 * @param {string} endpoint - The API endpoint to fetch data from
 * @returns {Promise} - A promise that resolves with the data
 */
function fetchChartData(endpoint) {
    return fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            return null;
        });
}
