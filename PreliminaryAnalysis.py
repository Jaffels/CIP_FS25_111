from pandas import read_csv
import pandas as pd
import matplotlib.pyplot as plt


Weather = read_csv("Data/clean.csv")
Weather["date"] = pd.to_datetime(Weather["date"]).dt.date
Weather = Weather.set_index("date")

### Dataframe with only Zurich data and drop City column
Weather = Weather[Weather["City"] != "Zurich"]
Weather = Weather.drop(['weather_code', 'City'], axis=1)

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

weather_monthly[['apparent_temperature_mean', 'apparent_temperature_min', 'apparent_temperature_max']].plot(
    figsize=(12, 6),
    subplots=True,
    title=['Mean Apparent Temperature (°C)', 'Min Apparent Temperature (°C)', 'Max Apparent Temperature (°C)']
)

plt.show()

plt.plot(weather_monthly.index, weather_monthly['apparent_temperature_mean'], label="Mean Apparent Temp", color='blue')
plt.plot(weather_monthly.index, weather_monthly['apparent_temperature_min'], label="Min Apparent Temp", color='orange')
plt.plot(weather_monthly.index, weather_monthly['apparent_temperature_max'], label="Max Apparent Temp", color='green')

plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.title("Apparent Temperatures Over Time")

plt.legend()

plt.show()

