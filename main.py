# %%
import database.tools.atmosphere
import database.operational.airtimeefficiency
import database.overall.overallefficiency
import database.emissions.icaoemssions
import database.emissions.to_vs_cruise_sfc
import database.overall.aircraft_engine_configurations
import database.emissions.engine_statistics
import database.emissions.thermal_efficiency
import database.emissions.propulsive_efficiency
import database.structural.structuralefficiency
import database.operational.seats
import database.operational.seatloadfactor
import database.aerodynamics.aerodynamicefficiency
import database.aerodynamics.aerodynamic_statistics
import database.emissions.therm_prop_eff
import database.overall.aggregate_per_aircraft
import database.index_decomposition.technological
import database.index_decomposition.technooperational
import database.aerodynamics.payload_range
import database.dashboard_prep.future_scen
import database.index_decomposition.waterfall_charts
import warnings
import datetime
import os
current_date = datetime.datetime.now()
datestamp = current_date.strftime("%Y-%m-%d")
warnings.filterwarnings("ignore")

# Create output folder with today's date and save graphs here
base_folder = r'database\graphs'
folder_path = os.path.join(base_folder, datestamp)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Parameters
savefig = True
mach = 0.82
altitude = 10500  # m

# Constants
km = 1.609344  # miles
heatingvalue_gallon = 142.2  # 142.2 MJ per Gallon of kerosene
heatingvalue_kg = 43.1  # MJ/kg
gravity = 9.81  # m/s^2

# COMPLETE
# print(' --> [START]')
# print(' --> [CREATE AIRCRAFT DATABASE]: Calculate Atmospheric Conditions...')
# air_density, flight_vel, temp = database.tools.atmosphere.calculate(altitude, mach)


print(' --> [CREATE AIRCRAFT DATABASE]: Calculate Airtime Efficiency...')
database.operational.airtimeefficiency.calculate(flight_vel, savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Load Demand Data from the US DOT...')
database.overall.overallefficiency.calculate(savefig, km, heatingvalue_gallon, folder_path)

# COMPLETE
# print(' --> [CREATE AIRCRAFT DATABASE]: Calibrate Linear Fit for Take-Off vs Cruise TSFC...')
# linear_fit = database.emissions.to_vs_cruise_sfc.calibrate(savefig, folder_path)
# print(' --> [CREATE AIRCRAFT DATABASE]: Scale Take-Off TFSC from ICAO emissions Databank to Cruise TSFC ...')
# database.emissions.icaoemssions.calculate(linear_fit)

# ONGOING
print(' --> [CREATE AIRCRAFT DATABASE]: Add all Aircraft-Engine Combinations and its Parameters ...')
limit_tsfc = database.overall.aircraft_engine_configurations.calculate(heatingvalue_kg, air_density, flight_vel, savefig, folder_path)


print(' --> [CREATE AIRCRAFT DATABASE]: Create Graphs for Engine Statistics ...')
database.emissions.engine_statistics.calculate(savefig, folder_path)

print(' --> [CREATE AIRCRAFT DATABASE]: Add Seats per Aircraft from US DOT ...')
database.operational.seats.calculate()
print(' --> [CREATE AIRCRAFT DATABASE]: Calculate Structural Efficiency...')
database.structural.structuralefficiency.calculate(savefig, folder_path)
print(' --> [CREATE ANNUAL VALUES]: Calculate Seat Load Factor and Airborne Efficiency ...')
database.operational.seatloadfactor.calculate(savefig, folder_path)

# ONGOING
print(' --> [CREATE AIRCRAFT DATABASE]: Calculate L/D Ratio from Breguet Range Equation...')
limit_aero = database.aerodynamics.aerodynamicefficiency.calculate(savefig, air_density, flight_vel, gravity, folder_path)


print(' --> [CREATE AIRCRAFT DATABASE]: Split Engine Efficiency into Thermal and Propulsive Efficiency...')
database.emissions.therm_prop_eff.calculate(savefig, flight_vel, folder_path)

# ONGOING
print(' --> [CREATE AIRCRAFT DATABASE]: Calculating Maximum Thermal Efficiency for a Turbofan Brayton-Cycle')
database.emissions.thermal_efficiency.calculate(savefig, folder_path, temp)
print(' --> [CREATE AIRCRAFT DATABASE]: Calculating Maximum Propulsive Efficiency fregarding Thrust Level and Fan Diameter')
database.emissions.propulsive_efficiency.calculate(savefig, folder_path, flight_vel, air_density)


print(' --> [CREATE AIRCRAFT DATABASE]: Summarize Data per Aircraft Type')
database.overall.aggregate_per_aircraft.calculate()
print(' --> [CREATE AIRCRAFT DATABASE]: Create Graphs for Aerodynamic Statistics...')
database.aerodynamics.aerodynamic_statistics.calculate(savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Create Payload Range Diagram for A320-200 and B777-200...')
database.aerodynamics.payload_range.calculate(savefig, folder_path)
print(' --> [INDEX DECOMPOSITION ANALYSIS]: LMDI for Technical Sub-Efficiencies')
database.index_decomposition.technological.calculate(savefig, folder_path)
print(' --> [INDEX DECOMPOSITION ANALYSIS]: LMDI for Technical and Operational Sub-Efficiencies')
database.index_decomposition.technooperational.calculate(savefig, folder_path)
print(' --> [INDEX DECOMPOSITION ANALYSIS]: Create Waterfall Charts')
database.index_decomposition.waterfall_charts.calculate(savefig, folder_path)
print(' --> [PREPARE DASHBOARD]: Create Future Scenarios and Model Fleet Integration')
database.dashboard_prep.future_scen.calculate(limit_tsfc, limit_aero, savefig, folder_path)
print(' --> [FINISH]')
