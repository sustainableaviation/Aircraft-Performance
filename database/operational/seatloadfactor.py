import pandas as pd
import numpy as np
from database.tools import dict, plot, T2_preprocessing
import matplotlib.pyplot as plt

def calculate(savefig, folder_path):

    #Load Dictionaries
    airplanes_dict = dict.AirplaneModels().get_models()
    airplanes = airplanes_dict.keys()
    airplane_types = dict.AirplaneTypes().get_types()
    airplane_types = pd.DataFrame({'Description': list(airplane_types.keys()), 'Type': list(airplane_types.values())})

    #Load Data, T2 is data from the US back to 1990, Historic_Slf contains data from the ICAO worldwide back to 1950
    T2 = pd.read_csv(r"database\rawdata\USDOT\T_SCHEDULE_T2.csv")
    AC_types = pd.read_csv(r"database\rawdata\USDOT\L_AIRCRAFT_TYPE (1).csv")
    historic_slf = pd.read_excel(r"database\rawdata\USDOT\Traffic and Operations 1929-Present_Vollständige D_data.xlsx")
    historic_slf = historic_slf.dropna(subset='PLF').reset_index()
    historic_slf['PLF'] = historic_slf['PLF'].str.replace(',', '.').astype(float)

    # Preprocess Data from Schedule T2
    T2 = T2_preprocessing.preprocessing(T2, AC_types, airplanes)
    T2 = T2.merge(airplane_types)

    # Get Annual values for the SLF per Type (Narrow, Wide, Regional)
    annual_type = T2.groupby(['YEAR','Type'], as_index=False).agg({'SLF':'median','Airborne Eff.':'mean'})
    annual = T2.groupby(['YEAR'], as_index=False).agg({'SLF':'median','Airborne Eff.':'mean'})
    narrow = annual_type.loc[annual_type['Type']=='Narrow'].reset_index()
    wide = annual_type.loc[annual_type['Type']=='Wide'].reset_index()

    #-----PLOT SLF vs. YEAR ---------------
    fig = plt.figure(dpi=300)

    # Add a subplot
    ax = fig.add_subplot(1, 1, 1)
    x_label = 'Aircraft Year of Introduction'
    y_label = 'Seat Load Factor'

    ax.plot(historic_slf['Year'], historic_slf['PLF'],color='black',marker='*',markersize=3, label='Worldwide')
    ax.plot(annual['YEAR'], annual['SLF'],color='turquoise', marker='*',markersize=3, label='US Overall')
    ax.plot(wide['YEAR'], wide['SLF'],color='orange', marker='s',markersize=3,label='US Widebody' )
    ax.plot(narrow['YEAR'], narrow['SLF'],color='blue', marker='^',markersize=3, label='US Narrowbody')
    ax.legend()

    plt.ylim(0, 1)
    plt.xlim(1948, 2023)
    plt.xticks(np.arange(1950, 2024, 10))

    plot.plot_layout(None, x_label, y_label, ax)
    if savefig:
        plt.savefig(folder_path+'/seatloadfactor.png')

    # -------------PLOT AIRBORNE EFF. vs. YEAR--------------
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    x_label = 'Aircraft Year of Introduction'
    y_label = 'Airborne Efficiency'

    ax.plot(annual['YEAR'], annual['Airborne Eff.'],color='turquoise', marker='o',markersize=3, label='US Overall')
    ax.plot(wide['YEAR'], wide['Airborne Eff.'],color='orange', marker='s',markersize=3, label='US Widebody')
    ax.plot(narrow['YEAR'], narrow['Airborne Eff.'],color='blue', marker='^',markersize=3, label='US Narrowbody')
    ax.legend()

    plt.ylim(0, 1)
    plt.xlim(1990, 2023)
    plt.xticks(np.arange(1990, 2024, 5))

    plot.plot_layout(None, x_label, y_label, ax)
    if savefig:
        plt.savefig(folder_path+'/airborneefficiency.png')