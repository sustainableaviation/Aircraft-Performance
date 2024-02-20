import pandas as pd
import os
from database.tools import dict
from pathlib import Path

def calculate():

    # Load Dictionaries
    airplanes_dict = dict.AirplaneModels().get_models()
    airplanes = airplanes_dict.keys()

    # Create an empty dataframe to hold the data
    T100 = pd.DataFrame()

    # Get a list of all files in the folder and load Databank
    file_list = os.listdir(Path("database/rawdata/USDOT/T100_Annual"))
    aircraft = pd.read_excel(Path("Databank.xlsx"))

    # Loop through each file and read it into a dataframe, and append to the combined dataframe
    for file_name in file_list:
        file_path = Path("database/rawdata/USDOT/T100_Annual") / file_name
        df = pd.read_csv(file_path)
        T100 = T100.append(df, ignore_index=True)


    AC_types = pd.read_csv(Path("database/rawdata/USDOT/L_AIRCRAFT_TYPE (1).csv"))

    # Get Aircraft passenger configuration and commercial aircraft group
    T100 = T100.loc[T100['CARRIER_GROUP'] == 3]
    T100 = T100.loc[T100['AIRCRAFT_CONFIG'] == 1]

    # Use the Airlines and Aircraft from the Dictionary
    T100 = pd.merge(T100, AC_types, left_on='AIRCRAFT_TYPE', right_on='Code')
    T100 = T100.loc[T100['Description'].isin(airplanes)]
    T100 = T100.loc[T100['SEATS']>0]

    # Calculate the Average Seats per Flight
    average_seats = T100.groupby(['Description', 'UNIQUE_CARRIER_NAME'], as_index=False).agg({'SEATS':'sum', 'DEPARTURES_PERFORMED':'sum'})
    average_seats['Average Seats']=average_seats['SEATS']/average_seats['DEPARTURES_PERFORMED']
    average_seats['Average Seats'] = average_seats['Average Seats'].round(0)
    average_seats = average_seats[['Description', 'Average Seats']]
    average_seats = average_seats.groupby(['Description'], as_index=False).agg({'Average Seats':'mean'})
    average_seats = average_seats.round(0)

    # Merge the average seat number to the aircraft Databank and save
    fullnames = dict.fullname().get_aircraftfullnames()
    average_seats['Description'] = average_seats['Description'].replace(fullnames)
    average_seats['Description'] = average_seats['Description'].str.strip()
    aircraft['Name'] = aircraft['Name'].str.strip()
    aircraft = pd.merge(aircraft, average_seats, left_on='Name', right_on='Description', how='left')
    aircraft = aircraft.rename(columns={'Average Seats': 'Pax'})
    aircraft = aircraft.drop(columns=['Description'])
    aircraft.to_excel(r'Databank.xlsx', index=False)
