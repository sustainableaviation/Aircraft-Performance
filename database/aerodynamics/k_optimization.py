import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

# Create the range of AR values
aircraft_data = pd.read_excel(r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\Databank.xlsx')
aircraft_data = aircraft_data.dropna(subset='Aspect Ratio')
aircraft_data = aircraft_data.groupby(['Name'], as_index=False).agg({'Aspect Ratio':'mean', 'MTOW':'mean','OEW':'mean', })

aircraft_data = aircraft_data.dropna()
aircraft_data['Wing Weight Estimation'] = aircraft_data['OEW']/4
aircraft_data['Wing Weight Estimation per AR'] = aircraft_data['Wing Weight Estimation']/aircraft_data['Aspect Ratio']
aircraft_data = aircraft_data.loc[aircraft_data['Name']=='737-900']
values = np.arange(6, 30, 0.1)

ar_values = []
bestar_values = []
for value in values:
    aircraft_data['Wing Weight'] = aircraft_data['Wing Weight Estimation per AR']*value
    aircraft_data['MTOW new'] = aircraft_data['MTOW']- aircraft_data['Wing Weight Estimation']+ aircraft_data['Wing Weight']
    aircraft_data['Best AR'] = aircraft_data['MTOW new']**2/value
    ar_values.append(aircraft_data['Best AR'])
# Create a pandas DataFrame to store the e and k values
df = pd.DataFrame({'AR': values, 'Best AR': ar_values})


# Plot k vs AR using matplotlib


#smallest k appears to be at an aspect ratio of around 22-23 which is not possible due to structural limitations so what is the closest to it?


