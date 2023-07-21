import pandas as pd
import math
import numpy as np

aircraft = pd.read_excel(r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\database_creation\rawdata\civiljet_aircraft_design\all_aircraft.xlsx')
aircraft = aircraft.set_index('Manufacturer')
aircraft.loc['Type'] = aircraft.loc['Type'].astype(str)+ aircraft.loc['Model'].astype(str)
aircraft = aircraft.rename(columns=aircraft.iloc[0]).drop(aircraft.index[0])
aircraft = aircraft.T

#Get Reynolds Number
flight_speed = 240
kinematic_viscosity = 9.22*10**-6
aircraft['Fuselage: Re'] = aircraft['Fuselage: Length (m)']*flight_speed/kinematic_viscosity
aircraft['Wings: Re'] = aircraft['Wing: MAC (m)']*flight_speed/kinematic_viscosity
aircraft['Vertical Tail: Re'] = (aircraft['Vertical Tail: Area (m²)']/aircraft['Vertical Tail: Height (m)'])*flight_speed/kinematic_viscosity
aircraft['Horizontal Tail: Re'] = (aircraft['Horizontal Tail: Area (m²)']/aircraft['Horizontal Tail: Span (m)'])*flight_speed/kinematic_viscosity
aircraft['Nacelle: Re'] = aircraft['Nacelle: Length (m)']*flight_speed/kinematic_viscosity
#Get CF

aircraft['Fuselage: Cf'] = 0.455/(aircraft['Fuselage: Re'].apply(lambda x: np.log10(x)))**2.58
aircraft['Wings: Cf'] = 0.455/(aircraft['Wings: Re'].apply(lambda x: np.log10(x)))**2.58
aircraft['Vertical Tail: Cf'] = 0.455/(aircraft['Vertical Tail: Re'].apply(lambda x: np.log10(x)))**2.58
aircraft['Horizontal Tail: Cf'] = 0.455/(aircraft['Horizontal Tail: Re'].apply(lambda x: np.log10(x)))**2.58
aircraft['Nacelle: Cf'] = 0.455/(aircraft['Nacelle: Re'].apply(lambda x: np.log10(x)))**2.58


#Get F

aircraft['factor'] = aircraft['Fuselage: Length (m)']/((4/math.pi)*aircraft['Fuselage: Height (m)'])**0.5
aircraft['Fuselage: F'] = 1 + 2.2/(aircraft['factor']**1.5) - 0.9/(aircraft['factor']**3)
aircraft['Wing: Average (t/c) %'] = aircraft['Wing: Average (t/c) %'].astype(float)

aircraft['F_star'] = 1 + 3.3*(aircraft['Wing: Average (t/c) %']/100) -0.008*(aircraft['Wing: Average (t/c) %']/100)**2 + 27*(aircraft['Wing: Average (t/c) %']/100)**3
aircraft['Wings: F'] = (aircraft['F_star']-1)*aircraft['Wing: Average (t/c) %'].apply(lambda x: np.cos(np.deg2rad(x)) ** 2) +1
aircraft['Vertical Tail: F'] = 1.4
aircraft['Horizontal Tail: F'] = 1.4

# no tail t/c values given therefore cant calcualte Fstar
# nacelle F*Q = 1.25

#Cdo

aircraft['Fuselage: Cd0'] = aircraft['Fuselage: F']*aircraft['Fuselage: Cf']*(aircraft['Fuselage: Length (m)']*(math.pi)*aircraft['Fuselage: Height (m)'])/aircraft['Wing: Area (m²)']
aircraft['Wings: Cd0'] = aircraft['Wings: F']*aircraft['Wings: Cf']*2*aircraft['Wing: Area (m²)']/aircraft['Wing: Area (m²)']