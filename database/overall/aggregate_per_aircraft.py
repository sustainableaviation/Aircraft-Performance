import pandas as pd

def calculate():

    # Load Data and only keep relevant Parameters
    aircrafts = pd.read_excel(r'Databank.xlsx')
    aircrafts = aircrafts[['Company',
                           'Name',
                           'Type',
                           'YOI',
                           'MTOW,integer,kilogram',
                           'MZFW,integer,kilogram',
                           'Exit Limit',
                           'Fuel capacity,integer,litre',
                           'TSFC Cruise',
                           'Engine Efficiency',
                           'EU (MJ/ASK)',
                           'OEW/Exit Limit',
                           'L/D estimate',
                           'Aspect Ratio',
                           'k',
                           'Wingspan,float,metre',
                           'prop_eff',
                           'thermal_eff',
                           'c_L',
                           'c_D',
                           'c_Di',
                           'c_D0',
                           'Pax',
                           'Height,float,metre',
                           'B/P Ratio',
                           'Overcome Thrust']]
    aircrafts = aircrafts.groupby(['Company','Name','Type','YOI'], as_index=False).agg('mean')
    aircrafts.to_excel(r'Databank.xlsx', index=False)





