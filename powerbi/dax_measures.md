# Power BI DAX Measures & Configuration Guide

This document contains copy-pasteable DAX formulas and configuration guidelines to build the **Smart City Analytics Dashboard** in Power BI.

---

## 📅 Calendar Table Setup
Before creating measures, ensure you have a standard `Calendar` table linked to your fact tables. You can generate one in Power BI with:

```dax
Calendar = 
ADDCOLUMNS(
    CALENDAR(DATE(2024, 1, 1), DATE(2026, 12, 31)),
    "Year", YEAR([Date]),
    "MonthNum", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMMM"),
    "MonthShort", FORMAT([Date], "MMM"),
    "DayOfWeekNum", WEEKDAY([Date]),
    "DayOfWeekName", FORMAT([Date], "dddd"),
    "Quarter", "Q" & FORMAT([Date], "Q")
)
```

---

## 📈 Base DAX Measures

### 1. Total Population
```dax
Total Population = SUM('population'[Population])
```

### 2. Crime Rate
*(Expressed per 100,000 residents)*
```dax
Crime Rate = 
DIVIDE(
    COUNT('crime'[id]), 
    [Total Population]
) * 100000
```

### 3. Congestion Index
```dax
Congestion Index = AVERAGE('traffic'[Congestion_Index])
```

### 4. AQI Score
```dax
AQI Score = AVERAGE('pollution'[AQI])
```

### 5. Average Temperature
```dax
Average Temperature = AVERAGE('weather'[Temperature])
```

---

## 🔄 Growth & Time Intelligence Measures

### 6. Passenger Growth % (Month-over-Month)
```dax
Passenger Growth % = 
VAR CurrentMonthRidership = SUM('transport'[Daily_Passengers])
VAR PrevMonthRidership = 
    CALCULATE(
        SUM('transport'[Daily_Passengers]), 
        DATEADD('Calendar'[Date], -1, MONTH)
    )
RETURN
    DIVIDE(
        CurrentMonthRidership - PrevMonthRidership, 
        PrevMonthRidership, 
        0
    )
```

### 7. Year-over-Year (YoY) Growth (General Template)
Use this measure template to calculate Year-over-Year growth for any metric (e.g., Energy, GDP, Crime):
```dax
YoY GDP Growth = 
VAR CurrentGDP = SUM('economy'[GDP])
VAR PriorGDP = 
    CALCULATE(
        SUM('economy'[GDP]), 
        SAMEPERIODLASTYEAR('Calendar'[Date])
    )
RETURN
    DIVIDE(CurrentGDP - PriorGDP, PriorGDP, 0)
```

### 8. Month-over-Month (MoM) Crime Growth
```dax
MoM Crime Growth = 
VAR CurrentCrimes = COUNT('crime'[id])
VAR PriorCrimes = 
    CALCULATE(
        COUNT('crime'[id]), 
        DATEADD('Calendar'[Date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentCrimes - PriorCrimes, PriorCrimes, 0)
```

---

## 📉 Averages & Running Totals

### 9. Rolling 30-Day Average AQI
```dax
Rolling 30-Day Average AQI = 
CALCULATE(
    [AQI Score],
    DATESINPERIOD(
        'Calendar'[Date],
        LASTDATE('Calendar'[Date]),
        -30,
        DAY
    )
)
```

### 10. Moving Average (Traffic Congestion)
```dax
Moving 7-Day Average Congestion = 
AVERAGEX(
    DATESINPERIOD(
        'Calendar'[Date],
        LASTDATE('Calendar'[Date]),
        -7,
        DAY
    ),
    [Congestion_Index]
)
```

### 11. Running Total Crimes
```dax
Running Total Crimes = 
TOTALYTD(
    COUNT('crime'[id]),
    'Calendar'[Date]
)
```

---

## 🏷 Ranking & Selection Analytics

### 12. Rank by District (Crime Incident Count)
```dax
Rank by District = 
IF(
    ISINSCOPE('crime'[District]),
    RANKX(
        ALLSELECTED('crime'[District]),
        COUNT('crime'[id]),
        ,
        DESC
    ),
    BLANK()
)
```

### 13. Top N Districts (Dynamic Parameter-based)
Create a Dynamic Parameter (e.g., table `'Top N Value'`) with a list of integers (e.g., 3, 5, 10) and then implement:
```dax
Show District Filter = 
VAR SelectedRank = [Rank by District]
VAR N_Value = SELECTEDVALUE('Top N Value'[Top N Value], 5)
RETURN
    IF(SelectedRank <= N_Value, 1, 0)
```
*(Apply this measure as a filter on visual: "Show District Filter is 1".)*

### 14. Dynamic KPI Selector (Slicer Switch)
Allows the user to select which KPI is plotted on a chart (e.g., "Electricity", "Renewable %", "Water Usage").
1. First, create a disconnected table `'KPI Option'` with the column `'KPI Name'`.
2. Implement the Switch measure:
```dax
Selected KPI Value = 
VAR SelectedKPI = SELECTEDVALUE('KPI Option'[KPI Name], "Electricity")
RETURN
    SWITCH(
        SelectedKPI,
        "Electricity", SUM('energy'[Electricity_Consumption]),
        "Renewable %", AVERAGE('energy'[Renewable_Energy_Percent]),
        "Water Usage", SUM('water'[Water_Usage]),
        "Daily Supply", SUM('water'[Daily_Supply]),
        BLANK()
    )
```

---

## 🛠 Power BI Modeling & Theme Setup
- **Row-Level Security (RLS)**: Go to **Modeling** > **Manage Roles**. Create a role named `CityManager` and set filter on the tables: `[City] = USERPRINCIPALNAME()` or `[City] = LOOKUPVALUE(SecurityTable[City], SecurityTable[Email], USERPRINCIPALNAME())`.
- **Dynamic Titles**: To make chart titles change based on slicers, use:
  ```dax
  Dynamic Traffic Title = "Traffic Congestion Trend for " & SELECTEDVALUE('traffic'[City], "All Cities") & " in " & SELECTEDVALUE('Calendar'[Year], "All Years")
  ```
  Set this under visual Title formatting > conditional formatting FX > field value > `Dynamic Traffic Title`.
