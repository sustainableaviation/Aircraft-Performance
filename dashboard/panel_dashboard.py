# Import Packages
import panel as pn
import pandas as pd
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, RadioButtonGroup, CustomJS, Label, Span, MultiLine, Text, HoverTool
from bokeh.models import CheckboxGroup, Legend, Div, RadioGroup, SingleIntervalTicker, FixedTicker, LegendItem
from bokeh.transform import dodge
from bokeh.transform import cumsum
from bokeh.models import FactorRange, Select, Slider
from bokeh.palettes import Category10
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues
from bokeh.layouts import column
from bokeh.layouts import row
import warnings
import requests
import openpyxl
from io import BytesIO
from PIL import Image
warnings.filterwarnings("ignore")

pn.extension(design='material')


def about_authors():
    # Create Photo and text for Philipp
    philipp = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/images/Philipp.JPG'
    pic1 = pn.pane.JPG(philipp, width=150, height=200)
    text1 = """
    The best student 

    Philipp is enrolled as a Masters Student in the Department of Mechanical and Process Engineering of ETH Zurich. This Dashboard was created as part of his Masters Thesis under the supervision of Michael Weinold and Prof. Russell McKenna. 

    Education: 
    - Master: Mech. Engineering, ETH Zurich, 2021-2023
    - Bachelor: Mech. Engineering, ETH Zurich, 2018-2021

    """
    # Create Photo and text for Michael
    michael = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/images/michael.png'
    pic2 = pn.pane.PNG(michael, width=150, height=200)
    text2 = """
    The best supervisor 

    Michael is a doctoral researcher in the Group for Technology Assessment under the supervision of Dr. Chris Mutel and Dr. Romain Sacchi at the Paul Scherrer Institute and Prof. Russell McKenna in the Department of Mechanical and Process Engineering of ETH Zurich.

    Education: 
    - PhD: Life-Cycle Assessment for Sustainable Aviation, PSI/ETH Zurich, 2022-ongoing
    - Master: Physics, ETH Zurich, 2018-2020
    - Bachelor: Engineering Physics, TU Vienna, 2014-2018

    """
    # Format for Dashboard page
    philipp = pn.Column('# Philipp Rohrer', pn.layout.Divider(sizing_mode='stretch_width'), pic1, text1, width=400, )
    michael = pn.Column('# Michael Weinold', pn.layout.Divider(sizing_mode='stretch_width'), pic2, text2, width=400, )
    dashboard = pn.Row(philipp, michael)
    return dashboard


def data():
    # Get Databank of Aircraft Data from GitHub
    databank = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/Databank.xlsx'
    databank = pd.read_excel(databank)

    # Write Text for Explanation
    text = """
    In the following Table the values for each sub-efficiency (Overall, Engine, Aerodynamic, Structural) for the 72 
    investigated aircraft will be shown. For some aircraft, not all sub-efficiencies could have been determined. 

    - Overall Efficiency was calculated using Data from the <a href="https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FIH&QO_fu146_anzr=Nv4+Pn44vr4+f7zzn4B">US DOT</a> and <a href="https://www.annualreviews.org/doi/10.1146/annurev.energy.26.1.167">Lee et al.</a>. 
    - Engine Efficiency was calculated using Data from the <a href="https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank">ICAO Emissions Databank</a>, <a href="https://www.annualreviews.org/doi/10.1146/annurev.energy.26.1.167">Lee et al.</a> and several sources for a TSFC T/O to 
    TSFC Cruise calibration
    - Aerodynamic Efficiency was calculated using Data from the Engine Efficiency and <a href="https://www.boeing.com/commercial/airports/plan_manuals.page">Airplane Characteristics for Airport Planning</a> to solve the Breguet Range Equation
    - Structural Efficiency was calculated using Data from <a href="https://www.easa.europa.eu/en/document-library/type-certificates">Type Certificate Data Sheets</a> and <a href="https://shop.janes.com/all-the-world-s-aircraft-unmanned-23-24-yearbook-6541-3000230012">Jane's All the World's Aircraft</a>. 
    """

    # Filter for the relevant sub-efficiency data, sort by year and round values
    data = databank[['Company', 'Name', 'YOI', 'EU (MJ/ASK)', 'TSFC Cruise', 'L/D estimate', 'OEW/Exit Limit']]
    data.set_index('YOI', inplace=True)
    columns_to_round = ['EU (MJ/ASK)', 'TSFC Cruise', 'L/D estimate', 'OEW/Exit Limit']
    data[columns_to_round] = data[columns_to_round].apply(pd.to_numeric)
    data[columns_to_round] = data[columns_to_round].round(2)
    data.sort_index(inplace=True)

    # Create a header and fill nan values with empty space
    header1 = ['', '', 'Overall Eff.', 'Engine Eff.', 'Aerodyn. Eff.', 'Structural Eff.']
    header2 = ['Company', 'Model', 'EU (MJ/ASK)', 'TSFC Cruise', 'L/D', 'OEW/Exit Limit']
    columns = pd.MultiIndex.from_arrays([header1, header2])
    data.columns = columns
    data = data.fillna('')

    # Formate for Dashboard
    data = pn.pane.DataFrame(data, width=1100, height=400, scroll=True)
    data = pn.Column('# Aircraft Efficiencies', text, pn.layout.Divider(), data)

    dashboard = pn.Row(data)

    return dashboard


def create_db1():
    # Function to request Excel Files from Github
    def read_excel_from_github(url):
        response = requests.get(url)
        if response.status_code == 200:
            return pd.read_excel(BytesIO(response.content))

    # Create a line and text for explanation
    line = pn.layout.Divider(sizing_mode='stretch_width')
    text = """
    <div style="max-width: 600px">
    The Dashboard displays future trajectories for efficiency improvements, specifically focusing on various design concepts. These concepts' efficiency improvements are assessed based on customizable parameters: seat load factor, air traffic management enhancements, and the annual growth rate for passenger air transport.

    Once a scenario is chosen, the Dashboard will calculate the corresponding CO2 emissions and compare them to the CO2 reduction targets set by IATA, ICAO, and Eurocontrol. This comparison will help gauge the effectiveness of the efficiency improvements in meeting the industry's environmental goals.

    - EC Target: 75% Reduction in Net CO2 Emissions until 2050 (Baseline 2011)
    - IATA Target: 50% Reduction in Net CO2 Emissions until 2050 (Baseline 2005)
    - ICAO Target: 60% Reduction in CO2/RPK until 2050 (Baseline 2005)

    </div>
    """

    # Load Files from Github.
    freeze = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/techfreeze.xlsx'
    freeze = read_excel_from_github(freeze)
    limit = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/techlimit.xlsx'
    limit = read_excel_from_github(limit)
    bwb = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/bwb.xlsx'
    bwb = read_excel_from_github(bwb)
    advancedtw = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/advancedtw.xlsx'
    advancedtw = read_excel_from_github(advancedtw)
    doublebubble = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/doublebubble.xlsx'
    doublebubble = read_excel_from_github(doublebubble)
    ttbw = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/ttwb.xlsx'
    ttbw = read_excel_from_github(ttbw)
    target = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/target.xlsx'
    target = read_excel_from_github(target)

    # Define the initial growth rate and limits
    initial_growth_rate = 2
    initial_slf = 90
    initial_atm = 0

    def scale_plf(df, slf, atm):
        # Extract the PLF column and the corresponding years
        years = df['Year']
        plf = df['PLF']
        start_index = years[years == 2022].index[0]

        # Scale PLF values after 2022
        scaled_plf = np.interp(years, [2022, 2050], [plf[start_index], slf / 100])
        df['PLF'] = np.where(years >= 2022, scaled_plf, plf)

        # Update other columns
        df['EI (MJ/RPK)'] = df['EU (MJ/ASK)'] / df['PLF']

        # Add ATM Improvements
        eu_at_2022 = df['EI (MJ/RPK)'][start_index]
        eu_at_2050 = df['EI (MJ/RPK)'][years == 2050].values[0]
        scaling_factors = [(1 - (atm / 100) * (i - 2022) / (2050 - 2022)) for i in years]
        df['EI (MJ/RPK)'] *= np.where(years >= 2022, scaling_factors, 1)

        # df['EI (MJ/RPK)'] = np.where(years >= 2022, scaled_atm, eu)

        # Convert to CO2 emissions
        mj_to_co2 = 3.16 / 43.15
        df['EI (CO2/RPK)'] = mj_to_co2 * df['EI (MJ/RPK)']
        return df

    # Create the Bokeh figure
    def plot(selected_targets, growth_rate, target, selected_tech, freeze, limit, bwb, ttbw, advancedtw, doublebubble,
             slf, atm):

        # Based on the Growth Rate, calculate future RPK
        target.loc[target['Year'] == 2023, 'Billion RPK'] = target.loc[target['Year'] == 2019, 'Billion RPK'].values[0]
        for year in range(2024, 2051):
            previous_year = year - 1
            previous_value = target.loc[target['Year'] == previous_year, 'Billion RPK'].values[0]
            new_value = previous_value * (1 + growth_rate / 100)
            target.loc[target['Year'] == year, 'Billion RPK'] = new_value

        # Multiply 'Billion RPK' with 'CO2'
        target['ICAO Target CO2'] = target.apply(lambda row: row['Billion RPK'] * row['ICAO Target CO2/RPK'], axis=1)

        # Create Bokeh Figure
        p = figure(title=' Future Efficiency and Forecast Scenarios', x_axis_label='Year',
                   y_axis_label='CO2 Emissions [Mt]', width=1000, height=500)
        p.y_range.start = 0
        target = target.loc[target['Year'] >= 2000]

        # Add CO2 Emission Targets
        if 'EC' in selected_targets:
            ec_data = target[target['EC Target CO2'].notna()]
            p.line(ec_data['Year'], ec_data['EC Target CO2'], line_color='darkred', legend_label='EC Target',
                   line_width=3, line_dash='dashed')
        if 'IATA' in selected_targets:
            iata_data = target[target['IATA Target CO2'].notna()]
            p.line(iata_data['Year'], iata_data['IATA Target CO2'], line_color='darkred', legend_label='IATA Target',
                   line_width=3, line_dash='dotted')
        if 'ICAO' in selected_targets:
            icao_data = target[target['ICAO Target CO2'].notna()]
            p.line(icao_data['Year'], icao_data['ICAO Target CO2'], line_color='darkred', legend_label='ICAO Target',
                   line_width=3, line_dash='dotdash')

        # Add Technology Targets
        if 'Tech Freeze' in selected_tech:
            freeze = scale_plf(freeze, slf, atm)
            freeze = freeze.merge(target[['Year', 'Billion RPK']], on='Year')
            freeze['EI CO2'] = freeze.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            freeze = freeze[freeze['EI CO2'].notna()]
            p.line(freeze['Year'], freeze['EI CO2'], line_color='blue', legend_label='Tech Freeze', line_width=3)
        if 'TW Limit' in selected_tech:
            limit = scale_plf(limit, slf, atm)
            limit = limit.merge(target[['Year', 'Billion RPK']], on='Year')
            limit['EI CO2'] = limit.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            limit = limit[limit['EI CO2'].notna()]
            p.line(limit['Year'], limit['EI CO2'], line_color='blue', legend_label='TW Limit', line_width=3)
        if 'BWB' in selected_tech:
            bwb = scale_plf(bwb, slf, atm)
            bwb = bwb.merge(target[['Year', 'Billion RPK']], on='Year')
            bwb['EI CO2'] = bwb.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            bwb = bwb[bwb['EI CO2'].notna()]
            p.line(bwb['Year'], bwb['EI CO2'], line_color='blue', legend_label='BWB', line_width=3)
        if 'Advanced TW' in selected_tech:
            advancedtw = scale_plf(advancedtw, slf, atm)
            advancedtw = advancedtw.merge(target[['Year', 'Billion RPK']], on='Year')
            advancedtw['EI CO2'] = advancedtw.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            advancedtw = advancedtw[advancedtw['EI CO2'].notna()]
            p.line(advancedtw['Year'], advancedtw['EI CO2'], line_color='blue', legend_label='Advanced TW',
                   line_width=3)
        if 'TTBW' in selected_tech:
            ttbw = scale_plf(ttbw, slf, atm)
            ttbw = ttbw.merge(target[['Year', 'Billion RPK']], on='Year')
            ttbw['EI CO2'] = ttbw.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            ttbw = ttbw[ttbw['EI CO2'].notna()]
            p.line(ttbw['Year'], ttbw['EI CO2'], line_color='blue', legend_label='TTBW', line_width=3)
        if 'Double Bubble' in selected_tech:
            doublebubble = scale_plf(doublebubble, slf, atm)
            doublebubble = doublebubble.merge(target[['Year', 'Billion RPK']], on='Year')
            doublebubble['EI CO2'] = doublebubble.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            doublebubble = doublebubble[doublebubble['EI CO2'].notna()]
            p.line(doublebubble['Year'], doublebubble['EI CO2'], line_color='blue', legend_label='Double Bubble',
                   line_width=3)

        # Define grid properties
        p.grid.grid_line_color = 'gray'
        p.grid.grid_line_alpha = 0.3
        p.grid.minor_grid_line_color = 'navy'
        p.grid.minor_grid_line_alpha = 0.1

        return p

    # Create the Checkboxes and Sliders, create a Layout with all Widgets together
    checkboxes = CheckboxGroup(labels=['EC', 'IATA', 'ICAO'], active=[])
    checkboxes_title = Div(text='<h4 >Forecast Scenarios</h4>')
    checkbox1 = column(checkboxes_title, checkboxes)
    checkboxes2 = RadioGroup(labels=['Tech Freeze', 'TW Limit', 'BWB', 'Advanced TW', 'TTBW', 'Double Bubble'],
                             active=0)
    checkboxes2_title = Div(text='<h4>Future Technologies</h4>')
    checkbox2 = column(checkboxes2_title, checkboxes2)
    growth_rate_slider = Slider(title='Annual Growth Rate (%)', start=0, end=5, value=2, step=0.1,
                                styles={'font-weight': 'bold'})
    slf_slider = Slider(title='Seat Load Factor 2050 (%)', start=80, end=100, value=90, step=0.5,
                        styles={'font-weight': 'bold'})
    atm_slider = Slider(title='ATM Improvements 2050 (%)', start=0, end=15, value=0, step=0.2,
                        styles={'font-weight': 'bold'})
    slider = pn.Column(slf_slider, growth_rate_slider, atm_slider)
    checkbox = pn.Column(checkbox1, checkbox2)
    everything = pn.Column(slider, checkbox)

    # Update the plot based on the slider and checkbox values
    def update_plot(attr, old, new):
        selected_targets = [checkboxes.labels[i] for i in checkboxes.active]
        selected_tech = [checkboxes2.labels[checkboxes2.active]]

        growth_rate = growth_rate_slider.value
        slf = slf_slider.value
        atm = atm_slider.value
        p = plot(selected_targets, growth_rate, target, selected_tech, freeze, limit, bwb, ttbw, advancedtw,
                 doublebubble, slf, atm)
        dashboard[-1][0] = p  # Assign the updated plot to the correct position

    # Link the callback functions to the components
    checkboxes.on_change('active', update_plot)
    checkboxes2.on_change('active', update_plot)
    growth_rate_slider.on_change('value', update_plot)
    slf_slider.on_change('value', update_plot)
    atm_slider.on_change('value', update_plot)

    # Create the initial plot
    p = plot([], initial_growth_rate, target, ['Tech Freeze'], freeze, limit, bwb, ttbw, advancedtw, doublebubble,
             initial_slf, initial_atm)

    # Create the Panel layout
    dashboard = pn.Column(text, line, pn.Row(p, everything))

    return dashboard


def create_db2():
    # Add Text
    line = pn.layout.Divider(sizing_mode='stretch_width')
    text = """
    <div style="max-width: 600px">
    This dashboard presents a comprehensive overview of historical efficiency improvements made in the commercial aircraft industry. The dataset spans from the introduction of the De Havilland DH.106 Comet 4 in 1958 to the latest Boeing 787-10 Dreamliner.

    To analyze the trajectories of various sub-efficiencies, fourth-order polynomials were used for fitting. Furthermore, an Index Decomposition Analysis was conducted for these polynomials. The analysis covered two aspects:

    - Technological Improvements: This includes advancements in engine technology, structural design, and aerodynamics.

    - Technological Improvements and Operational Improvements: This category encompasses the combined impact of technological advancements and operational enhancements, specifically related to passenger load factor (SLF).

    The complete code can be find in the <a href="https://github.com/sustainableaviation">GitHub Repository</a>
    </div>
    """

    # Load Data from Github and sort by Year
    ida = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/Dashboard.xlsx'
    ida = pd.read_excel(ida)
    ida = ida.set_index('YOI')
    initial = pd.Series([0] * len(ida.columns), name=1958)
    ida.loc[1958] = 0
    ida = ida.sort_index()
    ida = ida

    # Get Columns for the technological improvements
    ida_tech = ida[['deltaC_Engine', 'deltaC_Aerodyn', 'deltaC_Structural', 'deltaC_Res', 'deltaC_Tot']]
    ida_tech = ida_tech.rename(columns={
        'deltaC_Engine': 'Engine',
        'deltaC_Aerodyn': 'Aerodynamic',
        'deltaC_Structural': 'Structural',
        'deltaC_Res': 'Residual',
        'deltaC_Tot': 'Overall'})

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

    # Define the plot function
    def plot(start_year, middle_year, end_year, df):
        # Check which DF is used and define the colors
        if df == "Index Decomposition Analyis":
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

        else:
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
        df_dif_first['ValueSum'].iloc[-1] = df_dif_first['Value'].iloc[-1] + df.loc[start_year]['Overall_1']

        df_dif_second = pd.DataFrame((df.loc[end_year] - df.loc[middle_year])).reset_index()
        df_dif_second.columns = ['Eff', 'Value']
        df_dif_second['Offset'] = df_dif_second['Value'].cumsum() - df_dif_second['Value'] + df.loc[middle_year][
            'Overall_1']
        df_dif_second['Offset'].iloc[-1] = 0
        df_dif_second['ValueSum'] = df_dif_second['Value'].cumsum() + df.loc[middle_year]['Overall_1']
        df_dif_second['ValueSum'].iloc[-1] = df_dif_second['Value'].iloc[-1] + df.loc[middle_year]['Overall_1']
        df_dif = pd.concat([df_dif_first, df_dif_second])

        df_dif['Eff'] = df_dif.groupby('Eff').cumcount().astype(str).replace('0', '') + '_' + df_dif['Eff']

        value = df_dif.loc[df_dif['Eff'] == '_Engine', 'Offset']
        overall_baseline = pd.DataFrame({'Eff': 'Overall', 'Value': value, 'Offset': 0, 'ValueSum': value})
        df_dif = pd.concat([overall_baseline, df_dif]).reset_index(drop=True)
        df_dif['Color'] = colors[:len(df_dif)]

        source = ColumnDataSource(df_dif)

        # Plot the Figure
        p = figure(x_range=df_dif['Eff'], title=f"Efficiency Improvements Between {start_year} and {end_year}",
                   x_axis_label='Timeline', y_axis_label='Energy Usage: Basis 1958', width=1000, height=500, )

        eff = 'Eff'
        ops = '_Operational'
        ops = ops in df_dif[eff].values

        # Define the Legend Labels based on the chosen DF.
        if ops:
            legend = Legend(items=[
                ("Overall", [p.square([1], [1], color="dimgey")]),
                ("Engine", [p.square([1], [1], color="darkblue")]),
                ("Aerodynamic", [p.square([1], [1], color="royalblue")]),
                ("Structural", [p.square([1], [1], color="steelblue")]),
                ("Operational", [p.square([1], [1], color="lightblue")]),
                ("Residual", [p.square([1], [1], color="red")])])

        else:
            legend = Legend(items=[
                ("Overall", [p.square([1], [1], color="dimgrey")]),
                ("Engine", [p.square([1], [1], color="darkblue")]),
                ("Aerodynamic", [p.square([1], [1], color="royalblue")]),
                ("Structural", [p.square([1], [1], color="steelblue")]),
                ("Residual", [p.square([1], [1], color="red")])])

        # Plot vertical bars and legend
        p.vbar(x='Eff', top='ValueSum', width=0.9, source=source, bottom='Offset', fill_color='Color',
               line_color='Color')
        p.add_layout(legend, 'right')
        p.xaxis.major_label_text_font_size = "0pt"

        # Plot years as text and add to layout
        start = Label(x=12, y=5, x_units='screen', y_units='screen', text=str(start_year), text_font_size='12pt',
                      text_color='white', text_font_style='bold')
        middle = Label(x=370, y=5, x_units='screen', y_units='screen', text=str(middle_year), text_font_size='12pt',
                       text_color='white', text_font_style='bold')
        end = Label(x=723, y=5, x_units='screen', y_units='screen', text=str(end_year), text_font_size='12pt',
                    text_color='white', text_font_style='bold')
        p.add_layout(start)
        p.add_layout(middle)
        p.add_layout(end)
        line = Span(location=100, dimension='width', line_color='black', line_width=3, line_dash='dashed')

        # Define Grid Properties
        p.ygrid.grid_line_color = 'gray'
        p.ygrid.grid_line_alpha = 0.3
        p.ygrid.minor_grid_line_color = 'navy'
        p.ygrid.minor_grid_line_alpha = 0.1
        p.xgrid.grid_line_color = None
        p.xaxis.major_tick_line_color = None
        p.add_layout(line)
        p.y_range.start = 0
        p.y_range.end = 100

        return p

    # Define the callback function for widget changes
    def update_plot(event):
        selected_variable = variable_widget.value
        if selected_variable == "Index Decomposition Analyis" or selected_variable == "Include Operational":
            # Get values of chosen years
            start_year = int(start_year_widget.value)
            middle_year = int(middle_year_widget.value)
            end_year = int(end_year_widget.value)

            # Make that start year must be smaller than middle year and so on.
            start_year_widget.options = [str(year) for year in range(1958, middle_year)]
            middle_year_widget.options = [str(year) for year in range(start_year + 1, end_year)]
            end_year_widget.options = [str(year) for year in range(middle_year + 1, 2021)]

            p = plot(start_year, middle_year, end_year, selected_variable)
            dashboard[-1][0] = p

    # Create slider widget
    start_year_widget = pn.widgets.Select(name="Start Year", options=[str(year) for year in range(1958, 2019)],
                                          value=str(1958))
    middle_year_widget = pn.widgets.Select(name="Middle Year", options=[str(year) for year in range(1959, 2020)],
                                           value=str(2000))
    end_year_widget = pn.widgets.Select(name="End Year", options=[str(year) for year in range(1960, 2021)],
                                        value=str(2020))

    # Create a selection widget
    variable_widget = pn.widgets.Select(name="Variable", options=["Index Decomposition Analyis", "Include Operational"])

    # Define initial years
    start_year = 1958
    middle_year = 2000
    end_year = 2020

    # Register the callback function for widget changes
    variable_widget.param.watch(update_plot, 'value')
    start_year_widget.param.watch(update_plot, 'value')
    middle_year_widget.param.watch(update_plot, 'value')
    end_year_widget.param.watch(update_plot, 'value')

    p = plot(start_year, middle_year, end_year, "Index Decomposition Analyis")

    years = pn.Column(variable_widget, start_year_widget, middle_year_widget, end_year_widget)
    # Create a layout for the widgets and plot
    dashboard = pn.Column(text, line, pn.Row(p, years))

    return dashboard


def create_db3():
    # Load Data from GitHub
    aircraft = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/aircraft.xlsx'
    aircraft = pd.read_excel(aircraft)

    lee = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/data/aircraft_lee.xlsx'
    lee = pd.read_excel(lee)

    # Add text and divider Line
    line = pn.layout.Divider(sizing_mode='stretch_width')
    text = """
    <div style="max-width: 600px">
    In the following graph, overall efficiency improvements are visualized, starting with the first commercial aircraft, the de Havilland Comet 1. 

    Future projections are also integrated in the graph for comparison. The SB-Wing, Double Bubble, Advanced TW and BWB projects overall efficiency improvements were all given in literature in relation, to a current aircraft.

    The TW Limit is calculated based on the maximal sub-efficiency improvements that can be achieved with respect to technological and economic limitations. 
    </div>
    """

    # Divide Aircraft Data into Regional, Normal, Data from Lee, Comet 1 and Comet 4
    regionalcarriers = ['Canadair CRJ 900', 'Canadair RJ-200ER /RJ-440', 'Canadair RJ-700', 'Embraer 190'
                                                                                            'Embraer ERJ-175',
                        'Embraer-135', 'Embraer-145']
    regional = aircraft.loc[aircraft['Description'].isin(regionalcarriers)]
    normal = aircraft.loc[~aircraft['Description'].isin(regionalcarriers)]
    comet4 = lee.loc[lee['Label'] == 'Comet 4']
    comet1 = lee.loc[lee['Label'] == 'Comet 1']
    rest = lee.loc[~lee['Label'].isin(['Comet 4', 'Comet 1'])]

    # Use ColumnDataSource for the Plotting and add Future Design Concepts
    comet1_source = ColumnDataSource(data=dict(year=comet1['Year'], energy=comet1['EU (MJ/ASK)'], name=comet1['Label']))
    comet4_source = ColumnDataSource(data=dict(year=comet4['Year'], energy=comet4['EU (MJ/ASK)'], name=comet4['Label']))
    normal_source = ColumnDataSource(data=dict(year=normal['YOI'], energy=normal['MJ/ASK'], name=normal['Description']))
    regional_source = ColumnDataSource(
        data=dict(year=regional['YOI'], energy=regional['MJ/ASK'], name=regional['Description']))
    rest_source = ColumnDataSource(data=dict(year=rest['Year'], energy=rest['EU (MJ/ASK)'], name=rest['Label']))
    sbwing_source = ColumnDataSource(data=dict(year=[2035], energy=[0.592344579], name=['SB-Wing']))
    db_source = ColumnDataSource(data=dict(year=[2035], energy=[0.381840741], name=['Double Bubble']))
    adv_tw_source = ColumnDataSource(data=dict(year=[2040], energy=[0.82264895], name=['Advanced TW']))
    bwb_source = ColumnDataSource(data=dict(year=[2040], energy=[0.797082164], name=['BWB']))
    twlimit_source = ColumnDataSource(data=dict(year=[2050], energy=[0.618628347], name=['TW Limit']))

    # Create the figure
    p = figure(width=1000, height=500, )

    # Scatter plots
    comet1_renderer = p.scatter('year', 'energy', source=comet1_source, marker='*', size=10, color='blue',
                                legend_label='Comet 1')
    comet4_renderer = p.scatter('year', 'energy', source=comet4_source, marker='star', size=10, color='blue',
                                legend_label='Comet 4')
    normal_renderer = p.scatter('year', 'energy', source=normal_source, marker='^', size=10, color='blue',
                                legend_label='US DOT T2')
    regional_renderer = p.scatter('year', 'energy', source=regional_source, marker='^', size=10, color='purple',
                                  legend_label='Regional US DOT T2')
    rest_renderer = p.scatter('year', 'energy', source=rest_source, marker='o', size=10, color='red',
                              legend_label='Lee et al.')
    sbwing_renderer = p.scatter('year', 'energy', source=sbwing_source, marker='square', size=10, color='black',
                                legend_label='SB-Wing')
    db_renderer = p.scatter('year', 'energy', source=db_source, marker='circle', size=10, color='black',
                            legend_label='Double Bubble')
    adv_tw_renderer = p.scatter('year', 'energy', source=adv_tw_source, marker='inverted_triangle', size=10,
                                color='black', legend_label='Advanced TW')
    bwb_renderer = p.scatter('year', 'energy', source=bwb_source, marker='star', size=10, color='black',
                             legend_label='BWB')
    twlimit_renderer = p.scatter('year', 'energy', source=twlimit_source, marker='triangle', size=10, color='black',
                                 legend_label='TW Limit')

    p.add_layout(Legend())

    # Set axis labels
    p.xaxis.axis_label = 'Aircraft Year of Introduction'
    p.yaxis.axis_label = 'EU (MJ/ASK)'

    # Set plot range and ticks
    p.y_range.start = 0
    p.y_range.end = 9
    p.x_range.start = 1950
    p.x_range.end = 2052
    p.xaxis.ticker = list(range(1950, 2051, 10))
    p.grid.grid_line_color = 'gray'
    p.grid.grid_line_alpha = 0.3
    p.grid.minor_grid_line_color = 'navy'
    p.grid.minor_grid_line_alpha = 0.1

    # Create a HoverTool to see the data when clicking on it
    hover = HoverTool()
    hover.renderers = [comet1_renderer, comet4_renderer, normal_renderer, regional_renderer, rest_renderer,
                       sbwing_renderer
        , db_renderer, adv_tw_renderer, bwb_renderer, twlimit_renderer]
    hover.tooltips = [
        ("Name", "@name"),
        ("Year", "@year"),
        ("EU (MJ/ASK)", "@energy"),
    ]
    p.add_tools(hover)

    dashboard = pn.Column(text, line, p)

    return dashboard

dashboard_container = pn.Column()

# create the dashboard title and title row with the logos
title = pn.pane.HTML("""
<h1 style='font-size:36px;font-weight:bold;'>Aircraft Performance Analysis Tool</h1>
""")
# Load logos from GitHub
psi = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/images/psilogo.png'
psi = pn.pane.PNG(psi, width=150, height=100)
esa = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/images/esalogo.png'
esa = pn.pane.PNG(esa, width=150, height=100)
eth = 'https://raw.githubusercontent.com/sustainableaviation/Aircraft-Performance/main/dashboard/images/eth.png'
eth = pn.pane.PNG(eth, width=150, height=100)

# Create a panel to hold the title and logo
line = pn.layout.Divider(sizing_mode='stretch_width')
# Create the row with aligned items
header = pn.Row(title,pn.Spacer(width=100),psi,esa,eth,)

# Update the Dashboard, Display the selected Dashboard
def update_dashboard(event):
    selection_value = event.new
    if selection_value == 'Forecast':
        dashboard = create_db1()
    elif selection_value == 'Author':
        dashboard = about_authors()
    elif selection_value == 'Data':
        dashboard = data()
    elif selection_value == 'Historic Efficiency Decomposition':
        dashboard = create_db2()
    elif selection_value == 'Overall Efficiency Improvements':
        dashboard = create_db3()
    else:
        raise ValueError("Invalid dashboard selection.")
    dashboard_container.clear()
    dashboard_container.append(dashboard)

# Set the initial dashboard to the "Historic Efficiency Decomposition" plot
dashboard = create_db1()
dashboard_container.append(dashboard)

# Show the selection of Dashboards
selection = pn.widgets.RadioButtonGroup(options=['Forecast', 'Historic Efficiency Decomposition', 'Overall Efficiency Improvements','Data', 'Author'], name='Select Dashboard', value='Forecast')
selection.param.watch(update_dashboard, 'value')

layout = pn.Column(header,line, selection,line, dashboard_container)
layout.show()