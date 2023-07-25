import pandas as pd
from test_env.database_creation.tools import dict, plot
import matplotlib.pyplot as plt
import numpy as np

def calculate(savefig, folder_path):

    # Load Dictionaries
    airplanes_dict = dict.AirplaneModels().get_models()
    airplanes = airplanes_dict.keys()

    # Load Data for 2022
    AC_types = pd.read_csv(r"database_creation\rawdata\USDOT\L_AIRCRAFT_TYPE (1).csv")
    T100 = pd.read_csv(r"database_creation\rawdata\USDOT\T_T100_SEGMENT_ALL_CARRIER_2022.csv")

    # Use the 19 Airlines
    T100 = pd.merge(T100, AC_types, left_on='AIRCRAFT_TYPE', right_on='Code')
    T100 = T100.loc[T100['Description'].isin(airplanes)]
    T100 = T100.loc[T100['AIR_TIME'] > 0]
    T100["DISTANCE"] = T100["DISTANCE"] * 1.62
    T100["PAYLOAD"] = T100["PAYLOAD"] * 0.4535
    T100["PAYLOAD"] = T100["PAYLOAD"] / T100['DEPARTURES_PERFORMED'] / 1000
    T100 = T100.loc[T100.index.repeat(T100['DEPARTURES_PERFORMED'])]
    T100 = T100.reset_index(drop=True)

    # Check for a 777-200 and an A320 and create the payload range diagrams.
    a320 = T100.loc[T100['Description']=='Airbus Industrie A320-100/200']
    b777 = T100.loc[T100['Description']=='Boeing 777-200ER/200LR/233LR']

    #A320 Plot
    a320_boundaries = {
        'Range': [0, 4000, 5200, 6800],
        'Payload': [19.9, 19.9, 15.9, 0]}
    a320_boundaries = pd.DataFrame(a320_boundaries)

    fig, ax = plt.subplots(dpi=300)

    # Calculate the heatmap data
    heatmap, xedges, yedges = np.histogram2d(a320['DISTANCE'], a320['PAYLOAD'], bins=40)
    heatmap[heatmap<5] = np.nan
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    # Plot the heatmap
    im = ax.imshow(heatmap.T, origin='lower', extent=extent, aspect='auto', cmap='viridis_r')
    ax.plot(a320_boundaries['Range'], a320_boundaries['Payload'], label='Limit', color='black')

    ax.scatter(4000, 19.9, color='red', zorder=2)
    ax.scatter(5200, 15.9, color='red', zorder=2)
    plt.annotate('Point B', (4000, 19.9),
                    fontsize=10, xytext=(5, 0),
                    textcoords='offset points',weight='bold')
    plt.annotate('Point C', (5200, 15.9),
                    fontsize=10, xytext=(5, 0),
                    textcoords='offset points', weight='bold')

    title = 'Airbus A320-100/200'
    xlabel = 'Distance [km]'
    ylabel = 'Payload [t]'
    plot.plot_layout(title, xlabel, ylabel, ax)
    plt.colorbar(im).set_label('Number of Flights')
    plt.ylim(0,22)
    plt.xlim(0,6900)
    if savefig:
        plt.savefig(folder_path+ '/a320_payload_range.png')

    # PLOT 777-200
    b777_boundaries = {
        'Range': [0, 14070, 15023, 17687],
        'Payload': [50.352, 50.352, 43.262, 0]}
    b777_boundaries = pd.DataFrame(b777_boundaries)

    fig, ax = plt.subplots(dpi=300)

    # Calculate the heatmap data
    heatmap, xedges, yedges = np.histogram2d(b777['DISTANCE'], b777['PAYLOAD'], bins=40)
    heatmap[heatmap<5] = np.nan
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    # Plot the heatmap
    im = ax.imshow(heatmap.T, origin='lower', extent=extent, aspect='auto', cmap='viridis_r')
    ax.plot(b777_boundaries['Range'], b777_boundaries['Payload'], label='Limit', color='black')
    ax.scatter(14070, 50.352, color='red', zorder=2)
    ax.scatter(15023, 43.262, color='red', zorder=2)
    plt.annotate('Point B', (14070, 50.352),
                    fontsize=10, xytext=(5, 0),
                    textcoords='offset points', weight='bold')
    plt.annotate('Point C', (15023, 43.262),
                    fontsize=10, xytext=(5, 0),
                    textcoords='offset points', weight='bold')

    # Set labels
    title = 'Boeing B777-200'
    xlabel = 'Distance [km]'
    ylabel = 'Payload [t]'
    plt.ylim(0, 55)
    plot.plot_layout(title, xlabel, ylabel, ax)
    plt.colorbar(im).set_label('Number of Flights')
    if savefig:
        plt.savefig(folder_path+ '/b777_payload_range.png')

