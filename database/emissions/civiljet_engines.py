import pandas as pd
import os
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from not_maintained.tools import plot

# Create an empty dataframe to hold the data
engines = pd.read_excel(r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\database_creation\rawdata\civiljet_aircraft_design\all_engines.xlsx')

engines = engines.T
engines.columns = engines.iloc[0]
engines = engines[1:]
engines = engines[['CRUISE Sfc lb/hr/lb', 'TO SFC (lb/hr/lb) ', 'In service date']]
engines = engines.dropna()
engines['CRUISE Sfc lb/hr/lb'] = engines['CRUISE Sfc lb/hr/lb']*101972/3600
engines['TO SFC (lb/hr/lb) '] = engines['TO SFC (lb/hr/lb) ']*101972/3600
engines = engines.reset_index()
engines['In service date'] = engines['In service date'].str.replace(r'\D', '', regex=True)
engines.to_excel(r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\database_creation\rawdata\civiljet_aircraft_design\all_engines2.xlsx')

