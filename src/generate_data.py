import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Custom JSON Encoder to handle numpy data types
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# Directory Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DASHBOARD_DATA_DIR = os.path.join(BASE_DIR, "dashboard", "data")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DATA_DIR, exist_ok=True)

CITIES = ["Mumbai", "Bengaluru", "New Delhi"]
YEARS = [2024, 2025, 2026]
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 12, 31)
DATES = pd.date_range(start=START_DATE, end=END_DATE)

print("Generating weather and environment data...")
# 1. Weather Data (Daily)
weather_records = []
for city in CITIES:
    # Baseline climate parameters per city
    if city == "Mumbai":
        temp_base, temp_amp = 27, 4        # Hot & Humid (Coastal)
        rain_prob, rain_max = 0.35, 120    # Heavy Monsoon Rains
        humidity_base = 78
    elif city == "Bengaluru":
        temp_base, temp_amp = 22, 6        # Pleasant (Upland Plateau)
        rain_prob, rain_max = 0.25, 50     # Moderate rains
        humidity_base = 62
    else:  # New Delhi
        temp_base, temp_amp = 25, 14       # Extreme (Subtropical)
        rain_prob, rain_max = 0.18, 75     # Monsoon + Dry months
        humidity_base = 45

    for d in DATES:
        day_of_year = d.timetuple().tm_yday
        # Seasonality model (sine wave peaking in July, day 190-200)
        season = np.sin(2 * np.pi * (day_of_year - 100) / 365)
        
        # Temp with trend (warming 0.1C/year) + seasonal component + noise
        year_offset = (d.year - 2024) * 0.15
        temp = temp_base + temp_amp * season + np.random.normal(0, 2.5) + year_offset
        
        # Rain occurrence
        has_rain = np.random.rand() < (rain_prob + 0.1 * season) # more rain in wet seasons
        rain = np.random.exponential(12) if has_rain else 0.0
        rain = min(rain, rain_max)
        
        # Humidity: higher when cold/rainy
        humidity = humidity_base - 10 * season + (15 if rain > 0 else 0) + np.random.normal(0, 5)
        humidity = max(10, min(100, humidity))
        
        # Wind: higher in winter/spring
        wind = max(2, 12 - 4 * season + np.random.normal(0, 3.5))
        
        # Pressure: inverse to temperature/rain
        pressure = 1013 - 5 * season - (8 if rain > 0 else 0) + np.random.normal(0, 2)
        
        # UV Index: correlated with temp and sunny days
        uv = max(0, int(round((temp_base + temp_amp * season) / 4 + np.random.normal(0, 1.2))))
        if rain > 5:
            uv = max(0, uv - 3)
            
        weather_records.append({
            "Date": d.strftime("%Y-%m-%d"),
            "City": city,
            "Temperature": round(temp, 1),
            "Humidity": int(round(humidity)),
            "Rainfall": round(rain, 1),
            "Wind_Speed": round(wind, 1),
            "Pressure": int(round(pressure)),
            "UV_Index": int(uv)
        })

df_weather = pd.DataFrame(weather_records)
df_weather.to_csv(os.path.join(DATA_DIR, "weather.csv"), index=False)


print("Generating pollution data...")
# 2. Pollution Data (Daily, correlated with Weather)
pollution_records = []
for index, row in df_weather.iterrows():
    city = row["City"]
    temp = row["Temperature"]
    wind = row["Wind_Speed"]
    rain = row["Rainfall"]
    
    # Baseline pollution factors per city
    if city == "Mumbai":
        base_poll = 90      # Industrial & Coastal dispersion
    elif city == "Bengaluru":
        base_poll = 60      # Moderate vehicles
    else:  # New Delhi
        base_poll = 180     # Severe winter smog & dust
        
    # Weather interactions:
    # High wind disperses pollutants. Rain washes them out. High temp increases Ozone (AQI).
    dispersion = -1.2 * wind - 2.5 * rain
    ozone_effect = 1.1 * temp if temp > 22 else 0.0
    
    aqi_val = base_poll + dispersion + ozone_effect + np.random.normal(0, 8)
    aqi_val = max(12, int(round(aqi_val)))
    
    # Calculate sub-pollutants based on AQI scaling
    pm25 = aqi_val * 0.45 + np.random.normal(0, 3)
    pm10 = aqi_val * 0.75 + np.random.normal(0, 5)
    co = aqi_val * 0.008 + np.random.normal(0, 0.05)
    no2 = aqi_val * 0.28 + np.random.normal(0, 2)
    so2 = aqi_val * 0.06 + np.random.normal(0, 0.5)
    
    pollution_records.append({
        "Date": row["Date"],
        "City": city,
        "AQI": aqi_val,
        "PM2_5": round(max(1.0, pm25), 1),
        "PM10": round(max(2.0, pm10), 1),
        "CO": round(max(0.1, co), 2),
        "NO2": round(max(0.5, no2), 1),
        "SO2": round(max(0.1, so2), 1)
    })

df_pollution = pd.DataFrame(pollution_records)
df_pollution.to_csv(os.path.join(DATA_DIR, "pollution.csv"), index=False)


print("Generating traffic data...")
# 3. Traffic Data (Daily / Area Level)
# Areas in cities
AREAS = ["Downtown", "Suburbs", "Industrial", "Residential"]
traffic_records = []

for city in CITIES:
    # City congestion factors
    city_factor = 1.35 if city == "Mumbai" else (1.30 if city == "Bengaluru" else 1.25)
    
    for d in DATES:
        day_of_week = d.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Weather impact: Rain slows traffic down
        rain_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Rainfall"].values[0]
        weather_delay = 12 * (rain_val / 20) if rain_val > 0 else 0
        
        for area in AREAS:
            # Area factors
            if area == "Downtown":
                base_count, base_speed, base_cong = 45000, 30, 65
            elif area == "Suburbs":
                base_count, base_speed, base_cong = 20000, 60, 25
            elif area == "Industrial":
                base_count, base_speed, base_cong = 15000, 45, 35
            else:  # Residential
                base_count, base_speed, base_cong = 18000, 40, 30
                
            # Day of week adjustments
            weekend_mod = 0.5 if is_weekend and area != "Suburbs" else (1.1 if is_weekend and area == "Suburbs" else 1.0)
            
            # Compute indicators
            vehicle_count = int(base_count * weekend_mod * city_factor + np.random.normal(0, base_count * 0.05))
            congestion = base_cong * weekend_mod * city_factor + weather_delay + np.random.normal(0, 4)
            congestion = max(5, min(99, congestion))
            
            # Speed is inversely proportional to congestion
            speed = base_speed * (1 - (congestion / 150)) - (weather_delay / 4) + np.random.normal(0, 3)
            speed = max(10, min(100, speed))
            
            # Peak hours
            peak_hour = "08:00 - 10:00" if day_of_week < 5 else "12:00 - 14:00"
            if np.random.rand() > 0.5 and day_of_week < 5:
                peak_hour = "17:00 - 19:00"
                
            # Accidents: correlated with vehicle count, weather and congestion
            accidents = int(round((vehicle_count / 10000) * (congestion / 30) * (1.5 if rain_val > 5 else 1.0) * np.random.uniform(0.5, 1.5)))
            accidents = max(0, accidents)
            
            traffic_records.append({
                "Date": d.strftime("%Y-%m-%d"),
                "City": city,
                "Area": area,
                "Average_Speed": round(speed, 1),
                "Congestion_Index": round(congestion, 1),
                "Vehicle_Count": vehicle_count,
                "Peak_Hour": peak_hour,
                "Accident_Count": accidents
            })

df_traffic = pd.DataFrame(traffic_records)
df_traffic.to_csv(os.path.join(DATA_DIR, "traffic.csv"), index=False)


print("Generating crime data...")
# 4. Crime Data
CRIME_CATS = ["Theft", "Assault", "Burglary", "Vandalism", "Traffic Violation"]
crime_records = []
for city in CITIES:
    districts = ["District A", "District B", "District C", "District D"]
    city_crime_base = 45 if city == "Mumbai" else (25 if city == "Bengaluru" else 55)
    
    for d in DATES:
        day_of_week = d.weekday()
        # Crime increases slightly on weekends and warmer days
        temp_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Temperature"].values[0]
        heat_effect = (temp_val - 20) * 0.4 if temp_val > 20 else 0
        weekend_effect = 3 if day_of_week >= 4 else 0 # Fri, Sat, Sun
        
        # Decide how many crimes occur this day
        daily_crime_count = int(max(1, np.random.poisson(city_crime_base / 10 + heat_effect + weekend_effect)))
        
        for _ in range(daily_crime_count):
            cat = np.random.choice(CRIME_CATS, p=[0.4, 0.15, 0.15, 0.2, 0.1])
            district = np.random.choice(districts, p=[0.4, 0.3, 0.2, 0.1])
            
            # Arrest probability (e.g. traffic violation solved easily, assault high solved, theft low)
            arrest_probs = {"Theft": 0.15, "Assault": 0.65, "Burglary": 0.25, "Vandalism": 0.20, "Traffic Violation": 0.95}
            arrested = np.random.rand() < arrest_probs[cat]
            solved = arrested or (np.random.rand() < 0.1) # some solved without immediate arrest
            
            crime_records.append({
                "Date": d.strftime("%Y-%m-%d"),
                "City": city,
                "District": district,
                "Crime_Category": cat,
                "Arrest_Status": "Arrested" if arrested else "Not Arrested",
                "Case_Status": "Solved" if solved else "Active"
            })

df_crime = pd.DataFrame(crime_records)
df_crime.to_csv(os.path.join(DATA_DIR, "crime.csv"), index=False)


print("Generating public transport data...")
# 5. Public Transportation Data (Daily)
transport_records = []
for city in CITIES:
    base_ridership = 180000 if city == "Mumbai" else (90000 if city == "Bengaluru" else 130000)
    
    for d in DATES:
        day_of_week = d.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Weekdays have higher ridership
        ridership_mult = 0.55 if is_weekend else 1.0
        
        # Rain increases metro ridership, decreases bus ridership (people prefer shelter)
        rain_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Rainfall"].values[0]
        
        passengers = int(base_ridership * ridership_mult + np.random.normal(0, base_ridership * 0.03))
        # Metro ridership vs Bus utilization
        metro = int(passengers * (0.6 + (0.05 if rain_val > 5 else 0)))
        bus_util = 65 - (5 if rain_val > 5 else 0) + np.random.normal(0, 5)
        bus_util = max(20, min(100, bus_util))
        
        # Average delay: depends on rain and general traffic congestion
        traffic_df = df_traffic[(df_traffic["Date"] == d.strftime("%Y-%m-%d")) & (df_traffic["City"] == city)]
        avg_congestion = traffic_df["Congestion_Index"].mean() if not traffic_df.empty else 40
        delay = 2 + 0.25 * avg_congestion + 0.4 * rain_val + np.random.normal(0, 1.5)
        delay = max(1.0, delay)
        
        # Route efficiency: lower delay -> higher efficiency
        efficiency = max(50, min(99, 95 - 0.8 * delay + np.random.normal(0, 2)))
        
        transport_records.append({
            "Date": d.strftime("%Y-%m-%d"),
            "City": city,
            "Daily_Passengers": passengers,
            "Bus_Utilization": round(bus_util, 1),
            "Metro_Ridership": metro,
            "Average_Delay": round(delay, 1),
            "Route_Efficiency": round(efficiency, 1)
        })

df_transport = pd.DataFrame(transport_records)
df_transport.to_csv(os.path.join(DATA_DIR, "transport.csv"), index=False)


print("Generating energy consumption data...")
# 6. Energy Consumption (Daily)
energy_records = []
for city in CITIES:
    base_electricity = 5200 if city == "Mumbai" else (3000 if city == "Bengaluru" else 4200)
    renewable_base = 15 if city == "Mumbai" else (50 if city == "Bengaluru" else 25)
    
    for d in DATES:
        temp_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Temperature"].values[0]
        
        # Temperature effect (V-shape: heating in winter, cooling in summer)
        heating_cooling = 0.0
        if temp_val < 10:
            heating_cooling = (10 - temp_val) * 120 # Heating
        elif temp_val > 24:
            heating_cooling = (temp_val - 24) * 200 # Cooling (A/C)
            
        # Annual trend (growing 2% per year)
        growth_factor = 1 + (d.year - 2024) * 0.02
        
        electricity = (base_electricity + heating_cooling) * growth_factor + np.random.normal(0, 150)
        electricity = max(1000, electricity)
        
        # Renewable % increases slowly over years, varies with wind/sun (temp/rain)
        wind_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Wind_Speed"].values[0]
        rain_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Rainfall"].values[0]
        
        # Sun coefficient (proxy: temperature and no rain)
        solar_proxy = max(0, temp_val) if rain_val == 0 else max(0, temp_val) * 0.3
        renew_var = 0.4 * wind_val + 0.2 * solar_proxy
        renewable = renewable_base + (d.year - 2024) * 2.5 + renew_var + np.random.normal(0, 3)
        renewable = max(5.0, min(95.0, renewable))
        
        # Peak usage: typically 1.3x to 1.6x of average daily hourly load
        peak_usage = electricity * np.random.uniform(1.3, 1.55) / 24
        
        # Distribution by sector
        residential_pct = 0.35 if city != "Industrial" else 0.25
        commercial_pct = 0.35
        industrial_pct = 1 - residential_pct - commercial_pct
        
        energy_records.append({
            "Date": d.strftime("%Y-%m-%d"),
            "City": city,
            "Electricity_Consumption": round(electricity, 1),
            "Renewable_Energy_Percent": round(renewable, 1),
            "Peak_Usage": round(peak_usage, 1),
            "Residential_Consumption": round(electricity * residential_pct, 1),
            "Commercial_Consumption": round(electricity * commercial_pct, 1),
            "Industrial_Consumption": round(electricity * industrial_pct, 1)
        })

df_energy = pd.DataFrame(energy_records)
df_energy.to_csv(os.path.join(DATA_DIR, "energy.csv"), index=False)


print("Generating water analytics data...")
# 7. Water Analytics (Daily)
water_records = []
for city in CITIES:
    base_water = 900 if city == "Mumbai" else (500 if city == "Bengaluru" else 750)
    
    # Track reservoir level state dynamically
    reservoir_level = 80.0 # start at 80%
    
    for d in DATES:
        temp_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Temperature"].values[0]
        rain_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Rainfall"].values[0]
        
        # Temp effect: more water used when hot
        temp_effect = (temp_val - 20) * 12 if temp_val > 20 else 0
        water_use = base_water + temp_effect + np.random.normal(0, 20)
        water_use = max(100, water_use)
        
        # Loss: leakage in distribution (typically 10-25%)
        loss_pct = 18 - (1.5 if city == "Greenville" else 0) + np.random.normal(0, 1.2)
        loss_pct = max(5, min(40, loss_pct))
        
        # Reservoir replenishment from rain, depletion from supply
        replenishment = rain_val * 1.8
        depletion = (water_use / 100) # scale factor
        reservoir_level = reservoir_level + replenishment - depletion + np.random.normal(0, 0.1)
        reservoir_level = max(20.0, min(100.0, reservoir_level))
        
        # Daily supply matched to demand
        supply = water_use * (1 + loss_pct / 100)
        
        # Water Quality Index (0-100 scale, higher is better)
        quality = 88 if city == "Bengaluru" else (76 if city == "New Delhi" else 70)
        # Silt/runoff from heavy rain slightly lowers quality briefly
        quality -= (rain_val * 0.15)
        quality += np.random.normal(0, 1)
        quality = max(60, min(100, quality))
        
        water_records.append({
            "Date": d.strftime("%Y-%m-%d"),
            "City": city,
            "Water_Usage": round(water_use, 1),
            "Water_Loss": round(loss_pct, 1),
            "Reservoir_Level": round(reservoir_level, 1),
            "Daily_Supply": round(supply, 1),
            "Water_Quality": round(quality, 1)
        })

df_water = pd.DataFrame(water_records)
df_water.to_csv(os.path.join(DATA_DIR, "water.csv"), index=False)


print("Generating healthcare data...")
# 8. Healthcare Data (Daily)
healthcare_records = []
for city in CITIES:
    hosp_count = 18 if city == "Mumbai" else (10 if city == "Bengaluru" else 14)
    
    for d in DATES:
        temp_val = df_weather[(df_weather["Date"] == d.strftime("%Y-%m-%d")) & (df_weather["City"] == city)]["Temperature"].values[0]
        aqi_val = df_pollution[(df_pollution["Date"] == d.strftime("%Y-%m-%d")) & (df_pollution["City"] == city)]["AQI"].values[0]
        
        # Disease cases (flu spikes in winter, respiratory spikes with high AQI)
        winter_flu = max(0, (12 - temp_val) * 8) if temp_val < 12 else 0
        aqi_resp = max(0, (aqi_val - 100) * 0.5) if aqi_val > 100 else 0
        
        disease_cases = int(25 + winter_flu + aqi_resp + np.random.poisson(15))
        
        # Bed availability (decreases when disease cases are high)
        bed_avail = 78 - 0.25 * disease_cases + np.random.normal(0, 3)
        bed_avail = max(10.0, min(99.0, bed_avail))
        
        # Vaccination %: gradual climb
        days_passed = (d - START_DATE).days
        vac_pct = 72 + 15 * (days_passed / 1095) + np.random.normal(0, 0.2)
        vac_pct = min(95.0, vac_pct)
        
        healthcare_records.append({
            "Date": d.strftime("%Y-%m-%d"),
            "City": city,
            "Hospital_Count": hosp_count,
            "Bed_Availability": round(bed_avail, 1),
            "Disease_Cases": disease_cases,
            "Vaccination_Percent": round(vac_pct, 1)
        })

df_healthcare = pd.DataFrame(healthcare_records)
df_healthcare.to_csv(os.path.join(DATA_DIR, "healthcare.csv"), index=False)


print("Generating population, education, and economic data (Yearly)...")
# 9. Population Data (Yearly)
pop_records = []
pop_forecast_records = [] # Precomputed forecast data for dashboard

# 10. Education Data (Yearly)
edu_records = []

# 11. Economy Data (Yearly)
econ_records = []

for city in CITIES:
    # Set base metrics for 2024
    if city == "Mumbai":
        pop_base, density_base = 12500000, 21000
        literacy_base, employ_base = 89.2, 92.5
        schools, colleges = 1200, 150
        gdp_base, inflation_base, income_base = 250.0, 5.1, 75000
    elif city == "Bengaluru":
        pop_base, density_base = 8400000, 4380
        literacy_base, employ_base = 92.5, 94.0
        schools, colleges = 850, 110
        gdp_base, inflation_base, income_base = 110.0, 4.8, 90000
    else:  # New Delhi
        pop_base, density_base = 16800000, 11300
        literacy_base, employ_base = 86.2, 88.5
        schools, colleges = 1500, 180
        gdp_base, inflation_base, income_base = 180.0, 5.4, 70000

    # Pop growth rates
    growth_rates = {"Mumbai": 0.016, "Bengaluru": 0.028, "New Delhi": 0.021}
    gdp_growth_rates = {"Mumbai": 0.065, "Bengaluru": 0.078, "New Delhi": 0.059}

    # Populate 2024, 2025, 2026
    for idx, year in enumerate(YEARS):
        g_rate = growth_rates[city] + np.random.normal(0, 0.002)
        pop = pop_base * ((1 + growth_rates[city]) ** idx)
        density = density_base * ((1 + growth_rates[city]) ** idx)
        literacy = literacy_base + idx * 0.4 + np.random.normal(0, 0.1)
        employ = employ_base + idx * 0.3 + np.random.normal(0, 0.2)
        
        # Education progression
        s_count = int(schools + idx * 6)
        c_count = int(colleges + idx * 1)
        grad_rate = 82 + idx * 0.8 + np.random.normal(0, 0.5)
        enrollment = int(pop * 0.16)
        
        # Economic progression
        gdp = gdp_base * ((1 + gdp_growth_rates[city]) ** idx)
        inflation = inflation_base + np.random.normal(0, 0.4)
        income = income_base * ((1.035) ** idx) + np.random.normal(0, 500)
        
        pop_records.append({
            "Year": year,
            "City": city,
            "Population": int(round(pop)),
            "Density": int(round(density)),
            "Literacy_Rate": round(min(99.0, literacy), 1),
            "Employment_Rate": round(min(98.0, employ), 1),
            "Urban_Growth_Rate": round(g_rate * 100, 2)
        })
        
        edu_records.append({
            "Year": year,
            "City": city,
            "Schools": s_count,
            "Colleges": c_count,
            "Literacy": round(min(99.0, literacy), 1),
            "Graduation_Rate": round(min(98.0, grad_rate), 1),
            "Enrollment": enrollment
        })
        
        econ_records.append({
            "Year": year,
            "City": city,
            "GDP": round(gdp, 2),
            "Employment_Rate": round(min(98.0, employ), 1),
            "Inflation": round(max(0.5, inflation), 2),
            "Income": int(round(income))
        })

df_pop = pd.DataFrame(pop_records)
df_pop.to_csv(os.path.join(DATA_DIR, "population.csv"), index=False)

df_edu = pd.DataFrame(edu_records)
df_edu.to_csv(os.path.join(DATA_DIR, "education.csv"), index=False)

df_econ = pd.DataFrame(econ_records)
df_econ.to_csv(os.path.join(DATA_DIR, "economy.csv"), index=False)


# ----------------------------------------------------
# 🤖 Machine Learning Precomputation & Forecasting
# ----------------------------------------------------
print("Running Machine Learning Models and Precomputing Forecasts...")

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    ML_AVAILABLE = True
except ImportError:
    # Fallback to numpy calculations if scikit-learn is not loaded
    ML_AVAILABLE = False
    print("Scikit-learn not available. Using NumPy linear fittings.")

ml_forecasts = {}

# City specific ML computations
for city in CITIES:
    ml_forecasts[city] = {}
    
    # Filter data for current city
    city_weather = df_weather[df_weather["City"] == city].copy()
    city_pollution = df_pollution[df_pollution["City"] == city].copy()
    city_traffic = df_traffic[df_traffic["City"] == city].copy()
    city_transport = df_transport[df_transport["City"] == city].copy()
    city_energy = df_energy[df_energy["City"] == city].copy()
    city_pop = df_pop[df_pop["City"] == city].copy()
    
    # Make sure Date is parsed properly
    city_weather["Date_dt"] = pd.to_datetime(city_weather["Date"])
    city_pollution["Date_dt"] = pd.to_datetime(city_pollution["Date"])
    city_traffic["Date_dt"] = pd.to_datetime(city_traffic["Date"])
    city_transport["Date_dt"] = pd.to_datetime(city_transport["Date"])
    city_energy["Date_dt"] = pd.to_datetime(city_energy["Date"])
    
    # Set indexes
    city_weather.set_index("Date_dt", inplace=True)
    city_pollution.set_index("Date_dt", inplace=True)
    city_traffic.set_index("Date_dt", inplace=True)
    city_transport.set_index("Date_dt", inplace=True)
    city_energy.set_index("Date_dt", inplace=True)
    
    # ------------------
    # 1. Weather & AQI Forecasting (7 Days)
    # ------------------
    # We fit a model on historic data to predict next 7 days based on seasonality + recent lags
    weather_days = (city_weather.index - city_weather.index[0]).days.values.reshape(-1, 1)
    temp_vals = city_weather["Temperature"].values
    
    # Linear Regression trend + sine waves representing seasonality
    t = np.arange(len(temp_vals))
    sin_t = np.sin(2 * np.pi * t / 365.25)
    cos_t = np.cos(2 * np.pi * t / 365.25)
    X_weather = np.column_stack([t, sin_t, cos_t])
    
    if ML_AVAILABLE:
        lr_temp = LinearRegression().fit(X_weather, temp_vals)
        lr_rain = LinearRegression().fit(X_weather, city_weather["Rainfall"].values)
        lr_aqi = RandomForestRegressor(n_estimators=30, random_state=42).fit(
            np.column_stack([temp_vals, city_weather["Humidity"].values, city_weather["Wind_Speed"].values]),
            city_pollution["AQI"].values
        )
    
    # Forecast for Dec 2026 / Jan 2027 (Next 7 days: 2027-01-01 to 2027-01-07)
    future_dates = [END_DATE + timedelta(days=i) for i in range(1, 8)]
    future_t = np.arange(len(temp_vals), len(temp_vals) + 7)
    future_sin = np.sin(2 * np.pi * future_t / 365.25)
    future_cos = np.cos(2 * np.pi * future_t / 365.25)
    X_future = np.column_stack([future_t, future_sin, future_cos])
    
    if ML_AVAILABLE:
        pred_temp = lr_temp.predict(X_future)
        pred_rain = np.clip(lr_rain.predict(X_future), 0, None)
        # Mock weather predictors for AQI forecast
        mock_humidity = np.random.uniform(50, 75, size=7)
        mock_wind = np.random.uniform(5, 15, size=7)
        pred_aqi = lr_aqi.predict(np.column_stack([pred_temp, mock_humidity, mock_wind]))
    else:
        # Fallback math
        pred_temp = [temp_vals[-1] + np.random.normal(0, 1.5) for _ in range(7)]
        pred_rain = [max(0.0, np.random.exponential(5)) if np.random.rand() < 0.2 else 0.0 for _ in range(7)]
        pred_aqi = [city_pollution["AQI"].iloc[-1] + np.random.normal(0, 5) for _ in range(7)]
        
    ml_forecasts[city]["weather_aqi"] = {
        "dates": [d.strftime("%Y-%m-%d") for d in future_dates],
        "temperature": [round(float(v), 1) for v in pred_temp],
        "rainfall": [round(float(v), 1) for v in pred_rain],
        "aqi": [int(round(float(v))) for v in pred_aqi]
    }
    
    # ------------------
    # 2. Traffic Congestion Prediction (Tomorrow)
    # ------------------
    # Predict tomorrow's Congestion_Index based on: Day of week, Temperature, Rainfall
    # Combine traffic to daily average
    traffic_daily = city_traffic.groupby("Date_dt").agg({"Congestion_Index": "mean", "Average_Speed": "mean", "Vehicle_Count": "sum", "Accident_Count": "sum"})
    traffic_daily = traffic_daily.join(city_weather[["Temperature", "Rainfall"]])
    traffic_daily["DayOfWeek"] = traffic_daily.index.dayofweek
    
    X_traffic = traffic_daily[["DayOfWeek", "Temperature", "Rainfall"]].values
    y_traffic = traffic_daily["Congestion_Index"].values
    
    # Tomorrow's features (e.g. Friday, Jan 1, 2027. temp = pred_temp[0], rain = pred_rain[0])
    tomorrow_dow = future_dates[0].weekday()
    X_tomorrow = np.array([[tomorrow_dow, pred_temp[0], pred_rain[0]]])
    
    if ML_AVAILABLE:
        rf_traffic = RandomForestRegressor(n_estimators=30, random_state=42).fit(X_traffic, y_traffic)
        pred_cong_tomorrow = rf_traffic.predict(X_tomorrow)[0]
    else:
        # Fallback math
        pred_cong_tomorrow = traffic_daily["Congestion_Index"].iloc[-1] + (5.0 if tomorrow_dow < 5 else -10.0) + (2.0 if pred_rain[0] > 0 else 0)
        
    # Congestion forecast for next 7 days
    congestion_7day = []
    for idx, d in enumerate(future_dates):
        dow = d.weekday()
        if ML_AVAILABLE:
            c = rf_traffic.predict(np.array([[dow, pred_temp[idx], pred_rain[idx]]]))[0]
        else:
            c = traffic_daily["Congestion_Index"].iloc[-7 + idx] + np.random.normal(0, 3)
        congestion_7day.append(round(float(c), 1))
        
    ml_forecasts[city]["traffic"] = {
        "tomorrow_congestion": round(float(pred_cong_tomorrow), 1),
        "congestion_7day": congestion_7day
    }
    
    # ------------------
    # 3. Crime Prediction (District probabilities)
    # ------------------
    # Compute base crimes by district
    crime_summary = df_crime[df_crime["City"] == city].groupby("District").size().to_dict()
    total_crimes = sum(crime_summary.values())
    crime_dist_probs = {k: v / total_crimes for k, v in crime_summary.items()}
    
    # Predict crimes for future 7 days (Trend based + temperature effect)
    future_crimes_count = []
    for idx, temp in enumerate(pred_temp):
        heat_effect = (temp - 20) * 0.4 if temp > 20 else 0
        weekend_effect = 3 if future_dates[idx].weekday() >= 4 else 0
        # Expected crime Poisson average
        crime_base_avg = 45 if city == "Mumbai" else (25 if city == "Bengaluru" else 55)
        expected = crime_base_avg / 10 + heat_effect + weekend_effect
        future_crimes_count.append(max(1, int(round(expected))))
        
    ml_forecasts[city]["crime"] = {
        "district_probabilities": crime_dist_probs,
        "future_7day_crimes": future_crimes_count
    }
    
    # ------------------
    # 4. Public Transport Demand
    # ------------------
    transport_daily = city_transport.join(city_weather[["Temperature", "Rainfall"]])
    transport_daily["DayOfWeek"] = transport_daily.index.dayofweek
    
    X_trans = transport_daily[["DayOfWeek", "Rainfall"]].values
    y_trans = transport_daily["Daily_Passengers"].values
    
    trans_forecast = []
    for idx, d in enumerate(future_dates):
        dow = d.weekday()
        if ML_AVAILABLE:
            lr_trans = LinearRegression().fit(X_trans, y_trans)
            pass_pred = lr_trans.predict(np.array([[dow, pred_rain[idx]]]))[0]
        else:
            pass_pred = y_trans[-7 + idx] + np.random.normal(0, 3000)
        trans_forecast.append(int(round(float(pass_pred))))
        
    ml_forecasts[city]["transport"] = {
        "future_7day_passengers": trans_forecast
    }
    
    # ------------------
    # 5. Electricity Demand
    # ------------------
    energy_daily = city_energy.join(city_weather[["Temperature"]])
    X_energy = np.column_stack([energy_daily["Temperature"].values, energy_daily["Temperature"].values ** 2])
    y_energy = energy_daily["Electricity_Consumption"].values
    
    energy_forecast = []
    for idx, temp in enumerate(pred_temp):
        if ML_AVAILABLE:
            lr_energy = LinearRegression().fit(X_energy, y_energy)
            e_pred = lr_energy.predict(np.array([[temp, temp ** 2]]))[0]
        else:
            e_pred = y_energy[-7 + idx] + np.random.normal(0, 100)
        energy_forecast.append(round(float(e_pred), 1))
        
    ml_forecasts[city]["energy"] = {
        "future_7day_demand": energy_forecast
    }
    
    # ------------------
    # 6. Population Forecast (2024 to 2035)
    # ------------------
    pop_years = city_pop["Year"].values.reshape(-1, 1)
    pop_vals = city_pop["Population"].values
    
    # Linear forecast extrapolation
    if ML_AVAILABLE:
        lr_pop = LinearRegression().fit(pop_years, pop_vals)
        future_years = np.arange(2027, 2036).reshape(-1, 1)
        pred_pop_future = lr_pop.predict(future_years)
    else:
        # Fallback manual line math
        m = (pop_vals[-1] - pop_vals[0]) / (pop_years[-1][0] - pop_years[0][0])
        future_years = np.arange(2027, 2036).reshape(-1, 1)
        pred_pop_future = [pop_vals[-1] + m * (yr[0] - 2026) for yr in future_years]
        
    # Combine historical and forecast for UI plotting
    years_all = list(city_pop["Year"].values) + [int(yr[0]) for yr in future_years]
    pop_all = [int(v) for v in pop_vals] + [int(round(float(v))) for v in pred_pop_future]
    
    ml_forecasts[city]["population_growth"] = {
        "years": years_all,
        "population": pop_all
    }
    
    # ------------------
    # 7. Water Demand Forecast (Next 7 Days)
    # ------------------
    # Water usage depends heavily on temperature
    city_water_df = df_water[df_water["City"] == city].copy()
    city_water_df["Date_dt"] = pd.to_datetime(city_water_df["Date"])
    city_water_df.set_index("Date_dt", inplace=True)
    water_daily = city_water_df.join(city_weather[["Temperature"]])
    X_water = water_daily["Temperature"].values.reshape(-1, 1)
    y_water = water_daily["Water_Usage"].values
    
    water_forecast = []
    for idx, temp in enumerate(pred_temp):
        if ML_AVAILABLE:
            lr_water = LinearRegression().fit(X_water, y_water)
            w_pred = lr_water.predict(np.array([[temp]]))[0]
        else:
            w_pred = y_water[-7 + idx] + np.random.normal(0, 15)
        water_forecast.append(round(float(w_pred), 1))
        
    ml_forecasts[city]["water"] = {
        "future_7day_demand": water_forecast
    }

# Save final ML precomputed results to dashboard data folder
with open(os.path.join(DASHBOARD_DATA_DIR, "ml_forecasts.json"), "w") as f:
    json.dump(ml_forecasts, f, indent=4, cls=NpEncoder)

print("Precomputing clean data aggregates for Dashboard visualization...")
# We aggregate CSV data for the frontend so it loads super fast
aggregates = {}
for city in CITIES:
    aggregates[city] = {}
    for year in YEARS:
        aggregates[city][year] = {}
        
        # Filter datasets
        weather_yr = df_weather[(df_weather["City"] == city) & (pd.to_datetime(df_weather["Date"]).dt.year == year)]
        pollution_yr = df_pollution[(df_pollution["City"] == city) & (pd.to_datetime(df_pollution["Date"]).dt.year == year)]
        traffic_yr = df_traffic[(df_traffic["City"] == city) & (pd.to_datetime(df_traffic["Date"]).dt.year == year)]
        crime_yr = df_crime[(df_crime["City"] == city) & (pd.to_datetime(df_crime["Date"]).dt.year == year)]
        transport_yr = df_transport[(df_transport["City"] == city) & (pd.to_datetime(df_transport["Date"]).dt.year == year)]
        energy_yr = df_energy[(df_energy["City"] == city) & (pd.to_datetime(df_energy["Date"]).dt.year == year)]
        water_yr = df_water[(df_water["City"] == city) & (pd.to_datetime(df_water["Date"]).dt.year == year)]
        healthcare_yr = df_healthcare[(df_healthcare["City"] == city) & (pd.to_datetime(df_healthcare["Date"]).dt.year == year)]
        
        pop_yr = df_pop[(df_pop["City"] == city) & (df_pop["Year"] == year)]
        edu_yr = df_edu[(df_edu["City"] == city) & (df_edu["Year"] == year)]
        econ_yr = df_econ[(df_econ["City"] == city) & (df_econ["Year"] == year)]
        
        # Store KPIs
        pop_val = int(pop_yr["Population"].values[0]) if not pop_yr.empty else 0
        aqi_val = float(pollution_yr["AQI"].mean()) if not pollution_yr.empty else 0
        crime_val = int(crime_yr.shape[0]) if not crime_yr.empty else 0
        cong_val = float(traffic_yr["Congestion_Index"].mean()) if not traffic_yr.empty else 0
        pass_val = int(transport_yr["Daily_Passengers"].mean()) if not transport_yr.empty else 0
        temp_val = float(weather_yr["Temperature"].mean()) if not weather_yr.empty else 0
        energy_val = float(energy_yr["Electricity_Consumption"].mean()) if not energy_yr.empty else 0
        water_val = float(water_yr["Water_Usage"].mean()) if not water_yr.empty else 0
        
        # Static indicators
        green_pct = 12.5 if city == "Mumbai" else (28.4 if city == "Bengaluru" else 18.2)
        emergency_time = 16.5 if city == "Mumbai" else (14.2 if city == "Bengaluru" else 15.8)
        
        # Add monthly trend helper
        monthly_trends = {
            "traffic": traffic_yr.groupby(pd.to_datetime(traffic_yr["Date"]).dt.month)["Congestion_Index"].mean().to_dict(),
            "aqi": pollution_yr.groupby(pd.to_datetime(pollution_yr["Date"]).dt.month)["AQI"].mean().to_dict(),
            "weather": weather_yr.groupby(pd.to_datetime(weather_yr["Date"]).dt.month)["Temperature"].mean().to_dict(),
            "energy": energy_yr.groupby(pd.to_datetime(energy_yr["Date"]).dt.month)["Electricity_Consumption"].sum().to_dict(),
            "water": water_yr.groupby(pd.to_datetime(water_yr["Date"]).dt.month)["Water_Usage"].sum().to_dict(),
            "crime": crime_yr.groupby(pd.to_datetime(crime_yr["Date"]).dt.month).size().to_dict(),
            "passengers": transport_yr.groupby(pd.to_datetime(transport_yr["Date"]).dt.month)["Daily_Passengers"].sum().to_dict(),
            "diseases": healthcare_yr.groupby(pd.to_datetime(healthcare_yr["Date"]).dt.month)["Disease_Cases"].sum().to_dict()
        }
        
        # Add hourly traffic patterns
        area_congestions = traffic_yr.groupby("Area")["Congestion_Index"].mean().to_dict()
        area_speeds = traffic_yr.groupby("Area")["Average_Speed"].mean().to_dict()
        
        # Crime Category Breakdowns
        crime_categories = crime_yr.groupby("Crime_Category").size().to_dict() if not crime_yr.empty else {}
        crime_districts = crime_yr.groupby("District").size().to_dict() if not crime_yr.empty else {}
        
        aggregates[city][year] = {
            "kpis": {
                "population": pop_val,
                "aqi": round(aqi_val, 1),
                "crimes": crime_val,
                "traffic_congestion": round(cong_val, 1),
                "transport_users": pass_val,
                "temperature": round(temp_val, 1),
                "energy_consumption": round(energy_val, 1),
                "water_usage": round(water_val, 1),
                "green_area": green_pct,
                "emergency_response_time": emergency_time,
                # Economic KPIs
                "gdp": float(econ_yr["GDP"].values[0]) if not econ_yr.empty else 0.0,
                "inflation": float(econ_yr["Inflation"].values[0]) if not econ_yr.empty else 0.0,
                "employment": float(econ_yr["Employment_Rate"].values[0]) if not econ_yr.empty else 0.0,
                "income": int(econ_yr["Income"].values[0]) if not econ_yr.empty else 0,
                # Education KPIs
                "schools": int(edu_yr["Schools"].values[0]) if not edu_yr.empty else 0,
                "colleges": int(edu_yr["Colleges"].values[0]) if not edu_yr.empty else 0,
                "literacy": float(edu_yr["Literacy"].values[0]) if not edu_yr.empty else 0.0,
                "graduation": float(edu_yr["Graduation_Rate"].values[0]) if not edu_yr.empty else 0.0,
                "enrollment": int(edu_yr["Enrollment"].values[0]) if not edu_yr.empty else 0,
                # Healthcare KPIs
                "disease_cases": int(healthcare_yr["Disease_Cases"].sum()) if not healthcare_yr.empty else 0,
                "bed_availability": round(float(healthcare_yr["Bed_Availability"].mean()), 1) if not healthcare_yr.empty else 0.0,
                "vaccination_pct": round(float(healthcare_yr["Vaccination_Percent"].mean()), 1) if not healthcare_yr.empty else 0.0,
                # Traffic KPIs
                "avg_speed": round(float(traffic_yr["Average_Speed"].mean()), 1) if not traffic_yr.empty else 0.0,
                "vehicle_count": int(traffic_yr["Vehicle_Count"].mean()) if not traffic_yr.empty else 0,
                "accidents": int(traffic_yr["Accident_Count"].sum()) if not traffic_yr.empty else 0,
                # Pollution KPIs
                "pm2_5": round(float(pollution_yr["PM2_5"].mean()), 1) if not pollution_yr.empty else 0.0,
                "pm10": round(float(pollution_yr["PM10"].mean()), 1) if not pollution_yr.empty else 0.0,
                "co": round(float(pollution_yr["CO"].mean()), 2) if not pollution_yr.empty else 0.0,
                "no2": round(float(pollution_yr["NO2"].mean()), 1) if not pollution_yr.empty else 0.0,
                "so2": round(float(pollution_yr["SO2"].mean()), 1) if not pollution_yr.empty else 0.0,
                # Weather KPIs
                "humidity": round(float(weather_yr["Humidity"].mean()), 1) if not weather_yr.empty else 0.0,
                "rainfall": round(float(weather_yr["Rainfall"].sum()), 1) if not weather_yr.empty else 0.0,
                "wind_speed": round(float(weather_yr["Wind_Speed"].mean()), 1) if not weather_yr.empty else 0.0,
                "pressure": int(weather_yr["Pressure"].mean()) if not weather_yr.empty else 0,
                "uv_index": round(float(weather_yr["UV_Index"].mean()), 1) if not weather_yr.empty else 0.0,
                # Public Transport KPIs
                "bus_utilization": round(float(transport_yr["Bus_Utilization"].mean()), 1) if not transport_yr.empty else 0.0,
                "metro_ridership": int(transport_yr["Metro_Ridership"].mean()) if not transport_yr.empty else 0,
                "average_delay": round(float(transport_yr["Average_Delay"].mean()), 1) if not transport_yr.empty else 0.0,
                "route_efficiency": round(float(transport_yr["Route_Efficiency"].mean()), 1) if not transport_yr.empty else 0.0,
                # Water KPIs
                "water_loss": round(float(water_yr["Water_Loss"].mean()), 1) if not water_yr.empty else 0.0,
                "reservoir_level": round(float(water_yr["Reservoir_Level"].mean()), 1) if not water_yr.empty else 0.0,
                "daily_supply": round(float(water_yr["Daily_Supply"].mean()), 1) if not water_yr.empty else 0.0,
                # Energy KPIs
                "renewable_pct": round(float(energy_yr["Renewable_Energy_Percent"].mean()), 1) if not energy_yr.empty else 0.0,
                "peak_energy": round(float(energy_yr["Peak_Usage"].mean()), 1) if not energy_yr.empty else 0.0,
            },
            "monthly_trends": monthly_trends,
            "traffic_areas": {
                "congestion": area_congestions,
                "speeds": area_speeds
            },
            "crime_categories": crime_categories,
            "crime_districts": crime_districts
        }

with open(os.path.join(DASHBOARD_DATA_DIR, "city_aggregates.json"), "w") as f:
    json.dump(aggregates, f, indent=4, cls=NpEncoder)

print("Data generation and precomputation pipeline completed successfully!")
print(f"Generated CSV files in: {DATA_DIR}")
print(f"Generated JSON models in: {DASHBOARD_DATA_DIR}")
