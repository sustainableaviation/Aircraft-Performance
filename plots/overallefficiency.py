       # -----------Plot MJ/ASK vs Release Year------------------
       cm = 1 / 2.54  # for inches-cm conversion
       fig = plt.figure(dpi=300)
       ax = fig.add_subplot(1, 1, 1)
       ax.scatter(comet1['Year'], comet1['EU (MJ/ASK)'], marker='*', color='blue', label='Comet 1')
       ax.scatter(comet4['Year'], comet4['EU (MJ/ASK)'], marker='o', color='blue', label='Comet 4')
       ax.scatter(normal['YOI'], normal['MJ/ASK'], marker='^',color='blue', label='US DOT T2')
       ax.scatter(regional['YOI'], regional['MJ/ASK'], marker='^', color='cyan', label='Regional US DOT T2')
       ax.scatter(rest['Year'], rest['EU (MJ/ASK)'], marker='s',color='red', label='Lee')
       ax.plot(fleet_avg_year.index, fleet_avg_year['MJ/ASK'],color='blue', label='US DOT T2 Fleet')
       ax.plot(fleet_avg_year.index, fleet_avg_year['MJ/RPK'],color='blue',linestyle='--', label='US DOT T2 Fleet RPK')
       ax.plot(lee_fleet['Year'], lee_fleet['EU (MJ/ASK)'],color='red', label='Lee Fleet')

       ax.legend()
       future_legend = ax.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Historic Data", frameon=False)
       future_legend._legend_box.align = "left"

       #Add projections from Lee et al.
       plot_past_projections = False
       if plot_past_projections:
              ax.scatter([1997, 2007, 2022], [1.443, 1.238, 0.9578], marker='^', color='black', label='NASA 100 PAX')
              ax.scatter([1997, 2007, 2022], [1.2787, 1.0386, 0.741], marker='*', color='black', label='NASA 150 PAX')
              ax.scatter([1997, 2007, 2022], [1.2267, 0.9867, 0.681], marker='s', color='black', label='NASA 225 PAX')
              ax.scatter([1997, 2007, 2022], [1.1704, 0.9259, 0.637], marker='o', color='black', label='NASA 300 PAX')
              ax.scatter([1997, 2007, 2022], [0.91, 0.76, 0.559], marker='P', color='black', label='NASA 600 PAX')
              ax.scatter(2010, 0.6587 , marker='^', color='grey', label='NRC')
              ax.scatter(2015, 0.5866, marker='o', color='grey', label='Greene')
              ax.scatter([2025, 2025, 2025], [0.55449, 0.6, 0.68], marker='s', color='grey', label='Lee')

              # Projection legend
              projection_handles = ax.get_legend_handles_labels()[0][8:]  # Exclude the first 8 handles (historic data)
              projection_labels = ax.get_legend_handles_labels()[1][8:]  # Exclude the first 8 labels (historic data)
              ax.legend(projection_handles, projection_labels, loc='lower left', bbox_to_anchor=(1, -0.05),
                                            title="Historic Projections", frameon=False)
              ax.add_artist(future_legend)
       plot_future_projections = False
       if plot_future_projections:
              ax.scatter(2035,0.592344579, marker='s', color='black', label='SB-Wing')
              ax.scatter(2035,0.381840741, marker='o', color='black', label='Double Bubble')
              ax.scatter(2040,0.82264895, marker='P', color='black', label='Advanced TW')
              ax.scatter(2040,0.797082164, marker='*', color='black', label='BWB')
              ax.scatter(2050,0.618628347, marker='^', color='black', label='TW Limit')

              # Projection legend
              projection_handles = ax.get_legend_handles_labels()[0][8:]  # Exclude the first 8 handles (historic data)
              projection_labels = ax.get_legend_handles_labels()[1][8:]  # Exclude the first 8 labels (historic data)
              ax.legend(projection_handles, projection_labels, loc='lower left', bbox_to_anchor=(1, -0.05),
                                            title="Future Projections", frameon=False)
              ax.add_artist(future_legend)

       #Arrange plot size
       plt.ylim(0, 9)
       plt.xlim(1950, 2024)
       plt.xticks(np.arange(1950, 2023, 10))

       # Set the x and y axis labels
       xlabel = 'Aircraft Year of Introduction'
       ylabel = 'EU (MJ/ASK)'
       plot.plot_layout(None, xlabel, ylabel, ax)
       if savefig:
              plt.savefig(folder_path+ "\ovr_efficiency.png", bbox_inches='tight')