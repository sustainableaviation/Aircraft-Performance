import pandas as pd
from database.tools import plot
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

def calculate(savefig, folder_path):
    # Choose Years for Analysis
    start_year = 1958
    middle_year = 2000
    end_year = 2020

    # Code from the Dashboard, Bokeh Properties converted to Matplotlib
    dashboard = pd.read_excel(r'dashboard\data\Dashboard.xlsx')
    ida = dashboard.set_index('YOI')
    ida.loc[1958] = 0
    ida = ida.sort_index()
    # Get Columns for the technological improvements
    ida_tech = ida[['deltaC_Engine', 'deltaC_Aerodyn', 'deltaC_Structural', 'deltaC_Res', 'deltaC_Tot']]
    ida_tech = ida_tech.rename(columns={
        'deltaC_Engine': 'Engine',
        'deltaC_Aerodyn': 'Aerodynamic',
        'deltaC_Structural': 'Structural',
        'deltaC_Res': 'Residual',
        'deltaC_Tot': 'Overall'})
    df = ida_tech
    colors = ["dimgrey", 'darkblue', 'royalblue', 'steelblue', 'red',
              "dimgrey", 'darkblue', 'royalblue', 'steelblue', 'red',
              "dimgrey"]

    df['Overall_1'] = 10000 / (df['Overall'] + 100)
    df['Total'] = df['Engine'] + df['Aerodynamic'] + df['Structural'] + df['Residual']
    df['Overall Inverse'] = 100 - df['Overall_1']
    cols_to_update = ['Engine', 'Aerodynamic', 'Structural', 'Residual']
    for col in cols_to_update:
        df.loc[df.index[1:], col] = -1 * (df.loc[df.index[1:], col] / df.loc[df.index[1:], 'Total']) * df.loc[
            df.index[1:], 'Overall Inverse']

    df = df.drop(columns=['Overall Inverse', 'Total', 'Overall'])
    # Code to create the waterfall charts with the start, middle and end year.
    df_dif_first = pd.DataFrame((df.loc[middle_year] - df.loc[start_year])).reset_index()
    df_dif_first.columns = ['Eff', 'Value']
    df_dif_first['Offset'] = df_dif_first['Value'].cumsum() - df_dif_first['Value'] + df.loc[start_year][
            'Overall_1']
    df_dif_first['Offset'].iloc[-1] = 0
    df_dif_first['ValueSum'] = df_dif_first['Value'].cumsum() + df.loc[start_year]['Overall_1']
    df_dif_first['Value'].iloc[-1] = df_dif_first['Value'].iloc[-1] + df.loc[start_year]['Overall_1']

    df_dif_second = pd.DataFrame((df.loc[end_year] - df.loc[middle_year])).reset_index()
    df_dif_second.columns = ['Eff', 'Value']
    df_dif_second['Offset'] = df_dif_second['Value'].cumsum() - df_dif_second['Value'] + df.loc[middle_year][
            'Overall_1']
    df_dif_second['Offset'].iloc[-1] = 0
    df_dif_second['ValueSum'] = df_dif_second['Value'].cumsum() + df.loc[middle_year]['Overall_1']
    df_dif_second['Value'].iloc[-1] = df_dif_second['Value'].iloc[-1] + df.loc[middle_year]['Overall_1']
    df_dif = pd.concat([df_dif_first, df_dif_second])

    df_dif['Eff'] = df_dif.groupby('Eff').cumcount().astype(str).replace('0', '') + '_' + df_dif['Eff']

    value = df_dif.loc[df_dif['Eff'] == '_Engine', 'Offset']
    overall_baseline = pd.DataFrame({'Eff': 'Overall', 'Value': value, 'Offset': 0, 'ValueSum': value})
    df_dif = pd.concat([overall_baseline, df_dif]).reset_index(drop=True)
    df_dif['Color'] = colors[:len(df_dif)]
    df = df_dif

    # Create the waterfall chart
    fig, ax = plt.subplots(dpi=300)

    # Plot the bars
    for i in range(len(df)):
        color = df['Color'][i]
        value = df['Value'][i]
        offset = df['Offset'][i]
        label = df['Eff'][i]

        ax.bar(label, value, bottom=offset, color=color, label='_nolegend_')

    # Set y-axis labels to have + or - symbols
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.1f}' if x >= 0 else f'{-x:.1f}'))

    # Add gridlines and labels
    ax.axhline(0, color='black', linewidth=0.8)
    ylabel = 'Energy Usage: Basis 1958'
    xlabel = 'Timeline'
    title = 'Efficiency Improvements Between 1958 and 2020'
    plot.plot_layout(title, xlabel, ylabel, ax)

    # Show the plot
    custom_ticks = [0, 5, 10]  # Example arbitrary tick positions
    custom_tick_labels = ['1958', '2000', '2020']  # Example tick labels
    ax.set_xticks(custom_ticks)
    ax.set_xticklabels(custom_tick_labels)

    # Dummy scatter points to represent the legend markers
    dummy_points = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='dimgrey', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='darkblue', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='royalblue', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='steelblue', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10)
    ]

    # Create the legend
    ax.legend(dummy_points, ["Overall", "Engine", "Aerodynamic", "Structural", "Residual"], loc='upper right')

    if savefig:
        plt.savefig(folder_path + '/ida_waterfall_tech.png')


    # IDA OPERATIONAL
    # Get Columns for the technological + operational improvements
    ida_ops = ida[
        ['deltaC_Engine_Ops', 'deltaC_Aerodyn_Ops', 'deltaC_Structural_Ops', 'deltaC_SLF_Ops', 'deltaC_Res_Ops',
         'deltaC_Tot_Ops']]
    ida_ops = ida_ops.rename(columns={
        'deltaC_Engine_Ops': 'Engine',
        'deltaC_Aerodyn_Ops': 'Aerodynamic',
        'deltaC_Structural_Ops': 'Structural',
        'deltaC_SLF_Ops': 'Operational',
        'deltaC_Res_Ops': 'Residual',
        'deltaC_Tot_Ops': 'Overall'})

    df = ida_ops
    colors = ["dimgrey", 'darkblue', 'royalblue', 'steelblue', 'lightblue', 'red',
              "dimgrey", 'darkblue', 'royalblue', 'steelblue', 'lightblue', 'red',
              "dimgrey"]

    df['Overall_1'] = 10000 / (df['Overall'] + 100)
    df['Total'] = df['Engine'] + df['Aerodynamic'] + df['Structural'] + df['Residual'] + df['Operational']
    df['Overall Inverse'] = 100 - df['Overall_1']
    cols_to_update = ['Engine', 'Aerodynamic', 'Structural', 'Operational', 'Residual']
    for col in cols_to_update:
        df.loc[df.index[1:], col] = -1 * (df.loc[df.index[1:], col] / df.loc[df.index[1:], 'Total']) * df.loc[
            df.index[1:], 'Overall Inverse']

    df = df.drop(columns=['Overall Inverse', 'Total', 'Overall'])
    # Code to create the waterfall charts with the start, middle and end year.
    df_dif_first = pd.DataFrame((df.loc[middle_year] - df.loc[start_year])).reset_index()
    df_dif_first.columns = ['Eff', 'Value']
    df_dif_first['Offset'] = df_dif_first['Value'].cumsum() - df_dif_first['Value'] + df.loc[start_year][
            'Overall_1']
    df_dif_first['Offset'].iloc[-1] = 0
    df_dif_first['ValueSum'] = df_dif_first['Value'].cumsum() + df.loc[start_year]['Overall_1']
    df_dif_first['Value'].iloc[-1] = df_dif_first['Value'].iloc[-1] + df.loc[start_year]['Overall_1']

    df_dif_second = pd.DataFrame((df.loc[end_year] - df.loc[middle_year])).reset_index()
    df_dif_second.columns = ['Eff', 'Value']
    df_dif_second['Offset'] = df_dif_second['Value'].cumsum() - df_dif_second['Value'] + df.loc[middle_year][
            'Overall_1']
    df_dif_second['Offset'].iloc[-1] = 0
    df_dif_second['ValueSum'] = df_dif_second['Value'].cumsum() + df.loc[middle_year]['Overall_1']
    df_dif_second['Value'].iloc[-1] = df_dif_second['Value'].iloc[-1] + df.loc[middle_year]['Overall_1']
    df_dif = pd.concat([df_dif_first, df_dif_second])

    df_dif['Eff'] = df_dif.groupby('Eff').cumcount().astype(str).replace('0', '') + '_' + df_dif['Eff']

    value = df_dif.loc[df_dif['Eff'] == '_Engine', 'Offset']
    overall_baseline = pd.DataFrame({'Eff': 'Overall', 'Value': value, 'Offset': 0, 'ValueSum': value})
    df_dif = pd.concat([overall_baseline, df_dif]).reset_index(drop=True)
    df_dif['Color'] = colors[:len(df_dif)]
    df = df_dif

    # Create the waterfall chart
    fig, ax = plt.subplots(dpi=300)

    # Plot the bars
    for i in range(len(df)):
        color = df['Color'][i]
        value = df['Value'][i]
        offset = df['Offset'][i]
        label = df['Eff'][i]

        ax.bar(label, value, bottom=offset, color=color, label='_nolegend_')


    # Set y-axis labels to have + or - symbols
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.1f}' if x >= 0 else f'{-x:.1f}'))

    # Add gridlines and labels
    ax.axhline(0, color='black', linewidth=0.8)
    ylabel = 'Energy Usage: Basis 1958'
    xlabel = 'Timeline'
    title = 'Efficiency Improvements Between 1958 and 2020'
    plot.plot_layout(title, xlabel, ylabel, ax)

    # Show the plot
    custom_ticks = [0, 6, 12]  # Example arbitrary tick positions
    custom_tick_labels = ['1958', '2000', '2020']  # Example tick labels
    ax.set_xticks(custom_ticks)
    ax.set_xticklabels(custom_tick_labels)

    # Dummy scatter points to represent the legend markers
    dummy_points = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='dimgrey', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='darkblue', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='royalblue', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='steelblue', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='lightblue', markersize=10),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10)
    ]

    # Create the legend
    ax.legend(dummy_points, ["Overall", "Engine", "Aerodynamic", "Structural","Operational", "Residual"], loc='upper right')
    if savefig:
        plt.savefig(folder_path+'/ida_waterfall_operational.png')


