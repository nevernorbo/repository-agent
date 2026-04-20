const benchmarkData = {
    repositories: ['mean-flashcards', 'fastapi', 'express'],
    indexing: {
        regular: [11.12, 29.22, 9.00],
        hybrid: [10.93, 92.23, 9.38],
        total: [26.14, 147.74, 26.56]
    },
    latency: {
        mean: [132.77, 130.99, 124.17],
        p50: [123.38, 126.59, 124.08],
        p90: [146.43, 145.14, 136.46],
        p99: [306.19, 231.73, 155.46]
    },
    concurrency: {
        levels: [1, 2, 5, 10, 20],
        'mean-flashcards': {
            latency: [118.72, 210.62, 326.72, 374.77, 532.52],
            throughput: [7.63, 6.50, 9.14, 16.02, 21.80]
        },
        'fastapi': {
            latency: [321.92, 174.36, 225.46, 377.29, 628.30],
            throughput: [2.95, 8.54, 16.60, 18.23, 22.69]
        },
        'express': {
            latency: [167.65, 145.77, 216.64, 317.23, 615.01],
            throughput: [5.56, 9.61, 16.04, 22.27, 23.16]
        }
    },
    quality: {
        p5: [0.35, 0.22, 0.04],
        r5: [0.90, 0.84, 0.22],
        mrr: [0.45, 0.40, 0.07]
    },
    indexComparison: {
        dense: {
            p5: [0.35, 0.22, 0.04],
            r5: [0.90, 0.84, 0.22],
            mrr: [0.45, 0.40, 0.07],
            latency: [133.29, 136.07, 136.31]
        },
        hybrid: {
            p5: [0.32, 0.22, 0.06],
            r5: [0.82, 0.88, 0.26],
            mrr: [0.41, 0.38, 0.14],
            latency: [140.39, 148.46, 133.05]
        }
    },
    nlVsCode: {
        nl: { mrr: [0.40, 0.42, 0.11], p5: [0.35, 0.22, 0.06], r5: [0.82, 0.82, 0.32] },
        code: { mrr: [0.50, 0.39, 0.04], p5: [0.34, 0.22, 0.02], r5: [0.98, 0.86, 0.12] }
    }
};

const colors = {
    primary: '#6366f1',
    primaryLight: '#818cf8',
    secondary: '#ec4899',
    secondaryLight: '#f472b6',
    tertiary: '#10b981',
    quaternary: '#f59e0b',
    gray: '#94a3b8'
};

function initCharts() {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 14;
    Chart.defaults.color = '#64748b';
    Chart.defaults.scale.grid.color = '#f1f5f9';
    Chart.defaults.plugins.legend.labels.font = { size: 14, weight: '500' };
    Chart.defaults.plugins.title.font = { size: 20, weight: '700' };
    Chart.defaults.scale.title.font = { size: 16, weight: '600' };
    Chart.defaults.scale.ticks.font = { size: 12 };

    // 1. Indexing Performance
    new Chart(document.getElementById('chart-indexing'), {
        type: 'bar',
        data: {
            labels: benchmarkData.repositories,
            datasets: [
                { label: 'Regular Indexing (s)', data: benchmarkData.indexing.regular, backgroundColor: colors.primaryLight },
                { label: 'Hybrid Indexing (s)', data: benchmarkData.indexing.hybrid, backgroundColor: colors.secondaryLight },
                { label: 'Total Wall Clock (s)', data: benchmarkData.indexing.total, backgroundColor: colors.primary }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Seconds' } }
            }
        }
    });

    // 2. Search Latency
    new Chart(document.getElementById('chart-latency'), {
        type: 'bar',
        data: {
            labels: benchmarkData.repositories,
            datasets: [
                { label: 'Mean', data: benchmarkData.latency.mean, backgroundColor: colors.primary },
                { label: 'P90', data: benchmarkData.latency.p90, backgroundColor: colors.secondary },
                { label: 'P99', data: benchmarkData.latency.p99, backgroundColor: colors.tertiary }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Latency (ms)' } }
            }
        }
    });

    // 3. Concurrency - Latency
    new Chart(document.getElementById('chart-concurrency-latency'), {
        type: 'line',
        data: {
            labels: benchmarkData.concurrency.levels,
            datasets: [
                { label: 'mean-flashcards', data: benchmarkData.concurrency['mean-flashcards'].latency, borderColor: colors.primary, tension: 0.3 },
                { label: 'fastapi', data: benchmarkData.concurrency['fastapi'].latency, borderColor: colors.secondary, tension: 0.3 },
                { label: 'express', data: benchmarkData.concurrency['express'].latency, borderColor: colors.tertiary, tension: 0.3 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Latency vs Concurrency' }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Latency (ms)' } },
                x: { title: { display: true, text: 'Concurrency Level' } }
            }
        }
    });

    // 4. Concurrency - Throughput
    new Chart(document.getElementById('chart-concurrency-throughput'), {
        type: 'line',
        data: {
            labels: benchmarkData.concurrency.levels,
            datasets: [
                { label: 'mean-flashcards', data: benchmarkData.concurrency['mean-flashcards'].throughput, borderColor: colors.primary, tension: 0.3, fill: true, backgroundColor: 'rgba(99, 102, 241, 0.1)' },
                { label: 'fastapi', data: benchmarkData.concurrency['fastapi'].throughput, borderColor: colors.secondary, tension: 0.3, fill: true, backgroundColor: 'rgba(236, 72, 153, 0.1)' },
                { label: 'express', data: benchmarkData.concurrency['express'].throughput, borderColor: colors.tertiary, tension: 0.3, fill: true, backgroundColor: 'rgba(16, 185, 129, 0.1)' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Throughput vs Concurrency' }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Throughput (qps)' } },
                x: { title: { display: true, text: 'Concurrency Level' } }
            }
        }
    });

    // 5. Retrieval Quality
    new Chart(document.getElementById('chart-quality'), {
        type: 'radar',
        data: {
            labels: ['P@5', 'R@5', 'MRR'],
            datasets: [
                { label: 'mean-flashcards', data: benchmarkData.quality.p5.map((v, i) => [v, benchmarkData.quality.r5[i], benchmarkData.quality.mrr[i]][0]), data: [benchmarkData.quality.p5[0], benchmarkData.quality.r5[0], benchmarkData.quality.mrr[0]], borderColor: colors.primary, backgroundColor: 'rgba(99, 102, 241, 0.2)' },
                { label: 'fastapi', data: [benchmarkData.quality.p5[1], benchmarkData.quality.r5[1], benchmarkData.quality.mrr[1]], borderColor: colors.secondary, backgroundColor: 'rgba(236, 72, 153, 0.2)' },
                { label: 'express', data: [benchmarkData.quality.p5[2], benchmarkData.quality.r5[2], benchmarkData.quality.mrr[2]], borderColor: colors.tertiary, backgroundColor: 'rgba(16, 185, 129, 0.2)' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            scales: {
                r: { beginAtZero: true, max: 1 }
            }
        }
    });

    // 6. Index Type Comparison - MRR
    new Chart(document.getElementById('chart-index-comparison'), {
        type: 'bar',
        data: {
            labels: benchmarkData.repositories,
            datasets: [
                { label: 'Dense MRR', data: benchmarkData.indexComparison.dense.mrr, backgroundColor: colors.primary },
                { label: 'Hybrid MRR', data: benchmarkData.indexComparison.hybrid.mrr, backgroundColor: colors.secondary }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Dense vs Hybrid MRR' }
            },
            scales: {
                y: { beginAtZero: true, max: 1.0, title: { display: true, text: 'MRR Score' } }
            }
        }
    });

    // 7. Index Type Comparison - Latency
    new Chart(document.getElementById('chart-index-latency'), {
        type: 'bar',
        data: {
            labels: benchmarkData.repositories,
            datasets: [
                { label: 'Dense Latency', data: benchmarkData.indexComparison.dense.latency, backgroundColor: colors.primaryLight },
                { label: 'Hybrid Latency', data: benchmarkData.indexComparison.hybrid.latency, backgroundColor: colors.secondaryLight }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Dense vs Hybrid Latency' }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Latency (ms)' } }
            }
        }
    });

    // 8. NL vs Code Comparison
    new Chart(document.getElementById('chart-nl-code'), {
        type: 'bar',
        data: {
            labels: benchmarkData.repositories,
            datasets: [
                { label: 'Natural Language MRR', data: benchmarkData.nlVsCode.nl.mrr, backgroundColor: colors.primary },
                { label: 'Code Query MRR', data: benchmarkData.nlVsCode.code.mrr, backgroundColor: colors.secondary }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Natural Language vs Code MRR' }
            },
            scales: {
                y: { beginAtZero: true, max: 1.0, title: { display: true, text: 'MRR Score' } }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', initCharts);
