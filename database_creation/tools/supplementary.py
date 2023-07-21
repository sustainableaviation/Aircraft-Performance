# here i will create the list used in the dictionary
from test_env.database_creation.tools import dict
import pandas as pd

#Most common airlines by ASM over the Last 30 years. The idea is to look only at the airlines with the most ASM. At the end we look at the 19 biggest airlines
T52 = pd.read_csv(r"C:\Users\PRohr\Desktop\Masterarbeit\Data\T_SCHEDULE_T2.csv")
T52 = T52.dropna(subset = ['AVL_SEAT_MILES_320','REV_PAX_MILES_140','AIRCRAFT_FUELS_921'])

T52 = T52.loc[T52['CARRIER_GROUP'] == 3] #this subgroup 3 contains all "Major Carriers"
T52 = T52.loc[T52['AIRCRAFT_CONFIG'] == 1] #subgroup 1 for aircraft passenger configuration
most_common_airlines = T52.groupby(['UNIQUE_CARRIER_NAME']).agg({'AVL_SEAT_MILES_320':'sum'})
most_common_airlines = most_common_airlines.sort_values(by='AVL_SEAT_MILES_320', ascending=False)
most_common_airlines = most_common_airlines.loc[most_common_airlines['AVL_SEAT_MILES_320']>= 10**11]
#What are the most common used aircraft types of these 19 airlines ?
#At the end we look at the 45 Aircraft types from the 19 Airlines with the most AVL over the period of the last 30 years.
airlines = dict.USAirlines().get_airlines()
T52 = T52.loc[T52['UNIQUE_CARRIER_NAME'].isin(airlines)]

aircraft_codes = pd.read_csv(r"/test_env/database_creation/rawdata/USDOT/L_AIRCRAFT_TYPE (1).csv")

most_common_aircrafts = pd.merge(T52, aircraft_codes, left_on='AIRCRAFT_TYPE', right_on='Code')
most_common_aircrafts = most_common_aircrafts.drop(['Code', 'AIRCRAFT_TYPE'], axis = 1)
most_common_aircrafts = most_common_aircrafts.groupby(['Description']).agg({'AVL_SEAT_MILES_320':'sum'})
most_common_aircrafts = most_common_aircrafts.sort_values(by='AVL_SEAT_MILES_320', ascending=False)
#take all aircraft with more than 10^11 ASM and manually add some Aircraft to the list, such that there are a bit more recent datapoint of AC which have not been in service for a long time.
new_aircrafts = ['Boeing B737 Max 900','Airbus Industrie A330-900','Boeing 787-10 Dreamliner','Boeing B737 Max 800', 'Airbus Industrie A350-900', 'Airbus Industrie A320-200n', 'Airbus Industrie A321-200n','Airbus Industrie A-318', 'Airbus Industrie A310-200C/F']
most_common_aircrafts = most_common_aircrafts.loc[(most_common_aircrafts['AVL_SEAT_MILES_320']>= 10**11) | (most_common_aircrafts.index.isin(new_aircrafts))]
most_common_aircrafts.to_excel('used_aircrafts.xlsx')


