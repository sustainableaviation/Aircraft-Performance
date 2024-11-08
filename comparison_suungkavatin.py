
# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_excel(r"dashboard\data\polynoms.xlsx")
annual = pd.read_excel(r'dashboard\data\annualdata.xlsx')

data = data.loc[data['YOI']>=1960]
data = data.drop(columns=data.columns[0])
data = data.set_index('YOI')

first_row = data.iloc[0]
engine = first_row[0]
data = data.div(first_row)
data = 1/data

value2020 = data.loc[[2020]]
years = range(2020, 2051)

#calculate value for 2035 and 2045
ope2035 = 1/(301/engine)
ope2045 = 1/(337/engine)
limit = 1 /(288/engine)
nox = 1 / (272/engine)


# Create a DataFrame with constant values for each year
value2020 = pd.DataFrame(value2020, index=years)
first_row = value2020.iloc[0]
value2020 = value2020.fillna(first_row)
value2020.loc[value2020.index >= 2035, 'TSFC Cruise'] = ope2035
value2020.loc[value2020.index >= 2045, 'TSFC Cruise'] = ope2045

value2020['EU (MJ/ASK)1'] = value2020['TSFC Cruise']*value2020['L/D estimate']*value2020['OEW/Exit Limit']
value2020['Deviation'] = value2020['EU (MJ/ASK)']/value2020['EU (MJ/ASK)1']
value2020['EU (MJ/ASK)'] = value2020['EU (MJ/ASK)1']*value2020['Deviation'].iloc[0]

num_columns = len(data.columns)
fig, axs = plt.subplots(nrows=num_columns, ncols=1, figsize=(8,12), dpi=300)
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    'font.size': 10})

for i, column in enumerate(data.columns):
    axs[i].plot(data.index, data[column], color='blue')
    axs[i].set_title(column)
    axs[i].set_ylabel('$\eta$')
    axs[i].set_ylim(0, 1.1)
    axs[i].set_xlim(1960, 2050)
    if i == 0:
        axs[i].plot(data.index, data[column], color='blue', label = 'Historical Developments')
        axs[i].step(value2020.index, value2020[column], color='red', label='Su-ungkavatin et al.')
        axs[i].axhline(limit, color='black', label='Physical Limit')
        axs[i].axhline(nox, color='black', label='NOx Limit', linestyle='dashed')
        axs[i].legend()
    if i == 1 or i == 2:
        axs[i].plot(value2020.index, value2020[column], color='red')
    if i == 3:
        axs[i].step(value2020.index, value2020[column], color='red')

    axs[i].minorticks_on()
    axs[i].tick_params(axis='x', which='both', bottom=False)
    axs[i].tick_params(axis='y', which='both', bottom=False)

    axs[i].grid(which='both', axis='y', linestyle='-', linewidth=0.5)
    axs[i].grid(which='both', axis='x', linestyle='-', linewidth=0.5)

plt.xlabel('Year')
plt.tight_layout()
plt.savefig(r"database\graphs\graphssuungkavatin.png")



# Su-ungkavatin OPE in 2035: 58% in 2045: 65%, would translate into a TSFC Cruise at 240m/s of 9.6 and 8.57, which is both below our calculate values
# Would translate to values of 301% and 337% increased compared to the 1958 level (TSFC = 29.8)
# Our calculate theoretical limit would be an efficiency of thermal=0.6 and prop = 0.925 which suggests 0.555
# 0.555 is equal to a TSFC Cruise of 10.03 which would be a 288% increase compared to 1958 level

# The plot shows that Engine efficiency seems completely overestimated while aeordynamics are neglected
# Comparison with our forecast Scenarios: Difficult, we are modeling the fleet integration.
# Can't compare the energy usage on the fleet level with individual design concepts.

# With NOx Limit min TSFC Cruise is 10.95 which is a 272 percent increase

