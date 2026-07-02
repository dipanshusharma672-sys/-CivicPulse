-- SQL Schema for Smart City Analytics Platform Database (SQLite)

CREATE TABLE IF NOT EXISTS weather (
    Date TEXT,
    City TEXT,
    Temperature REAL,
    Humidity INTEGER,
    Rainfall REAL,
    Wind_Speed REAL,
    Pressure INTEGER,
    UV_Index INTEGER,
    PRIMARY KEY (Date, City)
);

CREATE TABLE IF NOT EXISTS pollution (
    Date TEXT,
    City TEXT,
    AQI INTEGER,
    PM2_5 REAL,
    PM10 REAL,
    CO REAL,
    NO2 REAL,
    SO2 REAL,
    PRIMARY KEY (Date, City),
    FOREIGN KEY (Date, City) REFERENCES weather (Date, City)
);

CREATE TABLE IF NOT EXISTS traffic (
    Date TEXT,
    City TEXT,
    Area TEXT,
    Average_Speed REAL,
    Congestion_Index REAL,
    Vehicle_Count INTEGER,
    Peak_Hour TEXT,
    Accident_Count INTEGER,
    PRIMARY KEY (Date, City, Area),
    FOREIGN KEY (Date, City) REFERENCES weather (Date, City)
);

CREATE TABLE IF NOT EXISTS crime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT,
    City TEXT,
    District TEXT,
    Crime_Category TEXT,
    Arrest_Status TEXT,
    Case_Status TEXT,
    FOREIGN KEY (Date, City) REFERENCES weather (Date, City)
);

CREATE TABLE IF NOT EXISTS transport (
    Date TEXT,
    City TEXT,
    Daily_Passengers INTEGER,
    Bus_Utilization REAL,
    Metro_Ridership INTEGER,
    Average_Delay REAL,
    Route_Efficiency REAL,
    PRIMARY KEY (Date, City),
    FOREIGN KEY (Date, City) REFERENCES weather (Date, City)
);

CREATE TABLE IF NOT EXISTS energy (
    Date TEXT,
    City TEXT,
    Electricity_Consumption REAL,
    Renewable_Energy_Percent REAL,
    Peak_Usage REAL,
    Residential_Consumption REAL,
    Commercial_Consumption REAL,
    Industrial_Consumption REAL,
    PRIMARY KEY (Date, City),
    FOREIGN KEY (Date, City) REFERENCES weather (Date, City)
);

CREATE TABLE IF NOT EXISTS water (
    Date TEXT,
    City TEXT,
    Water_Usage REAL,
    Water_Loss REAL,
    Reservoir_Level REAL,
    Daily_Supply REAL,
    Water_Quality REAL,
    PRIMARY KEY (Date, City),
    FOREIGN KEY (Date, City) REFERENCES weather (Date, City)
);

CREATE TABLE IF NOT EXISTS healthcare (
    Date TEXT,
    City TEXT,
    Hospital_Count INTEGER,
    Bed_Availability REAL,
    Disease_Cases INTEGER,
    Vaccination_Percent REAL,
    PRIMARY KEY (Date, City),
    FOREIGN KEY (Date, City) REFERENCES weather (Date, City)
);

CREATE TABLE IF NOT EXISTS population (
    Year INTEGER,
    City TEXT,
    Population INTEGER,
    Density INTEGER,
    Literacy_Rate REAL,
    Employment_Rate REAL,
    Urban_Growth_Rate REAL,
    PRIMARY KEY (Year, City)
);

CREATE TABLE IF NOT EXISTS education (
    Year INTEGER,
    City TEXT,
    Schools INTEGER,
    Colleges INTEGER,
    Literacy REAL,
    Graduation_Rate REAL,
    Enrollment INTEGER,
    PRIMARY KEY (Year, City)
);

CREATE TABLE IF NOT EXISTS economy (
    Year INTEGER,
    City TEXT,
    GDP REAL,
    Employment_Rate REAL,
    Inflation REAL,
    Income INTEGER,
    PRIMARY KEY (Year, City)
);
