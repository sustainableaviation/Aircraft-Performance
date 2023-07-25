import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from test_env.database_creation.tools import plot


def calculate(savefig, flight_speed, folder_path):

    # Load data
    data = pd.read_excel(r'Databank.xlsx')

    # Calculate Prop Eff.
    data['Overcome Thrust'] = data['Engine Efficiency']*data['Fuel Flow [kg/s]']*43.6*10**6/flight_speed
    data['prop_eff'] = 2 * flight_speed / (data['Overcome Thrust'] / (data['Air Mass Flow [kg/s]'] * data['engineCount']) + 2 * flight_speed)
    data['f'] = data['Fuel Flow [kg/s]']/data['Air Mass Flow [kg/s]']

    # Calculate Thermal Eff. Formula only valid for turbofan engines with BPR larger than 2
    data['thermal_eff'] = data['Engine Efficiency']/data['prop_eff']
    data.loc[data['B/P Ratio']<=2, 'thermal_eff'] = np.nan
    data.loc[data['B/P Ratio']<=2, 'prop_eff'] = np.nan

    data.to_excel(r'Databank.xlsx', index=False)

    # Prepare DF for plotting
    data = data.dropna(subset='thermal_eff')
    data = data.loc[data['Type']!='Regional']
    data = data.groupby(['Engine Identification', 'YOI'], as_index=False).agg({'thermal_eff':'mean', 'prop_eff':'mean', 'Engine Efficiency':'mean'})

    # Colormap for years
    column_data = pd.to_numeric(data['YOI'])
    norm = mcolors.Normalize(vmin=column_data.min(), vmax=column_data.max())
    norm_column_data = norm(column_data)
    cmap = plt.colormaps.get_cmap('cool')
    colors = cmap(norm_column_data)

    # ---------PLOT PROP vs THERMAL EFF. -------------
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(data['prop_eff'], data['thermal_eff'], marker='o', c=colors)

    ellipse2 = Ellipse((0.85, 0.48), 0.04, 0.03, color='darkred', fill=False)
    ax.text(0.85, 0.48, 'Future HBR Engines', horizontalalignment='center', verticalalignment='center')
    ellipse3 = Ellipse((0.91, 0.5), 0.03, 0.05, color='r', fill=False)
    ax.text(0.91, 0.5, 'Future Open Rotor Engines', horizontalalignment='center', verticalalignment='center')

    ax.add_artist(ellipse2)
    ax.add_artist(ellipse3)
    ax.vlines(0.925,0.4,0.65, color='b', label='Theoretical Limit')
    ax.hlines(0.55,0.7,1, color='r', label='Practical Limit NOx', linestyles='--')
    ax.hlines(0.6,0.7,1, color='r', label='Theoretical Limit')

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm).set_label('Aircraft Year of Introduction')
    ax.legend(loc='upper left')
    xlabel = 'Propulsive Efficiency [\%]'
    ylabel = 'Thermal Efficiency [\%]'
    plt.ylim(0.4, 0.65)
    plt.xlim(0.7, 1)

    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'/engine_subefficiency.png')


