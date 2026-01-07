// dashboard.js — Officer Dashboard Chart (Chart.js)

document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById('performanceChart');
    if (!chartCanvas || typeof Chart === 'undefined') return;

    // Safely extract numeric values from data attributes
    const pending = Number(chartCanvas.dataset.pending || 0);
    const inProgress = Number(chartCanvas.dataset.inprogress || 0);
    const resolved = Number(chartCanvas.dataset.resolved || 0);
    const overdue = Number(chartCanvas.dataset.overdue || 0);

    const ctx = chartCanvas.getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Pending', 'In Progress', 'Resolved', 'Overdue'],
            datasets: [{
                data: [pending, inProgress, resolved, overdue],
                backgroundColor: [
                    '#ffc107', // Pending
                    '#0dcaf0', // In Progress
                    '#198754', // Resolved
                    '#dc3545'  // Overdue
                ],
                borderRadius: 8,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 600,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.parsed.y} cases`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
});

/* ==========================================================================
   LOADER INITIALIZATION
   ========================================================================== */