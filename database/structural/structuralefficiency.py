import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from database.tools import plot


def calculate(savefig, folder_path):

    # Load Data and Calculate Exit Limit/OEW
    aircrafts = pd.read_excel(r'Databank.xlsx')
    aircrafts['OEW/Exit Limit'] = aircrafts['OEW'] / aircrafts['Exit Limit']
    aircrafts['OEW/Pax'] = aircrafts['OEW'] / aircrafts['Pax']
    aircrafts['OEW/MTOW_2'] = aircrafts['OEW'] / aircrafts['MTOW']
    aircrafts['Composites'] = aircrafts['Composites'].fillna(0)
    aircrafts.to_excel(r'Databank.xlsx', index=False)

    # Get Exit Limit of the B777 for the NASA ERA Project
    oew_exit_b777 = aircrafts.loc[aircrafts['Name'] == '777-300/300ER/333ER', 'OEW/Exit Limit'].iloc[0]

    # Divide Aircrafts by Type.
    #aircrafts = aircrafts.dropna(subset=['OEW/Exit Limit', 'OEW/MTOW_2'])
    aircrafts = aircrafts.groupby(['Name','Type','YOI'], as_index=False).agg({'OEW/Exit Limit':'mean', 'OEW/MTOW_2':'mean', 'OEW':'mean', 'OEW/Pax':'mean'})
    medium_aircrafts = aircrafts.loc[(aircrafts['Type']=='Narrow')]
    large_aircrafts = aircrafts.loc[(aircrafts['Type']=='Wide')]
    regional_aircrafts = aircrafts.loc[(aircrafts['Type']=='Regional')]

    #Linear regression for all aircraft to see how overall structural efficiency has increased.
    x_large = large_aircrafts['YOI'].astype(np.int64)
    y_large = large_aircrafts['OEW/Exit Limit'].astype(np.float64)
    z_large = np.polyfit(x_large,  y_large, 1)
    p_large = np.poly1d(z_large)
    x_medium = medium_aircrafts['YOI'].astype(np.int64)
    y_medium = medium_aircrafts['OEW/Exit Limit'].astype(np.float64)
    z_medium = np.polyfit(x_medium,  y_medium, 1)
    p_medium = np.poly1d(z_medium)

    #_______PLOT OEW/MTOW VS OEW________

    fig = plt.figure(dpi=300)
    y_label = 'OEW/MTOW'
    x_label = 'OEW[kt]'

    # Add a subplot
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(large_aircrafts['OEW']/1000, large_aircrafts['OEW/MTOW_2'], marker='s',color='orange', label='Widebody')
    ax.scatter(medium_aircrafts['OEW']/1000, medium_aircrafts['OEW/MTOW_2'], marker='^',color='blue', label='Narrowbody')
    ax.scatter(regional_aircrafts['OEW']/1000, regional_aircrafts['OEW/MTOW_2'], marker='o',color='darkred', label='Regional Jets')
    ax.legend()
    plot.plot_layout(None, x_label, y_label, ax)
    if savefig:
        plt.savefig(folder_path+'\oewmtow_vs_oew.png')

    #_______PLOT OEW/EXITLIMIT WIDEBODY________

    fig = plt.figure(dpi=300)
    y_label = 'OEW[kg]/Pax Exit Limit'
    x_label = 'Aircraft Year of Introduction'

    # Add a subplot
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(large_aircrafts['YOI'], large_aircrafts['OEW/Exit Limit'], marker='s',color='orange', label='Widebody')
    ax.axhline(y=oew_exit_b777*0.8, color='black', linestyle='--', linewidth=2, label='Physical Limitation') # From NASA ERA
    ax.plot(x_large, p_large(x_large), color='orange')
    plt.annotate('NASA ERA Project', (1960, oew_exit_b777*0.8),
                    fontsize=6, xytext=(-10, 5),
                    textcoords='offset points')

    plt.xlim(1955, 2025)
    plt.xticks(np.arange(1955, 2024, 10))

    plot.plot_layout(None, x_label, y_label, ax)
    ax.legend()
    if savefig:
        plt.savefig(folder_path+'\widebody_aircrafts.png')

    #_______PLOT OEW/EXITLIMIT NARROWBODY________

    fig = plt.figure(dpi=300)

    # Add a subplot
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(regional_aircrafts['YOI'], regional_aircrafts['OEW/Exit Limit'], marker='o',color='darkred', label='Regional Jets')
    ax.scatter(medium_aircrafts['YOI'], medium_aircrafts['OEW/Exit Limit'], marker='^',color='blue', label='Narrowbody')
    ax.plot(x_medium, p_medium(x_medium), color='blue')

    ax.legend()
    plt.xlim(1955, 2025)
    plt.xticks(np.arange(1955, 2024, 10))

    xlabel = 'Aircraft Year of Introduction'
    ylabel = 'OEW[kg]/Pax Exit Limit'

    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'/narrowbodyaircrafts.png')

    #_______PLOT EXITLIMIT VS OEW________

    fig = plt.figure(dpi=300)

    # Add a subplot
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(large_aircrafts['OEW']/1000, large_aircrafts['OEW/Exit Limit'], marker='s',color='orange', label='Widebody')
    ax.scatter(medium_aircrafts['OEW']/1000, medium_aircrafts['OEW/Exit Limit'], marker='^',color='blue', label='Narrowbody')
    ax.scatter(regional_aircrafts['OEW']/1000, regional_aircrafts['OEW/Exit Limit'], marker='o',color='darkred', label='Regional Jets')
    ax.legend()

    # Set the x and y axis labels
    xlabel='OEW[kt]'
    ylabel='OEW[kg]/Pax Exit Limit'
    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'/exit_limit_vs_oew.png')

    #-------- PAX/OEW per YOI-----------------
    cm = 1 / 2.54  # for inches-cm conversion
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(large_aircrafts['YOI'], large_aircrafts['OEW/Exit Limit'], marker='s',color='orange', label='Widebody')
    ax.scatter(medium_aircrafts['YOI'], medium_aircrafts['OEW/Exit Limit'], marker='^',color='blue', label='Narrowbody')
    ax.scatter(regional_aircrafts['YOI'], regional_aircrafts['OEW/Exit Limit'], marker='o',color='darkred', label='Regional Jets')
    ax.plot(x_large, p_large(x_large), color='orange')
    ax.plot(x_medium, p_medium(x_medium), color='blue')
    plt.annotate('A330-900', (2018, 299), fontsize=8, xytext=(-20, -10), textcoords='offset points')
    plt.annotate('B787-10', (2018, 308), fontsize=8, xytext=(-20, 5), textcoords='offset points')

    ax.legend(loc='lower right')
    # Add a legend to the plot
    ax.legend()

    #Arrange plot size
    plt.ylim(0, 800)
    plt.xlim(1950, 2020)

    xlabel = 'Aircraft Year of Introduction'
    ylabel = 'OEW[kg]/Pax Exit Limit'
    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'/exit_limit_vs_year.png',  bbox_inches='tight')

    #_______PLOT PAX VS OEW________
    cm = 1 / 2.54  # for inches-cm conversion
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(large_aircrafts['YOI'], large_aircrafts['OEW/Pax'], marker='s',color='orange', label='Widebody')
    ax.scatter(medium_aircrafts['YOI'], medium_aircrafts['OEW/Pax'], marker='^',color='blue', label='Narrowbody')
    ax.scatter(regional_aircrafts['YOI'], regional_aircrafts['OEW/Pax'], marker='o',color='darkred', label='Regional Jets')
    ax.legend(loc='upper left')
    ax.legend()

    #Arrange plot size
    plt.ylim(0, 600)
    plt.xlim(1955, 2020)

    xlabel = 'Aircraft Year of Introduction'
    ylabel = 'OEW[kg]/Pax'
    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'/pax_vs_year.png', bbox_inches='tight')


