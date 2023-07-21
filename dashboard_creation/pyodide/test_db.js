importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/1.0.2/dist/wheels/bokeh-3.1.1-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.0.2/dist/wheels/panel-1.0.2-py3-none-any.whl', 'pyodide-http==0.2.1', 'numpy', 'pandas']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

import panel as pn
import pandas as pd
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, RadioButtonGroup, CustomJS, Label, Span, MultiLine, Text
from bokeh.models import CheckboxGroup, Legend, Div, RadioGroup, SingleIntervalTicker, FixedTicker, LegendItem
from bokeh.transform import dodge
from bokeh.transform import cumsum
from bokeh.models import FactorRange, Select, Slider
from bokeh.palettes import Category10
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues
from bokeh.layouts import column
from bokeh.layouts import row

pn.extension(design='material')

def about_authors():
    text = """
    Add Informations about the authors and the GitHub repository.
    """

    dashboard = pn.Column('# Authors', pn.layout.Divider(), text, styles=dict(background='whitesmoke'), width=400,)
    return dashboard

def data():
    data = pd.read_excel(r'Databank.xlsx')
    data = data[['Company', 'Name', 'YOI','EU (MJ/ASK)', 'TSFC Cruise',  'L/D estimate','OEW/Exit Limit']]
    data.set_index('YOI', inplace=True)
    columns_to_round = ['EU (MJ/ASK)', 'TSFC Cruise', 'L/D estimate', 'OEW/Exit Limit']
    data[columns_to_round] = data[columns_to_round].apply(pd.to_numeric)
    data[columns_to_round] = data[columns_to_round].round(2)
    data.sort_index(inplace=True)
    header1 = ['', '', 'Overall Eff.', 'Engine Eff.', 'Aerodyn. Eff.', 'Structural Eff.']
    header2 = ['Company', 'Model', 'EU (MJ/ASK)', 'TSFC Cruise', 'L/D', 'OEW/Exit Limit']
    columns = pd.MultiIndex.from_arrays([header1, header2])
    data.columns = columns
    data = data.fillna('')
    data = pn.pane.DataFrame(data, width=1000, height=400, scroll=True)

    dashboard = pn.Column('# Aircraft Efficiencies', pn.layout.Divider(), data)
    return dashboard


def create_db1():
    # Read in Scenarios and Targets, Scenarios
    freeze = pd.read_excel(r'techfreeze.xlsx')
    limit = pd.read_excel(r'techlimit.xlsx')
    bwb = pd.read_excel(r'bwb.xlsx')
    advancedtw = pd.read_excel(r'advancedtw.xlsx')
    doublebubble = pd.read_excel(r'doublebubble.xlsx')
    ttbw = pd.read_excel(r'ttwb.xlsx')
    target = pd.read_excel(r'target.xlsx')

    # Define the initial growth rate and limits
    initial_growth_rate = 2
    initial_slf = 90

    def scale_plf(df, slf):
        # Extract the PLF column and the corresponding years
        years = df['Year']
        plf = df['PLF']
        start_index = years[years == 2022].index[0]

        # Scale PLF values after 2022
        scaled_plf = np.interp(years, [2022, 2050], [plf[start_index], slf / 100])
        df['PLF'] = np.where(years >= 2022, scaled_plf, plf)

        # Update other columns
        df['EI (MJ/RPK)'] = df['EU (MJ/ASK)'] / df['PLF']
        mj_to_co2 = 3.16 / 43.15
        df['EI (CO2/RPK)'] = mj_to_co2 * df['EI (MJ/RPK)']
        return df

    # Create the Bokeh figure
    def plot(selected_targets, growth_rate, target, selected_tech, freeze, limit, bwb, ttbw, advancedtw, doublebubble,
             slf):

        target.loc[target['Year'] == 2023, 'Billion RPK'] = target.loc[target['Year'] == 2019, 'Billion RPK'].values[0]
        for year in range(2024, 2051):
            previous_year = year - 1
            previous_value = target.loc[target['Year'] == previous_year, 'Billion RPK'].values[0]
            new_value = previous_value * (1 + growth_rate / 100)
            target.loc[target['Year'] == year, 'Billion RPK'] = new_value

        # Multiply 'Billion RPK' with 'CO2'
        target['ICAO Target CO2'] = target.apply(lambda row: row['Billion RPK'] * row['ICAO Target CO2/RPK'], axis=1)
        p = figure(title=' Future Efficiency and Forecast Scenarios', x_axis_label='Year', y_axis_label='CO2 Emissions',
                   width=800, height=400)
        p.y_range.start = 0
        target = target.loc[target['Year'] >= 2000]

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

        if 'Tech Freeze' in selected_tech:
            freeze = scale_plf(freeze, slf)
            freeze = freeze.merge(target[['Year', 'Billion RPK']], on='Year')
            freeze['EI CO2'] = freeze.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            freeze = freeze[freeze['EI CO2'].notna()]
            p.line(freeze['Year'], freeze['EI CO2'], line_color='blue', legend_label='Tech Freeze', line_width=3,
                   line_dash='dashed')
        if 'TW Limit' in selected_tech:
            limit = scale_plf(limit, slf)
            limit = limit.merge(target[['Year', 'Billion RPK']], on='Year')
            limit['EI CO2'] = limit.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            limit = limit[limit['EI CO2'].notna()]
            p.line(limit['Year'], limit['EI CO2'], line_color='blue', legend_label='TW Limit', line_width=3,
                   line_dash='dotted')
        if 'BWB' in selected_tech:
            bwb = scale_plf(bwb, slf)
            bwb = bwb.merge(target[['Year', 'Billion RPK']], on='Year')
            bwb['EI CO2'] = bwb.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            bwb = bwb[bwb['EI CO2'].notna()]
            p.line(bwb['Year'], bwb['EI CO2'], line_color='blue', legend_label='BWB', line_width=3, line_dash='dotdash')
        if 'Advanced TW' in selected_tech:
            advancedtw = scale_plf(advancedtw, slf)
            advancedtw = advancedtw.merge(target[['Year', 'Billion RPK']], on='Year')
            advancedtw['EI CO2'] = advancedtw.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            advancedtw = advancedtw[advancedtw['EI CO2'].notna()]
            p.line(advancedtw['Year'], advancedtw['EI CO2'], line_color='blue', legend_label='Advanced TW',
                   line_width=3, line_dash='dotdash')
        if 'TTBW' in selected_tech:
            ttbw = scale_plf(ttbw, slf)
            ttbw = ttbw.merge(target[['Year', 'Billion RPK']], on='Year')
            ttbw['EI CO2'] = ttbw.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            ttbw = ttbw[ttbw['EI CO2'].notna()]
            p.line(ttbw['Year'], ttbw['EI CO2'], line_color='blue', legend_label='TTBW', line_width=3,
                   line_dash='dotdash')
        if 'Double Bubble' in selected_tech:
            doublebubble = scale_plf(doublebubble, slf)
            doublebubble = doublebubble.merge(target[['Year', 'Billion RPK']], on='Year')
            doublebubble['EI CO2'] = doublebubble.apply(lambda row: row['Billion RPK'] * row['EI (CO2/RPK)'], axis=1)
            doublebubble = doublebubble[doublebubble['EI CO2'].notna()]
            p.line(doublebubble['Year'], doublebubble['EI CO2'], line_color='blue', legend_label='Double Bubble',
                   line_width=3, line_dash='dotdash')

        p.add_layout(Legend(), 'right')

        return p

    # Create the Panel components
    checkboxes = CheckboxGroup(labels=['EC', 'IATA', 'ICAO'], active=[])
    checkboxes_title = Div(text='<h3>Forecast Scenarios</h3>')
    checkbox1 = column(checkboxes_title, checkboxes)
    checkboxes2 = RadioGroup(labels=['Tech Freeze', 'TW Limit', 'BWB', 'Advanced TW', 'TTBW', 'Double Bubble'],
                             active=10)
    checkboxes2_title = Div(text='<h3>Future Technologies</h3>')
    checkbox2 = column(checkboxes2_title, checkboxes2)
    growth_rate_slider = Slider(title='Annual Growth Rate (%)', start=0, end=5, value=2, step=0.1)
    slf_slider = Slider(title='Seat Load Factor 2050 (%)', start=80, end=100, value=90, step=0.5)
    checkbox = row(checkbox1, checkbox2)

    def update_plot(attr, old, new):
        selected_targets = [checkboxes.labels[i] for i in checkboxes.active]
        selected_tech = [checkboxes2.labels[checkboxes2.active]]

        growth_rate = growth_rate_slider.value
        slf = slf_slider.value
        p = plot(selected_targets, growth_rate, target, selected_tech, freeze, limit, bwb, ttbw, advancedtw,
                 doublebubble, slf)
        dashboard[2] = p  # Assign the updated plot to the correct position

    # Link the callback functions to the components
    checkboxes.on_change('active', update_plot)
    checkboxes2.on_change('active', update_plot)
    growth_rate_slider.on_change('value', update_plot)
    slf_slider.on_change('value', update_plot)

    # Create the initial plot
    p = plot([], initial_growth_rate, target, ['TTBW'], freeze, limit, bwb, ttbw, advancedtw, doublebubble, initial_slf)

    # Create the Panel layout
    dashboard = pn.Column(
        pn.Row(checkbox),
        pn.Row(growth_rate_slider),
        pn.Row(p),
        pn.Row(slf_slider),
    )
    return dashboard


def create_db2():
    ida = pd.read_excel(r'Dashboard.xlsx')
    ida = ida.set_index('YOI')
    initial = pd.Series([0] * len(ida.columns), name=1959)
    ida.loc[1959] = 0
    ida = ida.sort_index()
    ida = ida + 100

    ida_tech = ida[['deltaC_Engine', 'deltaC_Aerodyn', 'deltaC_Structural', 'deltaC_Res', 'deltaC_Tot']]
    ida_tech = ida_tech.rename(columns={
        'deltaC_Engine': 'Engine',
        'deltaC_Aerodyn': 'Aerodynamic',
        'deltaC_Structural': 'Structural',
        'deltaC_Res': 'Residual',
        'deltaC_Tot': 'Overall'})
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
        if df == "Index Decomposition Analyis":
            df = ida_tech
            colors = ["dimgrey", 'darkblue', 'royalblue', 'steelblue', 'red',
                      "dimgrey", 'darkblue', 'royalblue', 'steelblue', 'red',
                      "dimgrey"]

        else:
            df = ida_ops
            colors = ["dimgrey", 'darkblue', 'royalblue', 'steelblue', 'lightblue', 'red',
                      "dimgrey", 'darkblue', 'royalblue', 'steelblue', 'lightblue', 'red',
                      "dimgrey"]

        df_dif_first = pd.DataFrame((df.loc[middle_year] - df.loc[start_year])).reset_index()
        df_dif_first.columns = ['Eff', 'Value']
        df_dif_first['Offset'] = df_dif_first['Value'].cumsum() - df_dif_first['Value'] + df.loc[start_year]['Overall']
        df_dif_first['Offset'].iloc[-1] = 0
        df_dif_first['ValueSum'] = df_dif_first['Value'].cumsum() + df.loc[start_year]['Overall']
        df_dif_first['ValueSum'].iloc[-1] = df_dif_first['Value'].iloc[-1] + df.loc[start_year]['Overall']

        df_dif_second = pd.DataFrame((df.loc[end_year] - df.loc[middle_year])).reset_index()
        df_dif_second.columns = ['Eff', 'Value']
        df_dif_second['Offset'] = df_dif_second['Value'].cumsum() - df_dif_second['Value'] + df.loc[middle_year][
            'Overall']
        df_dif_second['Offset'].iloc[-1] = 0
        df_dif_second['ValueSum'] = df_dif_second['Value'].cumsum() + df.loc[middle_year]['Overall']
        df_dif_second['ValueSum'].iloc[-1] = df_dif_second['Value'].iloc[-1] + df.loc[middle_year]['Overall']
        df_dif = pd.concat([df_dif_first, df_dif_second])

        df_dif['Eff'] = df_dif.groupby('Eff').cumcount().astype(str).replace('0', '') + '_' + df_dif['Eff']

        value = df_dif.loc[df_dif['Eff'] == '_Engine', 'Offset']
        overall_baseline = pd.DataFrame({'Eff': 'Overall', 'Value': value, 'Offset': 0, 'ValueSum': value})
        df_dif = pd.concat([overall_baseline, df_dif]).reset_index(drop=True)
        df_dif['Color'] = colors[:len(df_dif)]

        source = ColumnDataSource(df_dif)

        p = figure(x_range=df_dif['Eff'], title=f"Efficiency Improvements Between {start_year} and {end_year}",
                   x_axis_label='Timeline', y_axis_label='Efficiency Increase: Basis 1959', width=800, height=400, )

        eff = 'Eff'
        ops = '_Operational'
        ops = ops in df_dif[eff].values

        if ops:
            legend = Legend(items=[
                ("Overall", [p.square([1], [1], color="dimgrey")]),
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

        p.vbar(x='Eff', top='ValueSum', width=0.9, source=source, bottom='Offset', fill_color='Color',
               line_color='Color')
        p.add_layout(legend, 'right')
        p.xaxis.major_label_text_font_size = "0pt"

        start = Label(x=5, y=0, x_units='screen', y_units='screen', text=str(start_year), text_font_size='12pt',
                      text_color='black')
        middle = Label(x=270, y=0, x_units='screen', y_units='screen', text=str(middle_year), text_font_size='12pt',
                       text_color='black')
        end = Label(x=530, y=0, x_units='screen', y_units='screen', text=str(end_year), text_font_size='12pt',
                    text_color='black')
        p.add_layout(start)
        p.add_layout(middle)
        p.add_layout(end)
        line = Span(location=100, dimension='width', line_color='black', line_width=3, line_dash='dashed')
        p.add_layout(line)

        return p

    # Define the callback function for widget changes
    def update_plot(event):
        selected_variable = variable_widget.value
        if selected_variable == "Index Decomposition Analyis" or selected_variable == "Include Operational":
            start_year = int(start_year_widget.value)
            middle_year = int(middle_year_widget.value)
            end_year = int(end_year_widget.value)

            start_year_widget.options = [str(year) for year in range(1960, middle_year)]
            middle_year_widget.options = [str(year) for year in range(start_year + 1, end_year)]
            end_year_widget.options = [str(year) for year in range(middle_year + 1, 2021)]

            p = plot(start_year, middle_year, end_year, selected_variable)
            dashboard[-1] = p

    # Create slider widget
    start_year_widget = pn.widgets.Select(name="Start Year", options=[str(year) for year in range(1959, 2019)],
                                          value=str(1959))
    middle_year_widget = pn.widgets.Select(name="Middle Year", options=[str(year) for year in range(1960, 2020)],
                                           value=str(2000))
    end_year_widget = pn.widgets.Select(name="End Year", options=[str(year) for year in range(1961, 2021)],
                                        value=str(2020))

    # Create a selection widget
    variable_widget = pn.widgets.Select(name="Variable", options=["Index Decomposition Analyis", "Include Operational"])

    start_year = 1959
    middle_year = 2000
    end_year = 2020

    # Register the callback function for widget changes
    variable_widget.param.watch(update_plot, 'value')
    start_year_widget.param.watch(update_plot, 'value')
    middle_year_widget.param.watch(update_plot, 'value')
    end_year_widget.param.watch(update_plot, 'value')

    p = plot(start_year, middle_year, end_year, "Index Decomposition Analyis")

    years = pn.Row(start_year_widget, middle_year_widget, end_year_widget)
    # Create a layout for the widgets and plot
    dashboard = pn.Column(variable_widget, years, p)
    return dashboard

dashboard_container = pn.Column()

title = pn.pane.Markdown("Aircraft Efficiency Assessment", styles={'font-size': '24px', 'font-weight': 'bold'})

# Create a logo
psi = pn.pane.PNG('psilogo.png', width=150, height=150)
esa = pn.pane.PNG('esalogo.png', width=150, height=150)

# Create a panel to hold the title and logo
header = pn.Row(title, pn.layout.HSpacer(), esa, psi, align="center", sizing_mode="stretch_width")

line = pn.layout.Divider(width=800)

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
    else:
        raise ValueError("Invalid dashboard selection.")
    dashboard_container.clear()
    dashboard_container.append(dashboard)

# Set the initial dashboard to the "Historic Efficiency Decomposition" plot
dashboard = create_db1()
dashboard_container.append(dashboard)

selection = pn.widgets.RadioButtonGroup(options=['Forecast', 'Historic Efficiency Decomposition','Data', 'Author'], name='Select Dashboard', value='Forecast')
selection.param.watch(update_dashboard, 'value')

layout = pn.Column(header,line, selection, dashboard_container)
layout.servable()




await write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.globals.set('patch', msg.patch)
    self.pyodide.runPythonAsync(`
    state.curdoc.apply_json_patch(patch.to_py(), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.globals.set('location', msg.location)
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads(location)
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()