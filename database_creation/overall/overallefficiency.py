import pandas as pd
import numpy as np
from test_env.database_creation.tools import dict, plot, T2_preprocessing
import matplotlib.pyplot as plt

def calculate(savefig, km, mj, folder_path):

       # Load Dictionaries
       airplanes_dict = dict.AirplaneModels().get_models()
       aircraftnames = dict.AircraftNames().get_aircraftnames()
       airplanes = airplanes_dict.keys()
       fullnames = dict.fullname().get_aircraftfullnames()

       # Read Input Data
       T2 = pd.read_csv(r"database_creation\rawdata\USDOT\T_SCHEDULE_T2.csv")
       AC_types = pd.read_csv(r"database_creation\rawdata\USDOT\L_AIRCRAFT_TYPE (1).csv")
       overall = pd.read_excel(r"database_creation\rawdata\aircraftproperties\Data Extraction 2.xlsx", sheet_name='Figure 2')
       aircraft_database = pd.read_excel(r'database_creation\rawdata\aircraftproperties\Aircraft Databank v2.xlsx', sheet_name='New Data Entry')
       historic_slf = pd.read_excel(r"database_creation\rawdata\USDOT\Traffic and Operations 1929-Present_Vollständige D_data.xlsx")

       # Prepare Data from schedule T2
       T2 = T2_preprocessing.preprocessing(T2, AC_types, airplanes)

       # Group Data by Year and Per Aircraft Type
       fleet_avg_year= T2.groupby(['YEAR']).agg({'GAL/ASM':'median', 'GAL/RPM':'median'})
       AC_type = T2.groupby(['Description']).agg({'GAL/ASM':'median', 'GAL/RPM':'median', 'Fuel Flow [kg/s]':'mean'})

       # Add Names from Dictionary to DF
       airplanes_release_year = pd.DataFrame({'Description': list(airplanes), 'YOI': list(airplanes_dict.values())})
       airplanes_release_year = pd.merge(AC_type, airplanes_release_year, on='Description')

       # Get the Fuel Flow
       fuelflow = airplanes_release_year[['Description', 'Fuel Flow [kg/s]']]
       fuelflow.loc[:, 'Description'] = fuelflow['Description'].replace(fullnames)

       # Convert Gallon/Miles to MJ/km
       airplanes_release_year['MJ/ASK'] = airplanes_release_year['GAL/ASM']*mj/km
       airplanes_release_year['MJ/RPM'] = airplanes_release_year['GAL/RPM']*mj/km
       fleet_avg_year['MJ/ASK'] = fleet_avg_year['GAL/ASM']*mj/km
       fleet_avg_year['MJ/RPK'] = fleet_avg_year['GAL/RPM']*mj/km

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
       boeing747 = airplanes_release_year.loc[airplanes_release_year['Description']=='Boeing 747-400', 'MJ/ASK'].iloc[0]
       a380 = {'Description': 'A380', 'MJ/ASK': 0.88*boeing747}
       airplanes_release_year = airplanes_release_year.append(a380, ignore_index=True)
       airplanes_release_year.to_excel(
              r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\dashboard_creation\aircraft.xlsx')

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
       lee.to_excel(
              r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\dashboard_creation\aircraft_lee.xlsx')

       # Plot Comet 4 Separately
       comet4 = lee.loc[lee['Label']=='Comet 4']
       comet1 = lee.loc[lee['Label'] == 'Comet 1']
       rest = lee.loc[~lee['Label'].isin(['Comet 4', 'Comet 1'])]

       # -----------Plot MJ/ASK vs Release Year------------------
       cm = 1 / 2.54  # for inches-cm conversion
       fig = plt.figure(dpi=300)
       ax = fig.add_subplot(1, 1, 1)
       ax.scatter(comet1['Year'], comet1['EU (MJ/ASK)'], marker='*', color='blue', label='Comet 1')
       ax.scatter(comet4['Year'], comet4['EU (MJ/ASK)'], marker='o', color='blue', label='Comet 4')
       ax.scatter(normal['YOI'], normal['MJ/ASK'], marker='^',color='blue', label='US DOT T2')
       ax.scatter(regional['YOI'], regional['MJ/ASK'], marker='^', color='cyan', label='Regional US DOT T2')
       ax.scatter(rest['Year'], rest['EU (MJ/ASK)'], marker='s',color='red', label='Lee')
       ax.plot(fleet_avg_year.index, fleet_avg_year['MJ/ASK'],color='blue', label='US DOT T2 Fleet')
       ax.plot(fleet_avg_year.index, fleet_avg_year['MJ/RPK'],color='blue',linestyle='--', label='US DOT T2 Fleet RPK')
       ax.plot(lee_fleet['Year'], lee_fleet['EU (MJ/ASK)'],color='red', label='Lee Fleet')

       ax.legend()
       future_legend = ax.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Historic Data", frameon=False)
       future_legend._legend_box.align = "left"

       #Add projections from Lee et al.
       plot_past_projections = False
       if plot_past_projections:
              ax.scatter([1997, 2007, 2022], [1.443, 1.238, 0.9578], marker='^', color='black', label='NASA 100 PAX')
              ax.scatter([1997, 2007, 2022], [1.2787, 1.0386, 0.741], marker='*', color='black', label='NASA 150 PAX')
              ax.scatter([1997, 2007, 2022], [1.2267, 0.9867, 0.681], marker='s', color='black', label='NASA 225 PAX')
              ax.scatter([1997, 2007, 2022], [1.1704, 0.9259, 0.637], marker='o', color='black', label='NASA 300 PAX')
              ax.scatter([1997, 2007, 2022], [0.91, 0.76, 0.559], marker='P', color='black', label='NASA 600 PAX')
              ax.scatter(2010, 0.6587 , marker='^', color='grey', label='NRC')
              ax.scatter(2015, 0.5866, marker='o', color='grey', label='Greene')
              ax.scatter([2025, 2025, 2025], [0.55449, 0.6, 0.68], marker='s', color='grey', label='Lee')

              # Projection legend
              projection_handles = ax.get_legend_handles_labels()[0][8:]  # Exclude the first 8 handles (historic data)
              projection_labels = ax.get_legend_handles_labels()[1][8:]  # Exclude the first 8 labels (historic data)
              ax.legend(projection_handles, projection_labels, loc='lower left', bbox_to_anchor=(1, -0.05),
                                            title="Historic Projections", frameon=False)
              ax.add_artist(future_legend)
       plot_future_projections = False
       if plot_future_projections:
              ax.scatter(2035,0.592344579, marker='s', color='black', label='SB-Wing')
              ax.scatter(2035,0.381840741, marker='o', color='black', label='Double Bubble')
              ax.scatter(2040,0.82264895, marker='P', color='black', label='Advanced TW')
              ax.scatter(2040,0.797082164, marker='*', color='black', label='BWB')
              ax.scatter(2050,0.618628347, marker='^', color='black', label='TW Limit')

              # Projection legend
              projection_handles = ax.get_legend_handles_labels()[0][8:]  # Exclude the first 8 handles (historic data)
              projection_labels = ax.get_legend_handles_labels()[1][8:]  # Exclude the first 8 labels (historic data)
              ax.legend(projection_handles, projection_labels, loc='lower left', bbox_to_anchor=(1, -0.05),
                                            title="Future Projections", frameon=False)
              ax.add_artist(future_legend)

       #Arrange plot size
       plt.ylim(0, 9)
       plt.xlim(1950, 2024)
       plt.xticks(np.arange(1950, 2023, 10))

       # Set the x and y axis labels
       xlabel = 'Aircraft Year of Introduction'
       ylabel = 'EU (MJ/ASK)'
       plot.plot_layout(None, xlabel, ylabel, ax)
       if savefig:
              plt.savefig(folder_path+ "\ovr_efficiency.png", bbox_inches='tight')

       # Merge the Aircraft from Lee and the US DOT to one DF
       airplanes_release_year = airplanes_release_year[['Description','YOI','MJ/ASK']]
       airplanes_release_year = airplanes_release_year.rename(columns={'Description':'Label', 'YOI': 'Year', 'MJ/ASK':'EU (MJ/ASK)'})
       ovr_eff = pd.concat([airplanes_release_year, lee])
       ovr_eff['Label'] = ovr_eff['Label'].replace(fullnames)
       ovr_eff['Label'] = ovr_eff['Label'].str.strip()

       # Merge the MJ/ASK Data with the Databank I have created
       aircraft_database['Name'] = aircraft_database['Name'].str.strip()
       aircraft_database = aircraft_database.merge(ovr_eff, left_on='Name', right_on='Label', how='left')
       aircraft_database = aircraft_database.merge(fuelflow, left_on='Name', right_on='Description', how='left')
       aircraft_database = aircraft_database.drop(columns=['Label', 'Year', 'Description'])
       aircraft_database = aircraft_database[['Company', 'Name', 'YOI', 'TSFC (mg/Ns)', 'L/Dmax',
              'OEW/MTOW', 'Type', 'Exit Limit', 'OEW','MTOW',
              'Babikian', 'Composites', 'EU (MJ/ASK)', 'Fuel Flow [kg/s]']]
       aircraft_database.loc[aircraft_database['Name'] == 'A310-200C/F', 'Fuel Flow [kg/s]'] = np.nan
       aircraft_database.to_excel(r'Databank.xlsx', index=False)

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
       fleet_avg_year.to_excel(r'database_creation\rawdata\annualdata.xlsx', index=False)

