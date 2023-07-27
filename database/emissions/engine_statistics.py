import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from database.tools import plot
import matplotlib.colors as mcolors

def calculate(savefig, folder_path):

    # Load Engine Data and Aircraft Databank
    data = pd.read_excel(r'database\rawdata\emissions\all_engines_for_calibration_years.xlsx', skiprows=range(2), header=3, usecols='A,B,C,D,E,F')
    data = data.groupby(['Engine'], as_index=False).agg(
        {'Engine TSFC cruise [g/kNs]': 'mean', 'Engine TSFC take off [g/kNs]': 'mean', 'Release year': 'mean', 'Application Date':'mean'})
    emissions_df = pd.read_excel(r'Databank.xlsx')
    emissions_df = emissions_df[['Dry weight,integer,kilogram',
                                 'Fan diameter,float,metre',
                                 'Engine Identification',
                                 'TSFC Cruise',
                                 'TSFC T/O',
                                 'Overall pressure ratio,float,None',
                                 'B/P Ratio',
                                 'Pressure Ratio',
                                 'Engine Efficiency',
                                 'Name',
                                 'YOI']]
    # Get all Aircraft-Engine Combinations
    emissions_df = emissions_df.groupby(['YOI','Name', 'Engine Identification' ], as_index=False).mean()

    # Get the First Appearance of an Engine in a Commercial Aircraft
    yearly_emissions = emissions_df.groupby(['Engine Identification', 'Dry weight,integer,kilogram',
       'Fan diameter,float,metre', 'TSFC Cruise','TSFC T/O', 'B/P Ratio',
       'Pressure Ratio', 'Engine Efficiency', 'Overall pressure ratio,float,None'], as_index=False).agg({'YOI':'min'})

    # Create Colorspectrum for First Engine Appearance in Commercial Aircraft and the ICAO Testdate
    years = yearly_emissions['YOI']
    years2 = data['Application Date']

    column_data1 = pd.to_numeric(years, errors='coerce')
    column_data2 = pd.to_numeric(years2, errors='coerce')
    norm = mcolors.Normalize(vmin=1959, vmax=2000)
    norm_column_data1 = norm(column_data1)
    norm_column_data2 = norm(column_data2)
    # create a colormap and map normalized values to colors
    cmap = plt.colormaps.get_cmap('viridis')
    colors = cmap(norm_column_data1)
    colors2 = cmap(norm_column_data2)

    #-------------------Plot Weight vs Diameter-------------------------
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)
    x = yearly_emissions['Fan diameter,float,metre']
    y = yearly_emissions['Dry weight,integer,kilogram']/1000

    ax.scatter(x, y, c=colors)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm).set_label('Aircraft Release Year')
    xlabel = 'Fan Diameter [m]'
    ylabel = 'Engine Dry Weight [t]'
    plt.ylim(0, 10)
    plt.xlim(0.5, 3.5)

    # Plot y = x^2
    x = np.linspace(0,3.5, 50)
    y = x**2
    ax.plot(x, y, label='$y = x^2$', color='black')
    ax.legend()

    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'\weight_vs_diameter.png')

    #-------------------T/O vs Cruise TSFC-------------------------
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    x = data['Engine TSFC take off [g/kNs]']
    y = data['Engine TSFC cruise [g/kNs]']

    # Linear Regression
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    span = pd.Series(np.arange(7,19,0.2))

    # Calculate R-Squared
    y_mean = np.mean(y)
    tss = np.sum((y - y_mean)**2)
    y_pred = p(x)
    rss = np.sum((y - y_pred)**2)
    r_squared = 1 - (rss / tss)
    r_squared = r_squared.round(2)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm).set_label('Engine Year of Certification')
    ax.scatter(x, y, c=colors2, zorder=2)
    ax.plot(span, p(span),color='black', linewidth=2)
    equation_text = r'$y = {:.2f}x + {:.2f}$, $R^2 = {:.2f}$'.format(z[0], z[1], r_squared)

    #Polynom obtained by Lee et al. was 0.869x + 8.65 for comparison
    ax.text(0.30,0.15, equation_text, fontsize=12, color='black', transform=fig.transFigure)
    xlabel = 'Take-Off TSFC [g/kNs]'
    ylabel = 'Cruise TSFC  [g/kNs]'
    plt.ylim(14, 24)
    plt.xlim(6, 20)
    plot.plot_layout(None, xlabel, ylabel, ax)

    if savefig:
        plt.savefig(folder_path+'\icao_to_tsfc_vs_years.png')

    #------------- BYPASS RATIO vs Pressure Ratio --------------------
    # Note the only geared engine (PW1100 Series does not have the Pressure Ratio given, therefore not appearing in the Plot.
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    y = yearly_emissions['Overall pressure ratio,float,None']
    x = yearly_emissions['B/P Ratio']

    ax.scatter(x,y,c=colors)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm).set_label('Aircraft Year of Introduction')

    ylabel = 'Pressure Ratio'
    xlabel = 'Bypass Ratio'
    plt.ylim(10, 60)
    plt.xlim(0, 13)
    plot.plot_layout(None, xlabel, ylabel, ax)

    if savefig:
        plt.savefig(folder_path+'/bypass_vs_pressure_ratio.png')

    #-------------- BYPASS RATIO vs Weight--------------
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    y = yearly_emissions['Fan diameter,float,metre']
    x = yearly_emissions['B/P Ratio']

    ax.scatter(x, y, c=colors, marker='o')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm).set_label('Aircraft Year of Introduction')

    ylabel = 'Fan Diameter [m]'
    xlabel = 'Bypass Ratio'
    plt.xlim(0, 13)
    plt.ylim(0, 4)
    plot.plot_layout(None, xlabel, ylabel, ax)

    if savefig:
        plt.savefig(folder_path+'/bypass_vs_dia.png')
