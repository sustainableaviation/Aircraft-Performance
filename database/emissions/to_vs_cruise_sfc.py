import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from database.tools import plot


def calibrate(savefig, folder_path):

    # Read Data
    data = pd.read_excel(r'database\rawdata\emissions\all_engines_for_calibration_years.xlsx', skiprows=range(2), header=3, usecols='A,B,C,D,E,F')
    all = data.groupby(['Engine'], as_index=False).agg({'Engine TSFC cruise [g/kNs]':'mean','Engine TSFC take off [g/kNs]':'mean', 'Release year':'mean'})

    #-------------------PLOT TAKE OFF vs CRUISE-------------------------
    y_all = all['Engine TSFC cruise [g/kNs]']
    x_all = all['Engine TSFC take off [g/kNs]']

    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    # Make a Linear Regression
    z_all = np.polyfit(x_all, y_all, 1)
    p_all = np.poly1d(z_all)
    span = pd.Series(np.arange(8,19,0.2))

    # Calculate R-Squared
    y_mean = np.mean(y_all)
    tss = np.sum((y_all - y_mean)**2)
    y_pred = p_all(x_all)
    rss = np.sum((y_all - y_pred)**2)
    r_squared = 1 - (rss / tss)
    r_squared = r_squared.round(2)

    ax.scatter(x_all, y_all, marker='o', color='black', label='Turbofan Engines',zorder=2)
    ax.plot(span, p_all(span),color='black', label='Linear Regression', linewidth=2)

    # Add Text to the Plot
    equation_text = f'y = {z_all[0]:.2f}x + {z_all[1]:.2f} , R-squared = {r_squared}'
    ax.text(0.4,0.15, equation_text, fontsize=12, color='black', transform=fig.transFigure)
    ax.legend(loc='upper left')

    #Arrange plot size
    plt.ylim(15, 25)
    plt.xlim(6, 20)
    plt.xticks(np.arange(6, 19, 2))

    title = 'TSFC Calibration'
    xlabel = 'Take-Off TSFC [g/kNs]'
    ylabel = 'Cruise TSFC [g/kNs]'
    plot.plot_layout(title, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+ '/takeoff_vs_cruise_tsfc_second_order.png')
    print(' --> [TSFC CALIBRATION]: Cruise TFSC = ' + str(round(z_all[0], 3))+'*Take-Off TFSC'+ ' + '+str(round(z_all[1], 3)))

    # Return the obtained Polynom
    return(z_all)


