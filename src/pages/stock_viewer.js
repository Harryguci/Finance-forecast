// Stock Data Viewer JavaScript
class StockViewer {
  constructor() {
    this.symbols = ["FPT.VN", "GOOG"];
    this.activeSymbol = "FPT.VN";
    this.charts = {}; // { [symbol]: { price, volume } }
    this.currentData = {};
    this.timeRange = "1d";

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
    document.getElementById("refreshBtn").addEventListener("click", () => {
      this.loadStockData();
    });

    // Time range selector
    document.getElementById("timeRange").addEventListener("change", (e) => {
      this.timeRange = e.target.value;
      this.loadStockData();
    });

    // Tab buttons
    const tabsContainer = document.getElementById("symbolTabs");
    if (tabsContainer) {
      tabsContainer.addEventListener("click", (event) => {
        const target = event.target;
        if (target && target.classList.contains("tab-btn")) {
          const symbol = target.getAttribute("data-symbol");
          if (this.symbols.includes(symbol) && symbol !== this.activeSymbol) {
            this.setActiveSymbol(symbol);
          }
        }
      });
    }
  }

  initializeCharts() {
    this.symbols.forEach((symbol) => {
      const priceCanvas = document.getElementById(`priceChart-${symbol}`);
      const volumeCanvas = document.getElementById(`volumeChart-${symbol}`);
      if (!priceCanvas || !volumeCanvas) {
        return;
      }

      const priceCtx = priceCanvas.getContext("2d");
      const volumeCtx = volumeCanvas.getContext("2d");

      const priceChart = new Chart(priceCtx, {
        type: "line",
        data: {
          labels: [],
          datasets: [],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "top" },
            title: { display: true, text: `${symbol} Price` },
          },
          scales: {
            y: {
              beginAtZero: false,
              title: { display: true, text: "Price ($)" },
            },
            x: {
              title: { display: true, text: "Metric" },
            },
          },
        },
      });

      const volumeChart = new Chart(volumeCtx, {
        type: "bar",
        data: {
          labels: [],
          datasets: [],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "top" },
            title: { display: true, text: `${symbol} Volume` },
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: "Volume" },
            },
            x: {
              title: { display: true, text: "Symbol" },
            },
          },
        },
      });

      this.charts[symbol] = { price: priceChart, volume: volumeChart };
    });
  }

  async loadStockData() {
    try {
      this.showLoading(true);

      // Simulate API call - replace with actual API endpoint
      const data = await this.fetchStockData();

      this.currentData = data;
      this.updateUIForAllSymbols(data);
      this.updateChartsForAllSymbols(data);
      this.updateTablesForAllSymbols(data);
      this.updateStatusForAllSymbols();
    } catch (error) {
      console.error("Error loading stock data:", error);
      this.showError("Failed to load stock data. Please try again.");
    } finally {
      this.showLoading(false);
    }
  }

  async fetchStockData() {
    try {
      // Call the actual API endpoint
      const response = await fetch(
        `/stock-viewer/api/stock-data?time_range=${this.timeRange}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Extract the data from the API response
      if (result.data && typeof result.data === "object") {
        return result.data;
      } else {
        throw new Error("Invalid data format received from API");
      }
    } catch (error) {
      console.error("Error fetching stock data:", error);

      // Fallback to mock data if API fails
      return this.getFallbackData();
    }
  }

  getFallbackData() {
    const now = new Date();
    return {
      "FPT.VN": {
        symbol: "FPT.VN",
        price: 45.2 + Math.random() * 2,
        volume: 1500000 + Math.floor(Math.random() * 500000),
        open_price: 44.8,
        high_price: 46.5,
        low_price: 44.2,
        previous_close: 44.8,
        change: 0.4 + (Math.random() - 0.5) * 2,
        change_percent: 0.89 + (Math.random() - 0.5) * 2,
        market_cap: 15000000000,
        pe_ratio: 15.2,
        dividend_yield: 2.5,
        timestamp: now,
        sync_timestamp: now,
        provider: "yahoo",
        status: "success",
        is_trading_hours: true,
        trading_day: this.getTradingDay(now),
      },
      GOOG: {
        symbol: "GOOG",
        price: 145.8 + Math.random() * 5,
        volume: 25000000 + Math.floor(Math.random() * 10000000),
        open_price: 144.5,
        high_price: 147.2,
        low_price: 143.8,
        previous_close: 144.5,
        change: 1.3 + (Math.random() - 0.5) * 3,
        change_percent: 0.9 + (Math.random() - 0.5) * 2,
        market_cap: 1850000000000,
        pe_ratio: 28.5,
        dividend_yield: 0.0,
        timestamp: now,
        sync_timestamp: now,
        provider: "yahoo",
        status: "success",
        is_trading_hours: true,
        trading_day: this.getTradingDay(now),
      },
    };
  }

  getTradingDay(date) {
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    return days[date.getDay()];
  }

  updateUIForAllSymbols(data) {
    const fptData = data["FPT.VN"];
    if (fptData) {
      const priceEl = document.getElementById("fpt-price");
      if (priceEl)
        priceEl.textContent = fptData.price
          ? `$${fptData.price.toFixed(2)}`
          : "--";
      if (fptData.change !== null && fptData.change_percent !== null) {
        this.updateChangeElement(
          "fpt-change",
          fptData.change,
          fptData.change_percent
        );
      } else {
        const chg = document.getElementById("fpt-change");
        if (chg) chg.textContent = "--";
      }
      const vol = document.getElementById("fpt-volume");
      if (vol) vol.textContent = this.formatNumber(fptData.volume);
      const mcap = document.getElementById("fpt-market-cap");
      if (mcap) mcap.textContent = this.formatCurrency(fptData.market_cap);
    }

    const googData = data["GOOG"];
    if (googData) {
      const priceEl = document.getElementById("goog-price");
      if (priceEl)
        priceEl.textContent = googData.price
          ? `$${googData.price.toFixed(2)}`
          : "--";
      if (googData.change !== null && googData.change_percent !== null) {
        this.updateChangeElement(
          "goog-change",
          googData.change,
          googData.change_percent
        );
      } else {
        const chg = document.getElementById("goog-change");
        if (chg) chg.textContent = "--";
      }
      const vol = document.getElementById("goog-volume");
      if (vol) vol.textContent = this.formatNumber(googData.volume);
      const mcap = document.getElementById("goog-market-cap");
      if (mcap) mcap.textContent = this.formatCurrency(googData.market_cap);
    }
  }

  updateChangeElement(elementId, change, changePercent) {
    const element = document.getElementById(elementId);

    // Handle null/undefined values
    if (
      change === null ||
      change === undefined ||
      changePercent === null ||
      changePercent === undefined
    ) {
      element.textContent = "--";
      element.className = "change";
      return;
    }

    const isPositive = change >= 0;
    const sign = isPositive ? "+" : "";

    element.textContent = `${sign}$${change.toFixed(
      2
    )} (${sign}${changePercent.toFixed(2)}%)`;
    element.className = `change ${isPositive ? "positive" : "negative"}`;

    // Add animation
    element.classList.add("price-change-animation");
    setTimeout(() => element.classList.remove("price-change-animation"), 500);
  }

  updateChartsForAllSymbols(data) {
    this.symbols.forEach((symbol) => {
      const stockData = data[symbol];
      const chartsForSymbol = this.charts[symbol];
      if (!stockData || !chartsForSymbol) return;

      const priceData = this.prepareSingleSymbolPriceChartData(
        stockData,
        symbol
      );
      chartsForSymbol.price.data.labels = priceData.labels;
      chartsForSymbol.price.data.datasets = priceData.datasets;
      chartsForSymbol.price.update();

      const volumeData = this.prepareSingleSymbolVolumeChartData(
        stockData,
        symbol
      );
      chartsForSymbol.volume.data.labels = volumeData.labels;
      chartsForSymbol.volume.data.datasets = volumeData.datasets;
      chartsForSymbol.volume.update();
    });
  }

  prepareSingleSymbolPriceChartData(stockData, symbol) {
    const labels = ["Previous Close", "Open", "Current", "High", "Low"];
    const color = symbol === "FPT.VN" ? "#36A2EB" : "#FF6384";
    return {
      labels,
      datasets: [
        {
          label: symbol,
          data: [
            stockData.previous_close || 0,
            stockData.open_price || 0,
            stockData.price || 0,
            stockData.high_price || 0,
            stockData.low_price || 0,
          ],
          borderColor: color,
          backgroundColor: `${color}20`,
          tension: 0.1,
          fill: false,
        },
      ],
    };
  }

  prepareSingleSymbolVolumeChartData(stockData, symbol) {
    const color = symbol === "FPT.VN" ? "#36A2EB" : "#FF6384";
    return {
      labels: [symbol],
      datasets: [
        {
          label: "Volume",
          data: [stockData.volume || 0],
          backgroundColor: [color],
          borderColor: [color],
          borderWidth: 1,
        },
      ],
    };
  }

  updateTablesForAllSymbols(data) {
    this.symbols.forEach((symbol) => {
      const tbody = document.getElementById(`stockTableBody-${symbol}`);
      if (!tbody) return;
      tbody.innerHTML = "";
      const stock = data[symbol];
      if (!stock) return;
      const row = document.createElement("tr");
      row.innerHTML = `
                <td><strong>${stock.symbol || "--"}</strong></td>
                <td>${stock.price ? `$${stock.price.toFixed(2)}` : "--"}</td>
                <td class="${
                  stock.change !== null && stock.change >= 0
                    ? "positive"
                    : "negative"
                }">
                    ${
                      stock.change !== null
                        ? `${
                            stock.change >= 0 ? "+" : ""
                          }$${stock.change.toFixed(2)}`
                        : "--"
                    }
                </td>
                <td>${this.formatNumber(stock.volume)}</td>
                <td>${
                  stock.open_price ? `$${stock.open_price.toFixed(2)}` : "--"
                }</td>
                <td>${
                  stock.high_price ? `$${stock.high_price.toFixed(2)}` : "--"
                }</td>
                <td>${
                  stock.low_price ? `$${stock.low_price.toFixed(2)}` : "--"
                }</td>
                <td>${this.formatCurrency(stock.market_cap)}</td>
                <td>${stock.pe_ratio ? stock.pe_ratio.toFixed(1) : "--"}</td>
                <td>${
                  stock.timestamp ? this.formatDateTime(stock.timestamp) : "--"
                }</td>
            `;
      tbody.appendChild(row);
    });
  }

  updateStatusForAllSymbols() {
    const lastUpdate = new Date();
    this.symbols.forEach((symbol) => {
      const last = document.getElementById(`lastUpdate-${symbol}`);
      if (last) last.textContent = this.formatDateTime(lastUpdate);
      const prov = document.getElementById(`dataProvider-${symbol}`);
      if (prov) prov.textContent = "Yahoo Finance";
      const status = document.getElementById(`syncStatus-${symbol}`);
      if (status) status.textContent = "Active";
    });
  }

  formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) {
      return "--";
    }
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toLocaleString();
  }

  formatCurrency(num) {
    if (num === null || num === undefined || isNaN(num)) {
      return "--";
    }
    if (num >= 1000000000) {
      return "$" + (num / 1000000000).toFixed(1) + "B";
    } else if (num >= 1000000) {
      return "$" + (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return "$" + (num / 1000).toFixed(1) + "K";
    }
    return "$" + num.toLocaleString();
  }

  formatDateTime(date) {
    if (!date) {
      return "--";
    }
    if (typeof date === "string") {
      date = new Date(date);
    }
    if (isNaN(date.getTime())) {
      return "--";
    }
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  showLoading(show) {
    const container = document.querySelector(".container");
    if (show) {
      container.classList.add("loading");
    } else {
      container.classList.remove("loading");
    }
  }

  showError(message) {
    // Create and show error notification
    const errorDiv = document.createElement("div");
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

  setActiveSymbol(symbol) {
    this.activeSymbol = symbol;

    // Toggle active tab button
    const tabButtons = document.querySelectorAll("#symbolTabs .tab-btn");
    tabButtons.forEach((btn) => {
      if (btn.getAttribute("data-symbol") === symbol) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // Toggle active panels
    this.symbols.forEach((sym) => {
      const panel = document.getElementById(`panel-${sym}`);
      if (!panel) return;
      if (sym === symbol) {
        panel.classList.add("active");
      } else {
        panel.classList.remove("active");
      }
    });

    // Ensure charts are responsive to visibility change
    const chartsForSymbol = this.charts[symbol];
    if (chartsForSymbol) {
      chartsForSymbol.price.resize();
      chartsForSymbol.volume.resize();
    }
  }
}

// Initialize the stock viewer when the page loads
document.addEventListener("DOMContentLoaded", () => {
  new StockViewer();
});

// Add some utility functions for external use
window.StockViewerUtils = {
  formatNumber: (num) => {
    if (num === null || num === undefined || isNaN(num)) {
      return "--";
    }
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toLocaleString();
  },

  formatCurrency: (num) => {
    if (num === null || num === undefined || isNaN(num)) {
      return "--";
    }
    if (num >= 1000000000) {
      return "$" + (num / 1000000000).toFixed(1) + "B";
    } else if (num >= 1000000) {
      return "$" + (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return "$" + (num / 1000).toFixed(1) + "K";
    }
    return "$" + num.toLocaleString();
  },
};
