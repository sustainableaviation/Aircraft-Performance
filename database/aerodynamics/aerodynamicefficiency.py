import pandas as pd
import math
from database.tools import plot
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def calculate_aerodynamic_efficiency(
    path_excel_aircraft_data_payload_range: Path,
    beta_widebody: float = 0.04,
    beta_narrowbody: float = 0.06,
) -> pd.DataFrame:
    """_summary_

    .. image:: https://upload.wikimedia.org/wikipedia/commons/0/04/Payload_Range_Diagram_Airbus_A350-900.svg

    Parameters
    ----------
    path_excel_aircraft_data_payload_range : Path
        _description_
    beta_widebody : float, optional
        _description_, by default 0.96
    beta_narrowbody : float, optional
        _description_, by default 0.88

    Returns
    -------
    pd.DataFrame
        _description_
    """
    
    df_payload_range = pd.read_excel(
        io=path_excel_aircraft_data_payload_range,
        sheet_name='Data',
        engine='openpyxl',
    )

    list_regional_aircraft = [
        'RJ-200ER /RJ-440',
        'RJ-700',
        'Embraer ERJ-175',
        'Embraer-145',
        'Embraer-135',
        'Embraer 190'
    ]
    df_payload_range = df_payload_range[~df_payload_range['Name'].isin(list_regional_aircraft)]

    df_payload_range

def calculate(savefig, air_density,flight_vel, g, folder_path):

    # Load Data
    aircraft_data = pd.read_excel(Path("Databank.xlsx"))
    # lift_data = pd.read_excel(Path("database/rawdata/aircraftproperties/Aicrraft Range Data Extraction.xlsx"), sheet_name='2. Table')

    # Remove these Regional jets, it seems, that their data is not accurate, possibly because overall all values are much smaller.
    # lift_data = lift_data[~lift_data['Name'].isin([
    breguet = aircraft_data.merge(lift_data, on='Name', how='left')

    # Factor Beta which accounts for the weight fraction burnt in non cruise phase and reserve fuel
    # beta = lambda x: 0.96 if x == 'Wide' else(0.94 if x =='Narrow' else 0.88)

    # Calculate Range Paramer K at point B and C

    def calculate_():

    breguet['Factor'] = breguet['Type'].apply(beta)
    breguet['Ratio 1']= breguet['Factor']*breguet["MTOW\n(Kg)"]/breguet['MZFW_POINT_1\n(Kg)']
    breguet['Ratio 2']= breguet['Factor']*breguet["MTOW\n(Kg)"]/breguet['MZFW_POINT_2\n(Kg)']
    breguet['Ratio 1']=breguet['Ratio 1'].apply(np.log)
    breguet['Ratio 2']=breguet['Ratio 2'].apply(np.log)
    breguet['K_1']= breguet['RANGE_POINT_1\n(Km)']/breguet['Ratio 1']
    breguet['K_2']= breguet['RANGE_POINT_2\n(Km)']/breguet['Ratio 2']
    breguet['K']=(breguet['K_1']+breguet['K_2'])/2

    # Add K_1 for the Comet 4
    comet4_k1 = 5190 / (np.log(0.94*73480/43410)) # data for the Comet 4 from Aerospaceweb.org
    breguet.loc[breguet['Name'] == 'Comet 4', 'K_1'] = comet4_k1

    # Add K_1 for the Comet 1. Real Flight Data
    comet1_k1 = 2761.4 / (np.log(98370/73000)) # data for the Comet 4 from Aerospaceweb.org
    breguet.loc[breguet['Name'] == 'Comet 1', 'K_1'] = comet1_k1
    # Calculate L /D, important only K_1 (Point B) is considered
    breguet['A'] = breguet['K_1']*g*0.001*breguet['TSFC Cruise']
    breguet['L/D estimate'] = breguet['A']/flight_vel

    comet4_A = breguet.loc[breguet['Name'] == 'Comet 4', 'A']
    comet1_A = breguet.loc[breguet['Name'] == 'Comet 1', 'A']
    breguet.loc[breguet['Name'] == 'Comet 4', 'L/D estimate'] = comet4_A/223.6 # account for lower speed of the Comet 4
    breguet.loc[breguet['Name'] == 'Comet 1', 'L/D estimate'] = comet1_A / 201.4  # account for lower speed of the Comet 1

    # Calculate further Aerodynamic Statistics
    aircraft_data = breguet.drop(columns=['#', 'Aircraft Model Chart', 'Link', 'Factor', 'Ratio 1',
           'Ratio 2', 'K_1', 'K_2', 'K', 'A'])
    aircraft_data['Dmax'] = (g * aircraft_data['MTOW\n(Kg)']) / aircraft_data['L/D estimate']
    aircraft_data['Aspect Ratio'] = aircraft_data['Wingspan,float,metre']**2/aircraft_data['Wing area,float,square-metre']
    aircraft_data['c_L'] = (2* g * aircraft_data['MTOW\n(Kg)']) / (air_density*(flight_vel**2)*aircraft_data['Wing area,float,square-metre'])
    aircraft_data['c_D'] = aircraft_data['c_L'] / aircraft_data['L/D estimate']
    aircraft_data['k'] = 1 / (math.pi * aircraft_data['Aspect Ratio'] * 0.8)
    aircraft_data['c_Di'] = aircraft_data['k']*(aircraft_data['c_L']**2)
    aircraft_data['c_D0'] = aircraft_data['c_D']-aircraft_data['c_Di']

    # Load Data from Lee
    lee = pd.read_excel(Path("database/rawdata/aircraftproperties/Aircraft Databank v2.xlsx"), sheet_name='New Data Entry')
    lee = lee.dropna(subset='L/Dmax')
    lee = lee.groupby(['Name','YOI'], as_index=False).agg({'L/Dmax':'mean'})
    lee['L/D estimate'] = lee['L/Dmax']

    # If set True use Data from Lee for L/D when possible.
    use_lee_et_al = True
    if use_lee_et_al:
        for index, row in lee.iterrows():
            name = row['Name']
            value = row['L/D estimate']

            # update corresponding row in aircraftdata with the value from lee
            aircraft_data.loc[aircraft_data['Name'] == name, 'L/D estimate'] = value

    # Drop some Rows and Save DF
    aircraft_data = aircraft_data.drop(columns=['MTOW\n(Kg)', 'MZFW_POINT_1\n(Kg)', 'RANGE_POINT_1\n(Km)', 'MZFW_POINT_2\n(Kg)', 'RANGE_POINT_2\n(Km)'])
    aircraft_data.to_excel(r'Databank.xlsx', index=False)

    # Prepare Aircrafts for Plotting
    breguet = aircraft_data.dropna(subset='L/D estimate')
    breguet = breguet.groupby(['Name', 'YOI', 'Type'], as_index=False).agg({'L/D estimate':'mean'})

    # Divide between Widebody and Narrowbody&Regionals
    wide = breguet.loc[breguet['Type']=='Wide']
    narrow = breguet.loc[breguet['Type'] != 'Wide']

    # Use value for 737-900 also for the ER version
    b737 = narrow.loc[narrow['Name'] == '737-900', 'L/D estimate'].values[0]
    narrow.loc[narrow['Name'] == '737-900ER', 'L/D estimate'] = b737

    # Get Referenced Aircraft
    a350 = wide.loc[wide['Name'] == 'A350-900', 'L/D estimate'].iloc[0]
    a340 = wide.loc[wide['Name'] == 'A340-500', 'L/D estimate'].iloc[0]
    limit = a350 * 1.05 * 1.15 # Limit based on NLF technology plus 777x

    # ----------PLOT L/D vs YEAR----------------
    cm = 1 / 2.54  # for inches-cm conversion
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(wide['YOI'], wide['L/D estimate'], marker='s', label='Widebody', color='orange')
    ax.scatter(narrow['YOI'], narrow['L/D estimate'], marker='^', label='Narrowbody \& Regional', color='blue')
    xlabel = 'Aircraft Year of Introduction'
    ylabel ='L/D'
    plt.ylim(10,30)
    future_projections = True
    if future_projections:
        ax.scatter(2025, a350*1.05, color='green', s=30, label='Future Projections')
        ax.axhline(y=limit, color='black', linestyle='-', linewidth=2, label='Theoretical Limit for TW')
        plt.annotate('777X', (2025, a350*1.05,),
                        fontsize=8, xytext=(-10, 5),
                        textcoords='offset points')
        ax.scatter(2030, a340*1.046, color='green', s=30)
        plt.annotate('BLADE', (2030, a340*1.046),
                        fontsize=8, xytext=(-10, 10),
                        textcoords='offset points')
        ax.scatter(2035, 27.8, color='green')
        plt.annotate('SB-Wing', (2035, 27.8),
                        fontsize=8, xytext=(-10,5),
                        textcoords='offset points')
        plt.xlim(1950,2050)
    ax.legend(loc='upper left')

    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'/aerodynamicsL_over_D_estimation_approach.png', bbox_inches='tight')
    # Return the aerodynamic limit NLF+777X
    return limit
