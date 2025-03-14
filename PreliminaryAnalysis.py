from pandas import read_csv
import pandas as pd
import matplotlib.pyplot as plt

Weather = read_csv("Data/Zurich(1990-2024).csv")
Weather["date"] = pd.to_datetime(Weather["date"]).dt.date
Weather = Weather.set_index("date")

pd.set_option('display.max_columns', None)
print(Weather.info)
print(Weather.describe)

Weather[['apparent_temperature_mean', 'wind_speed_10m_max', 'precipitation_hours']].plot(
    figsize=(12, 6),
    subplots=True,
    title=['Apparent Temperature (°C)', 'Max Wind Speed (m/s)', 'Precipitation Hours']
)

plt.show()

print(type(Weather.index))
Weather.index = pd.to_datetime(Weather.index)
print(type(Weather.index))

weather_monthly = Weather.resample('MS').mean()

print(weather_monthly.head())

weather_monthly[['apparent_temperature_mean', 'wind_speed_10m_max', 'precipitation_hours']].plot(
    figsize=(12, 6),
    subplots=True,
    title=['Apparent Temperature (°C)', 'Max Wind Speed (m/s)', 'Precipitation Hours']
)

plt.show()