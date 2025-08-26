// Stock Data Viewer JavaScript
class StockViewer {
  constructor() {
    this.symbols = ["FPT.VN", "GOOG", "SSI.VN"];
    this.activeSymbol = "FPT.VN";
    this.charts = {}; // { [symbol]: { price, volume } }
    this.currentData = {};
    this.timeRange = "1d";

    this.init();
  }

  init() {
    this.buildUIFromTemplate();
    this.setupEventListeners();
    this.initializeCharts();
    this.loadStockData();
    this.startAutoRefresh();
  }

  buildUIFromTemplate() {
    const tabsContainer = document.getElementById("symbolTabs");
    const dashboard = document.querySelector(".dashboard");
    const template = document.getElementById("stock-data-template");

    if (!tabsContainer || !dashboard || !template) {
      return;
    }

    tabsContainer.innerHTML = "";
    dashboard.innerHTML = "";

    this.symbols.forEach((symbol, index) => {
      // Create tab button
      const btn = document.createElement("button");
      btn.className = `tab-btn${index === 0 ? " active" : ""} btn btn-primary`;
      btn.setAttribute("data-symbol", symbol);
      btn.textContent = symbol;
      tabsContainer.appendChild(btn);

      // Create panel from template by substituting {{symbol}}
      const html = template.innerHTML.replaceAll("{{symbol}}", symbol);
      const wrapper = document.createElement("div");
      wrapper.innerHTML = html;
      const panel = wrapper.firstElementChild;
      if (index === 0) {
        panel.classList.add("active");
      }
      dashboard.appendChild(panel);
    });

    // Ensure activeSymbol matches the first tab by default
    this.activeSymbol = this.symbols[0];
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
            title: { display: true, text: `${symbol} Price History` },
            tooltip: {
              mode: "index",
              intersect: false,
              callbacks: {
                title: function (context) {
                  return `Time: ${context[0].label}`;
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: false,
              title: { display: true, text: "Price ($)" },
            },
            x: {
              title: { display: true, text: "Time" },
              ticks: {
                maxRotation: 45,
                minRotation: 0,
              },
            },
          },
          interaction: {
            mode: "nearest",
            axis: "x",
            intersect: false,
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
            title: { display: true, text: `${symbol} Volume History` },
            tooltip: {
              mode: "index",
              intersect: false,
              callbacks: {
                title: function (context) {
                  return `Time: ${context[0].label}`;
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: "Volume" },
            },
            x: {
              title: { display: true, text: "Time" },
              ticks: {
                maxRotation: 45,
                minRotation: 0,
              },
            },
          },
          interaction: {
            mode: "nearest",
            axis: "x",
            intersect: false,
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
      this.updateDataSummary(data);
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
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const twoDaysAgo = new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000);

    return {
      "FPT.VN": [
        {
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
        {
          symbol: "FPT.VN",
          price: 44.8,
          volume: 1400000,
          open_price: 44.5,
          high_price: 45.1,
          low_price: 44.0,
          previous_close: 44.2,
          change: 0.6,
          change_percent: 1.36,
          market_cap: 15000000000,
          pe_ratio: 15.2,
          dividend_yield: 2.5,
          timestamp: yesterday,
          sync_timestamp: yesterday,
          provider: "yahoo",
          status: "success",
          is_trading_hours: true,
          trading_day: this.getTradingDay(yesterday),
        },
        {
          symbol: "FPT.VN",
          price: 44.2,
          volume: 1350000,
          open_price: 43.8,
          high_price: 44.5,
          low_price: 43.5,
          previous_close: 43.9,
          change: 0.3,
          change_percent: 0.68,
          market_cap: 15000000000,
          pe_ratio: 15.2,
          dividend_yield: 2.5,
          timestamp: twoDaysAgo,
          sync_timestamp: twoDaysAgo,
          provider: "yahoo",
          status: "success",
          is_trading_hours: true,
          trading_day: this.getTradingDay(twoDaysAgo),
        },
      ],
      GOOG: [
        {
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
        {
          symbol: "GOOG",
          price: 144.5,
          volume: 24000000,
          open_price: 143.2,
          high_price: 145.8,
          low_price: 142.9,
          previous_close: 143.1,
          change: 1.4,
          change_percent: 0.98,
          market_cap: 1850000000000,
          pe_ratio: 28.5,
          dividend_yield: 0.0,
          timestamp: yesterday,
          sync_timestamp: yesterday,
          provider: "yahoo",
          status: "success",
          is_trading_hours: true,
          trading_day: this.getTradingDay(yesterday),
        },
        {
          symbol: "GOOG",
          price: 143.1,
          volume: 23500000,
          open_price: 142.5,
          high_price: 143.8,
          low_price: 142.0,
          previous_close: 142.3,
          change: 0.8,
          change_percent: 0.56,
          market_cap: 1850000000000,
          pe_ratio: 28.5,
          dividend_yield: 0.0,
          timestamp: twoDaysAgo,
          sync_timestamp: twoDaysAgo,
          provider: "yahoo",
          status: "success",
          is_trading_hours: true,
          trading_day: this.getTradingDay(twoDaysAgo),
        },
      ],
    };
  }

  getTradingDay(date) {
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    return days[date.getDay()];
  }

  updateUIForAllSymbols(data) {
    this.symbols.forEach((symbol) => {
      const stockRecords = data[symbol];
      if (
        !stockRecords ||
        !Array.isArray(stockRecords) ||
        stockRecords.length === 0
      ) {
        return;
      }

      // Latest record is first due to desc ordering
      const latest = stockRecords[0];

      const priceEl = document.getElementById(`${symbol}-price`);
      if (priceEl) {
        priceEl.textContent = latest.price
          ? `$${latest.price.toFixed(2)}`
          : "--";
      }

      if (latest.change !== null && latest.change_percent !== null) {
        this.updateChangeElement(
          `${symbol}-change`,
          latest.change,
          latest.change_percent
        );
      } else {
        const chg = document.getElementById(`${symbol}-change`);
        if (chg) chg.textContent = "--";
      }

      const vol = document.getElementById(`${symbol}-volume`);
      if (vol) vol.textContent = this.formatNumber(latest.volume);

      const mcap = document.getElementById(`${symbol}-market-cap`);
      if (mcap) mcap.textContent = this.formatCurrency(latest.market_cap);
    });
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

      // Handle empty data
      if (!Array.isArray(stockData) || stockData.length === 0) {
        this.clearChartsForSymbol(symbol);
        return;
      }

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

  clearChartsForSymbol(symbol) {
    const chartsForSymbol = this.charts[symbol];
    if (!chartsForSymbol) return;

    // Clear price chart
    chartsForSymbol.price.data.labels = [];
    chartsForSymbol.price.data.datasets = [
      {
        label: `${symbol} Price`,
        data: [],
        borderColor: symbol === "FPT.VN" ? "#36A2EB" : "#FF6384",
        backgroundColor: `${symbol === "FPT.VN" ? "#36A2EB" : "#FF6384"}20`,
        tension: 0.1,
        fill: false,
      },
    ];
    chartsForSymbol.price.update();

    // Clear volume chart
    chartsForSymbol.volume.data.labels = [];
    chartsForSymbol.volume.data.datasets = [
      {
        label: `${symbol} Volume`,
        data: [],
        backgroundColor: symbol === "FPT.VN" ? "#36A2EB" : "#FF6384",
        borderColor: symbol === "FPT.VN" ? "#36A2EB" : "#FF6384",
        borderWidth: 1,
      },
    ];
    chartsForSymbol.volume.update();
  }

  prepareSingleSymbolPriceChartData(stockData, symbol) {
    // Check if stockData is an array (historical data) or single object
    if (Array.isArray(stockData) && stockData.length > 0) {
      // Use historical data for time series chart
      const labels = stockData.map((record) =>
        this.formatDateTime(record.timestamp)
      );
      const prices = stockData.map((record) => record.price || 0);
      const color = symbol === "FPT.VN" ? "#36A2EB" : "#FF6384";

      return {
        labels: labels.reverse(), // Reverse to show oldest to newest
        datasets: [
          {
            label: `${symbol} Price`,
            data: prices.reverse(), // Reverse to show oldest to newest
            borderColor: color,
            backgroundColor: `${color}20`,
            tension: 0.1,
            fill: false,
            pointRadius: 3,
            pointHoverRadius: 6,
          },
        ],
      };
    } else {
      // Fallback to single data point (for backward compatibility)
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
  }

  prepareSingleSymbolVolumeChartData(stockData, symbol) {
    // Check if stockData is an array (historical data) or single object
    if (Array.isArray(stockData) && stockData.length > 0) {
      // Use historical data for time series chart
      const labels = stockData.map((record) =>
        this.formatDateTime(record.timestamp)
      );
      const volumes = stockData.map((record) => record.volume || 0);
      const color = symbol === "FPT.VN" ? "#36A2EB" : "#FF6384";

      return {
        labels: labels.reverse(), // Reverse to show oldest to newest
        datasets: [
          {
            label: `${symbol} Volume`,
            data: volumes.reverse(), // Reverse to show oldest to newest
            backgroundColor: color,
            borderColor: color,
            borderWidth: 1,
            borderRadius: 2,
          },
        ],
      };
    } else {
      // Fallback to single data point (for backward compatibility)
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
  }

  updateTablesForAllSymbols(data) {
    this.symbols.forEach((symbol) => {
      const tbody = document.getElementById(`stockTableBody-${symbol}`);
      if (!tbody) return;
      tbody.innerHTML = "";

      const stockRecords = data[symbol];
      if (
        !stockRecords ||
        !Array.isArray(stockRecords) ||
        stockRecords.length === 0
      ) {
        this.showEmptyTableMessage(tbody, symbol);
        return;
      }

      // Display all historical records
      stockRecords.forEach((stock, index) => {
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
    });
  }

  showEmptyTableMessage(tbody, symbol) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td colspan="10" style="text-align: center; padding: 20px; color: #7f8c8d; font-style: italic;">
        No historical data available for ${symbol}
      </td>
    `;
    tbody.appendChild(row);
  }

  updateStatusForAllSymbols() {
    this.symbols.forEach((symbol) => {
      const last = document.getElementById(`lastUpdate-${symbol}`);
      const prov = document.getElementById(`dataProvider-${symbol}`);
      const status = document.getElementById(`syncStatus-${symbol}`);

      if (
        this.currentData &&
        this.currentData[symbol] &&
        Array.isArray(this.currentData[symbol])
      ) {
        const records = this.currentData[symbol];
        if (records.length > 0) {
          const latestRecord = records[0];
          const oldestRecord = records[records.length - 1];

          if (last) {
            last.textContent = this.formatDateTime(latestRecord.timestamp);
          }

          if (prov) {
            prov.textContent = `${
              records.length
            } records from ${this.formatDateTime(
              oldestRecord.timestamp
            )} to ${this.formatDateTime(latestRecord.timestamp)}`;
          }

          if (status) {
            status.textContent = `Active (${records.length} historical records)`;
          }
        } else {
          if (last) last.textContent = "--";
          if (prov) prov.textContent = "No data";
          if (status) status.textContent = "No records";
        }
      } else {
        if (last) last.textContent = "--";
        if (prov) prov.textContent = "No data";
        if (status) status.textContent = "No records";
      }
    });
  }

  updateDataSummary(data) {
    this.symbols.forEach((symbol) => {
      const totalRecords = document.getElementById(`totalRecords-${symbol}`);
      const dataRange = document.getElementById(`dataRange-${symbol}`);

      if (
        this.currentData &&
        this.currentData[symbol] &&
        Array.isArray(this.currentData[symbol])
      ) {
        const records = this.currentData[symbol];
        if (totalRecords) totalRecords.textContent = records.length;
        if (dataRange) {
          const oldestRecord = records[records.length - 1];
          const latestRecord = records[0];
          dataRange.textContent = `${this.formatDateTime(
            oldestRecord.timestamp
          )} to ${this.formatDateTime(latestRecord.timestamp)}`;
        }
      } else {
        if (totalRecords) totalRecords.textContent = "0";
        if (dataRange) dataRange.textContent = "No data";
      }
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
    const container = document.getElementById("container");
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
  // Expose the instance so utility functions can access charts for resizing
  window.stockViewer = new StockViewer();
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

  expandCharts: (symbol) => {
    const priceChartContainer = document.getElementById(
      `priceChartContainer-${symbol}`
    );
    if (!priceChartContainer) return;

    const button = document.getElementById(`expandChartsBtn-${symbol}`);
    const icon = button ? button.querySelector("i") : null;

    const enterFullscreen = async () => {
      try {
        priceChartContainer.classList.add("fullscreen");
        if (priceChartContainer.requestFullscreen) {
          await priceChartContainer.requestFullscreen();
        }
        if (icon) {
          icon.classList.remove("bi-arrows-angle-expand");
          icon.classList.add("bi-arrows-angle-contract");
        }
      } catch (e) {
        console.error("Failed to enter fullscreen", e);
      }
    };

    const exitFullscreen = async () => {
      try {
        priceChartContainer.classList.remove("fullscreen");
        if (document.fullscreenElement && document.exitFullscreen) {
          await document.exitFullscreen();
        }
        if (icon) {
          icon.classList.remove("bi-arrows-angle-contract");
          icon.classList.add("bi-arrows-angle-expand");
        }
      } catch (e) {
        console.error("Failed to exit fullscreen", e);
      }
    };

    const isCurrentlyFullscreen =
      document.fullscreenElement === priceChartContainer;
    if (isCurrentlyFullscreen) {
      exitFullscreen();
    } else {
      enterFullscreen();
    }

    // Ensure the Chart.js instance resizes appropriately
    const resizeActiveChart = () => {
      if (!window.stockViewer || !window.stockViewer.charts) return;
      const chartsForSymbol = window.stockViewer.charts[symbol];
      if (chartsForSymbol && chartsForSymbol.price) {
        chartsForSymbol.price.resize();
      }
    };

    // Resize immediately and also when fullscreen state changes
    resizeActiveChart();
    const onFsChange = () => {
      const nowFullscreen = document.fullscreenElement === priceChartContainer;
      if (!nowFullscreen) {
        // Ensure class/icon reset if exited via ESC
        priceChartContainer.classList.remove("fullscreen");
        if (icon) {
          icon.classList.remove("bi-arrows-angle-contract");
          icon.classList.add("bi-arrows-angle-expand");
        }
      }
      // slight delay lets layout settle
      setTimeout(resizeActiveChart, 50);
    };
    document.removeEventListener("fullscreenchange", onFsChange);
    document.addEventListener("fullscreenchange", onFsChange, { once: true });
  },
};
