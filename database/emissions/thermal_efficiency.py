import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from database.tools import plot

def calculate(savefig, folder_path, temp):

    # Parameters
    T1 = temp  # Kelvin, Air Temperature in Altitude
    T3_NOx = 2000  # Max Temp in Kelvin regarding NOx emissions
    T3s = np.linspace(1000, 2600, 1600)
    gamma = 1.4  # Isentropic Coefficient
    R = 287  # Gas Constant
    eta_c = 0.9  # Compressor Efficiency
    eta_t = 0.9  # Turbine Efficiency
    cp = R * gamma / (gamma - 1)
    pressure_ratios = np.linspace(10, 100, 90)

    results = []

    # For loops to create all combinations of values
    for pressure_ratio in pressure_ratios:
        for T3 in T3s:
            T2_s = T1 * (pressure_ratio) ** ((gamma - 1) / gamma)
            T2 = (T2_s - T1) / eta_c + T1
            T4_s = T3 * (1 / pressure_ratio) ** ((gamma - 1) / gamma)
            T4 = T3 - (T3 - T4_s) * eta_t
            T4_NOx_s = T3_NOx * (1 / pressure_ratio) ** ((gamma - 1) / gamma)
            T4_NOx = T3_NOx - (T3_NOx - T4_NOx_s) * eta_t
            heat = cp * ((T3 - T4) - (T2 - T1))
            heat_NOx = cp * ((T3_NOx - T4_NOx) - (T2 - T1))
            work = cp * (T3 - T2)
            work_NOx = cp * (T3_NOx - T2)

            thermal_eff = heat / work
            thermal_eff_NOx = heat_NOx / work_NOx

            results.append({'Burner Exit Temperature': T3,'Pressure Ratio': pressure_ratio, 'Thermal Efficiency': thermal_eff, 'NOx Thermal Efficiency': thermal_eff_NOx})

    df = pd.DataFrame(results)

    # Reshape data for heatmap
    efficiency_heatmap = df.pivot('Burner Exit Temperature', 'Pressure Ratio', 'Thermal Efficiency')
    efficiency_heatmap = efficiency_heatmap.mask(efficiency_heatmap < 0.4)

    # Transpose Data
    data = efficiency_heatmap.T

    # Create a figure and axes
    fig, ax = plt.subplots(dpi=300)

    # Plot the array as a heatmap using imshow
    im = ax.imshow(data[::-1], cmap='viridis', aspect='auto', vmin=0.4, vmax=0.625)
    contours = plt.contour(data[::-1], colors='black', linestyles='dashed', levels=10)
    plt.clabel(contours, inline=True, fontsize=10)
    plt.colorbar(im, label='Thermal Efficiency [\%]')

    ylabel ='Pressure Ratio'
    xlabel = 'Burner Exit Temperature [K]'


    # Use arbitrary Ticks
    new_xticks = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600]
    new_xlabels = ['1000', '1200', '1400','1600','1800','2000', '2200', '2400', '2600']
    plt.xticks(new_xticks, new_xlabels)

    new_yticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    new_ylabels = ['100', '90', '80','70','60','50', '40', '30', '20', '10']
    plt.yticks(new_yticks, new_ylabels)

    # Add Limit Lines
    ax.vlines(1000,0,90, color='black', label=r'\textbf{Temp NOx Limit}', linewidth=1.5)
    ax.vlines(1600,0,90, color='black', label=r'\textbf{Stoichiometric Limit}', linewidth=1.5)
    ax.text(1040, 45, r'\textbf{Temp NOx Limit}',rotation=90, horizontalalignment='center', verticalalignment='center',  weight='bold')
    ax.text(1640, 45, r'\textbf{Stoichiometric Limit}',rotation=90,  horizontalalignment='center', verticalalignment='center',  weight='bold')

    plot.plot_layout(None, xlabel, ylabel, ax)
    ax.set_title(r'With $\eta_{Compressor}$ and $\eta_{Turbine}$ = 0.9', loc='left')
    if savefig:
        plt.savefig(folder_path + '/thermal_efficiency_limitation.png')


    # Same with a intercooling

    # Parameters
    T1 = 233  # Kelvin, Air Temperature in Altitude
    T3 = 320
    T5_NOx = 2000  # Max Temp in Kelvin regarding NOx emissions
    T5s = np.linspace(1000, 2600, 1600)
    gamma = 1.4  # Isentropic Coefficient
    R = 287  # Gas Constant
    eta_c = 0.9  # Compressor Efficiency
    eta_t = 0.9  # Turbine Efficiency
    cp = R * gamma / (gamma - 1)
    pressure_ratios = np.linspace(2, 20, 90)

    results = []

    # For loops to create all combinations of values
    for pressure_ratio in pressure_ratios:
        for T5 in T5s:
            T2_s = T1 * 5 ** ((gamma - 1) / gamma)
            T2 = (T2_s - T1) / eta_c + T1
            T4_s = T3 * (pressure_ratio) ** ((gamma - 1) / gamma)
            T4 = T3 - (T3 - T4_s) * eta_c
            T6_s = T5 * (1 / (5*pressure_ratio)) ** ((gamma - 1) / gamma)
            T6 = T5 - (T5 - T6_s) * eta_c
            T6_NOx_s = T5_NOx * (1 / (5 * pressure_ratio)) ** ((gamma - 1) / gamma)
            T6_NOx = T5_NOx - (T5_NOx - T6_NOx_s) * eta_c

            heat = cp * ((T5 - T6) - (T4 - T3) - (T2 - T1))
            heat_NOx = cp * ((T5_NOx - T6_NOx) - (T4 - T3) - (T2 - T1))
            work = cp * (T5 - T4)
            work_NOx = cp * (T5_NOx - T4)

            thermal_eff = heat / work
            thermal_eff_NOx = heat_NOx / work_NOx

            results.append({'Burner Exit Temperature': T5,'Pressure Ratio': pressure_ratio, 'Thermal Efficiency': thermal_eff, 'NOx Thermal Efficiency': thermal_eff_NOx})

    df = pd.DataFrame(results)

    # Reshape data for heatmap
    efficiency_heatmap = df.pivot('Burner Exit Temperature', 'Pressure Ratio', 'Thermal Efficiency')
    efficiency_heatmap = efficiency_heatmap.mask(efficiency_heatmap < 0.4)

    # Transpose Data
    data = efficiency_heatmap.T

    # Create a figure and axes
    fig, ax = plt.subplots(dpi=300)

    # Plot the array as a heatmap using imshow
    im = ax.imshow(data[::-1], cmap='viridis', aspect='auto', vmin=0.4, vmax=0.625)
    contours = plt.contour(data[::-1], colors='black', linestyles='dashed', levels=10)
    plt.clabel(contours, inline=True, fontsize=10)
    plt.colorbar(im, label='Thermal Efficiency [\%]')

    ylabel ='Pressure Ratio'
    xlabel = 'Burner Exit Temperature [K]'


    # Use arbitrary Ticks
    new_xticks = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600]
    new_xlabels = ['1000', '1200', '1400','1600','1800','2000', '2200', '2400', '2600']
    plt.xticks(new_xticks, new_xlabels)

    new_yticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    new_ylabels = ['100', '90', '80','70','60','50', '40', '30', '20', '10']
    plt.yticks(new_yticks, new_ylabels)

    # Add Limit Lines
    ax.vlines(1000,0,90, color='black', label=r'\textbf{Temp NOx Limit}', linewidth=1.5)
    ax.vlines(1600,0,90, color='black', label=r'\textbf{Stoichiometric Limit}', linewidth=1.5)
    ax.text(1040, 45, r'\textbf{Temp NOx Limit}',rotation=90, horizontalalignment='center', verticalalignment='center',  weight='bold')
    ax.text(1640, 45, r'\textbf{Stoichiometric Limit}',rotation=90,  horizontalalignment='center', verticalalignment='center',  weight='bold')

    plot.plot_layout(None, xlabel, ylabel, ax)

    # Assumptions made: T3 = 300 K , Pressure Ratio P2/P1 = 5 and P4/P3 is in a range from 2 to 20
    ax.set_title(r'With $\eta_{Compressor}$ and $\eta_{Turbine}$ = 0.9', loc='left')
    if savefig:
        plt.savefig(folder_path + '/thermal_efficiency_limitation_intercooler.png')




