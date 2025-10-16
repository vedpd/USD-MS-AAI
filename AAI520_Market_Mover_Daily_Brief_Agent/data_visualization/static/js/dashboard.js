// Connect to WebSocket
const socket = io();

// Chart instances
let priceChart = null;
let sentimentChart = null;

// DOM Elements
const marketHealthEl = document.getElementById('market-health');
const lastUpdatedEl = document.getElementById('last-updated');
const gainersCountEl = document.getElementById('gainers-count');
const losersCountEl = document.getElementById('losers-count');
const moversTableBody = document.getElementById('movers-table-body');
const newsContainer = document.getElementById('news-container');
const sentimentScoreEl = document.getElementById('sentiment-score');
const sentimentFillEl = document.getElementById('sentiment-fill');
const connectionStatusEl = document.getElementById('connection-status');

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format percentage
function formatPercent(value) {
    const prefix = value > 0 ? '+' : '';
    return `${prefix}${value.toFixed(2)}%`;
}

// Format currency
function formatCurrency(value) {
    return `$${value.toFixed(2)}`;
}

// Update market overview
function updateMarketOverview(data) {
    if (data.market_health) {
        marketHealthEl.textContent = data.market_health.toUpperCase();
        marketHealthEl.className = `badge badge-${data.market_health.toLowerCase()}`;
    }
    
    if (data.gainers_count !== undefined) {
        gainersCountEl.textContent = data.gainers_count;
    }
    
    if (data.losers_count !== undefined) {
        losersCountEl.textContent = data.losers_count;
    }
    
    if (data.overall_sentiment !== undefined) {
        const sentiment = data.overall_sentiment;
        sentimentScoreEl.textContent = sentiment.toFixed(2);
        
        // Update sentiment bar (0-100 scale)
        const percentage = ((sentiment + 1) / 2) * 100;
        sentimentFillEl.style.width = `${percentage}%`;
        
        // Update color based on sentiment
        if (sentiment > 0.3) {
            sentimentFillEl.style.backgroundColor = '#2ecc71'; // Green for positive
        } else if (sentiment < -0.3) {
            sentimentFillEl.style.backgroundColor = '#e74c3c'; // Red for negative
        } else {
            sentimentFillEl.style.backgroundColor = '#3498db'; // Blue for neutral
        }
    }
    
    lastUpdatedEl.textContent = new Date().toLocaleTimeString();
}

// Update movers table
function updateMoversTable(movers) {
    if (!movers || !Array.isArray(movers)) return;
    
    moversTableBody.innerHTML = '';
    
    movers.forEach((mover, index) => {
        const row = document.createElement('tr');
        const isGainer = mover.percent_change > 0;
        const changeClass = isGainer ? 'text-success' : 'text-danger';
        const changeIcon = isGainer ? '↑' : '↓';
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${mover.symbol}</strong></td>
            <td>${formatCurrency(mover.price)}</td>
            <td class="${changeClass}">${changeIcon} ${formatPercent(mover.percent_change)}</td>
            <td>${formatNumber(mover.volume)}</td>
            <td><span class="badge badge-${isGainer ? 'success' : 'danger'}">${mover.category || 'N/A'}</span></td>
            <td>${mover.reason || 'N/A'}</td>
        `;
        
        moversTableBody.appendChild(row);
    });
}

// Update news feed
function updateNewsFeed(newsItems) {
    if (!newsItems || !Array.isArray(newsItems)) return;
    
    newsContainer.innerHTML = '';
    
    newsItems.forEach(item => {
        const newsEl = document.createElement('div');
        newsEl.className = 'news-item';
        
        const sentimentClass = item.sentiment > 0 ? 'text-success' : item.sentiment < 0 ? 'text-danger' : '';
        const sentimentIcon = item.sentiment > 0 ? '↑' : item.sentiment < 0 ? '↓' : '→';
        
        newsEl.innerHTML = `
            <div class="news-title">
                <a href="${item.url}" target="_blank" rel="noopener noreferrer">${item.title}</a>
                <span class="${sentimentClass} ml-2">${sentimentIcon}</span>
            </div>
            <div class="news-meta">
                <span>${item.source}</span>
                <span>${new Date(item.published_at).toLocaleString()}</span>
            </div>
        `;
        
        newsContainer.appendChild(newsEl);
    });
}

// Initialize price chart
function initPriceChart(data) {
    const ctx = document.getElementById('price-chart').getContext('2d');
    
    if (priceChart) {
        priceChart.destroy();
    }
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Price',
                data: data.prices || [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Initialize sentiment chart
function initSentimentChart(data) {
    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    
    if (sentimentChart) {
        sentimentChart.destroy();
    }
    
    sentimentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Sentiment',
                data: data.scores || [],
                backgroundColor: [
                    'rgba(46, 204, 113, 0.7)',  // Green for positive
                    'rgba(52, 152, 219, 0.7)',  // Blue for neutral
                    'rgba(231, 76, 60, 0.7)'    // Red for negative
                ],
                borderColor: [
                    'rgba(46, 204, 113, 1)',
                    'rgba(52, 152, 219, 1)',
                    'rgba(231, 76, 60, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.2
                    }
                }
            }
        }
    });
}

// Handle incoming WebSocket messages
socket.on('connect', () => {
    console.log('Connected to WebSocket server');
    connectionStatusEl.innerHTML = '<span class="status-indicator status-online"></span> Connected';
    connectionStatusEl.className = 'text-success';
});

socket.on('disconnect', () => {
    console.log('Disconnected from WebSocket server');
    connectionStatusEl.innerHTML = '<span class="status-indicator status-offline"></span> Disconnected';
    connectionStatusEl.className = 'text-danger';
});

socket.on('market_update', (data) => {
    console.log('Received market update:', data);
    
    if (data.overview) {
        updateMarketOverview(data.overview);
    }
    
    if (data.movers) {
        updateMoversTable(data.movers);
    }
    
    if (data.news) {
        updateNewsFeed(data.news);
    }
    
    if (data.price_chart) {
        initPriceChart(data.price_chart);
    }
    
    if (data.sentiment_chart) {
        initSentimentChart(data.sentiment_chart);
    }
    
    // Show notification for new data
    showNotification('Market data updated');
});

// Show notification
function showNotification(message, type = 'info') {
    try {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.role = 'alert';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        let container = document.getElementById('notifications');
        
        // Create notifications container if it doesn't exist
        if (!container) {
            container = document.createElement('div');
            container.id = 'notifications';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            container.style.width = '300px';
            document.body.appendChild(container);
        }
        
        // Add notification to the container
        if (container.firstChild) {
            container.insertBefore(notification, container.firstChild);
        } else {
            container.appendChild(notification);
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    } catch (error) {
        console.error('Error showing notification:', error);
    }
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    initTooltips();
    
    // Request initial data
    socket.emit('request_initial_data');
    
    // Set up periodic refresh (as fallback)
    setInterval(() => {
        socket.emit('request_update');
    }, 30000); // Every 30 seconds
});

// Export for Webpack/ESM if needed
try {
    if (module) {
        module.exports = {
            updateMarketOverview,
            updateMoversTable,
            updateNewsFeed,
            initPriceChart,
            initSentimentChart,
            showNotification
        };
    }
} catch (e) {
    // Not in a module environment, ignore
}
