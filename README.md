# Smart City Analytics Platform: AI-Driven Urban Planning Dashboard

An interactive, AI-powered analytics platform designed for urban administrators to monitor, analyze, and forecast key city indicators. The dashboard consolidates 12 public datasets to identify historical trends, run machine learning predictions, and support data-driven municipal planning.

---

## 📂 Project Structure

```
smart-city-analytics/
│
├── data/                       # Raw CSVs & SQLite Database
│   ├── traffic.csv
│   ├── pollution.csv
│   ├── weather.csv
│   ├── crime.csv
│   ├── transport.csv
│   ├── population.csv
│   ├── energy.csv
│   ├── water.csv
│   ├── healthcare.csv
│   ├── education.csv
│   ├── economy.csv
│   └── smart_city.db           # Consolidated SQLite Database
│
├── notebooks/                  # Jupyter Notebooks for analysis
│   ├── data_cleaning.ipynb
│   ├── eda.ipynb
│   ├── feature_engineering.ipynb
│   └── forecasting.ipynb
│
├── src/                        # Core Python scripts
│   ├── generate_data.py        # Generates CSVs and runs ML forecasts
│   └── create_notebooks.py     # Compiles Jupyter notebooks
│
├── sql/                        # SQL schemas and imports
│   ├── database.sql
│   └── import_data.py
│
├── powerbi/                    # Power BI DAX configuration
│   └── dax_measures.md         # Reference code block of measures
│
└── dashboard/                  # Premium Web Application Dashboard
    ├── index.html              # Single page HTML layout
    ├── style.css               # Modern dark-theme glassmorphic CSS
    ├── app.js                  # ECharts visual logic controller
    ├── map.js                  # Leaflet.js GIS map layer configuration
    └── data/                   # Precalculated ML data aggregates
        ├── city_aggregates.json
        └── ml_forecasts.json
```

---

## ⚡ Quick Start: Running the Data & ML Pipeline

Follow these steps to generate the datasets, run the machine learning predictions, and build the SQL database.

### 1. Ingest/Generate the Datasets and Run ML Predictions
Run the core simulation script. This script will:
- Synthesize 3 years (2024-2026) of hourly/daily records for three distinct cities: **Metropolis**, **Greenville**, and **Sunset Valley**.
- Train Random Forest and Linear Regression models to predict:
  - 7-Day Air Quality Index (AQI) forecasts
  - Tomorrow's traffic congestion indexes
  - Expected crime rates by district
  - Peak electricity grids demands
  - 10-year population growth trends (up to 2035)
  - 7-Day weather forecasts
- Output the clean datasets to `data/` and dashboard aggregates to `dashboard/data/`.

```powershell
python src/generate_data.py
```

### 2. Compile the Jupyter Notebooks
Build the standard Jupyter notebooks:
```powershell
python src/create_notebooks.py
```

### 3. Create the Database and Import Datasets
Build the SQLite database and populate tables from the generated CSVs:
```powershell
python sql/import_data.py
```

---

## 🌐 Opening the Interactive Web Dashboard

To run the premium analytics dashboard locally:
1. Spin up a lightweight Python server inside the dashboard directory:
   ```powershell
   python -m http.server -d dashboard 8080
   ```
2. Open your web browser and navigate to:
   ```
   http://localhost:8080
   ```

### 🎨 Visual & GIS Dashboard Features
- **12 Interactive Sub-Dashboards**: Use the sidebar to switch between Executive, Traffic, Pollution, Weather, Crime, Transit, Population, Energy, Water, Healthcare, Education, and Economy dashboards.
- **Dynamic Slicers**: Filter all KPI cards and charts globally by selecting a **City** and **Year** from the top-left sidebar.
- **AI Forecasting Cards**: Explore next 7-day timelines powered by scikit-learn regressor projections.
- **Leaflet GIS Map**: Click layer toggles on the Executive Dashboard to visualize real-time Traffic congestions, Crime hotspot heatmaps, or Transit route layers overlayed directly onto a dark-mode vector map.
- **Premium Glassmorphic Aesthetics**: Modern dark/light theme toggle, glowing metrics, and responsive ECharts charts.

---

## 📊 Power BI Reference

For those compiling dashboards in Power BI Desktop:
- Refer to [dax_measures.md](file:///C:/Users/Dipanshu%20Sharma/.gemini/antigravity-ide/scratch/smart-city-analytics/powerbi/dax_measures.md) for copies of required DAX measures (YoY growth, moving averages, rolling YTD totals, dynamic ranking filters).
- Setup the SQLite database using an ODBC connector or load the raw CSVs from the `data/` folder directly.
