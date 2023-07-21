import pandas as pd
from test_env.database_creation.tools import plot
import matplotlib.pyplot as plt
import numpy as np
# Probably Delete this code, does not seem useful

def calculate(savefig, folder_path):
    # Prepare data and normalize
    data = pd.read_excel(r'Databank.xlsx')
    data = data.sort_values('YOI', ascending=True)
    data = data.loc[data['Type']!='Regional']
    data = data[['Name','YOI','Engine Efficiency', 'prop_eff', 'thermal_eff']]
    data = data.dropna()

    # Normalize Efficiency Improvements
    therm = data.loc[data['YOI']==1970, 'thermal_eff'].iloc[0]
    data['thermal_eff'] = (100 / (data['thermal_eff'] / therm))-100
    data['thermal_eff'] = -1 * data['thermal_eff']

    prop = data.loc[data['YOI']==1970, 'prop_eff'].iloc[0]
    data['prop_eff'] = (100 / (data['prop_eff'] / prop))-100
    data['prop_eff'] = -1 * data['prop_eff']

    engine = data.loc[data['YOI']==1970, 'Engine Efficiency'].iloc[0]
    data['Engine Efficiency'] = (100 / (data['Engine Efficiency'] / engine))-100
    data['Engine Efficiency'] = -1 * data['Engine Efficiency']

    # Create Polynomials
    years = np.arange(1970, 2021)
    x_all = data['YOI'].astype(np.int64)
    y_all = data['thermal_eff'].astype(np.float64)
    z_all = np.polyfit(x_all,  y_all, 4)
    p_all_thermal = np.poly1d(z_all)

    y_all = data['prop_eff'].astype(np.float64)
    z_all = np.polyfit(x_all,  y_all, 4)
    p_all_prop = np.poly1d(z_all)

    y_all = data['Engine Efficiency'].astype(np.float64)
    z_all = np.polyfit(x_all,  y_all, 4)
    p_all_engine = np.poly1d(z_all)

    # Plot Engines and Polynomials
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)
    x_label = 'Aircraft Year of Introduction'
    y_label = 'Efficiency Improvements [\%]'

    ax.scatter(data['YOI'], data['Engine Efficiency'],color='black', label='Overall Efficiency')
    ax.scatter(data['YOI'], data['thermal_eff'],color='turquoise', label='Thermal Efficiency')
    ax.scatter(data['YOI'], data['prop_eff'],color='orange', label='Propulsive Efficiency')

    ax.plot(years, p_all_engine(years),color='black')
    ax.plot(years, p_all_thermal(years),color='turquoise')
    ax.plot(years, p_all_prop(years),color='orange')

    # Add a legend to the plot
    ax.legend()
    plt.xlim(1970, 2020)
    plt.ylim(-20, 20)
    plot.plot_layout(None, x_label, y_label, ax)
    if savefig:
        plt.savefig(folder_path+'/ida_engine_normalized.png')

    # Evaluate the polynomials for the x values
    p_all_engine_values = p_all_engine(years) + 100
    p_all_prop_values = p_all_prop(years) + 100
    p_all_thermal_values = p_all_thermal(years) + 100

    # Create a dictionary with the polynomial values
    data = {
        'YOI': years,
        'Overall Efficiency': p_all_engine_values,
        'Propulsive Efficiency': p_all_prop_values,
        'Thermal Efficiency': p_all_thermal_values,
    }
    # Create the DataFrame
    data = pd.DataFrame(data)

    # Use LMDI Method
    data['LMDI'] = (data['Overall Efficiency'] - data['Overall Efficiency'].iloc[0]) / (np.log(data['Overall Efficiency']) - np.log(data['Overall Efficiency'].iloc[0]))
    data['Thermal_LMDI'] = np.log(data['Thermal Efficiency'] / data['Thermal Efficiency'].iloc[0])
    data['Prop_LMDI'] = np.log(data['Propulsive Efficiency'] / data['Propulsive Efficiency'].iloc[0])
    data['deltaC_thermal'] = data['LMDI'] * data['Thermal_LMDI']
    data['deltaC_prop'] = data['LMDI'] * data['Prop_LMDI']
    data['deltaC_Tot'] = data['Overall Efficiency'] - data['Overall Efficiency'].iloc[0]
    data['deltaC_Res'] = data['deltaC_Tot'] - data['deltaC_thermal'] - data['deltaC_prop']

    # Get percentage increase of each efficiency and drop first row which only contains NaN
    data = data[['YOI',  'deltaC_Tot', 'deltaC_Res', 'deltaC_thermal', 'deltaC_prop']]
    data = data.drop(0)
    data = data.set_index('YOI')

    columns = data.columns
    group_width = 1.3
    num_columns = len(data.columns)

    # Create new Labels
    labels = ['Overall Efficiency', 'Residual', 'Thermal Efficiency', 'Propulsive Efficiency']

    # Create subplots for each column
    fig, ax = plt.subplots(dpi=300)

    # Plot stacked areas for other columns
    data_positive = data.drop('deltaC_Tot', axis=1).clip(lower=0)
    data_negative = data.drop('deltaC_Tot', axis=1).clip(upper=0)
    data_negative = data_negative.loc[:, (data_negative != 0).any(axis=0)]
    # Create arrays for stacking the areas
    positive_stack = np.zeros(len(data))
    negative_stack = np.zeros(len(data))

    colors = ['royalblue', 'steelblue', 'lightblue']
    for i, column in enumerate(data_positive.columns):
        ax.fill_between(data.index, positive_stack, positive_stack + data_positive.iloc[:, i], color=colors[i],
                        label=labels[i + 1])
        positive_stack += data_positive.iloc[:, i]
    for i, column in enumerate(data_negative.columns):
        ax.fill_between(data.index, negative_stack, negative_stack + data_negative.iloc[:, i], color=colors[i], linewidth=0)
        negative_stack += data_negative.iloc[:, i]

    # Plot overall efficiency as a line
    overall_efficiency = data['deltaC_Tot']
    ax.plot(data.index, overall_efficiency, color='black', label=labels[0], linewidth= 3)
    xlabel = 'Year'
    ylabel = 'Efficiency Improvements [\%]'
    ax.set_xlim(1970, 2020)
    ax.set_ylim(-5, 20)
    ax.legend(loc='upper left')
    plot.plot_layout(None, xlabel, ylabel, ax)

    if savefig:
        plt.savefig(folder_path+'/ida_engine.png')