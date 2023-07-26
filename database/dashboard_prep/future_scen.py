import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from test_env.database_creation.tools import plot
from test_env.database_creation.tools import dict, plot, T2_preprocessing
import scipy.interpolate

def calculate(limit_tsfc, limit_aero, savefig, folder_path):
    # Load Data
    mj_to_co2 = 3.16 / 43.15  # kg CO2 produced per MJ of Jet fuel
    historic_rpk = pd.read_excel(r'dashboard\data\forecast.xlsx')
    annual_data = pd.read_excel(r'dashboard\data\annualdata.xlsx')
    data = pd.read_excel(r'Databank.xlsx')
    data = data.sort_values('YOI', ascending=True)
    slf_2019 = annual_data.loc[annual_data['Year'] == 2019, 'PLF'].iloc[0]

    # Define Functions
    def sigmoid(x, k, x0):
        return 1 / (1 + np.exp(-k * (x - x0)))
    def k(l,d):
        return np.log(100/l-1)/d

    # Create Years Column
    years = np.arange(2022, 2051)
    years = pd.DataFrame(years, columns=['Year'])

    # Create a Tech Freeze Scenario, assume in 2035 all aircraft are swapped by the A321neo
    k_techfreeze = k(l=2, d=6.5) #l is 2 when 98 % are renewed in 2035, d is 6.5 which is (2035-2022)/2
    x_techfreeze = np.arange(2022, 2036)
    s_techfreeze = sigmoid(x_techfreeze, k=k_techfreeze, x0=2028)
    s_techfreeze = np.concatenate((s_techfreeze, np.full(2050 - 2036 + 1, 1.0)))

    a321neo = data.loc[data['Name'] == 'A321-200n', 'EU (MJ/ASK)'].values[0]
    future = pd.DataFrame({
        'Year': [2022, 2035, 2050],
        'EU (MJ/ASK)': [annual_data.loc[53, 'EU (MJ/ASK)'], a321neo,  a321neo],
        'PLF': [slf_2019] * 3,
        'EI (MJ/RPK)': [annual_data.loc[53, 'EI (MJ/RPK)'], a321neo/slf_2019, a321neo/slf_2019]})
    future = future.merge(years, on='Year', how='outer')
    future = future.sort_values(by=['Year'])

    eu_2022 = future.loc[future['Year'] == 2022, 'EU (MJ/ASK)'].values[0]
    eu_2035 = future.loc[future['Year'] == 2035, 'EU (MJ/ASK)'].values[0]

    future['EU (MJ/ASK)'] = eu_2022 + (eu_2035 - eu_2022) * s_techfreeze

    # Since 'EI (MJ/RPK)' is proportional to 'EU (MJ/ASK)', we can scale it similarly
    ei_2022 = future.loc[future['Year'] == 2022, 'EI (MJ/RPK)'].values[0]
    ei_2035 = future.loc[future['Year'] == 2035, 'EI (MJ/RPK)'].values[0]

    future['EI (MJ/RPK)'] = ei_2022 + (ei_2035 - ei_2022) * s_techfreeze

    future = future.interpolate('linear')

    techfreeze = pd.concat([annual_data, future], ignore_index=True)
    techfreeze['EI (CO2/RPK)'] = mj_to_co2 * techfreeze['EI (MJ/RPK)']
    techfreeze['EU (CO2/ASK)'] = mj_to_co2 * techfreeze['EU (MJ/ASK)']
    techfreeze.to_excel(r'dashboard\data\techfreeze.xlsx')

    # Tech Limit Scenario, assumption to reach tech limit in 2050
    # Get Baseline Data
    tsfc_baseline = data.loc[data['YOI'] == 1959, 'TSFC Cruise'].iloc[0]
    ld_baseline = data.loc[data['YOI'] == 1959, 'L/D estimate'].iloc[0]
    oew_777 = data.loc[data['Name'] == '777-300/300ER/333ER', 'OEW/Exit Limit'].iloc[0]
    oew_1959 = data.loc[data['YOI'] == 1959, 'OEW/Exit Limit'].iloc[0]
    ovr_1959 = data.loc[data['YOI'] == 1959, 'EU (MJ/ASK)'].values[0]
    tsfc_2050 = 1 / (limit_tsfc / tsfc_baseline)
    ld_2050 = limit_aero / ld_baseline
    oew_2050 = (oew_777 / oew_1959) * 1.2
    ovr_2050_percentage = tsfc_2050 * ld_2050 * oew_2050
    ovr_2050_eu = ovr_1959 / ovr_2050_percentage
    ovr_2050_ei = ovr_2050_eu/slf_2019

    future = pd.DataFrame({
        'Year': [2021, 2035, 2050],
        'EU (MJ/ASK)': [annual_data.loc[53, 'EU (MJ/ASK)'], a321neo, ovr_2050_eu],
        'PLF': [slf_2019] * 3,
        'EI (MJ/RPK)': [annual_data.loc[53, 'EI (MJ/RPK)'], a321neo/slf_2019, ovr_2050_ei]})
    future = future.merge(years, on='Year', how='outer')
    future = future.sort_values(by=['Year'])
    future = future.interpolate()

    future = future[future['Year']!=2021]

    techlimit = pd.concat([annual_data, future], ignore_index=True)
    techfreeze_until_2035 = techfreeze[techfreeze['Year'] <= 2035]
    techlimit.loc[techlimit['Year'] <= 2035, 'EU (MJ/ASK)'] = techfreeze_until_2035['EU (MJ/ASK)']
    techlimit.loc[techlimit['Year'] <= 2035, 'EI (MJ/RPK)'] = techfreeze_until_2035['EI (MJ/RPK)']

    k_techlimit = k(l=2, d=7.5)
    x_techlimit = np.arange(2035, 2051)
    s_techlimit = sigmoid(x_techlimit, k=k_techlimit, x0=2042.5)

    eu_2050 = future.loc[future['Year'] == 2050, 'EU (MJ/ASK)'].values[0]
    techlimit.loc[techlimit['Year'] >= 2035, 'EU (MJ/ASK)'] = eu_2035 + (eu_2050 - eu_2035) * s_techlimit

    # Calculate the scaled 'EI (MJ/RPK)' for years 2035 to 2050
    ei_2050 = future.loc[future['Year'] == 2050, 'EI (MJ/RPK)'].values[0]
    techlimit.loc[techlimit['Year'] >= 2035, 'EI (MJ/RPK)'] = ei_2035 + (ei_2050 - ei_2035) * s_techlimit

    techlimit['EI (CO2/RPK)'] = mj_to_co2 * techlimit['EI (MJ/RPK)']
    techlimit['EU (CO2/ASK)'] = mj_to_co2 * techlimit['EU (MJ/ASK)']
    techlimit.to_excel(r'dashboard\data\techlimit.xlsx')

    # NASA HWB301-GTF AIRCRAFT, assume techfreeze scenario until 2040 then from 2040 until 2050 complete change to BWB
    b777 = data.loc[data['Name'] == 'B777', 'EU (MJ/ASK)'].values[0]
    future = pd.DataFrame({
        'Year': [2021, 2035, 2040, 2050],
        'EU (MJ/ASK)': [annual_data.loc[53, 'EU (MJ/ASK)'], a321neo,a321neo, 0.53*b777],
        'PLF': [slf_2019] * 4,
        'EI (MJ/RPK)': [annual_data.loc[53, 'EI (MJ/RPK)'], a321neo/slf_2019, a321neo/slf_2019, 0.53*b777/slf_2019]})
    future = future.merge(years, on='Year', how='outer')
    future = future.sort_values(by=['Year'])
    future = future.interpolate()
    future = future[future['Year']!=2021]

    bwb = pd.concat([annual_data, future], ignore_index=True)
    techfreeze_until_2040 = techfreeze[techfreeze['Year'] <= 2040]
    bwb.loc[bwb['Year'] <= 2040, 'EU (MJ/ASK)'] = techfreeze_until_2040['EU (MJ/ASK)']
    bwb.loc[bwb['Year'] <= 2040, 'EI (MJ/RPK)'] = techfreeze_until_2040['EI (MJ/RPK)']

    k_bwb = k(l=2, d=5)
    x_bwb = np.arange(2040, 2051)
    s_bwb = sigmoid(x_bwb, k=k_bwb, x0=2045)

    eu_2040 = future.loc[future['Year'] == 2040, 'EU (MJ/ASK)'].values[0]
    eu_2050 = future.loc[future['Year'] == 2050, 'EU (MJ/ASK)'].values[0]
    bwb.loc[bwb['Year'] >= 2040, 'EU (MJ/ASK)'] = eu_2040 + (eu_2050 - eu_2040) * s_bwb

    # Calculate the scaled 'EI (MJ/RPK)' for years 2040 to 2050
    ei_2040 = future.loc[future['Year'] == 2040, 'EI (MJ/RPK)'].values[0]
    ei_2050 = future.loc[future['Year'] == 2050, 'EI (MJ/RPK)'].values[0]
    bwb.loc[bwb['Year'] >= 2040, 'EI (MJ/RPK)'] = ei_2040 + (ei_2050 - ei_2040) * s_bwb

    bwb['EI (CO2/RPK)'] = mj_to_co2 * bwb['EI (MJ/RPK)']
    bwb['EU (CO2/ASK)'] = mj_to_co2 * bwb['EU (MJ/ASK)']
    bwb.to_excel(r'dashboard\data\bwb.xlsx')

    # NASA ADVANCED TUBE WING CONCEPT ALSO BASED ON THE 777-200
    future = pd.DataFrame({
        'Year': [2021, 2035, 2050],
        'EU (MJ/ASK)': [annual_data.loc[53, 'EU (MJ/ASK)'], a321neo, 0.547*b777],
        'PLF': [slf_2019] * 3,
        'EI (MJ/RPK)': [annual_data.loc[53, 'EI (MJ/RPK)'], a321neo/slf_2019, 0.547*b777/slf_2019]})
    future = future.merge(years, on='Year', how='outer')
    future = future.sort_values(by=['Year'])
    future = future.interpolate()
    future = future[future['Year']!=2021]

    advancedtw = pd.concat([annual_data, future], ignore_index=True)
    advancedtw.loc[advancedtw['Year'] <= 2040, 'EU (MJ/ASK)'] = techfreeze_until_2040['EU (MJ/ASK)']
    advancedtw.loc[advancedtw['Year'] <= 2040, 'EI (MJ/RPK)'] = techfreeze_until_2040['EI (MJ/RPK)']

    k_advancedtw = k(l=2, d=5)
    x_advancedtw = np.arange(2040, 2051)
    s_advancedtw = sigmoid(x_advancedtw, k=k_advancedtw, x0=2045)


    eu_2050 = future.loc[future['Year'] == 2050, 'EU (MJ/ASK)'].values[0]
    advancedtw.loc[advancedtw['Year'] >= 2040, 'EU (MJ/ASK)'] = eu_2040 + (eu_2050 - eu_2040) * s_advancedtw

    # Calculate the scaled 'EI (MJ/RPK)' for years 2040 to 2050
    ei_2050 = future.loc[future['Year'] == 2050, 'EI (MJ/RPK)'].values[0]
    advancedtw.loc[advancedtw['Year'] >= 2040, 'EI (MJ/RPK)'] = ei_2040 + (ei_2050 - ei_2040) * s_advancedtw

    advancedtw['EI (CO2/RPK)'] = mj_to_co2 * advancedtw['EI (MJ/RPK)']
    advancedtw['EU (CO2/ASK)'] = mj_to_co2 * advancedtw['EU (MJ/ASK)']
    advancedtw.to_excel(r'dashboard\data\advancedtw.xlsx')

    # MIT DOUBLE BUBBLE D8 AIRCRAFT BASED ON THE 737-800
    start = annual_data.loc[53, 'EU (MJ/ASK)']
    b737_8 = data.loc[data['Name'] == '737-800', 'EU (MJ/ASK)'].values[0]
    future = pd.DataFrame({
        'Year': [2021, 2035, 2045, 2050],
        'EU (MJ/ASK)': [annual_data.loc[53, 'EU (MJ/ASK)'], a321neo, 0.341*b737_8,  0.341*b737_8],
        'PLF': [slf_2019] * 4,
        'EI (MJ/RPK)': [annual_data.loc[53, 'EI (MJ/RPK)'], a321neo/slf_2019, 0.341*b737_8/slf_2019,  0.341*b737_8/slf_2019]})
    future = future.merge(years, on='Year', how='outer')
    future = future.sort_values(by=['Year'])
    future = future.interpolate()
    future = future[future['Year']!=2021]

    doublebubble = pd.concat([annual_data, future], ignore_index=True)

    doublebubble.loc[doublebubble['Year'] <= 2035, 'EU (MJ/ASK)'] = techfreeze_until_2040['EU (MJ/ASK)']
    doublebubble.loc[doublebubble['Year'] <= 2035, 'EI (MJ/RPK)'] = techfreeze_until_2040['EI (MJ/RPK)']

    k_doublebubble = k(l=2, d=5)
    x_doublebubble = np.arange(2035, 2046)
    s_doublebubble = sigmoid(x_doublebubble, k=k_doublebubble, x0=2040)

    eu_2045 = future.loc[future['Year'] == 2045, 'EU (MJ/ASK)'].values[0]
    doublebubble.loc[(doublebubble['Year'] >= 2035) & (doublebubble['Year'] <= 2045), 'EU (MJ/ASK)'] = eu_2035 + (eu_2045 - eu_2035) * s_doublebubble

    # Calculate the scaled 'EI (MJ/RPK)' for years 2040 to 2050
    ei_2045 = future.loc[future['Year'] == 2045, 'EI (MJ/RPK)'].values[0]
    doublebubble.loc[(doublebubble['Year'] >= 2035) & (doublebubble['Year'] <= 2045), 'EI (MJ/RPK)'] = ei_2035 + (ei_2045 - ei_2035) * s_doublebubble

    doublebubble['EI (CO2/RPK)'] = mj_to_co2 * doublebubble['EI (MJ/RPK)']
    doublebubble['EU (CO2/ASK)'] = mj_to_co2 * doublebubble['EU (MJ/ASK)']
    doublebubble.to_excel(r'dashboard\data\doublebubble.xlsx')

    # Truss Braced Wings
    future = pd.DataFrame({
        'Year': [2021, 2035, 2045, 2050],
        'EU (MJ/ASK)': [annual_data.loc[53, 'EU (MJ/ASK)'], a321neo, 0.7*a321neo,  0.7*a321neo],
        'PLF': [slf_2019] * 4,
        'EI (MJ/RPK)': [annual_data.loc[53, 'EI (MJ/RPK)'], a321neo/slf_2019, 0.7*a321neo/slf_2019,  0.7*a321neo/slf_2019]})
    future = future.merge(years, on='Year', how='outer')
    future = future.sort_values(by=['Year'])
    future = future.interpolate()
    future = future[future['Year']!=2021]

    ttwb = pd.concat([annual_data, future], ignore_index=True)

    ttwb.loc[ttwb['Year'] <= 2035, 'EU (MJ/ASK)'] = techfreeze_until_2040['EU (MJ/ASK)']
    ttwb.loc[ttwb['Year'] <= 2035, 'EI (MJ/RPK)'] = techfreeze_until_2040['EI (MJ/RPK)']

    k_ttwb = k(l=2, d=5)
    x_ttwb = np.arange(2035, 2046)
    s_ttwb = sigmoid(x_ttwb, k=k_ttwb, x0=2040)

    eu_2045 = future.loc[future['Year'] == 2045, 'EU (MJ/ASK)'].values[0]
    ttwb.loc[(ttwb['Year'] >= 2035) & (ttwb['Year'] <= 2045), 'EU (MJ/ASK)'] = eu_2035 + (eu_2045 - eu_2035) * s_ttwb

    # Calculate the scaled 'EI (MJ/RPK)' for years 2040 to 2050
    ei_2045 = future.loc[future['Year'] == 2045, 'EI (MJ/RPK)'].values[0]
    ttwb.loc[(ttwb['Year'] >= 2035) & (ttwb['Year'] <= 2045), 'EI (MJ/RPK)'] = ei_2035 + (ei_2045 - ei_2035) * s_ttwb

    ttwb['EI (CO2/RPK)'] = mj_to_co2 * ttwb['EI (MJ/RPK)']
    ttwb['EU (CO2/ASK)'] = mj_to_co2 * ttwb['EU (MJ/ASK)']
    ttwb.to_excel(r'dashboard\data\ttwb.xlsx')


    ###############################     TARGET SCENARIOS
    # ICAO Target 60% Reduction per CO2/RPK
    target = annual_data
    target = target.merge(years, how='outer')
    target['EI (CO2/RPK)'] = mj_to_co2 * target['EI (MJ/RPK)']

    icao_target_start = target.loc[target['Year'] == 2005, 'EI (CO2/RPK)'].values[0]
    icao_percentage_decrease = 0.02
    target['ICAO Target CO2/RPK'] = np.where(target['Year'] >= 2005,
                                          icao_target_start * (1 - icao_percentage_decrease) ** (target['Year'] - 2005),
                                          target['EI (CO2/RPK)'])
    target.loc[target['Year'] < 2005, 'ICAO Target CO2/RPK'] = ''

    # IATA 50% NET EMISSIONS
    rpk_2005 = historic_rpk.loc[historic_rpk['Year'] == 2005, 'Billion RPK'].values[0]
    iata_target_start = target.loc[target['Year'] == 2005, 'EI (CO2/RPK)'].values[0]
    iata_target_start = rpk_2005*iata_target_start
    iata_percentage_decrease = 0.015
    target['IATA Target CO2'] = np.where(target['Year'] >= 2005,
                                          iata_target_start * (1 - iata_percentage_decrease) ** (target['Year'] - 2005),
                                          target['EI (CO2/RPK)'])
    target.loc[target['Year'] < 2005, 'IATA Target CO2'] = ''

    # EUROCONTROL 75% OF ALl EMISSIONS
    rpk_2011 = historic_rpk.loc[historic_rpk['Year'] == 2011, 'Billion RPK'].values[0]
    ec_target_start = target.loc[target['Year'] == 2011, 'EI (CO2/RPK)'].values[0]
    ec_target_start = rpk_2011*ec_target_start
    ec_percentage_decrease = 0.035
    target['EC Target CO2'] = np.where(target['Year'] >= 2011,
                                          ec_target_start * (1 - ec_percentage_decrease) ** (target['Year'] - 2011),
                                          target['EI (CO2/RPK)'])
    target.loc[target['Year'] < 2011, 'EC Target CO2'] = ''
    target = target.merge(historic_rpk, on='Year', how='outer')
    target = target[['Year', 'ICAO Target CO2/RPK', 'IATA Target CO2', 'EC Target CO2', 'Billion RPK']]
    target.to_excel(r'dashboard\data\target.xlsx')

    fig = plt.figure(dpi=300)

    # Add a subplot
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(techlimit['Year'], techlimit['EU (MJ/ASK)'], color='blue', label='TW Tech Limit')
    ax.plot(advancedtw['Year'], advancedtw['EU (MJ/ASK)'], color='purple', label='Advanced TW')
    ax.plot(bwb['Year'], bwb['EU (MJ/ASK)'], color='green', label='Blended Wing Body')
    ax.plot(doublebubble['Year'], doublebubble['EU (MJ/ASK)'], color='grey', label='Double Bubble D8')
    ax.plot(ttwb['Year'], ttwb['EU (MJ/ASK)'], color='pink', label='Strut-Braced Wing')
    ax.plot(techfreeze['Year'],techfreeze['EU (MJ/ASK)'],color='red', label= 'TW Tech Freeze', zorder=2)
    ax.legend()
    ylabel = 'Energy Usage (MJ/ASK)'
    xlabel = 'Year'
    plot.plot_layout(None, xlabel, ylabel, ax)
    plt.xlim(2020, 2050)
    plt.ylim(0, 1.5)

    if savefig:
        plt.savefig(folder_path+'/futurefleeteff.png')

    ### Compare annual value with the single aircraft values

    # Load Dictionaries
    airplanes_dict = dict.AirplaneModels().get_models()
    airplanes = airplanes_dict.keys()

    # Read Input Data
    T2 = pd.read_csv(r"database\rawdata\USDOT\T_SCHEDULE_T2.csv")
    AC_types = pd.read_csv(r"database\rawdata\USDOT\L_AIRCRAFT_TYPE (1).csv")

    # What is the Fleet Age ?
    # Prepare Data from schedule T2
    T2 = T2_preprocessing.preprocessing(T2, AC_types, airplanes)
    # Add Names from Dictionary to DF
    airplanes_release_year = pd.DataFrame({'Description': list(airplanes), 'YOI': list(airplanes_dict.values())})
    airplanes_release_year = pd.merge(T2, airplanes_release_year, on='Description')
    airplanes_release_year['Age'] = airplanes_release_year['YEAR'] - airplanes_release_year['YOI']
    airplanes_release_year = airplanes_release_year.groupby(['YEAR','UNIQUE_CARRIER_NAME'], as_index=False).agg({'Age':'mean'})
    ovr = airplanes_release_year.groupby(['YEAR'], as_index=False).agg({'Age':'mean'})
    airlines = ['Alaska Airlines Inc.',
       'American Airlines Inc.',
       'Delta Air Lines Inc.',
       'Southwest Airlines Co.',
       'US Airways Inc.', 'United Air Lines Inc.',
       'Spirit Air Lines']

    df = airplanes_release_year[airplanes_release_year['UNIQUE_CARRIER_NAME'].isin(airlines)]

    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    for airline in df['UNIQUE_CARRIER_NAME'].unique():
        airline_data = df[df['UNIQUE_CARRIER_NAME'] == airline]
        ax.plot(airline_data['YEAR'], airline_data['Age'], label=airline, marker='o')
    ax.legend()
    ylabel = 'Age'
    xlabel = 'Year'
    plot.plot_layout(None, xlabel, ylabel, ax)

    if savefig:
        plt.savefig(folder_path+'/fleetage.png')


    # Plot for complete fleet.
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(ovr['YEAR'], ovr['Age'], label='US Fleet', marker='o')
    ax.legend()
    ylabel = 'Fleet Age'
    xlabel = 'Year'
    plot.plot_layout(None, xlabel, ylabel, ax)

    if savefig:
        plt.savefig(folder_path+'/ovrfleetage.png')