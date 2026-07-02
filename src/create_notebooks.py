import os
import json

# Setup folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "notebooks")
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

# Helper function to create notebook cell structures
def make_markdown_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }

def make_code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }

def save_notebook(filepath, cells):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    with open(filepath, "w") as f:
        json.dump(nb, f, indent=2)
    print(f"Created Notebook: {filepath}")

# 1. DATA CLEANING NOTEBOOK
cleaning_cells = [
    make_markdown_cell(
        "# Data Cleaning and Preprocessing\n"
        "This notebook outlines the standard ingestion pipeline to verify data integrity, format time-series fields, and clean outliers."
    ),
    make_code_cell(
        "import os\n"
        "import pandas as pd\n"
        "import numpy as np\n\n"
        "# Path configuration\n"
        "DATA_DIR = '../data'\n"
        "print('Data Directory:', os.path.abspath(DATA_DIR))"
    ),
    make_markdown_cell(
        "## Ingesting Datasets & Checking Integrity"
    ),
    make_code_cell(
        "weather_df = pd.read_csv(os.path.join(DATA_DIR, 'weather.csv'))\n"
        "pollution_df = pd.read_csv(os.path.join(DATA_DIR, 'pollution.csv'))\n"
        "traffic_df = pd.read_csv(os.path.join(DATA_DIR, 'traffic.csv'))\n\n"
        "print('Weather shape:', weather_df.shape)\n"
        "print('Pollution shape:', pollution_df.shape)\n"
        "print('Traffic shape:', traffic_df.shape)"
    ),
    make_markdown_cell(
        "## Checking for Null Values and Data Types"
    ),
    make_code_cell(
        "print('Missing Values in Weather:\\n', weather_df.isnull().sum())\n"
        "print('\\nMissing Values in Pollution:\\n', pollution_df.isnull().sum())\n"
        "print('\\nMissing Values in Traffic:\\n', traffic_df.isnull().sum())"
    ),
    make_markdown_cell(
        "## Standardizing Date Fields and Column Formats"
    ),
    make_code_cell(
        "# Convert Date columns to datetime object\n"
        "weather_df['Date'] = pd.to_datetime(weather_df['Date'])\n"
        "pollution_df['Date'] = pd.to_datetime(pollution_df['Date'])\n"
        "traffic_df['Date'] = pd.to_datetime(traffic_df['Date'])\n\n"
        "print('Weather Date type:', weather_df['Date'].dtype)"
    ),
    make_markdown_cell(
        "## Final Cleaned Output Validation"
    ),
    make_code_cell(
        "print('Weather Summary Stats:\\n', weather_df.describe())\n"
        "print('Ingestion & Cleaning completed successfully!')"
    )
]
save_notebook(os.path.join(NOTEBOOKS_DIR, "data_cleaning.ipynb"), cleaning_cells)

# 2. EDA NOTEBOOK
eda_cells = [
    make_markdown_cell(
        "# Exploratory Data Analysis (EDA)\n"
        "In this notebook, we explore the correlations between weather conditions, air quality, electricity consumption, and transport ridership."
    ),
    make_code_cell(
        "import os\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n\n"
        "DATA_DIR = '../data'\n"
        "sns.set_theme(style='darkgrid')"
    ),
    make_markdown_cell(
        "## Load Data and Merge"
    ),
    make_code_cell(
        "weather = pd.read_csv(os.path.join(DATA_DIR, 'weather.csv'))\n"
        "pollution = pd.read_csv(os.path.join(DATA_DIR, 'pollution.csv'))\n"
        "energy = pd.read_csv(os.path.join(DATA_DIR, 'energy.csv'))\n\n"
        "# Merge datasets on Date and City\n"
        "merged = pd.merge(weather, pollution, on=['Date', 'City'])\n"
        "merged = pd.merge(merged, energy, on=['Date', 'City'])\n"
        "print('Merged Data Columns:', merged.columns)\n"
        "print('Merged Data Shape:', merged.shape)"
    ),
    make_markdown_cell(
        "## Correlation Matrix Analysis"
    ),
    make_code_cell(
        "corr_cols = ['Temperature', 'Humidity', 'Rainfall', 'Wind_Speed', 'AQI', 'PM2_5', 'Electricity_Consumption', 'Renewable_Energy_Percent']\n"
        "corr_matrix = merged[corr_cols].corr()\n"
        "print('Correlation Matrix:\\n', corr_matrix.round(2))"
    ),
    make_markdown_cell(
        "## Plotting Correlations"
    ),
    make_code_cell(
        "plt.figure(figsize=(10, 8))\n"
        "sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)\n"
        "plt.title('Urban indicators Correlation Matrix')\n"
        "plt.show()"
    ),
    make_markdown_cell(
        "## Identifying Outliers / Extremes"
    ),
    make_code_cell(
        "extreme_aqi = merged[merged['AQI'] > 150]\n"
        "print(f'Number of days with AQI > 150 (Unhealthy): {len(extreme_aqi)}')\n"
        "print(extreme_aqi[['Date', 'City', 'AQI', 'Temperature', 'Wind_Speed']].head())"
    )
]
save_notebook(os.path.join(NOTEBOOKS_DIR, "eda.ipynb"), eda_cells)

# 3. FORECASTING NOTEBOOK
forecasting_cells = [
    make_markdown_cell(
        "# Machine Learning: Time-Series Forecasting\n"
        "This notebook outlines training a Random Forest Regressor to forecast tomorrow's air quality index (AQI) and future energy demands."
    ),
    make_code_cell(
        "import os\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "from sklearn.model_selection import train_test_split\n"
        "from sklearn.ensemble import RandomForestRegressor\n"
        "from sklearn.metrics import mean_absolute_error, r2_score\n"
        "import matplotlib.pyplot as plt\n\n"
        "DATA_DIR = '../data'"
    ),
    make_markdown_cell(
        "## Load Feature Data"
    ),
    make_code_cell(
        "weather = pd.read_csv(os.path.join(DATA_DIR, 'weather.csv'))\n"
        "pollution = pd.read_csv(os.path.join(DATA_DIR, 'pollution.csv'))\n"
        "df = pd.merge(weather, pollution, on=['Date', 'City'])\n"
        "print('Datasets merged. Shape:', df.shape)"
    ),
    make_markdown_cell(
        "## Feature Engineering"
    ),
    make_code_cell(
        "# Create date variables\n"
        "df['Date'] = pd.to_datetime(df['Date'])\n"
        "df['Month'] = df['Date'].dt.month\n"
        "df['DayOfWeek'] = df['Date'].dt.dayofweek\n"
        "df['AQI_Lag_1'] = df.groupby('City')['AQI'].shift(1)\n"
        "# Drop rows with NaN due to lag\n"
        "df.dropna(inplace=True)"
    ),
    make_markdown_cell(
        "## Model Training: Predicting AQI"
    ),
    make_code_cell(
        "features = ['Temperature', 'Humidity', 'Rainfall', 'Wind_Speed', 'Month', 'DayOfWeek', 'AQI_Lag_1']\n"
        "X = df[df['City'] == 'Mumbai'][features]\n"
        "y = df[df['City'] == 'Mumbai']['AQI']\n\n"
        "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n"
        "model = RandomForestRegressor(n_estimators=50, random_state=42)\n"
        "model.fit(X_train, y_train)\n"
        "y_pred = model.predict(X_test)\n\n"
        "print('Model Evaluation Metrics:')\n"
        "print('Mean Absolute Error (MAE):', round(mean_absolute_error(y_test, y_pred), 3))\n"
        "print('R2 Score (Variance Explained):', round(r2_score(y_test, y_pred), 3))"
    ),
    make_markdown_cell(
        "## Plotting Actual vs Predicted AQI"
    ),
    make_code_cell(
        "plt.figure(figsize=(12, 6))\n"
        "plt.plot(y_test.values[:50], label='Actual AQI', color='blue')\n"
        "plt.plot(y_pred[:50], label='Predicted AQI', color='red', linestyle='--')\n"
        "plt.title('Actual vs Predicted AQI - Mumbai')\n"
        "plt.legend()\n"
        "plt.show()"
    )
]
save_notebook(os.path.join(NOTEBOOKS_DIR, "forecasting.ipynb"), forecasting_cells)

# 4. FEATURE ENGINEERING NOTEBOOK
feature_eng_cells = [
    make_markdown_cell(
        "# Feature Engineering and Selection\n"
        "This notebook focuses on creating time-series features such as lag variables, rolling window statistics, and seasonal indicators to improve our prediction models."
    ),
    make_code_cell(
        "import os\n"
        "import pandas as pd\n"
        "import numpy as np\n\n"
        "DATA_DIR = '../data'"
    ),
    make_markdown_cell(
        "## Loading Data & Creating Base Time Features"
    ),
    make_code_cell(
        "weather = pd.read_csv(os.path.join(DATA_DIR, 'weather.csv'))\n"
        "pollution = pd.read_csv(os.path.join(DATA_DIR, 'pollution.csv'))\n"
        "df = pd.merge(weather, pollution, on=['Date', 'City'])\n"
        "df['Date'] = pd.to_datetime(df['Date'])\n\n"
        "# Base Date features\n"
        "df['Year'] = df['Date'].dt.year\n"
        "df['Month'] = df['Date'].dt.month\n"
        "df['Day'] = df['Date'].dt.day\n"
        "df['DayOfWeek'] = df['Date'].dt.dayofweek\n"
        "df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)\n"
        "print(df[['Date', 'Month', 'DayOfWeek', 'IsWeekend']].head())"
    ),
    make_markdown_cell(
        "## Generating Lag and Rolling Window Features"
    ),
    make_code_cell(
        "# 1-day and 7-day Lags for AQI\n"
        "df['AQI_Lag_1'] = df.groupby('City')['AQI'].shift(1)\n"
        "df['AQI_Lag_7'] = df.groupby('City')['AQI'].shift(7)\n\n"
        "# 7-day Rolling Averages\n"
        "df['AQI_7Day_Mean'] = df.groupby('City')['AQI'].transform(lambda x: x.shift(1).rolling(7).mean())\n"
        "df['AQI_7Day_Std'] = df.groupby('City')['AQI'].transform(lambda x: x.shift(1).rolling(7).std())\n\n"
        "# Fill or drop NaNs due to shifting\n"
        "df.dropna(inplace=True)\n"
        "print('Features summary stats:\\n', df[['AQI', 'AQI_Lag_1', 'AQI_7Day_Mean', 'AQI_7Day_Std']].describe())"
    ),
    make_markdown_cell(
        "## Feature Correlation Heatmap"
    ),
    make_code_cell(
        "import seaborn as sns\n"
        "import matplotlib.pyplot as plt\n\n"
        "plt.figure(figsize=(10, 6))\n"
        "sns.heatmap(df[['AQI', 'Temperature', 'Humidity', 'Wind_Speed', 'AQI_Lag_1', 'AQI_7Day_Mean']].corr(), annot=True, cmap='viridis')\n"
        "plt.title('Engineered Features Correlation Analysis')\n"
        "plt.show()"
    )
]
save_notebook(os.path.join(NOTEBOOKS_DIR, "feature_engineering.ipynb"), feature_eng_cells)

