import openmeteo_requests
import requests_cache
import pandas as pd
import numpy as np
from retry_requests import retry
import os
import time

# Declare the latitude and longitude for both cities
cities = {"Zurich": {'loc': ["47.3769", "8.5417"]},
		  "Toronto": {'loc': ["43.6532", "79.3832"]}}

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def call_API(city, openmeteo):
	# Set the API call parameters
	url = "https://archive-api.open-meteo.com/v1/archive"
	params = {
		"latitude": cities[city]['loc'][0],
		"longitude": cities[city]['loc'][1],
		"start_date": "1940-01-01",
		"end_date": "2024-12-31",
		"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
				  "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean", "sunrise",
				  "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum",
				  "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
				  "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
		"timezone": cities[city].get('timezone', "Europe/Berlin"),
		"temperature_unit": "celsius",
		"wind_speed_unit": "kmh",
		"precipitation_unit": "mm"
	}
	responses = openmeteo.weather_api(url, params=params)

	# Print the first part of the API response to validate the call data is valid
	response = responses[0]
	print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation {response.Elevation()} m asl")
	print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
	print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
	
	# Process data and validate variable types
	daily = response.Daily()
	daily_weather_code = daily.Variables(0).ValuesAsNumpy()
	daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
	daily_temperature_2m_mean = daily.Variables(3).ValuesAsNumpy()
	daily_apparent_temperature_max = daily.Variables(4).ValuesAsNumpy()
	daily_apparent_temperature_min = daily.Variables(5).ValuesAsNumpy()
	daily_apparent_temperature_mean = daily.Variables(6).ValuesAsNumpy()
	daily_sunrise = daily.Variables(7).ValuesAsNumpy()
	daily_sunset = daily.Variables(8).ValuesAsNumpy()
	daily_daylight_duration = daily.Variables(9).ValuesAsNumpy()
	daily_sunshine_duration = daily.Variables(10).ValuesAsNumpy()
	daily_precipitation_sum = daily.Variables(11).ValuesAsNumpy()
	daily_rain_sum = daily.Variables(12).ValuesAsNumpy()
	daily_snowfall_sum = daily.Variables(13).ValuesAsNumpy()
	daily_precipitation_hours = daily.Variables(14).ValuesAsNumpy()
	daily_wind_speed_10m_max = daily.Variables(15).ValuesAsNumpy()
	daily_wind_gusts_10m_max = daily.Variables(16).ValuesAsNumpy()
	daily_wind_direction_10m_dominant = daily.Variables(17).ValuesAsNumpy()
	daily_shortwave_radiation_sum = daily.Variables(18).ValuesAsNumpy()
	daily_et0_fao_evapotranspiration = daily.Variables(19).ValuesAsNumpy()

	# Format the date variable to readable format
	daily_data = {"date": pd.date_range(
		start=pd.to_datetime(daily.Time(), unit="s", utc=True),
		end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
		freq=pd.Timedelta(seconds=daily.Interval()),
		inclusive="left"
	).strftime('%Y/%m/%d')
				  }
	
	# Create the pandas dataframe
	daily_data["weather_code"] = daily_weather_code
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min
	daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
	daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
	daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
	daily_data["apparent_temperature_mean"] = daily_apparent_temperature_mean
	daily_data["sunrise"] = daily_sunrise
	daily_data["sunset"] = daily_sunset
	daily_data["daylight_duration"] = daily_daylight_duration
	daily_data["sunshine_duration"] = daily_sunshine_duration
	daily_data["precipitation_sum"] = daily_precipitation_sum
	daily_data["rain_sum"] = daily_rain_sum
	daily_data["snowfall_sum"] = daily_snowfall_sum
	daily_data["precipitation_hours"] = daily_precipitation_hours
	daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
	daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
	daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
	daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
	daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration
	
	# Make a dataframe from the dictionary
	daily_dataframe = pd.DataFrame(data = daily_data)
	
	return daily_dataframe

def create_folder():
	# create a data directory call Data for our data
	os.makedirs("Data", exist_ok=True)
	print(f"Folder Data created successfully!")

def save_df(data, city):
	# Save the dataframe as csv file
	data.to_csv(f"Data/{city}.csv", index = False)
	print(f"Saved data for '{city}' successfully!")

def combine_dataframes():
	# Create a single dataframe from the 2 datasets
	# Load the 2 datasets
	df1 = pd.read_csv("Data/Zurich.csv")
	df2 = pd.read_csv("Data/Toronto.csv")
	
	# Add a column to contains the city name
	df1['City'] = 'Zurich'
	df2['City'] = 'Toronto'
	
	# Concatenate the 2 dataframes
	start_df = pd.concat([df1, df2], ignore_index=True)
	
	# Write combined dataframes to csv file
	start_df.to_csv("Data/start.csv", index = False)

def clean_dataset():
	# Load the original dataset
	clean_df = pd.read_csv("Data/start.csv")

	# Identify numerical columns
	numerical_cols = clean_df.select_dtypes(include=[np.number]).columns.tolist()

	# Check for empty or all zeros columns
	empty_cols = []
	for col in numerical_cols:
		if clean_df[col].sum() == 0:
			empty_cols.append(col)

	# Remove two columns with only zero values
	clean_df = clean_df.drop(empty_cols, axis=1)

	# Get index of rows with NaN values
	nan_rows = clean_df[clean_df.isna().any(axis=1)].index.tolist()

	clean_df = clean_df.drop(index=nan_rows, axis=0)

	clean_df['weather_code'] = clean_df['weather_code'].astype(int)

	# Write cleaned dataframe to csv file to limit API calls
	clean_df.to_csv("Data/clean.csv", index=False)

if __name__ == "__main__":
	create_folder()
	count = 0
	# Call the API and save the as csv files
	# Saving as csv files to limit the amount of calls to data provider
	for city in cities:
		data = call_API(city, openmeteo)
		save_df(data, city)

		# Delay the 2nd api call for 2 minutes to not violate limits
		# on api calls
		if count < 1:
			print("\n")
			print("\n Taking a 2 minute break......")
			time.sleep(120)
		count += 1

	combine_dataframes()

	clean_dataset()