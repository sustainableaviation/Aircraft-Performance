import pandas as pd
from test_env.database_creation.tools import dict, plot, T2_preprocessing
import numpy as np
import matplotlib.pyplot as plt
def calculate(savefig, folder_path):
        databank = pd.read_excel(r'Databank.xlsx')
        databank = databank[['Name', 'Type', 'TSFC Cruise', 'EU (MJ/ASK)', 'OEW/Exit Limit', 'L/D estimate']]
        airplanes_dict = dict.AirplaneModels().get_models()
        aircraftnames = dict.AircraftNames().get_aircraftnames()
        airplanes = airplanes_dict.keys()
        airlines = dict.USAirlines().get_airlines()
        fullnames = dict.fullname().get_aircraftfullnames()

        # Read Data
        T2 = pd.read_csv(r'database/rawdata/USDOT/T_SCHEDULE_T2.csv')
        AC_types = pd.read_csv(r"database/rawdata/USDOT/L_AIRCRAFT_TYPE (1).csv")

        # Prepare Data from schedule T2
        T2 = T2_preprocessing.preprocessing(T2, AC_types, airlines, airplanes)
        T2.loc[:, 'Description'] = T2['Description'].replace(fullnames)
        fleet = pd.merge(T2, databank, left_on='Description', right_on='Name')
        fleet = fleet.groupby(['YEAR', 'Description', 'Type'], as_index=False).agg({'AVL_SEAT_MILES_320':'sum',
                                                                                    'REV_PAX_MILES_140':'sum',
                                                                                    'TSFC Cruise':'mean',
                                                                                    'OEW/Exit Limit':'mean',
                                                                                    'EU (MJ/ASK)':'mean',
                                                                                    'L/D estimate':'mean'})
        fleet = fleet.dropna()
        narrowbody = fleet.loc[fleet['Type']!='Wide']
        widebody = fleet.loc[fleet['Type']=='Wide']

        def calculate(df):
                engine = df.dropna(subset='TSFC Cruise')
                engine['Aircraft Usage Factor'] = engine['AVL_SEAT_MILES_320'] * engine['TSFC Cruise']
                engine = engine.groupby(['YEAR'], as_index=False).agg({'Aircraft Usage Factor': 'sum', 'AVL_SEAT_MILES_320': 'sum'})
                engine['Annual TSFC'] = engine['Aircraft Usage Factor'] / engine['AVL_SEAT_MILES_320']
                engine = engine[['YEAR', 'Annual TSFC']]

                # Calculate Structural Efficiency
                structural = df.dropna(subset='OEW/Exit Limit')
                structural['Aircraft Usage Factor'] = structural['AVL_SEAT_MILES_320'] * structural['OEW/Exit Limit']
                structural = structural.groupby(['YEAR'], as_index=False).agg(
                        {'Aircraft Usage Factor': 'sum', 'AVL_SEAT_MILES_320': 'sum'})
                structural['Annual Weight'] = structural['Aircraft Usage Factor'] / structural['AVL_SEAT_MILES_320']
                structural = structural[['YEAR', 'Annual Weight']]

                # Calculate Overall Efficiency
                overall = df.dropna(subset='EU (MJ/ASK)')
                overall['Aircraft Usage Factor'] = overall['AVL_SEAT_MILES_320'] * overall['EU (MJ/ASK)']
                overall = overall.groupby(['YEAR'], as_index=False).agg(
                        {'Aircraft Usage Factor': 'sum', 'AVL_SEAT_MILES_320': 'sum'})
                overall['Annual EU'] = overall['Aircraft Usage Factor'] / overall['AVL_SEAT_MILES_320']
                overall = overall[['YEAR', 'Annual EU']]

                # Calculate Aerodynamic Efficiency
                aerodynamic = df.dropna(subset='L/D estimate')
                aerodynamic['Aircraft Usage Factor'] = aerodynamic['AVL_SEAT_MILES_320'] * aerodynamic['L/D estimate']
                aerodynamic = aerodynamic.groupby(['YEAR'], as_index=False).agg(
                        {'Aircraft Usage Factor': 'sum', 'AVL_SEAT_MILES_320': 'sum'})
                aerodynamic['Annual L/D'] = aerodynamic['Aircraft Usage Factor'] / aerodynamic['AVL_SEAT_MILES_320']
                aerodynamic = aerodynamic[['YEAR', 'Annual L/D']]

                # Merge the efficiency DataFrames
                df = pd.merge(overall, structural, on='YEAR')
                df = pd.merge(df, aerodynamic, on='YEAR')
                df = pd.merge(df, engine, on='YEAR')
                return df

        widebody = calculate(widebody)
        narrowbody = calculate(narrowbody)
        fleet = calculate(fleet)

        # Somehow this works accurate on fleet level, but there is a huge residual factor for wide and narrow body aircraft.
        data = fleet

        max_eu = data['Annual EU'].iloc[0]
        data['Annual EU'] = 100 / (data['Annual EU'] / max_eu)

        max_weight = data['Annual Weight'].iloc[0]
        data['Annual Weight'] = 100 / (data['Annual Weight'] / max_weight)

        max_tsfc = data['Annual TSFC'].iloc[0]
        data['Annual TSFC'] = 100 / (data['Annual TSFC'] / max_tsfc)

        max_aero = data['Annual L/D'].iloc[0]
        data['Annual L/D'] = 100 / (max_aero / data['Annual L/D'])

        # Normalize Data for TSFC, L/D, OEW/Exit Limit and EU using 1959 as a Basis, for OEW normalize regarding heaviest value of each Type


        data['LMDI'] = (data['Annual EU'] - data['Annual EU'].iloc[0]) / (
                        np.log(data['Annual EU']) - np.log(data['Annual EU'].iloc[0]))
        data['Engine_LMDI'] = np.log(data['Annual TSFC'] / data['Annual TSFC'].iloc[0])
        data['Aerodyn_LMDI'] = np.log(data['Annual L/D'] / data['Annual L/D'].iloc[0])
        data['Structural_LMDI'] = np.log(data['Annual Weight'] / data['Annual Weight'].iloc[0])
        data['deltaC_Aerodyn'] = data['LMDI'] * data['Aerodyn_LMDI']
        data['deltaC_Engine'] = data['LMDI'] * data['Engine_LMDI']
        data['deltaC_Structural'] = data['LMDI'] * data['Structural_LMDI']
        data['deltaC_Tot'] = data['Annual EU'] - data['Annual EU'].iloc[0]
        data['deltaC_Res'] = data['deltaC_Tot'] - data['deltaC_Aerodyn'] - data['deltaC_Engine'] - data['deltaC_Structural']

        # Get percentage increase of each efficiency and drop first row which only contains NaN
        data = data[['YEAR', 'deltaC_Structural', 'deltaC_Engine', 'deltaC_Aerodyn', 'deltaC_Res', 'deltaC_Tot']]
        data = data.drop(0)
        data = data.set_index('YEAR')

        # Set the width of each group and create new indexes just the set the space right
        data = data[['deltaC_Tot', 'deltaC_Engine', 'deltaC_Aerodyn', 'deltaC_Structural', 'deltaC_Res']]
        # Define the desired order of columns
        column_order = ['deltaC_Tot', 'deltaC_Res', 'deltaC_Aerodyn', 'deltaC_Structural', 'deltaC_Engine']

        # Reorder the columns
        data = data[column_order]
        # Create new Labels
        labels = ['Overall (MJ/ASK)', 'Residual', 'Aerodynamic (L/D)', 'Structural (OEW/Exit)', 'Engine (TSFC)']

        # Create subplots for each column
        fig, ax = plt.subplots(dpi=300)

        # Plot stacked areas for other columns
        data_positive = data.drop('deltaC_Tot', axis=1).clip(lower=0)
        data_negative = data.drop('deltaC_Tot', axis=1).clip(upper=0)
        # Create arrays for stacking the areas
        positive_stack = np.zeros(len(data))
        negative_stack = np.zeros(len(data))

        colors = ['blue', 'royalblue', 'steelblue', 'lightblue']
        for i, column in enumerate(data_positive.columns):
                ax.fill_between(data.index, positive_stack, positive_stack + data_positive.iloc[:, i], color=colors[i],
                                label=labels[i + 1], linewidth=0)
                positive_stack += data_positive.iloc[:, i]
        for i, column in enumerate(data_negative.columns):
                ax.fill_between(data.index, negative_stack, negative_stack + data_negative.iloc[:, i], color=colors[i],
                                linewidth=0)
                negative_stack += data_negative.iloc[:, i]

        # Plot overall efficiency as a line
        overall_efficiency = data['deltaC_Tot']
        ax.plot(data.index, overall_efficiency, color='black', label=labels[0], linewidth=3)

        xlabel = 'Year'
        ylabel = 'Efficiency Improvements [%]'
        ax.set_xlim(1990, 2022)
        ax.legend(loc='upper left')
        plot.plot_layout(None, xlabel, ylabel, ax)
        if savefig:
                plt.savefig(folder_path + '/ida_fleet_level.png')
