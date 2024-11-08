# %%
from pathlib import Path

import pandas as pd
import numpy as np


def determine_takeoff_to_cruise_tsfc_ratio(path_excel_engine_data_for_calibration: Path) -> float:
    """_summary_

    _extended_summary_

    Parameters
    ----------
    path_excel_engine_data_for_calibration : Path
        _description_

    Returns
    -------
    float
        _description_
    """
    df_engines = pd.read_excel(
        io=path_excel_engine_data_for_calibration,
        sheet_name='Data',
        engine='openpyxl',
    )
    df_engines_grouped = df_engines.groupby(['Engine Identification'], as_index=False).agg(
        {
            'TSFC(cruise) [g/kNs]' : 'mean',
            'TSFC(takeoff) [g/kNs]' : 'mean',
            'Introduction':'mean'
        }
    )

    x = df_engines_grouped['TSFC(takeoff) [g/kNs]']
    y = df_engines_grouped['TSFC(cruise) [g/kNs]']

    linear_regression = np.polynomial.Polynomial.fit(
        x=x,
        y=y,
        deg=1,
    )
    polynomial_fit = np.polynomial.Polynomial.fit(
        x=x,
        y=y,
        deg=2,
    )

    def r_squared(y, y_pred):
        # https://en.wikipedia.org/wiki/Coefficient_of_determination#Definitions
        tss = np.sum((y - np.mean(y))**2)
        rss = np.sum((y - y_pred)**2)
        return 1 - (rss / tss)

    r_squared_linear = r_squared(y, linear_regression(x))
    r_squared_polynomial = r_squared(y, polynomial_fit(x))

    return linear_regression, polynomial_fit, r_squared_linear, r_squared_polynomial


def calculate(z):
    # Read Data
    emissions_df = pd.read_excel(Path("database/rawdata/emissions/edb-emissions-databank_v29 (web).xlsx"), sheet_name='Gaseous Emissions and Smoke')

    # Calculate T/O TSFC
    emissions_df['TSFC T/O']= emissions_df['Fuel Flow T/O (kg/sec)']/emissions_df['Rated Thrust (kN)']*1000

    # Get Test Year
    emissions_df['Final Test Date']= pd.to_datetime(emissions_df['Final Test Date'])
    emissions_df['Final Test Date']= emissions_df['Final Test Date'].dt.strftime('%Y')

    # Drop Engines for which important Data is unknown
    yearly_emissions = emissions_df[['Engine Identification','Final Test Date', 'Fuel Flow T/O (kg/sec)', 'B/P Ratio', 'Pressure Ratio', 'Rated Thrust (kN)','TSFC T/O']]
    yearly_emissions = yearly_emissions.dropna()

    # Scale with the Polynomial
    poly = lambda x: z[0]*x + z[1]
    yearly_emissions['TSFC Cruise'] = yearly_emissions['TSFC T/O'].apply(poly)

    # Save Engines
    yearly_emissions.to_excel(Path("database/rawdata/emissions/icao_cruise_emissions.xlsx"))




# %%

path_excel = Path('/Users/michaelweinold/Library/CloudStorage/OneDrive-TheWeinoldFamily/Documents/University/PhD/Data/Aircraft Performance/Aircraft Engine Database.xlsx')

lin, pol, r2_lin, r2_pol  = determine_takeoff_to_cruise_tsfc_ratio(path_excel)



import matplotlib.pyplot as plt



fig = plt.figure(dpi=300)
plt.scatter(
    x=df_engines_grouped['TSFC(takeoff) [g/kNs]'],
    y=df_engines_grouped['TSFC(cruise) [g/kNs]'],
    color='black',
    label='Turbofan Engines',
)
plt.plot(
    np.arange(8, 19, 0.2),
    reg(np.arange(8, 19, 0.2)),
    color='blue',
    label='Linear Regression',
    linewidth=2,
)
plt.plot(
    np.arange(8, 19, 0.2),
    poly(np.arange(8, 19, 0.2)),
    color='red',
    label='Second Order Regression',
    linewidth=2,
)
