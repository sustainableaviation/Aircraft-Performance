import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from test_env.database_creation.tools import plot
def calculate(savefig, folder_path, vel, air_density):

    # Parameters
    thrusts = np.linspace(0, 200000, 200)
    fan_diameters = np.linspace(1, 5, 80)
    engine_count= 2

    results = []
    # Calculate Propelsive Eff. for all combinations of thrust and Diameter
    for thrust in thrusts:
        for fan_diameter in fan_diameters:
            fan_area = (math.pi*fan_diameter**2)/4
            air_mass_flow = air_density * fan_area * vel
            prop_eff = 2*vel/((thrust/(engine_count*air_mass_flow)+2*vel))

            results.append({'Thrust': thrust,'Fan Diameter': fan_diameter, 'Propulsive Efficiency': prop_eff})

    df = pd.DataFrame(results)

    # Reshape data for heatmap
    efficiency_heatmap = df.pivot('Thrust', 'Fan Diameter', 'Propulsive Efficiency')
    efficiency_heatmap = efficiency_heatmap.T
    efficiency_heatmap = efficiency_heatmap.mask(efficiency_heatmap < 0.6)

    # Create a figure and axes
    fig, ax = plt.subplots(dpi=300)

    # Plot the array as a heatmap using imshow
    im = ax.imshow(efficiency_heatmap[::-1], cmap='viridis', aspect='auto')
    contours = plt.contour(efficiency_heatmap[::-1], colors='black', linestyles='dashed', levels=10)
    plt.clabel(contours, inline=True, fontsize=10)
    plt.colorbar(im, label='Propulsive Efficiency [\%]')

    # Set x and y labels
    ylabel='Fan Diameter [m]'
    xlabel='Thrust [kN]'

    # Add arbitrary ticks
    new_xticks = [0, 50, 100, 150, 200]
    new_xlabels = ['0', '50', '100','150','200']
    plt.xticks(new_xticks, new_xlabels)

    new_yticks = [0, 20, 40, 60, 80]
    new_ylabels = ['5','4', '3', '2', '1']
    plt.yticks(new_yticks, new_ylabels)

    # Add Lines and Text for some Examples
    ax.hlines(69, 0, 200, color='black', label='CFM56-7 Series', linewidth=1.5)
    ax.hlines(43, 0, 200, color='black', label='PW4090', linewidth=1.5)
    ax.hlines(10, 0, 200, color='black', label='Open Rotor', linewidth=1.5)
    ax.vlines(166.95,0,80, color='black', label='Boeing 777-300', linewidth=1.5)
    ax.vlines(54.584, 0, 80, color='black', label='Boeing 737-800', linewidth=1.5)
    ax.text(166.95, 82, 'Boeing 777-300', horizontalalignment='center', verticalalignment='center')
    ax.text(54.585, 82, 'Boeing 737-800', horizontalalignment='center', verticalalignment='center')
    ax.text(2, 67, 'CFM56-7B Series', horizontalalignment='left', verticalalignment='center')
    ax.text(2, 41, 'PW4090', horizontalalignment='left', verticalalignment='center')
    ax.text(2, 8, 'Open Rotor', horizontalalignment='left', verticalalignment='center')
    plot.plot_layout(None, xlabel, ylabel, ax)
    ax.set_title(r'Commercial Aircraft with 2 Turbofan Engines', loc = 'center')
    if savefig:
        plt.savefig(folder_path + '/prop_efficiency_limitation.png')

