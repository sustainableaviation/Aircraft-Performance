import pandas as pd
import numpy as np
from database.tools import dict, plot, T2_preprocessing
import matplotlib.pyplot as plt
from pathlib import Path

def calculate(savefig, km, mj, folder_path):

       # Load Dictionaries
       airplanes_dict = dict.AirplaneModels().get_models()
       aircraftnames = dict.AircraftNames().get_aircraftnames()
       airplanes = airplanes_dict.keys()
       fullnames = dict.fullname().get_aircraftfullnames()

       # Read Input Data
       # T2 = pd.read_csv(Path("database/rawdata/USDOT/T_SCHEDULE_T2.csv"))
       # AC_types = pd.read_csv(Path("database/rawdata/USDOT/L_AIRCRAFT_TYPE (1).csv"))
       overall = pd.read_excel(Path("database/rawdata/aircraftproperties/Data Extraction 2.xlsx"), sheet_name="Figure 2")
       
       # what was in this originally, where did eg. TSFC values come from?
       aircraft_database = pd.read_excel(Path("database/rawdata/aircraftproperties/Aircraft Databank v2.xlsx"), sheet_name="New Data Entry")
       historic_slf = pd.read_excel(Path("database/rawdata/USDOT/Traffic and Operations 1929-Present_Vollständige D_data.xlsx"))

       # Prepare Data from schedule T2
       # T2 = T2_preprocessing.preprocessing(T2, AC_types, airplanes)

       # Group Data by Year and Per Aircraft Type
       fleet_avg_year= T2.groupby(['YEAR']).agg({'GAL/ASM':'median', 'GAL/RPM':'median'})
       
       # relevant for fuelflow
       AC_type = T2.groupby(['Description']).agg({'GAL/ASM':'median', 'GAL/RPM':'median', 'Fuel Flow [kg/s]':'mean'})

       # Add Names from Dictionary to DF
       airplanes_release_year = pd.DataFrame({'Description': list(airplanes), 'YOI': list(airplanes_dict.values())})
       airplanes_release_year = pd.merge(AC_type, airplanes_release_year, on='Description')

       # Get the Fuel Flow
       fuelflow = airplanes_release_year[['Description', 'Fuel Flow [kg/s]']]
       fuelflow.loc[:, 'Description'] = fuelflow['Description'].replace(fullnames)

       # Convert Gallon/Miles to MJ/km
       # airplanes_release_year['MJ/ASK'] = airplanes_release_year['GAL/ASM']*mj/km
       # airplanes_release_year['MJ/RPM'] = airplanes_release_year['GAL/RPM']*mj/km
       # fleet_avg_year['MJ/ASK'] = fleet_avg_year['GAL/ASM']*mj/km
       # fleet_avg_year['MJ/RPK'] = fleet_avg_year['GAL/RPM']*mj/km

       #Prepare Data from Babikian/Lee
       lee_fleet = overall.iloc[:, 9:11]
       lee_fleet.columns = lee_fleet.iloc[0]
       lee_fleet = lee_fleet[1:].dropna()

       lee = overall.iloc[:, 0:3]
       lee.columns = lee.iloc[0]
       lee = lee[1:].dropna()
       lee['Label'] = lee['Label'].map(aircraftnames)

       # Check which Data is in both, Lee and US DOT Form 41, and remove those from Lee
       doubled = pd.merge(lee, airplanes_release_year, left_on=['Label','Year'], right_on=['Description', 'YOI'])
       lee= lee.loc[~lee['Label'].isin(list(doubled['Label']))]

       # Remove Embraer 135 as value can't be true.
       airplanes_release_year = airplanes_release_year.loc[airplanes_release_year['Description'] != 'Embraer-135']

       # Get MJ/ASK value for the A380
       # boeing747 = airplanes_release_year.loc[airplanes_release_year['Description']=='Boeing 747-400', 'MJ/ASK'].iloc[0]
       # a380 = {'Description': 'A380', 'MJ/ASK': 0.88*boeing747}
       # airplanes_release_year = airplanes_release_year.append(a380, ignore_index=True)
       airplanes_release_year.to_excel(Path("dashboard/data/aircraft.xlsx"))

       # Divide between Regional Aircraft and the Rest.
       regionalcarriers = ['Canadair CRJ 900','Canadair RJ-200ER /RJ-440', 'Canadair RJ-700','Embraer 190'
                           'Embraer ERJ-175', 'Embraer-135','Embraer-145']
       regional = airplanes_release_year.loc[airplanes_release_year['Description'].isin(regionalcarriers)]
       normal = airplanes_release_year.loc[~airplanes_release_year['Description'].isin(regionalcarriers)]
       # Get MJ/ASK value for the Comet 4
       boeing707 = lee.loc[lee['Label']=='B707-100B/300', 'EU (MJ/ASK)'].iloc[0]
       comet4 = {'Label': 'Comet 4', 'EU (MJ/ASK)': boeing707/0.88, 'Year':1958}
       comet1 = {'Label': 'Comet 1', 'EU (MJ/ASK)': 2.499*comet4['EU (MJ/ASK)'], 'Year': 1952}
       lee = lee.append(comet4, ignore_index=True)
       lee = lee.append(comet1, ignore_index=True)
       lee.to_excel(Path("dashboard/data/aircraft_lee.xlsx"))

       # Plot Comet 4 Separately
       # comet4 = lee.loc[lee['Label']=='Comet 4']
       # comet1 = lee.loc[lee['Label'] == 'Comet 1']
       # rest = lee.loc[~lee['Label'].isin(['Comet 4', 'Comet 1'])]



       # Merge the Aircraft from Lee and the US DOT to one DF
       airplanes_release_year = airplanes_release_year[['Description','YOI','MJ/ASK']]
       airplanes_release_year = airplanes_release_year.rename(columns={'Description':'Label', 'YOI': 'Year', 'MJ/ASK':'EU (MJ/ASK)'})
       ovr_eff = pd.concat([airplanes_release_year, lee])
       ovr_eff['Label'] = ovr_eff['Label'].replace(fullnames)
       ovr_eff['Label'] = ovr_eff['Label'].str.strip()

       # Merge the MJ/ASK Data with the Databank I have created
       # aircraft_database['Name'] = aircraft_database['Name'].str.strip()
       aircraft_database = aircraft_database.merge(ovr_eff, left_on='Name', right_on='Label', how='left')
       aircraft_database = aircraft_database.merge(fuelflow, left_on='Name', right_on='Description', how='left')
       aircraft_database = aircraft_database.drop(columns=['Label', 'Year', 'Description'])
       aircraft_database = aircraft_database[['Company', 'Name', 'YOI', 'TSFC (mg/Ns)', 'L/Dmax',
              'OEW/MTOW', 'Type', 'Exit Limit', 'OEW','MTOW',
              'Babikian', 'Composites', 'EU (MJ/ASK)', 'Fuel Flow [kg/s]']]
       aircraft_database.loc[aircraft_database['Name'] == 'A310-200C/F', 'Fuel Flow [kg/s]'] = np.nan
       aircraft_database.to_excel(r'Databank.xlsx', index=False) # THIS IS WHERE THE DATABANK IS FIRST CREATED!

       # Get annual values for the fleet MJ/ASK from the US DOT
       fleet_avg_year = fleet_avg_year.reset_index(drop=False)
       fleet_avg_year = fleet_avg_year.loc[:,['YEAR', 'MJ/ASK']].rename(columns={'YEAR':'Year', 'MJ/ASK':'EU (MJ/ASK)'})

       # Add values from the fleet from Lee
       fleet_avg_year = fleet_avg_year.append(lee_fleet)

       # Average per year if data is captured in both DF
       fleet_avg_year = fleet_avg_year.groupby(['Year'], as_index=False).agg({'EU (MJ/ASK)':'mean'})

       # Add Seat Load Factor and calculate MJ/RPK
       historic_slf['PLF'] = historic_slf['PLF'].str.replace(',', '.').astype(float)
       fleet_avg_year = fleet_avg_year.merge(historic_slf[['Year', 'PLF']], on='Year')
       fleet_avg_year['EI (MJ/RPK)'] = fleet_avg_year['EU (MJ/ASK)']/fleet_avg_year['PLF']

       #Save DF
       fleet_avg_year.to_excel(Path("dashboard/data/annualdata.xlsx"), index=False)

