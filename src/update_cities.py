import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Update src/generate_data.py
generate_data_path = os.path.join(BASE_DIR, "src", "generate_data.py")
print("Updating generate_data.py...")
with open(generate_data_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replacements
replacements_gen = [
    # Cities list
    ('CITIES = ["Metropolis", "Greenville", "Sunset Valley"]', 'CITIES = ["Mumbai", "Bengaluru", "New Delhi"]'),
    
    # Weather settings
    ('''    if city == "Metropolis":
        temp_base, temp_amp = 18, 12       # Moderate, high amplitude
        rain_prob, rain_max = 0.25, 45     # Moderate rain
        humidity_base = 65
    elif city == "Greenville":
        temp_base, temp_amp = 15, 10       # Cooler
        rain_prob, rain_max = 0.35, 60     # Rainy
        humidity_base = 75
    else:  # Sunset Valley
        temp_base, temp_amp = 24, 8        # Warm/Dry
        rain_prob, rain_max = 0.12, 30     # Low rain
        humidity_base = 45''', 
     '''    if city == "Mumbai":
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
        humidity_base = 45'''),
        
    # Pollution settings
    ('''    if city == "Metropolis":
        base_poll = 85      # Industrial/Dense
    elif city == "Greenville":
        base_poll = 35      # Eco-friendly
    else:  # Sunset Valley
        base_poll = 60      # Moderate dust/ozone''',
     '''    if city == "Mumbai":
        base_poll = 90      # Industrial & Coastal dispersion
    elif city == "Bengaluru":
        base_poll = 60      # Moderate vehicles
    else:  # New Delhi
        base_poll = 180     # Severe winter smog & dust'''),
        
    # Traffic settings
    ('city_factor = 1.3 if city == "Metropolis" else (0.8 if city == "Greenville" else 1.0)',
     'city_factor = 1.35 if city == "Mumbai" else (1.30 if city == "Bengaluru" else 1.25)'),
     
    # Crime base
    ('city_crime_base = 50 if city == "Metropolis" else (20 if city == "Greenville" else 35)',
     'city_crime_base = 45 if city == "Mumbai" else (25 if city == "Bengaluru" else 55)'),
     
    # Transit passengers
    ('base_ridership = 150000 if city == "Metropolis" else (80000 if city == "Greenville" else 100000)',
     'base_ridership = 180000 if city == "Mumbai" else (90000 if city == "Bengaluru" else 130000)'),
     
    # Energy settings
    ('''    base_electricity = 5000 if city == "Metropolis" else (2500 if city == "Greenville" else 3500)
    renewable_base = 20 if city == "Metropolis" else (65 if city == "Greenville" else 40)''',
     '''    base_electricity = 5200 if city == "Mumbai" else (3000 if city == "Bengaluru" else 4200)
    renewable_base = 15 if city == "Mumbai" else (50 if city == "Bengaluru" else 25)'''),
    
    # Water settings
    ('base_water = 850 if city == "Metropolis" else (450 if city == "Greenville" else 650)',
     'base_water = 900 if city == "Mumbai" else (500 if city == "Bengaluru" else 750)'),
    
    ('quality = 92 if city == "Greenville" else (84 if city == "Sunset Valley" else 78)',
     'quality = 88 if city == "Bengaluru" else (76 if city == "New Delhi" else 70)'),
     
    # Healthcare settings
    ('hosp_count = 15 if city == "Metropolis" else (6 if city == "Greenville" else 8)',
     'hosp_count = 18 if city == "Mumbai" else (10 if city == "Bengaluru" else 14)'),
     
    # Yearly population base
    ('''    if city == "Metropolis":
        pop_base, density_base = 2500000, 5200
        literacy_base, employ_base = 88.5, 91.2
        schools, colleges = 480, 55
        gdp_base, inflation_base, income_base = 120.5, 3.2, 58000
    elif city == "Greenville":
        pop_base, density_base = 680000, 1400
        literacy_base, employ_base = 94.2, 93.5
        schools, colleges = 160, 18
        gdp_base, inflation_base, income_base = 38.2, 2.4, 62000
    else:  # Sunset Valley
        pop_base, density_base = 1200000, 2800
        literacy_base, employ_base = 90.8, 89.5
        schools, colleges = 270, 32
        gdp_base, inflation_base, income_base = 65.4, 2.9, 52000''',
     '''    if city == "Mumbai":
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
        gdp_base, inflation_base, income_base = 180.0, 5.4, 70000'''),
        
    ('growth_rates = {"Metropolis": 0.018, "Greenville": 0.012, "Sunset Valley": 0.025}',
     'growth_rates = {"Mumbai": 0.016, "Bengaluru": 0.028, "New Delhi": 0.021}'),
     
    ('gdp_growth_rates = {"Metropolis": 0.035, "Greenville": 0.040, "Sunset Valley": 0.048}',
     'gdp_growth_rates = {"Mumbai": 0.065, "Bengaluru": 0.078, "New Delhi": 0.059}'),
     
    # Crime base ML
    ('crime_base_avg = 50 if city == "Metropolis" else (20 if city == "Greenville" else 35)',
     'crime_base_avg = 45 if city == "Mumbai" else (25 if city == "Bengaluru" else 55)'),
     
    # Aggregates KPI indicators
    ('green_pct = 15.2 if city == "Metropolis" else (42.5 if city == "Greenville" else 28.3)',
     'green_pct = 12.5 if city == "Mumbai" else (28.4 if city == "Bengaluru" else 18.2)'),
     
    ('emergency_time = 14.5 if city == "Metropolis" else (11.2 if city == "Greenville" else 12.8)',
     'emergency_time = 16.5 if city == "Mumbai" else (14.2 if city == "Bengaluru" else 15.8)')
]

for old, new in replacements_gen:
    if old in code:
        code = code.replace(old, new)
    else:
        # try single-line replacements or printing error
        print(f"Warning: could not find code block:\n{old[:50]}...")

with open(generate_data_path, "w", encoding="utf-8") as f:
    f.write(code)

# 2. Update dashboard/index.html
index_path = os.path.join(BASE_DIR, "dashboard", "index.html")
print("Updating index.html...")
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

replacements_html = [
    ('<option value="Metropolis">Metropolis</option>', '<option value="Mumbai">Mumbai</option>'),
    ('<option value="Greenville">Greenville</option>', '<option value="Bengaluru">Bengaluru</option>'),
    ('<option value="Sunset Valley">Sunset Valley</option>', '<option value="New Delhi">New Delhi</option>'),
    ('Metropolis (2026)', 'Mumbai (2026)'),
    ('Metropolis', 'Mumbai')
]

for old, new in replacements_html:
    html = html.replace(old, new)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

# 3. Update dashboard/map.js
map_path = os.path.join(BASE_DIR, "dashboard", "map.js")
print("Updating map.js...")
with open(map_path, "r", encoding="utf-8") as f:
    js_map = f.read()

replacements_map = [
    ('''const CITY_COORDINATES = {
    "Metropolis": [40.7128, -74.0060],      // Central Park / NYC style
    "Greenville": [45.5152, -122.6784],     // Pacific Northwest style
    "Sunset Valley": [34.0522, -118.2437]   // LA valley style
};''',
     '''const CITY_COORDINATES = {
    "Mumbai": [19.0760, 72.8777],
    "Bengaluru": [12.9716, 77.5946],
    "New Delhi": [28.6139, 77.2090]
};'''),
    ('"Metropolis"', '"Mumbai"'),
    ('"Greenville"', '"Bengaluru"'),
    ('currentCityName === "Metropolis"', 'currentCityName === "Mumbai"'),
    ('currentCityName === "Greenville"', 'currentCityName === "Bengaluru"'),
    
    # Station and loop name replacements to fit Indian cities
    ('"Central Terminal Hub"', '"CST Terminal Hub"'),
    ('"North Station"', '"Bandra Kurla Terminus"'),
    ('"South Gate Station"', '"Gateway of India Station"'),
    ('"Commercial Way Loop"', '"Nariman Point Loop"'),
    ('"Residential Park Corner"', '"Andheri East Crossing"')
]

for old, new in replacements_map:
    js_map = js_map.replace(old, new)

with open(map_path, "w", encoding="utf-8") as f:
    f.write(js_map)

# 4. Update dashboard/app.js
app_path = os.path.join(BASE_DIR, "dashboard", "app.js")
print("Updating app.js...")
with open(app_path, "r", encoding="utf-8") as f:
    js_app = f.read()

replacements_app = [
    ('Metropolis (2026)', 'Mumbai (2026)'),
    ('Metropolis', 'Mumbai'),
    ('Greenville', 'Bengaluru'),
    ('Sunset Valley', 'New Delhi'),
    # Density divider updates
    ('(city === "Mumbai" ? 480 : (city === "Bengaluru" ? 485 : 420))', 
     '(city === "Mumbai" ? 603 : (city === "Bengaluru" ? 709 : 1484))')
]

for old, new in replacements_app:
    js_app = js_app.replace(old, new)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(js_app)

# 5. Update src/create_notebooks.py
notebooks_script_path = os.path.join(BASE_DIR, "src", "create_notebooks.py")
print("Updating create_notebooks.py...")
with open(notebooks_script_path, "r", encoding="utf-8") as f:
    js_nb = f.read()

js_nb = js_nb.replace("Metropolis", "Mumbai")

with open(notebooks_script_path, "w", encoding="utf-8") as f:
    f.write(js_nb)

print("All city updates completed!")
