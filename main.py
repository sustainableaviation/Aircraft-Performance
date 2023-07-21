import database_creation.tools.atmospheric_conditions
import database_creation.operational.airtimeefficiency
import database_creation.overall.overallefficiency
import database_creation.emissions.icaoemssions
import database_creation.emissions.to_vs_cruise_sfc
import database_creation.overall.aircraft_engine_configurations
import database_creation.emissions.engine_statistics
import database_creation.emissions.thermal_efficiency
import database_creation.emissions.propulsive_efficiency
import database_creation.structural.structuralefficiency
import database_creation.operational.seats
import database_creation.operational.seatloadfactor
import database_creation.aerodynamics.aerodynamicefficiency
import database_creation.aerodynamics.aerodynamic_statistics
import database_creation.emissions.therm_prop_eff
import database_creation.overall.aggregate_per_aircraft
import database_creation.index_decomposition.technological
import database_creation.index_decomposition.engine
import database_creation.index_decomposition.technooperational
import database_creation.aerodynamics.payload_range
import database_creation.dashboard_prep.future_scen
import database_creation.dashboard_prep.fleet_behavior
import warnings
import datetime
import os
current_date = datetime.datetime.now()
datestamp = current_date.strftime("%Y-%m-%d")
warnings.filterwarnings("ignore")

# Create output folder with today's date and save graphs here
base_folder = r'database_creation\graphs'
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

print(' --> [START]')
print(' --> [CREATE AIRCRAFT DATABASE]: Calculate Atmospheric Conditions...')
air_density, flight_vel, temp = database_creation.tools.atmospheric_conditions.calculate(altitude, mach)
print(' --> [CREATE AIRCRAFT DATABASE]: Calculate Airtime Efficiency...')
database_creation.operational.airtimeefficiency.calculate(flight_vel, savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Load Demand Data from the US DOT...')
database_creation.overall.overallefficiency.calculate(savefig, km, heatingvalue_gallon, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Calibrate Linear Fit for Take-Off vs Cruise TSFC...')
linear_fit = database_creation.emissions.to_vs_cruise_sfc.calibrate(savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Scale Take-Off TFSC from ICAO emissions Databank to Cruise TSFC ...')
database_creation.emissions.icaoemssions.calculate(linear_fit)
print(' --> [CREATE AIRCRAFT DATABASE]: Add all Aircraft-Engine combinations and its Parameters ...')
limit_tsfc = database_creation.overall.aircraft_engine_configurations.calculate(heatingvalue_kg, air_density, flight_vel, savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Create Graphs for Engine Statistics ...')
database_creation.emissions.engine_statistics.calculate(savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Add Seats per Aircraft from US DOT ...')
database_creation.operational.seats.calculate()
print(' --> [CREATE AIRCRAFT DATABASE]: Calculate Structural Efficiency...')
database_creation.structural.structuralefficiency.calculate(savefig, folder_path)
print(' --> [CREATE ANNUAL VALUES]: Calculate Seat Load Factor and Airborne Efficiency ...')
database_creation.operational.seatloadfactor.calculate(savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Calculate L/D Ratio from Breguet Range Equation...')
limit_aero = database_creation.aerodynamics.aerodynamicefficiency.calculate(savefig, air_density, flight_vel, gravity, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Split Engine Efficiency into Thermal and Propulsive Efficiency...')
database_creation.emissions.therm_prop_eff.calculate(savefig, flight_vel, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Calculating maximal Thermal Efficiency for a Turbofan Brayton-Cycle')
database_creation.emissions.thermal_efficiency.calculate(savefig, folder_path, temp)
print(' --> [CREATE AIRCRAFT DATABASE]: Calculating maximal Propulsive Efficiency fregarding Thrust Level and Fan Diameter')
database_creation.emissions.propulsive_efficiency.calculate(savefig, folder_path, flight_vel, air_density)
print(' --> [CREATE AIRCRAFT DATABASE]: Summarize Data per Aircraft Type')
database_creation.overall.aggregate_per_aircraft.calculate()
print(' --> [CREATE AIRCRAFT DATABASE]: Create Graphs for Aerodynamic Statistics...')
database_creation.aerodynamics.aerodynamic_statistics.calculate(savefig, folder_path)
print(' --> [CREATE AIRCRAFT DATABASE]: Create Payload Range Diagram for A320-200 and B777-200...')
database_creation.aerodynamics.payload_range.calculate(savefig, folder_path)
print(' --> [INDEX DECOMPOSITION ANALYSIS]: LMDI for Technical Sub-Efficiencies')
database_creation.index_decomposition.technological.calculate(savefig, folder_path)
print(' --> [INDEX DECOMPOSITION ANALYSIS]: LMDI for Technical and Operational Sub-Efficiencies')
database_creation.index_decomposition.technooperational.calculate(savefig, folder_path)
print(' --> [INDEX DECOMPOSITION ANALYSIS]: LMDI for Engine Sub-Efficiencies')
database_creation.index_decomposition.engine.calculate(savefig, folder_path)
print(' --> [PREPARE DASHBOARD]: Create Future Scenarios')
database_creation.dashboard_prep.future_scen.calculate(limit_tsfc, limit_aero, savefig, folder_path)
print(' --> [FINISH]')
