import pandas as pd
import numpy as np
from test_env.database_creation.tools import dict, plot, T2_preprocessing
import matplotlib.pyplot as plt
from pathlib import Path

def calculate(savefig, km, folder_path):

       #load dictionaries
       airplanes_dict = dict.AirplaneModels().get_models()
       aircraftnames = dict.AircraftNames().get_aircraftnames()
       airplanes = airplanes_dict.keys()
       airlines = dict.USAirlines().get_airlines()

       #Read Data
       T2 = pd.read_csv(Path("database/rawdata/USDOT/T_SCHEDULE_T2.csv"))
       AC_types = pd.read_csv(Path("database/rawdata/USDOT/L_AIRCRAFT_TYPE (1).csv"))

       #Prepare Data from schedule T2
       T2 = T2_preprocessing.preprocessing(T2, AC_types, airlines, airplanes)
       T2 = T2.loc[T2['UNIQUE_CARRIER_NAME']=='American Airlines Inc.']
       T2['Type'] = T2['Description']
       T2 = T2.groupby(['YEAR', 'Description'], as_index=False).agg(
              {'AVL_SEAT_MILES_320': 'sum', 'Type': 'size'})

       T2['ASK'] = T2['AVL_SEAT_MILES_320']*km
       T2.to_excel(Path.home() / "Downloads/t2.xlsx")
       a320 = T2.loc[T2['Description']=="Airbus Industrie A320-100/200"]
       b7378 =  T2.loc[T2['Description']=="Boeing 737-800"]

       # Plot all Data as Scatterpoints and the data for the years above as a line
       fig = plt.figure(dpi=300)
       ax = fig.add_subplot(1, 1, 1)
       x_label = 'Aircraft Year of Introduction'
       y_label = 'Efficiency Improvements [\%]'

       ax.plot(a320['YEAR'], a320['ASK'], color='black')
       ax.plot(b7378['YEAR'], b7378['ASK'], color='black')

       # Add a legend to the plot
       ax.legend()
       plot.plot_layout(None, x_label, y_label, ax)
       plt.show()
       #if savefig:
           #plt.savefig(folder_path + '/fleet_behavior.png')

       grouped = T2.groupby('Description')

       # Calculate the number of subplots needed
       num_subplots = len(grouped)
       num_rows = num_subplots // 4
       num_cols = 4

       # Create subplots
       fig, axes = plt.subplots(num_rows, num_cols, sharex=True, figsize=(8, 4))

       # Iterate over each group (aircraft) and plot the trajectory in a separate subplot
       for i, (aircraft, group) in enumerate(grouped):
              # Extract the relevant data for the current aircraft
              years = group['YEAR']
              rpk = group['Type']

              row = i // num_cols
              col = i % num_cols

              # Plot the trajectory in the corresponding subplot
              ax = axes[row, col] if num_rows > 1 else axes[col]
              ax.plot(years, rpk)
              ax.set_title(aircraft)
              ax.set_xlabel('Year')
              ax.set_ylabel('Number')

       # Adjust the spacing between subplots
       plt.tight_layout()

       # Show the plot
       plt.show()
