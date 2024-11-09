# %%
from pathlib import Path

import pandas as pd
import numpy as np


def determine_takeoff_to_cruise_tsfc_ratio(
    path_excel_engine_data_for_calibration: Path
) -> tuple[np.polynomial.Polynomial, np.polynomial.Polynomial, float, float]:
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

    linear_fit = np.polynomial.Polynomial.fit(
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

    r_squared_linear = r_squared(y, linear_fit(x))
    r_squared_polynomial = r_squared(y, polynomial_fit(x))

    return linear_fit, polynomial_fit, r_squared_linear, r_squared_polynomial


# %%
def scale_engine_data_from_icao_emissions_database(
    path_excel_engine_data_icao_in: Path,
    path_excel_engine_data_icao_out: Path,
    scaling_polynomial: np.polynomial.Polynomial
) -> None:
    """_summary_

    _extended_summary_

    Parameters
    ----------
    path_excel_engine_data_icao_in : Path
        _description_
    path_excel_engine_data_icao_out : Path
        _description_
    scaling_polynomial : np.polynomial.Polynomial
        _description_
    """

    df_engines = pd.read_excel(
        io=path_excel_engine_data_icao_in,
        sheet_name='Gaseous Emissions and Smoke',
        engine='openpyxl',
    )
    df_engines = df_engines[
        [
            'Engine Identification',
            'Final Test Date',
            'Fuel Flow T/O (kg/sec)',
            'B/P Ratio',
            'Pressure Ratio',
            'Rated Thrust (kN)',
        ]
    ]
    df_engines = df_engines.dropna(how='any')

    # calculate TSFC(takeoff) from fuel flow and rated thrust
    df_engines['TSFC(takeoff)'] = df_engines['Fuel Flow T/O (kg/sec)'] / df_engines['Rated Thrust (kN)'] * 1000
    # calculate TSFC(cruise) from polynomial provided by function `determine_takeoff_to_cruise_tsfc_ratio()`
    df_engines['TSFC(cruise)'] = df_engines['TSFC(takeoff)'].apply(lambda x:scaling_polynomial(x))

    df_engines['Final Test Date']= df_engines['Final Test Date'].dt.strftime('%Y')

    df_engines.to_excel(
        excel_writer=path_excel_engine_data_icao_out,
        sheet_name='Data',
        engine='openpyxl',
    )

    return


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
