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
  const env_spec = ['https://cdn.holoviz.org/panel/1.0.2/dist/wheels/bokeh-3.1.1-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.0.2/dist/wheels/panel-1.0.2-py3-none-any.whl', 'pyodide-http==0.2.1', 'Authors', 'Data', 'Efficiency', 'Future', 'import_ipynb', 'numpy', 'pandas']
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

#!/usr/bin/env python
# coding: utf-8

# In[2]:


import panel as pn
import pandas as pd
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, RadioButtonGroup, CustomJS
from bokeh.models import CheckboxGroup, Legend, Div, RadioGroup
from bokeh.transform import dodge
from bokeh.transform import cumsum
from bokeh.models import FactorRange, Select, Slider
from bokeh.palettes import Category10
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues
from bokeh.layouts import column
from bokeh.layouts import row
import import_ipynb
from Future import create_db1
from Efficiency import create_db2
from Authors import about_authors
from Data import data


import warnings 
warnings.filterwarnings("ignore")
pn.extension(design='material')


# In[3]:


dashboard_container = pn.Column()

title = pn.pane.Markdown("Aircraft Efficiency Assessment", style={'font-size': '24px', 'font-weight': 'bold'})

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


# In[ ]:





# In[ ]:






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