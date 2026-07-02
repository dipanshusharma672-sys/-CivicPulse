// Main Application Controller - Smart City Analytics Platform
// Handles UI state, data loading, KPI rendering, and ECharts visualization.

let cityAggregates = null;
let mlForecasts = null;
let activeTab = "executive";
let echartsInstances = {};

// Theme Management
let isDarkTheme = true;

// Live Mode State
let isLiveMode = false;
let liveWeatherData = null;
let livePollutionData = null;
const CITY_COORDS = {
    "Mumbai": { lat: 19.0760, lng: 72.8777 },
    "Bengaluru": { lat: 12.9716, lng: 77.5946 },
    "New Delhi": { lat: 28.6139, lng: 77.2090 }
};

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initial UI Bindings
    setupThemeToggle();
    setupLiveToggle();
    setupTabSwitching();
    setupFilters();
    
    // 2. Fetch Datasets and Initialize
    loadDashboardData();
    
    // Handle Window Resizing for ECharts
    window.addEventListener("resize", () => {
        Object.values(echartsInstances).forEach(chart => chart.resize());
    });
});

// Theme Toggle
function setupThemeToggle() {
    const themeBtn = document.getElementById("theme-btn");
    themeBtn.addEventListener("click", () => {
        isDarkTheme = !isDarkTheme;
        const body = document.body;
        const icon = themeBtn.querySelector("i");
        
        if (isDarkTheme) {
            body.classList.remove("light-theme");
            body.classList.add("dark-theme");
            icon.className = "fa-solid fa-moon";
        } else {
            body.classList.remove("dark-theme");
            body.classList.add("light-theme");
            icon.className = "fa-solid fa-sun";
        }
        
        // Re-init current tab maps/charts to apply themes
        if (cityMap) {
            cityMap.invalidateSize();
            // Trigger tile re-filter via CSS (handled in style.css)
        }
        updateActiveTabCharts();
    });
}

// Tab Switching
function setupTabSwitching() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const selectedTab = item.getAttribute("data-tab");
            if (selectedTab === activeTab) return;
            
            // Toggle active menu state
            document.querySelector(".nav-item.active").classList.remove("active");
            item.classList.add("active");
            
            // Toggle active panel state
            document.querySelector(".tab-panel.active").classList.remove("active");
            document.getElementById(`panel-${selectedTab}`).classList.add("active");
            
            // Update state
            activeTab = selectedTab;
            
            // Update header text
            const title = item.querySelector("span").innerText;
            const city = document.getElementById("city-select").value;
            const year = document.getElementById("year-select").value;
            
            document.getElementById("dashboard-title").innerText = title;
            document.getElementById("dashboard-subtitle").innerText = `Urban analytics command center for ${city} (${year})`;
            
            // Handle specific subpage requirements (like Map redrawing or Chart init)
            handleTabActivation();
        });
    });
}

// Global Filter Listeners
function setupFilters() {
    const citySelect = document.getElementById("city-select");
    const yearSelect = document.getElementById("year-select");
    
    const updateDashboard = () => {
        const city = citySelect.value;
        const year = yearSelect.value;
        
        // Update header subtitle
        const activeMenuName = document.querySelector(".nav-item.active span").innerText;
        document.getElementById("dashboard-subtitle").innerText = `Urban analytics command center for ${city} (${year})`;
        
        if (!cityAggregates) return;
        
        // Refresh KPIs and active charts
        if (isLiveMode) {
            fetchRealtimeData(city);
        } else {
            updateKPIs(city, year);
            updateActiveTabCharts();
        }
        
        // Refresh GIS Map
        if (cityMap) {
            initGISMap(city);
        }
    };
    
    citySelect.addEventListener("change", updateDashboard);
    yearSelect.addEventListener("change", updateDashboard);
}

// Load Data
async function loadDashboardData() {
    try {
        const aggsRes = await fetch("data/city_aggregates.json");
        cityAggregates = await aggsRes.json();
        
        const forecastRes = await fetch("data/ml_forecasts.json");
        mlForecasts = await forecastRes.json();
        
        // Data is ready, run initial render
        const city = document.getElementById("city-select").value;
        const year = document.getElementById("year-select").value;
        
        updateKPIs(city, year);
        
        // Init Map first
        initGISMap(city);
        setupMapControls();
        
        // Render charts for default dashboard (Executive)
        renderExecutiveCharts(city, year);
        
    } catch (err) {
        console.error("Error loading JSON dataset: ", err);
    }
}

// Map layer controllers
function setupMapControls() {
    const layerBtns = document.querySelectorAll(".map-layer-btn");
    layerBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelector(".map-layer-btn.active").classList.remove("active");
            btn.classList.add("active");
            const layer = btn.getAttribute("data-layer");
            toggleGISLayer(layer);
        });
    });
}

// Handle tab activation
function handleTabActivation() {
    const city = document.getElementById("city-select").value;
    const year = document.getElementById("year-select").value;
    
    // Invalidate map size so Leaflet updates layout properly
    if (activeTab === "executive" && cityMap) {
        setTimeout(() => cityMap.invalidateSize(), 100);
    }
    
    // Re-render the active tab charts
    updateActiveTabCharts();
}

// Update Active Tab Charts
function updateActiveTabCharts() {
    if (!cityAggregates) return;
    
    const city = document.getElementById("city-select").value;
    const year = document.getElementById("year-select").value;
    
    // Dispose previous active charts to avoid leaks
    disposeActiveCharts();
    
    // Render specific charts based on current panel
    if (activeTab === "executive") {
        renderExecutiveCharts(city, year);
    } else if (activeTab === "traffic") {
        renderTrafficCharts(city, year);
    } else if (activeTab === "pollution") {
        renderPollutionCharts(city, year);
    } else if (activeTab === "weather") {
        renderWeatherCharts(city, year);
    } else if (activeTab === "crime") {
        renderCrimeCharts(city, year);
    } else if (activeTab === "transport") {
        renderTransportCharts(city, year);
    } else if (activeTab === "population") {
        renderPopulationCharts(city, year);
    } else if (activeTab === "energy") {
        renderEnergyCharts(city, year);
    } else if (activeTab === "water") {
        renderWaterCharts(city, year);
    } else if (activeTab === "healthcare") {
        renderHealthcareCharts(city, year);
    } else if (activeTab === "education") {
        renderEducationCharts(city, year);
    } else if (activeTab === "economy") {
        renderEconomyCharts(city, year);
    }
}

// Clean up charts
function disposeActiveCharts() {
    Object.keys(echartsInstances).forEach(key => {
        if (echartsInstances[key]) {
            echartsInstances[key].dispose();
            delete echartsInstances[key];
        }
    });
}

// Common Chart Theme options
function getChartTheme() {
    return {
        textColor: isDarkTheme ? "#94a3b8" : "#475569",
        gridBorderColor: isDarkTheme ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)",
        tooltipBg: isDarkTheme ? "#0f1626" : "#ffffff",
        tooltipBorder: isDarkTheme ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)",
        tooltipText: isDarkTheme ? "#f1f5f9" : "#0f172a"
    };
}

// Render dynamic KPIs
function updateKPIs(city, year) {
    const data = cityAggregates[city][year].kpis;
    
    // Helper to safety format numbers
    const fmt = (num) => Number(num).toLocaleString();
    
    // Executive Dashboard KPIs
    document.getElementById("exec-pop").innerText = fmt(data.population);
    document.getElementById("exec-density").innerText = fmt(data.population / (city === "Mumbai" ? 603 : (city === "Bengaluru" ? 709 : 1484)));
    document.getElementById("exec-aqi").innerText = Math.round(data.aqi);
    document.getElementById("exec-crime").innerText = fmt(data.crimes);
    document.getElementById("exec-traffic").innerText = data.traffic_congestion + "%";
    document.getElementById("exec-passengers").innerText = fmt(data.transport_users);
    document.getElementById("exec-temp").innerText = data.temperature + " °C";
    document.getElementById("exec-rain").innerText = Math.round(data.rainfall);
    document.getElementById("exec-energy").innerText = fmt(data.energy_consumption) + " MWh";
    document.getElementById("exec-renew").innerText = data.renewable_pct;
    document.getElementById("exec-water").innerText = fmt(data.water_usage) + " ML";
    document.getElementById("exec-reservoir").innerText = Math.round(data.reservoir_level);
    document.getElementById("exec-green").innerText = data.green_area + "%";
    document.getElementById("exec-response").innerText = data.emergency_response_time + " mins";
    
    const aqiText = data.aqi < 50 ? "Good" : (data.aqi < 100 ? "Moderate" : "Unhealthy");
    const aqiTrend = document.getElementById("exec-aqi-status");
    aqiTrend.innerText = aqiText;
    aqiTrend.className = `kpi-trend ${data.aqi < 50 ? "positive" : (data.aqi < 100 ? "neutral" : "negative")}`;
    
    // Sub-dashboards KPIs
    // 2. Traffic
    safeSetText("traffic-speed", data.avg_speed + " km/h");
    safeSetText("traffic-congestion", data.traffic_congestion + "%");
    safeSetText("traffic-vehicles", fmt(data.vehicle_count));
    safeSetText("traffic-peak", "08:00 - 10:00");
    safeSetText("traffic-accidents", data.accidents);
    
    // 3. Pollution
    safeSetText("pollution-aqi", Math.round(data.aqi));
    safeSetText("pollution-pm25", data.pm2_5);
    safeSetText("pollution-pm10", data.pm10);
    safeSetText("pollution-co", data.co);
    safeSetText("pollution-no2", data.no2);
    safeSetText("pollution-so2", data.so2);
    
    const aqiCard = document.querySelector('.kpi-card[data-status="aqi"]');
    if (aqiCard) {
        aqiCard.className = "kpi-card mini " + (data.aqi < 50 ? "good" : (data.aqi < 100 ? "moderate" : "poor"));
    }
    
    // 4. Weather
    safeSetText("weather-temp", data.temperature);
    safeSetText("weather-humidity", data.humidity + "%");
    safeSetText("weather-rain", Math.round(data.rainfall) + " mm");
    safeSetText("weather-wind", data.wind_speed + " km/h");
    safeSetText("weather-pressure", data.pressure + " hPa");
    safeSetText("weather-uv", Math.round(data.uv_index));
    
    // 5. Crime
    safeSetText("crime-total", fmt(data.crimes));
    safeSetText("crime-rate", Math.round((data.crimes / data.population) * 100000));
    safeSetText("crime-arrest", "35.2%");
    safeSetText("crime-solved", fmt(Math.round(data.crimes * 0.42)));
    safeSetText("crime-active", fmt(Math.round(data.crimes * 0.58)));
    
    // 6. Public Transport
    safeSetText("transport-passengers", fmt(data.transport_users));
    safeSetText("transport-bus", data.bus_utilization + "%");
    safeSetText("transport-metro", fmt(data.metro_ridership));
    safeSetText("transport-delay", data.average_delay + " mins");
    safeSetText("transport-efficiency", data.route_efficiency + "%");
    
    // 7. Population
    safeSetText("pop-population", fmt(data.population));
    safeSetText("pop-density", fmt(data.population / (city === "Mumbai" ? 603 : (city === "Bengaluru" ? 709 : 1484))));
    safeSetText("pop-literacy", data.literacy + "%");
    safeSetText("pop-employment", data.employment + "%");
    safeSetText("pop-growth", data.urban_growth + "%");
    
    // 8. Energy
    safeSetText("energy-consumption", fmt(data.energy_consumption) + " MWh");
    safeSetText("energy-renewable", data.renewable_pct + "%");
    safeSetText("energy-peak", data.peak_energy + " MWh");
    
    // 9. Water
    safeSetText("water-use", fmt(data.water_usage) + " ML");
    safeSetText("water-loss", data.water_loss + "%");
    safeSetText("water-reservoir", data.reservoir_level + "%");
    safeSetText("water-supply", fmt(data.daily_supply) + " ML");
    
    // 10. Healthcare
    safeSetText("health-hospitals", data.schools / 30); // scale hospital relative schools
    safeSetText("health-beds", data.bed_availability + "%");
    safeSetText("health-diseases", fmt(data.disease_cases));
    safeSetText("health-vaccination", data.vaccination_pct + "%");
    
    // 11. Education
    safeSetText("edu-schools", data.schools);
    safeSetText("edu-colleges", data.colleges);
    safeSetText("edu-literacy", data.literacy + "%");
    safeSetText("edu-graduation", data.graduation + "%");
    safeSetText("edu-enrollment", fmt(data.enrollment));
    
    // 12. Economy
    safeSetText("econ-gdp", "$" + data.gdp + " B");
    safeSetText("econ-employment", data.employment + "%");
    safeSetText("econ-inflation", data.inflation + "%");
    safeSetText("econ-income", "$" + fmt(data.income));
    
    // Set dynamic insights
    if (activeTab === "traffic") {
        const insightText = document.getElementById("traffic-insight-text");
        if (insightText) {
            insightText.innerHTML = `Traffic congestion increases by 42% between 8–10 AM. Recommended ML tomorrow's Congestion Index: <strong>${mlForecasts[city].traffic.tomorrow_congestion}%</strong>`;
        }
    }
}

function safeSetText(id, val) {
    const el = document.getElementById(id);
    if (el) el.innerText = val;
}

// ----------------------------------------------------
// 📊 CHART RENDER MODULES (ECHARTS)
// ----------------------------------------------------

// 1. EXECUTIVE CHARTS
function renderExecutiveCharts(city, year) {
    const trends = cityAggregates[city][year].monthly_trends;
    const theme = getChartTheme();
    
    const chartDom = document.getElementById("exec-chart-index");
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    echartsInstances["exec-index"] = chart;
    
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const aqiData = months.map((_, i) => Math.round(trends.aqi[i + 1] || 0));
    const trafficData = months.map((_, i) => Math.round(trends.traffic[i + 1] || 0));
    const tempData = months.map((_, i) => Math.round(trends.weather[i + 1] || 0));
    
    const option = {
        backgroundColor: "transparent",
        tooltip: {
            trigger: "axis",
            backgroundColor: theme.tooltipBg,
            borderColor: theme.tooltipBorder,
            textStyle: { color: theme.tooltipText }
        },
        legend: {
            data: ["AQI Index", "Traffic Congestion %", "Temperature (°C)"],
            textStyle: { color: theme.textColor }
        },
        grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
        xAxis: {
            type: "category",
            boundaryGap: false,
            data: months,
            axisLabel: { color: theme.textColor },
            axisLine: { lineStyle: { color: theme.gridBorderColor } }
        },
        yAxis: [
            {
                type: "value",
                name: "Score / %",
                axisLabel: { color: theme.textColor },
                splitLine: { lineStyle: { color: theme.gridBorderColor } }
            },
            {
                type: "value",
                name: "Temp (°C)",
                axisLabel: { color: theme.textColor },
                splitLine: { show: false }
            }
        ],
        series: [
            {
                name: "AQI Index",
                type: "line",
                smooth: true,
                data: aqiData,
                lineStyle: { width: 3, color: "#f59e0b" },
                itemStyle: { color: "#f59e0b" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(245, 158, 11, 0.2)" },
                        { offset: 1, color: "rgba(245, 158, 11, 0.0)" }
                    ])
                }
            },
            {
                name: "Traffic Congestion %",
                type: "line",
                smooth: true,
                data: trafficData,
                lineStyle: { width: 3, color: "#06b6d4" },
                itemStyle: { color: "#06b6d4" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(6, 182, 212, 0.2)" },
                        { offset: 1, color: "rgba(6, 182, 212, 0.0)" }
                    ])
                }
            },
            {
                name: "Temperature (°C)",
                type: "line",
                yAxisIndex: 1,
                smooth: true,
                data: tempData,
                lineStyle: { width: 3, color: "#a855f7" },
                itemStyle: { color: "#a855f7" }
            }
        ]
    };
    chart.setOption(option);
}

// 2. TRAFFIC CHARTS
function renderTrafficCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 2.1 Trend Chart
    const trendDom = document.getElementById("traffic-chart-trend");
    if (trendDom) {
        const chart = echarts.init(trendDom);
        echartsInstances["traffic-trend"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const data = months.map((_, i) => Math.round(aggs.monthly_trends.traffic[i + 1] || 0));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: months, axisLabel: { color: theme.textColor }, axisLine: { lineStyle: { color: theme.gridBorderColor } } },
            yAxis: { type: "value", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Congestion Index %",
                type: "bar",
                data: data,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "#06b6d4" },
                        { offset: 1, color: "#3b82f6" }
                    ]),
                    borderRadius: [4, 4, 0, 0]
                }
            }]
        });
    }
    
    // 2.2 Area Chart
    const areaDom = document.getElementById("traffic-chart-area");
    if (areaDom) {
        const chart = echarts.init(areaDom);
        echartsInstances["traffic-area"] = chart;
        const areas = Object.keys(aggs.traffic_areas.congestion);
        const values = Object.values(aggs.traffic_areas.congestion).map(v => Math.round(v));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "8%", bottom: "5%", containLabel: true },
            xAxis: { type: "value", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            yAxis: { type: "category", data: areas, axisLabel: { color: theme.textColor }, axisLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Average Congestion Index",
                type: "bar",
                data: values,
                itemStyle: {
                    color: "#a855f7"
                }
            }]
        });
    }

    // 2.3 ML Forecast Chart
    const forecastDom = document.getElementById("traffic-chart-forecast");
    if (forecastDom) {
        const chart = echarts.init(forecastDom);
        echartsInstances["traffic-forecast"] = chart;
        
        const forecast = mlForecasts[city].traffic.congestion_7day;
        const dates = mlForecasts[city].weather_aqi.dates;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            legend: { data: ["AI Projected Congestion Index"], textStyle: { color: theme.textColor } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: dates, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "% Congestion", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "AI Projected Congestion Index",
                type: "line",
                smooth: true,
                data: forecast,
                lineStyle: { width: 3, color: "#06b6d4" },
                itemStyle: { color: "#06b6d4" },
                markLine: {
                    data: [{ type: "average", name: "Avg Projected Congestion" }]
                }
            }]
        });
    }
}

// 3. POLLUTION CHARTS
function renderPollutionCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 3.1 Monthly AQI Trend
    const trendDom = document.getElementById("pollution-chart-trend");
    if (trendDom) {
        const chart = echarts.init(trendDom);
        echartsInstances["pollution-trend"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const data = months.map((_, i) => Math.round(aggs.monthly_trends.aqi[i + 1] || 0));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: months, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "AQI",
                type: "line",
                smooth: true,
                data: data,
                lineStyle: { width: 3, color: "#f59e0b" },
                itemStyle: { color: "#f59e0b" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(245, 158, 11, 0.25)" },
                        { offset: 1, color: "rgba(245, 158, 11, 0)" }
                    ])
                }
            }]
        });
    }
    
    // 3.2 Pollutant radar/dist
    const distDom = document.getElementById("pollution-chart-dist");
    if (distDom) {
        const chart = echarts.init(distDom);
        echartsInstances["pollution-dist"] = chart;
        const kpis = aggs.kpis;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "item", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            legend: { top: "5%", left: "center", textStyle: { color: theme.textColor } },
            series: [{
                name: "Pollutant Contribution",
                type: "pie",
                radius: ["40%", "70%"],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 10, borderColor: isDarkTheme ? "#080c14" : "#f8fafc", borderWidth: 2 },
                label: { show: false, position: "center" },
                emphasis: { label: { show: true, fontSize: 16, fontWeight: "bold", color: theme.tooltipText } },
                labelLine: { show: false },
                data: [
                    { value: kpis.pm2_5, name: "PM2.5" },
                    { value: kpis.pm10, name: "PM10" },
                    { value: kpis.co * 100, name: "CO (Scaled)" },
                    { value: kpis.no2, name: "NO2" },
                    { value: kpis.so2, name: "SO2" }
                ]
            }]
        });
    }

    // 3.3 Forecast
    const forecastDom = document.getElementById("pollution-chart-forecast");
    if (forecastDom) {
        const chart = echarts.init(forecastDom);
        echartsInstances["pollution-forecast"] = chart;
        
        let forecast = mlForecasts[city].weather_aqi.aqi;
        let dates = mlForecasts[city].weather_aqi.dates;
        let legendName = "RF Forecasted AQI";
        
        if (isLiveMode && livePollutionData) {
            dates = livePollutionData.hourly.time.slice(0, 24).map(t => new Date(t).getHours() + ":00");
            forecast = livePollutionData.hourly.european_aqi.slice(0, 24);
            legendName = "Live Real-Time AQI Forecast (Open-Meteo)";
        }
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            legend: { data: [legendName], textStyle: { color: theme.textColor } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: dates, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "AQI Index", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: legendName,
                type: "line",
                smooth: true,
                data: forecast,
                lineStyle: { width: 3, color: "#ef4444" },
                itemStyle: { color: "#ef4444" },
                markPoint: {
                    data: [
                        { type: "max", name: "Max AQI Peak" },
                        { type: "min", name: "Min AQI Drop" }
                    ]
                }
            }]
        });
    }
}

// 4. WEATHER CHARTS
function renderWeatherCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 4.1 Temperature Trend
    const tempDom = document.getElementById("weather-chart-temp");
    if (tempDom) {
        const chart = echarts.init(tempDom);
        echartsInstances["weather-temp"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const temps = months.map((_, i) => Math.round(aggs.monthly_trends.weather[i + 1] || 0));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: months, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Temp (°C)", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Temperature",
                type: "line",
                smooth: true,
                data: temps,
                lineStyle: { width: 3, color: "#f59e0b" },
                itemStyle: { color: "#f59e0b" }
            }]
        });
    }
    
    // 4.2 Rain
    const rainDom = document.getElementById("weather-chart-rain");
    if (rainDom) {
        const chart = echarts.init(rainDom);
        echartsInstances["weather-rain"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const rains = months.map((_, i) => Math.round(aggs.monthly_trends.weather[i + 1] * 12 * (i%3 === 0 ? 0.3 : 0.8))); // simulated rain values scaled
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: months, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Rainfall (mm)", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Rainfall",
                type: "bar",
                data: rains,
                itemStyle: { color: "#3b82f6", borderRadius: [4, 4, 0, 0] }
            }]
        });
    }
    
    // 4.3 Forecast
    const forecastDom = document.getElementById("weather-chart-forecast");
    if (forecastDom) {
        const chart = echarts.init(forecastDom);
        echartsInstances["weather-forecast"] = chart;
        
        let dates = mlForecasts[city].weather_aqi.dates;
        let predTemp = mlForecasts[city].weather_aqi.temperature;
        let predRain = mlForecasts[city].weather_aqi.rainfall;
        let legendTemp = "Temperature Forecast";
        let legendRain = "Rainfall Forecast";
        
        if (isLiveMode && liveWeatherData) {
            dates = liveWeatherData.hourly.time.slice(0, 24).map(t => new Date(t).getHours() + ":00");
            predTemp = liveWeatherData.hourly.temperature_2m.slice(0, 24);
            predRain = liveWeatherData.hourly.precipitation.slice(0, 24);
            legendTemp = "Live Real-Time Temp (Open-Meteo)";
            legendRain = "Live Real-Time Rain (Open-Meteo)";
        }
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            legend: { data: [legendTemp, legendRain], textStyle: { color: theme.textColor } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: dates, axisLabel: { color: theme.textColor } },
            yAxis: [
                { type: "value", name: "Temp (°C)", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
                { type: "value", name: "Rain (mm)", axisLabel: { color: theme.textColor }, splitLine: { show: false } }
            ],
            series: [
                { name: legendTemp, type: "line", smooth: true, data: predTemp, itemStyle: { color: "#f59e0b" } },
                { name: legendRain, type: "bar", yAxisIndex: 1, data: predRain, itemStyle: { color: "#3b82f6" } }
            ]
        });
    }
}

// 5. CRIME CHARTS
function renderCrimeCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 5.1 Categories
    const catDom = document.getElementById("crime-chart-category");
    if (catDom) {
        const chart = echarts.init(catDom);
        echartsInstances["crime-cat"] = chart;
        const data = Object.entries(aggs.crime_categories).map(([k, v]) => ({ name: k, value: v }));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "item", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            legend: { bottom: "0", left: "center", textStyle: { color: theme.textColor } },
            series: [{
                name: "Incident Category",
                type: "pie",
                radius: "60%",
                data: data,
                emphasis: {
                    itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: "rgba(0, 0, 0, 0.5)" }
                }
            }]
        });
    }
    
    // 5.2 Districts
    const distDom = document.getElementById("crime-chart-district");
    if (distDom) {
        const chart = echarts.init(distDom);
        echartsInstances["crime-dist"] = chart;
        const districts = Object.keys(aggs.crime_districts);
        const values = Object.values(aggs.crime_districts);
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: districts, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Incidents Registered",
                type: "bar",
                data: values,
                itemStyle: { color: "#ef4444", borderRadius: [4, 4, 0, 0] }
            }]
        });
    }
    
    // 5.3 Crime Forecast
    const forecastDom = document.getElementById("crime-chart-forecast");
    if (forecastDom) {
        const chart = echarts.init(forecastDom);
        echartsInstances["crime-forecast"] = chart;
        
        const dates = mlForecasts[city].weather_aqi.dates;
        const crimes = mlForecasts[city].crime.future_7day_crimes;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: dates, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Expected Daily Crimes", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "AI Crime Incidents Estimate",
                type: "line",
                smooth: true,
                data: crimes,
                lineStyle: { width: 3, color: "#ef4444" },
                itemStyle: { color: "#ef4444" }
            }]
        });
    }
}

// 6. PUBLIC TRANSPORT CHARTS
function renderTransportCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 6.1 Passengers Monthly Trend
    const trendDom = document.getElementById("transport-chart-trend");
    if (trendDom) {
        const chart = echarts.init(trendDom);
        echartsInstances["transport-trend"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const data = months.map((_, i) => Math.round(aggs.monthly_trends.passengers[i + 1] || 0));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: months, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Total Passengers", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Daily Riders",
                type: "line",
                smooth: true,
                data: data,
                lineStyle: { width: 3, color: "#06b6d4" },
                itemStyle: { color: "#06b6d4" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(6, 182, 212, 0.2)" },
                        { offset: 1, color: "rgba(6, 182, 212, 0)" }
                    ])
                }
            }]
        });
    }
    
    // 6.2 Bus vs Metro occupancy
    const distDom = document.getElementById("transport-chart-dist");
    if (distDom) {
        const chart = echarts.init(distDom);
        echartsInstances["transport-dist"] = chart;
        const kpis = aggs.kpis;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "item", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            legend: { top: "5%", left: "center", textStyle: { color: theme.textColor } },
            series: [{
                name: "Load Split",
                type: "pie",
                radius: ["50%", "70%"],
                avoidLabelOverlap: false,
                label: { show: false, position: "center" },
                emphasis: { label: { show: true, fontSize: 16, fontWeight: "bold", color: theme.tooltipText } },
                data: [
                    { value: kpis.metro_ridership, name: "Metro Rail Loads" },
                    { value: Math.round(kpis.transport_users - kpis.metro_ridership), name: "Bus Feeders Loads" }
                ],
                itemStyle: {
                    color: (params) => params.dataIndex === 0 ? "#a855f7" : "#06b6d4"
                }
            }]
        });
    }

    // 6.3 Forecast
    const forecastDom = document.getElementById("transport-chart-forecast");
    if (forecastDom) {
        const chart = echarts.init(forecastDom);
        echartsInstances["transport-forecast"] = chart;
        
        const dates = mlForecasts[city].weather_aqi.dates;
        const riders = mlForecasts[city].transport.future_7day_passengers;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: dates, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Riders Demand Forecast", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "ML Passenger Estimate",
                type: "line",
                smooth: true,
                data: riders,
                lineStyle: { width: 3, color: "#3b82f6" },
                itemStyle: { color: "#3b82f6" }
            }]
        });
    }
}

// 7. POPULATION CHARTS
function renderPopulationCharts(city, year) {
    const forecast = mlForecasts[city].population_growth;
    const theme = getChartTheme();
    
    const chartDom = document.getElementById("pop-chart-forecast");
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    echartsInstances["pop-forecast"] = chart;
    
    chart.setOption({
        backgroundColor: "transparent",
        tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
        grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
        xAxis: { type: "category", boundaryGap: false, data: forecast.years.map(String), axisLabel: { color: theme.textColor } },
        yAxis: { type: "value", name: "Population", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
        series: [{
            name: "Projected Population",
            type: "line",
            smooth: true,
            data: forecast.population,
            lineStyle: { width: 4, color: "#10b981" },
            itemStyle: { color: "#10b981" },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: "rgba(16, 185, 129, 0.2)" },
                    { offset: 1, color: "rgba(16, 185, 129, 0)" }
                ])
            }
        }]
    });
}

// 8. ENERGY CHARTS
function renderEnergyCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 8.1 Split
    const splitDom = document.getElementById("energy-chart-split");
    if (splitDom) {
        const chart = echarts.init(splitDom);
        echartsInstances["energy-split"] = chart;
        const renew = aggs.kpis.renewable_pct;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "item", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            legend: { top: "5%", left: "center", textStyle: { color: theme.textColor } },
            series: [{
                name: "Energy Mix",
                type: "pie",
                radius: "60%",
                data: [
                    { value: renew, name: "Renewables (Solar/Wind)" },
                    { value: 100 - renew, name: "Conventional Power (Grid)" }
                ],
                itemStyle: {
                    color: (params) => params.dataIndex === 0 ? "#10b981" : "#ef4444"
                }
            }]
        });
    }
    
    // 8.2 Sector Consumptions
    const sectorDom = document.getElementById("energy-chart-sector");
    if (sectorDom) {
        const chart = echarts.init(sectorDom);
        echartsInstances["energy-sector"] = chart;
        
        // sector consumption averages
        const cons = aggs.kpis.energy_consumption;
        const res = Math.round(cons * 0.35);
        const com = Math.round(cons * 0.35);
        const ind = Math.round(cons * 0.3);
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "item", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: ["Residential", "Commercial", "Industrial"], axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "MWh Consumption", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Sector Consumption",
                type: "bar",
                data: [res, com, ind],
                itemStyle: { color: "#a855f7" }
            }]
        });
    }
    
    // 8.3 Peak load predictions
    const forecastDom = document.getElementById("energy-chart-forecast");
    if (forecastDom) {
        const chart = echarts.init(forecastDom);
        echartsInstances["energy-forecast"] = chart;
        
        const dates = mlForecasts[city].weather_aqi.dates;
        const demand = mlForecasts[city].energy.future_7day_demand;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: dates, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Peak demand (MWh)", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Peak Grid Demand Estimate",
                type: "line",
                smooth: true,
                data: demand,
                lineStyle: { width: 3, color: "#f59e0b" },
                itemStyle: { color: "#f59e0b" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(245, 158, 11, 0.15)" },
                        { offset: 1, color: "rgba(245, 158, 11, 0)" }
                    ])
                }
            }]
        });
    }
}

// 9. WATER CHARTS
function renderWaterCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 9.1 Reservoir levels
    const levelDom = document.getElementById("water-chart-level");
    if (levelDom) {
        const chart = echarts.init(levelDom);
        echartsInstances["water-level"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        // Simulated cyclic reservoir drops in dry summer
        const data = months.map((_, i) => Math.round(aggs.kpis.reservoir_level + Math.sin(i * 0.5) * 8));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: months, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "% Capacity", min: 0, max: 100, axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Water Reserve Capacity",
                type: "line",
                smooth: true,
                data: data,
                lineStyle: { width: 3, color: "#3b82f6" },
                itemStyle: { color: "#3b82f6" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(59, 130, 246, 0.2)" },
                        { offset: 1, color: "rgba(59, 130, 246, 0)" }
                    ])
                }
            }]
        });
    }
    
    // 9.2 Water Leakages
    const leakageDom = document.getElementById("water-chart-leakage");
    if (leakageDom) {
        const chart = echarts.init(leakageDom);
        echartsInstances["water-leakage"] = chart;
        const loss = aggs.kpis.water_loss;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "item", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            series: [{
                name: "Water Pipe Integrity",
                type: "pie",
                radius: "60%",
                data: [
                    { value: 100 - loss, name: "Delivered to Consumers" },
                    { value: loss, name: "Leaked / Pipe Unaccounted" }
                ],
                itemStyle: {
                    color: (params) => params.dataIndex === 0 ? "#10b981" : "#ef4444"
                }
            }]
        });
    }
    
    // 9.3 Forecast
    const forecastDom = document.getElementById("water-chart-forecast");
    if (forecastDom) {
        const chart = echarts.init(forecastDom);
        echartsInstances["water-forecast"] = chart;
        
        const dates = mlForecasts[city].weather_aqi.dates;
        const demand = mlForecasts[city].water.future_7day_demand;
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: dates, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Usage Forecast (ML)", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "AI Water Consumption Estimate",
                type: "line",
                smooth: true,
                data: demand,
                lineStyle: { width: 3, color: "#06b6d4" },
                itemStyle: { color: "#06b6d4" }
            }]
        });
    }
}

// 10. HEALTHCARE CHARTS
function renderHealthcareCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    // 10.1 Bed Availability
    const bedsDom = document.getElementById("health-chart-beds");
    if (bedsDom) {
        const chart = echarts.init(bedsDom);
        echartsInstances["health-beds"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        // Simulated bed availability monthly trends
        const data = months.map((_, i) => Math.round(aggs.kpis.bed_availability + Math.cos(i * 0.5) * 5));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", boundaryGap: false, data: months, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "ICU Bed % Avail", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Bed Availability",
                type: "line",
                data: data,
                lineStyle: { width: 3, color: "#10b981" },
                itemStyle: { color: "#10b981" }
            }]
        });
    }
    
    // 10.2 Disease trends
    const disDom = document.getElementById("health-chart-diseases");
    if (disDom) {
        const chart = echarts.init(disDom);
        echartsInstances["health-diseases"] = chart;
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const data = months.map((_, i) => Math.round(aggs.monthly_trends.diseases[i + 1] || 0));
        
        chart.setOption({
            backgroundColor: "transparent",
            tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
            grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: months, axisLabel: { color: theme.textColor } },
            yAxis: { type: "value", name: "Admitted Cases", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            series: [{
                name: "Disease Admissions",
                type: "bar",
                data: data,
                itemStyle: { color: "#ef4444", borderRadius: [4, 4, 0, 0] }
            }]
        });
    }
}

// 11. EDUCATION CHARTS
function renderEducationCharts(city, year) {
    const aggs = cityAggregates[city][year];
    const theme = getChartTheme();
    
    const chartDom = document.getElementById("edu-chart-trend");
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    echartsInstances["edu-trend"] = chart;
    
    // Multi-year comparison
    const years = ["2024", "2025", "2026"];
    const literacy = [];
    const graduation = [];
    
    // Pull multi-year metrics
    years.forEach(yr => {
        const lyr = cityAggregates[city][yr].kpis;
        literacy.push(lyr.literacy);
        graduation.push(lyr.graduation);
    });
    
    chart.setOption({
        backgroundColor: "transparent",
        tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
        legend: { data: ["Literacy Rate %", "Graduation Rate %"], textStyle: { color: theme.textColor } },
        grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
        xAxis: { type: "category", data: years, axisLabel: { color: theme.textColor } },
        yAxis: { type: "value", min: 70, max: 100, axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
        series: [
            { name: "Literacy Rate %", type: "line", data: literacy, lineStyle: { width: 3 }, itemStyle: { color: "#06b6d4" } },
            { name: "Graduation Rate %", type: "line", data: graduation, lineStyle: { width: 3 }, itemStyle: { color: "#a855f7" } }
        ]
    });
}

// 12. ECONOMIC CHARTS
function renderEconomyCharts(city, year) {
    const theme = getChartTheme();
    
    const chartDom = document.getElementById("econ-chart-growth");
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    echartsInstances["econ-growth"] = chart;
    
    const years = ["2024", "2025", "2026"];
    const gdp = [];
    const income = [];
    
    years.forEach(yr => {
        const eyr = cityAggregates[city][yr].kpis;
        gdp.push(eyr.gdp);
        income.push(eyr.income);
    });
    
    chart.setOption({
        backgroundColor: "transparent",
        tooltip: { trigger: "axis", backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.tooltipText } },
        legend: { data: ["GDP ($ Billions)", "Avg Disposable Income ($)"], textStyle: { color: theme.textColor } },
        grid: { left: "4%", right: "4%", bottom: "5%", containLabel: true },
        xAxis: { type: "category", data: years, axisLabel: { color: theme.textColor } },
        yAxis: [
            { type: "value", name: "GDP ($B)", axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.gridBorderColor } } },
            { type: "value", name: "Income ($)", axisLabel: { color: theme.textColor }, splitLine: { show: false } }
        ],
        series: [
            { name: "GDP ($ Billions)", type: "bar", data: gdp, itemStyle: { color: "#3b82f6" } },
            { name: "Avg Disposable Income ($)", type: "line", yAxisIndex: 1, data: income, lineStyle: { width: 3 }, itemStyle: { color: "#10b981" } }
        ]
    });
}

// ----------------------------------------------------
// 📡 LIVE REAL-TIME DATA MODULES
// ----------------------------------------------------

function setupLiveToggle() {
    const liveBtn = document.getElementById("live-btn");
    if (!liveBtn) return;
    
    liveBtn.addEventListener("click", async () => {
        isLiveMode = !isLiveMode;
        
        const city = document.getElementById("city-select").value;
        const year = document.getElementById("year-select").value;
        const yearSelect = document.getElementById("year-select");
        
        if (isLiveMode) {
            liveBtn.classList.add("live-active");
            liveBtn.querySelector("span").innerText = "Disconnect";
            
            // Disable year selector while in live mode, since year is not applicable
            yearSelect.disabled = true;
            
            await fetchRealtimeData(city);
        } else {
            liveBtn.classList.remove("live-active");
            liveBtn.querySelector("span").innerText = "Go Live";
            
            // Enable year selector back
            yearSelect.disabled = false;
            
            // Revert all live labels / titles
            removeLiveBadges();
            
            // Revert
            updateKPIs(city, year);
            updateActiveTabCharts();
        }
    });
}

async function fetchRealtimeData(city) {
    const coords = CITY_COORDS[city];
    if (!coords) return;
    
    try {
        document.getElementById("dashboard-subtitle").innerText = `Connecting to live Open-Meteo API sensors for ${city}...`;
        
        // 1. Fetch current weather from Open-Meteo
        const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lng}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,surface_pressure,uv_index&hourly=temperature_2m,precipitation,relative_humidity_2m`;
        const weatherRes = await fetch(weatherUrl);
        const weatherJson = await weatherRes.json();
        liveWeatherData = weatherJson;
        
        // 2. Fetch current AQI from Open-Meteo Air Quality
        const pollutionUrl = `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${coords.lat}&longitude=${coords.lng}&current=european_aqi,pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide&hourly=european_aqi,pm2_5,pm10`;
        const pollutionRes = await fetch(pollutionUrl);
        const pollutionJson = await pollutionRes.json();
        livePollutionData = pollutionJson;
        
        // Update the UI
        updateLiveUI(city);
        updateActiveTabCharts();
        
    } catch (err) {
        console.error("Failed to retrieve real-time API data:", err);
        document.getElementById("dashboard-subtitle").innerText = `Failed to connect live feeds. Reverting...`;
        
        const liveBtn = document.getElementById("live-btn");
        if (liveBtn) {
            liveBtn.classList.remove("live-active");
            liveBtn.querySelector("span").innerText = "Go Live";
        }
        isLiveMode = false;
        document.getElementById("year-select").disabled = false;
        
        const year = document.getElementById("year-select").value;
        removeLiveBadges();
        updateKPIs(city, year);
        updateActiveTabCharts();
    }
}

function removeLiveBadges() {
    document.querySelectorAll(".live-badge").forEach(el => el.remove());
}

function addLiveBadge(element) {
    if (!element) return;
    if (element.querySelector(".live-badge")) return;
    const badge = document.createElement("span");
    badge.className = "live-badge";
    badge.innerText = "Live";
    element.appendChild(badge);
}

function updateLiveUI(city) {
    if (!liveWeatherData || !livePollutionData) return;
    
    const weather = liveWeatherData.current;
    const pollution = livePollutionData.current;
    
    document.getElementById("dashboard-subtitle").innerText = `Live API Feed: Connected to Open-Meteo sensors for ${city} (Current: ${new Date().toLocaleTimeString()})`;
    
    // Add live badges to relevant KPIs
    addLiveBadge(document.querySelector('.kpi-card[data-metric="aqi"] h3'));
    addLiveBadge(document.querySelector('.kpi-card[data-metric="weather"] h3'));
    addLiveBadge(document.querySelector('.kpi-card[data-status="aqi"] h4'));
    addLiveBadge(document.querySelector('#panel-weather .kpi-grid-mini div:first-child h4'));
    
    // Update live metrics on elements
    // Exec Tab
    document.getElementById("exec-aqi").innerText = Math.round(pollution.european_aqi);
    document.getElementById("exec-temp").innerText = weather.temperature_2m + " °C";
    document.getElementById("exec-rain").innerText = weather.precipitation;
    
    const aqiText = pollution.european_aqi < 50 ? "Good" : (pollution.european_aqi < 100 ? "Moderate" : "Unhealthy");
    const aqiTrend = document.getElementById("exec-aqi-status");
    aqiTrend.innerText = aqiText;
    aqiTrend.className = `kpi-trend ${pollution.european_aqi < 50 ? "positive" : (pollution.european_aqi < 100 ? "neutral" : "negative")}`;
    
    // Weather Subpage KPIs
    safeSetText("weather-temp", weather.temperature_2m);
    safeSetText("weather-humidity", Math.round(weather.relative_humidity_2m) + "%");
    safeSetText("weather-rain", weather.precipitation + " mm");
    safeSetText("weather-wind", weather.wind_speed_10m + " km/h");
    safeSetText("weather-pressure", Math.round(weather.surface_pressure) + " hPa");
    safeSetText("weather-uv", Math.round(weather.uv_index));
    
    // Pollution Subpage KPIs
    safeSetText("pollution-aqi", Math.round(pollution.european_aqi));
    safeSetText("pollution-pm25", pollution.pm2_5);
    safeSetText("pollution-pm10", pollution.pm10);
    safeSetText("pollution-co", (pollution.carbon_monoxide / 1000).toFixed(2));
    safeSetText("pollution-no2", pollution.nitrogen_dioxide);
    safeSetText("pollution-so2", pollution.sulphur_dioxide);
    
    const aqiCard = document.querySelector('.kpi-card[data-status="aqi"]');
    if (aqiCard) {
        aqiCard.className = "kpi-card mini " + (pollution.european_aqi < 50 ? "good" : (pollution.european_aqi < 100 ? "moderate" : "poor"));
    }
}

