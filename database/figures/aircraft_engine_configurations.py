
    # ------PLOT TSFC CRUISE vs. YOI ------------------------ with Colors for BPR
    cm = 1 / 2.54  # for inches-cm conversion
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    #  Limits from Kurzke/Singh et al.
    limit = (0.555 * heatingvalue / flight_vel)**-1
    limit_nox = (0.50875 * heatingvalue / flight_vel) ** -1

    # Make Groups of BPR
    bpr = databank.groupby(['Name', 'YOI'], as_index=False).agg({'TSFC Cruise': 'mean',  'B/P Ratio': 'mean', 'Pressure Ratio':'mean'})
    low = bpr.loc[bpr['B/P Ratio'] <= 2]
    medium = bpr.loc[(bpr['B/P Ratio'] >= 2) & (bpr['B/P Ratio'] <= 8)]
    high = bpr.loc[bpr['B/P Ratio'] >= 8]

    ax.scatter(comet1['YOI'], comet1['TSFC Cruise'], color='red')
    ax.scatter(comet4['YOI'], comet4['TSFC Cruise'], color='red')
    ax.scatter(low['YOI'], low['TSFC Cruise'], color='red', label='BPR $<$ 2')
    ax.scatter(medium['YOI'], medium['TSFC Cruise'], color='purple', label='BPR 2 - 8')
    ax.scatter(high['YOI'], high['TSFC Cruise'], color='blue', label='BPR $>$ 8')

    ax.axhline(y=limit_nox, color='black', linestyle='--', linewidth=2, label='Practical Limit w.r.t. NOx')
    ax.axhline(y=limit, color='black', linestyle='-', linewidth=2, label = 'Theoretical Limit')

    # Fuse in Data for Future projections
    ax.scatter(2020, 14.94, color='green', label='Future Projections')
    plt.annotate('GE9X', (2020, 14.94),
                    fontsize=6, xytext=(-10, -10),
                    textcoords='offset points')
    ax.scatter(2025, 12.88, color='green')
    plt.annotate('Ultrafan', (2025, 12.88),
                    fontsize=6, xytext=(-10, 5),
                    textcoords='offset points')
    ax.scatter(2030, 12.152, color='green')
    plt.annotate('Open Rotor', (2030, 12.152),
                    fontsize=6, xytext=(-10, 5),
                    textcoords='offset points')
    ax.scatter(2035, 12, color='green')
    plt.annotate('CFM RISE', (2035, 12),
                    fontsize=6, xytext=(10, 0),
                    textcoords='offset points')
    plt.xlim(1950,2050)

    ax.legend()
    xlabel = 'Aircraft Year of Introduction'
    ylabel = 'Cruise TSFC [g/kNs]'
    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'\engineefficiency.png', bbox_inches='tight')

    # ------PLOT TSFC CRUISE vs. YOI ------------------------ with Colors for OPR
    cm = 1 / 2.54  # for inches-cm conversion
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    # Make Groups of OPR
    low = bpr.loc[bpr['Pressure Ratio'] <= 20]
    medium = bpr.loc[(bpr['Pressure Ratio'] >= 20) & (bpr['Pressure Ratio'] <= 35)]
    high = bpr.loc[bpr['Pressure Ratio'] >= 35]

    ax.scatter(comet4['YOI'], comet4['TSFC Cruise'], color='red')
    ax.scatter(low['YOI'], low['TSFC Cruise'], color='red', label='OPR $<$ 20')
    ax.scatter(medium['YOI'], medium['TSFC Cruise'], color='purple', label='OPR 20 - 35')
    ax.scatter(high['YOI'], high['TSFC Cruise'], color='blue', label='OPR $>$ 35')

    ax.axhline(y=limit_nox, color='black', linestyle='--', linewidth=2, label='Practical Limit w.r.t. NOx')
    ax.axhline(y=limit, color='black', linestyle='-', linewidth=2, label = 'Theoretical Limit')

    ax.legend()
    xlabel = 'Aircraft Year of Introduction'
    ylabel = 'Cruise TSFC [g/kNs]'
    plot.plot_layout(None, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path+'\engineefficiency_opr.png')

    # ------PLOT Engine Weight/OEW vs. YOI --------------

    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)

    # Remove Regional Jets
    databank = databank.loc[databank['Type']!='Regional']

    # Calculate Total Engine Weight and divide by the OEW
    databank['Dry weight,integer,kilogram'] = databank['Dry weight,integer,kilogram']*databank['engineCount']
    databank['Dry weight,integer,kilogram'] = databank['Dry weight,integer,kilogram'] / databank['OEW']

    # Again make groups for the BPR
    databank = databank.groupby(['Name', 'YOI'], as_index=False).agg({'Dry weight,integer,kilogram': 'mean',  'B/P Ratio': 'mean'})
    low = databank.loc[databank['B/P Ratio'] <= 2]
    medium = databank.loc[(databank['B/P Ratio'] >= 2) & (databank['B/P Ratio'] <= 8)]
    high = databank.loc[databank['B/P Ratio'] >= 8]

    ax.scatter(low['YOI'], low['Dry weight,integer,kilogram'], color='red', label='BPR $< 2$')
    ax.scatter(medium['YOI'], medium['Dry weight,integer,kilogram'], color='purple', label='BPR 2 - 8')
    ax.scatter(high['YOI'], high['Dry weight,integer,kilogram'], color='blue', label=r'BPR $> 8$')
    plt.xlim(1955, 2025)
    plt.ylim(0, 0.2)
    ax.legend()

    title = 'Individual Aircraft'
    xlabel = 'Aircraft Year of Introduction'
    ylabel = 'Engine Weight / OEW'
    plot.plot_layout(title, xlabel, ylabel, ax)
    if savefig:
        plt.savefig(folder_path + '\engineweight.png')

    # Return the Engine Efficiency Limits from Kurzke
    return limit

