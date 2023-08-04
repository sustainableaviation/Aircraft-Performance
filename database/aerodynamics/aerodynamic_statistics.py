import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from database.tools import plot


def calculate(savefig, folder_path):

    # Load Data
    data = pd.read_excel(r'Databank.xlsx')

    # Filer for relevant Data
    data = data.loc[data['Aspect Ratio']<=15] # Filter out 767-400 where a wrong value is set in the database
    data = data.loc[data['Type']!='Regional']
    data = data.dropna(subset=['Wingspan,float,metre', 'MTOW,integer,kilogram'])

    # Values for the Height of the B787 are missing
    data.loc[data['Name'] == 'B787-800 Dreamliner', 'Height,float,metre'] = 16.92
    data.loc[data['Name'] == 'B787-900 Dreamliner', 'Height,float,metre'] = 17.02
    data.loc[data['Name'] == '787-10 Dreamliner', 'Height,float,metre'] = 17.02

    # FAA Airplane Design Groups
    groups = [
        {'Group': 'Group I', 'Min Span': 0, 'Max Span': 15, 'Min Height': 0, 'Max Height': 6.1},
        {'Group': 'Group II', 'Min Span': 15, 'Max Span': 24, 'Min Height': 6.1, 'Max Height': 9.1},
        {'Group': 'Group III', 'Min Span': 24, 'Max Span': 36, 'Min Height': 9.1, 'Max Height': 13.7},
        {'Group': 'Group IV', 'Min Span': 36, 'Max Span': 52, 'Min Height': 13.7, 'Max Height': 18.3},
        {'Group': 'Group V', 'Min Span': 52, 'Max Span': 65, 'Min Height': 18.3, 'Max Height': 20.1},
        {'Group': 'Group VI', 'Min Span': 65, 'Max Span': 80, 'Min Height': 20.1, 'Max Height': 24.4}
    ]
    df = pd.DataFrame(groups)

    # Plot FAA Group Regulations for Airport Wingspan and Height
    fig, ax = plt.subplots(dpi=300)

    # Create Colormap
    column_data = pd.to_numeric(data['YOI'], errors='coerce')
    norm = mcolors.Normalize(vmin=1959, vmax=2020)
    norm_column_data = norm(column_data)
    colors = ['white', 'lightcoral', 'red']
    cmap = mcolors.ListedColormap(colors)
    colors = cmap(norm_column_data)
    colormap = plt.cm.get_cmap('Blues', len(df))

    # Plot Groups
    for _, group in df[::-1].iterrows():
        x2, y2 = group['Max Span'], group['Max Height']

        square = patches.Rectangle((0, 0), x2, y2, linewidth=1, edgecolor=colormap(_), facecolor=colormap(_), label=group['Group'], alpha=0.7)
        ax.add_patch(square)
        ax.legend(loc='lower right')

    # Plot and annotate Aircraft
    ax.scatter(data['Wingspan,float,metre'], data['Height,float,metre'], color=colors, s=30)
    ax.scatter(64.85 , 19.5, color='yellow', s=30, label='777X Folded Wings')
    ax.scatter(71.75, 19.5, color='yellow', s=30, label='777X')
    plt.annotate('777X Folded Wings', (64.85 , 19.5),
                     fontsize=8, xytext=(-10, -10),
                     textcoords='offset points', weight='bold')
    plt.annotate('777X', (71.75, 19.5),
                     fontsize=8, xytext=(-10, 5),
                     textcoords='offset points', weight='bold')
    plt.annotate('A380', (80 , 24.4),
                     fontsize=8, xytext=(-30, -10),
                     textcoords='offset points', weight='bold')

    # Plot Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm).set_label('Aircraft Year of Introduction')

    plt.xlabel('Wingspan [m]')
    plt.ylabel('Height [m]')

    plt.ylim(0,24.4)
    plt.xlim(0,80)
    plt.tight_layout()
    if savefig:
        plt.savefig(folder_path+ '/faa_wingspan_regulations.png')

    # Plot Aspect Ratio vs the Year of Release
    fig, ax = plt.subplots(dpi=300)

    ax.scatter(data['YOI'], data['Aspect Ratio'], color='black', s=30)
    ax.scatter(2025, 9.96, color='blue', s=30)
    plt.annotate('777X', (2025, 9.96),
                     fontsize=8, xytext=(-10, 5),
                     textcoords='offset points')
    plt.annotate('A380', (2007, 7.6),
                     fontsize=8, xytext=(-10, 5),
                     textcoords='offset points')

    xlabel = 'Aircraft Year of Introduction'
    ylabel = 'Aspect Ratio'

    plot.plot_layout(None, xlabel, ylabel, ax)
    plt.tight_layout()
    if savefig:
        plt.savefig(folder_path+ '/aspectratio_vs_releaseyear.png')


