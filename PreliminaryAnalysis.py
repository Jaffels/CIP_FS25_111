from pandas import read_csv
import pandas as pd

Weather = read_csv("Data/Zurich(1990-2024).csv")
Weather["date"] = pd.to_datetime(Weather["date"]).dt.date
Weather = Weather.set_index("date")

pd.set_option('display.max_columns', None)
print(Weather.info)
print(Weather.describe)
