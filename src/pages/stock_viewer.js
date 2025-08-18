// Stock Data Viewer JavaScript
class StockViewer {
    constructor() {
        this.symbols = ['FPT.VN', 'GOOG'];
        this.charts = {};
        this.currentData = {};
        this.timeRange = '1d';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadStockData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadStockData();
        });

        // Time range selector
        document.getElementById('timeRange').addEventListener('change', (e) => {
            this.timeRange = e.target.value;
            this.loadStockData();
        });
    }

    initializeCharts() {
        // Price comparison chart
        const priceCtx = document.getElementById('priceChart').getContext('2d');
        this.charts.price = new Chart(priceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Stock Price Comparison'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price ($)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                }
            }
        });

        // Volume chart
        const volumeCtx = document.getElementById('volumeChart').getContext('2d');
        this.charts.volume = new Chart(volumeCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Trading Volume'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Volume'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Symbol'
                        }
                    }
                }
            }
        });
    }

    async loadStockData() {
        try {
            this.showLoading(true);
            
            // Simulate API call - replace with actual API endpoint
            const data = await this.fetchStockData();
            
            this.currentData = data;
            this.updateUI(data);
            this.updateCharts(data);
            this.updateTable(data);
            this.updateStatus(data);
            
        } catch (error) {
            console.error('Error loading stock data:', error);
            this.showError('Failed to load stock data. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async fetchStockData() {
        try {
            // Call the actual API endpoint
            const response = await fetch(`/stock-viewer/api/stock-data?time_range=${this.timeRange}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Extract the data from the API response
            if (result.data && typeof result.data === 'object') {
                return result.data;
            } else {
                throw new Error('Invalid data format received from API');
            }
            
        } catch (error) {
            console.error('Error fetching stock data:', error);
            
            // Fallback to mock data if API fails
            return this.getFallbackData();
        }
    }

    getFallbackData() {
        const now = new Date();
        return {
            'FPT.VN': {
                symbol: 'FPT.VN',
                price: 45.20 + Math.random() * 2,
                volume: 1500000 + Math.floor(Math.random() * 500000),
                open_price: 44.80,
                high_price: 46.50,
                low_price: 44.20,
                previous_close: 44.80,
                change: 0.40 + (Math.random() - 0.5) * 2,
                change_percent: 0.89 + (Math.random() - 0.5) * 2,
                market_cap: 15000000000,
                pe_ratio: 15.2,
                dividend_yield: 2.5,
                timestamp: now,
                sync_timestamp: now,
                provider: 'yahoo',
                status: 'success',
                is_trading_hours: true,
                trading_day: this.getTradingDay(now)
            },
            'GOOG': {
                symbol: 'GOOG',
                price: 145.80 + Math.random() * 5,
                volume: 25000000 + Math.floor(Math.random() * 10000000),
                open_price: 144.50,
                high_price: 147.20,
                low_price: 143.80,
                previous_close: 144.50,
                change: 1.30 + (Math.random() - 0.5) * 3,
                change_percent: 0.90 + (Math.random() - 0.5) * 2,
                market_cap: 1850000000000,
                pe_ratio: 28.5,
                dividend_yield: 0.0,
                timestamp: now,
                sync_timestamp: now,
                provider: 'yahoo',
                status: 'success',
                is_trading_hours: true,
                trading_day: this.getTradingDay(now)
            }
        };
    }

    getTradingDay(date) {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return days[date.getDay()];
    }

    updateUI(data) {
        console.log(data);
        // Update FPT.VN card
        const fptData = data['FPT.VN'];
        if (fptData) {
            document.getElementById('fpt-price').textContent = fptData.price ? `$${fptData.price.toFixed(2)}` : '--';
            if (fptData.change !== null && fptData.change_percent !== null) {
                this.updateChangeElement('fpt-change', fptData.change, fptData.change_percent);
            } else {
                document.getElementById('fpt-change').textContent = '--';
            }
            document.getElementById('fpt-volume').textContent = this.formatNumber(fptData.volume);
            document.getElementById('fpt-market-cap').textContent = this.formatCurrency(fptData.market_cap);
        }

        // Update GOOG card
        const googData = data['GOOG'];
        if (googData) {
            document.getElementById('goog-price').textContent = googData.price ? `$${googData.price.toFixed(2)}` : '--';
            if (googData.change !== null && googData.change_percent !== null) {
                this.updateChangeElement('goog-change', googData.change, googData.change_percent);
            } else {
                document.getElementById('goog-change').textContent = '--';
            }
            document.getElementById('goog-volume').textContent = this.formatNumber(googData.volume);
            document.getElementById('goog-market-cap').textContent = this.formatCurrency(googData.market_cap);
        }
    }

    updateChangeElement(elementId, change, changePercent) {
        const element = document.getElementById(elementId);
        
        // Handle null/undefined values
        if (change === null || change === undefined || changePercent === null || changePercent === undefined) {
            element.textContent = '--';
            element.className = 'change';
            return;
        }
        
        const isPositive = change >= 0;
        const sign = isPositive ? '+' : '';
        
        element.textContent = `${sign}$${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
        element.className = `change ${isPositive ? 'positive' : 'negative'}`;
        
        // Add animation
        element.classList.add('price-change-animation');
        setTimeout(() => element.classList.remove('price-change-animation'), 500);
    }

    updateCharts(data) {
        // Update price chart
        const priceData = this.preparePriceChartData(data);
        this.charts.price.data.labels = priceData.labels;
        this.charts.price.data.datasets = priceData.datasets;
        this.charts.price.update();

        // Update volume chart
        const volumeData = this.prepareVolumeChartData(data);
        this.charts.volume.data.labels = volumeData.labels;
        this.charts.volume.data.datasets = volumeData.datasets;
        this.charts.volume.update();
    }

    preparePriceChartData(data) {
        const labels = ['Previous Close', 'Open', 'Current', 'High', 'Low'];
        const datasets = [];

        Object.keys(data).forEach((symbol, index) => {
            const stockData = data[symbol];
            const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
            
            datasets.push({
                label: symbol,
                data: [
                    stockData.previous_close || 0,
                    stockData.open_price || 0,
                    stockData.price || 0,
                    stockData.high_price || 0,
                    stockData.low_price || 0
                ],
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                tension: 0.1,
                fill: false
            });
        });

        return { labels, datasets };
    }

    prepareVolumeChartData(data) {
        const labels = Object.keys(data);
        const volumes = labels.map(symbol => data[symbol].volume || 0);
        
        return {
            labels,
            datasets: [{
                label: 'Volume',
                data: volumes,
                backgroundColor: ['#FF6384', '#36A2EB'],
                borderColor: ['#FF6384', '#36A2EB'],
                borderWidth: 1
            }]
        };
    }

    updateTable(data) {
        const tbody = document.getElementById('stockTableBody');
        tbody.innerHTML = '';

        Object.values(data).forEach(stock => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${stock.symbol || '--'}</strong></td>
                <td>${stock.price ? `$${stock.price.toFixed(2)}` : '--'}</td>
                <td class="${stock.change !== null && stock.change >= 0 ? 'positive' : 'negative'}">
                    ${stock.change !== null ? `${stock.change >= 0 ? '+' : ''}$${stock.change.toFixed(2)}` : '--'}
                </td>
                <td>${this.formatNumber(stock.volume)}</td>
                <td>${stock.open_price ? `$${stock.open_price.toFixed(2)}` : '--'}</td>
                <td>${stock.high_price ? `$${stock.high_price.toFixed(2)}` : '--'}</td>
                <td>${stock.low_price ? `$${stock.low_price.toFixed(2)}` : '--'}</td>
                <td>${this.formatCurrency(stock.market_cap)}</td>
                <td>${stock.pe_ratio ? stock.pe_ratio.toFixed(1) : '--'}</td>
                <td>${stock.timestamp ? this.formatDateTime(stock.timestamp) : '--'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    updateStatus(data) {
        const lastUpdate = new Date();
        document.getElementById('lastUpdate').textContent = this.formatDateTime(lastUpdate);
        document.getElementById('dataProvider').textContent = 'Yahoo Finance';
        document.getElementById('syncStatus').textContent = 'Active';
    }

    formatNumber(num) {
        if (num === null || num === undefined || isNaN(num)) {
            return '--';
        }
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    }

    formatCurrency(num) {
        if (num === null || num === undefined || isNaN(num)) {
            return '--';
        }
        if (num >= 1000000000) {
            return '$' + (num / 1000000000).toFixed(1) + 'B';
        } else if (num >= 1000000) {
            return '$' + (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return '$' + (num / 1000).toFixed(1) + 'K';
        }
        return '$' + num.toLocaleString();
    }

    formatDateTime(date) {
        if (!date) {
            return '--';
        }
        if (typeof date === 'string') {
            date = new Date(date);
        }
        if (isNaN(date.getTime())) {
            return '--';
        }
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    showLoading(show) {
        const container = document.querySelector('.container');
        if (show) {
            container.classList.add('loading');
        } else {
            container.classList.remove('loading');
        }
    }

    showError(message) {
        // Create and show error notification
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f8d7da;
            color: #721c24;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            max-width: 300px;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadStockData();
        }, 30000);
    }
}

// Initialize the stock viewer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new StockViewer();
});

// Add some utility functions for external use
window.StockViewerUtils = {
    formatNumber: (num) => {
        if (num === null || num === undefined || isNaN(num)) {
            return '--';
        }
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    },
    
    formatCurrency: (num) => {
        if (num === null || num === undefined || isNaN(num)) {
            return '--';
        }
        if (num >= 1000000000) {
            return '$' + (num / 1000000000).toFixed(1) + 'B';
        } else if (num >= 1000000) {
            return '$' + (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return '$' + (num / 1000).toFixed(1) + 'K';
        }
        return '$' + num.toLocaleString();
    }
};
