import pandas as pd
from test_env.database_creation.tools import plot
import matplotlib.pyplot as plt
import numpy as np

def calculate(savefig, folder_path):
    # Load SLF data
    slf = pd.read_excel(r"database\rawdata\USDOT\Traffic and Operations 1929-Present_Vollständige D_data.xlsx")
    slf = slf[['Year', 'PLF']]
    slf['PLF'] = slf['PLF'].str.replace(',', '.').astype(float)
    slf = slf[slf['Year'] >= 1958]

    # Load Aircraft Data and Calculate MJ/RPK
    data = pd.read_excel(r'Databank.xlsx')
    data = data.sort_values('YOI', ascending=True)
    data = data.drop(data.index[0])
    data = data.merge(slf, left_on='YOI', right_on='Year', how='left')
    data['EI (MJ/RPK)'] = data['EU (MJ/ASK)']/data['PLF']

    # Normalize Data for TSFC, L/D, OEW/Exit Limit and EU using 1959 as a Basis, for OEW normalize regarding heaviest value of each Type
    data['OEW/Exit Limit'] = data.groupby('Type')['OEW/Exit Limit'].transform(lambda x: x / x.max())
    data['OEW/Exit Limit'] = 100 / data['OEW/Exit Limit']
    data = data[['Name','YOI', 'TSFC Cruise','EI (MJ/RPK)', 'OEW/Exit Limit', 'L/D estimate']]
    data = data.dropna()
    data['OEW/Exit Limit'] = data['OEW/Exit Limit'] - 100

    max_tsfc = data.loc[data['YOI']==1958, 'TSFC Cruise'].iloc[0]
    data['TSFC Cruise'] = 100 / (data['TSFC Cruise'] / max_tsfc)
    data['TSFC Cruise'] = data['TSFC Cruise']-100

    max_eu = data.loc[data['YOI']==1958, 'EI (MJ/RPK)'].iloc[0]
    data['EI (MJ/RPK)'] = 100/ (data['EI (MJ/RPK)'] / max_eu)
    data['EI (MJ/RPK)'] = data['EI (MJ/RPK)'] - 100

    min_ld = data.loc[data['YOI']==1958, 'L/D estimate'].iloc[0]
    data['L/D estimate'] = 100 / (min_ld / data['L/D estimate'])
    data['L/D estimate'] = data['L/D estimate'] - 100

    # Groupby Aircraft by the release Year and take the following years for the IDA
    data = data[['Name','YOI', 'TSFC Cruise','EI (MJ/RPK)', 'OEW/Exit Limit', 'L/D estimate']]

    # Create Polynomial Regression
    years = np.arange(1958, 2022)
    x_all = data['YOI'].astype(np.int64)
    y_all = data['L/D estimate'].astype(np.float64)
    z_all = np.polyfit(x_all,  y_all, 4)
    p_all_ld = np.poly1d(z_all)

    y_all = data['OEW/Exit Limit'].astype(np.float64)
    z_all = np.polyfit(x_all,  y_all, 4)
    p_all_oew = np.poly1d(z_all)

    y_all = data['TSFC Cruise'].astype(np.float64)
    z_all = np.polyfit(x_all,  y_all, 4)
    p_all_tsfc = np.poly1d(z_all)

    y_all = data['EI (MJ/RPK)'].astype(np.float64)
    z_all = np.polyfit(x_all,  y_all, 6)
    p_all_eu = np.poly1d(z_all)

    slf['PLF'] = (100*slf['PLF'] / slf['PLF'].iloc[0]) -100

    # Plot Scatterpoint for the Aircraft and the Polynomials
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)
    x_label = 'Aircraft Year of Introduction'
    y_label = 'Efficiency Improvements [\%]'

    ax.scatter(data['YOI'], data['EI (MJ/RPK)'],color='black', label='Overall (MJ/RPK)')
    ax.scatter(slf['Year'], slf['PLF'], color='blue', label='Operational (SLF (1959 normalized))')
    ax.scatter(data['YOI'], data['L/D estimate'],color='royalblue', label='Aerodynamic (L/D)')
    ax.scatter(data['YOI'], data['OEW/Exit Limit'],color='steelblue', label='Structural (OEW/Exit)')
    ax.scatter(data['YOI'], data['TSFC Cruise'],color='lightblue', label='Engine (TSFC)')

    ax.plot(years, p_all_tsfc(years),color='lightblue')
    ax.plot(years, p_all_eu(years),color='black')
    ax.plot(years, p_all_oew(years),color='steelblue')
    ax.plot(years, p_all_ld(years), color='royalblue')
    ax.plot(slf['Year'], slf['PLF'], color='blue')

    # Add a legend to the plot
    ax.legend()
    plt.xlim(1955, 2025)
    plt.ylim(-30, 500)
    plot.plot_layout(None, x_label, y_label, ax)
    if savefig:
        plt.savefig(folder_path+'/ida_operational_normalized.png')

    # Evaluate the polynomials for the x values
    p_all_tsfc_values = p_all_tsfc(years) + 100
    p_all_oew_values = p_all_oew(years) + 100
    p_all_ld_values = p_all_ld(years) + 100
    p_all_eu_values = p_all_eu(years) + 100
    p_all_slf = slf['PLF'] + 100

    # Create a dictionary with the polynomial values
    data = {
        'YOI': years,
        'TSFC Cruise': p_all_tsfc_values,
        'OEW/Exit Limit': p_all_oew_values,
        'L/D estimate': p_all_ld_values,
        'EU (MJ/ASK)': p_all_eu_values,
        'SLF': p_all_slf
    }

    # Create the DataFrame
    data = pd.DataFrame(data)

    # Use LMDI Method
    data['LMDI'] = (data['EU (MJ/ASK)'] - data['EU (MJ/ASK)'].iloc[0]) / (np.log(data['EU (MJ/ASK)']) - np.log(data['EU (MJ/ASK)'].iloc[0]))
    data['Engine_LMDI'] = np.log(data['TSFC Cruise'] / data['TSFC Cruise'].iloc[0])
    data['Aerodyn_LMDI'] = np.log(data['L/D estimate'] / data['L/D estimate'].iloc[0])
    data['Structural_LMDI'] = np.log(data['OEW/Exit Limit'] / data['OEW/Exit Limit'].iloc[0])
    data['SLF_LMDI'] = np.log(data['SLF'] / data['SLF'].iloc[0])
    data['deltaC_Aerodyn_Ops'] = data['LMDI'] * data['Aerodyn_LMDI']
    data['deltaC_Engine_Ops'] = data['LMDI'] * data['Engine_LMDI']
    data['deltaC_Structural_Ops'] = data['LMDI'] * data['Structural_LMDI']
    data['deltaC_SLF_Ops'] = data['LMDI'] * data['SLF_LMDI']
    data['deltaC_Tot_Ops'] = data['EU (MJ/ASK)'] - data['EU (MJ/ASK)'].iloc[0]
    data['deltaC_Res_Ops'] = data['deltaC_Tot_Ops'] - data['deltaC_Aerodyn_Ops'] - data['deltaC_Engine_Ops'] - data['deltaC_Structural_Ops']- data['deltaC_SLF_Ops']

    # Get percentage increase of each efficiency and drop first row which only contains NaN
    data = data[['YOI', 'deltaC_Structural_Ops', 'deltaC_Engine_Ops', 'deltaC_Aerodyn_Ops', 'deltaC_SLF_Ops','deltaC_Res_Ops', 'deltaC_Tot_Ops']]
    dashboard = pd.read_excel(r'dashboard\data\Dashboard.xlsx')
    data = data.drop(data.index[0])
    dashboard = dashboard.merge(data, on='YOI')
    dashboard.to_excel(r'dashboard\data\Dashboard.xlsx', index=False)
    data = data.set_index('YOI')

    # Set the width of each group and create new indexes just the set the space right
    data = data[['deltaC_Tot_Ops', 'deltaC_SLF_Ops','deltaC_Engine_Ops', 'deltaC_Aerodyn_Ops', 'deltaC_Structural_Ops', 'deltaC_Res_Ops']]

    # Reorder the columns
    column_order = ['deltaC_Tot_Ops','deltaC_SLF_Ops', 'deltaC_Aerodyn_Ops', 'deltaC_Structural_Ops', 'deltaC_Engine_Ops', 'deltaC_Res_Ops']
    data = data[column_order]

    # Create new Labels
    labels = ['Overall Eff. (baseline MJ/RPK(1960))','Operational (SLF)', 'Aerodynamic (L/D)','Structural (OEW/Exit)','Engine (TSFC)', 'Residual' ]

    # Create subplots for each column
    cm = 1 / 2.54  # for inches-cm conversion
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    # Plot stacked areas for other columns
    data_positive = data.drop('deltaC_Tot_Ops', axis=1).clip(lower=0)
    data_negative = data.drop('deltaC_Tot_Ops', axis=1).clip(upper=0)
    # Create arrays for stacking the areas
    positive_stack = np.zeros(len(data))
    negative_stack = np.zeros(len(data))

    # Plot overall efficiency as a line
    overall_efficiency = data['deltaC_Tot_Ops']
    ax.plot(data.index, overall_efficiency, color='black', label=labels[0], linewidth= 3)

    # Plot Subefficiencies
    colors = ['blue', 'royalblue', 'steelblue', 'lightblue', 'red']
    for i, column in enumerate(data_positive.columns):
        ax.fill_between(data.index, positive_stack, positive_stack + data_positive.iloc[:, i], color=colors[i],
                        label=labels[i + 1], linewidth=0)
        positive_stack += data_positive.iloc[:, i]
    for i, column in enumerate(data_negative.columns):
        ax.fill_between(data.index, negative_stack, negative_stack + data_negative.iloc[:, i], color=colors[i], linewidth=0)
        negative_stack += data_negative.iloc[:, i]

    xlabel = 'Year'
    ylabel = 'Efficiency Improvements [\%]'
    ax.set_xlim(1958, 2020)
    ax.set_ylim(-50, 500)

    ax.legend(loc='upper left')
    plot.plot_layout(None, xlabel, ylabel, ax)

    if savefig:
        plt.savefig(folder_path+'/ida_operational.png')



