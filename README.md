# Aircraft Performance Code Documentation
## Repository Structure
All the relevant code is in the test_env folder. 
### Database Creation
The folder database_creation contains all the files executed by the master.py. Further, the folder rawdata contains all Input Data and in the 
folder "graphs", all created figures will be saved.

### master.py 
This is the main file, which executes the modelling pipeline. The Output Folder for all Graphs and all constants can be specified here. It will create a new output folder for the graphs for each day a simulation is carried out in order to not overwrite the existing ones. 
You can choose the Mach number and the Altitude for which the analysis should be carried out. 
As an output the Excel File Databank.xlsx will be produced.

* [atmospheric_conditions](test_env/database_creation/tools/atmospheric_conditions.py): Calculates the Air density, Flight velocity and Temperature
* [airtimeefficiency](test_env/database_creation/operational/airtimeefficiency.py): Calculates the Airtime Efficiency
* [overallefficiency](test_env/database_creation/overall/overallefficiency.py) : Uses US DOT Schedule T2 and Data from Lee et al. to calculate Overall Efficiency regarding MJ/ASK and creates the Databank
* [to_vs_cruise_sfc](test_env/database_creation/emissions/to_vs_cruise_sfc.py) : Using different sources, Engines where both T/O and Cruise TSFC is known are gathered and a calibration between T/O and Cruise fuel consumption is made. 
* [icaoemssions](test_env/database_creation/emissions/icaoemssions.py): Scales the T/O TSFC from the ICAO Emissions Databank to Cruise TSFC
* [aircraft_engine_configurations](test_env/database_creation/overall/aircraft_engine_configurations.py) : [Aircraft Database](https://aircraft-database.com/) is used to gather all relevant Aircraft and engine parameters, and aswell Aircraft-Engine combinations. The Engines are then matched to the engine of the ICAO Emissions Databank to connect the Cruise TSFC to the Aircraft. Finally, all values are added to the Databank
* [engine_statistics](test_env/database_creation/emissions/engine_statistics.py): Calculates and Plots some Engine Statistics regarding Dry Weight, Bypass Ratio, Pressure Ratio...
* [structuralefficiency](test_env/database_creation/structural/structuralefficiency.py) : Calculates Structural Efficiency in OEW/Pax Exit Limit and adds it to the Databank
* [seats](test_env/database_creation/operational/seats.py) : Based on Data from the US DOT, real seating capacities for Aircraft are averaged and added to the Databank
* [seatloadfactor](test_env/database_creation/operational/seatloadfactor.py) : SLF measured by the US DOT and the ICAO are gathered. 
* [aerodynamicefficiency](test_env/database_creation/aerodynamics/aerodynamicefficiency.py) : Using the Breguet Range Equation and Data regarding the Weight and Range of Aircraft from Airport Planning Manuals the Aerodynamic Efficiency is calculated. To do so, the TSFC calculated before is used. The results are then added to the Databank. 
* [therm_prop_eff](test_env/database_creation/emissions/therm_prop_eff.py) : This File splits the Engine Efficiency into Propulsive and Thermal Efficiency by calculating the Propulsive Efficiency, assuming that Propulsive efficiency * Thermal efficiency = Engine efficiency. The values are then added to the Databank.   
* [aggregate_per_aircraft](test_env/database_creation/overall/aggregate_per_aircraft.py) : The Databank contains now multiple entries for each Aircraft, accounting for different Engines, different OEW and MTOW series. This file groups all the data on Aircraft Level. 
* [aerodynamic_statistics](test_env/database_creation/aerodynamics/aerodynamic_statistics.py) : Creates Plots regarding the FAA Box Limit and the evolution of AR
* [payload_range](test_env/database_creation/aerodynamics/payload_range.py) : Creates Payload Range Diagrams for the A320 and the B777-200
* [index_decomposition](test_env/database_creation/index_decomposition/technological.py) : Decomposes the Technical Efficiency Improvements MJ/ASK into Structural, Aerodynamic, Engine and Residual Efficiency.  
* [index_decomposition_operational](test_env/database_creation/index_decomposition/technooperational.py) : Integrates the SLF to calculate MJ/RPK and decomposes the efficiency gains into Structural, Aerodynamic, Engine, Operational and Residual.
* [index_decomposition_engine](test_env/database_creation/index_decomposition/engine.py) : Decomposes Engine Efficiency into Thermal- and Propulsive- Efficiency
* [future_scen](test_env.database_creation.dashboard_prep.future_scen.py) : Calculate Efficiency and CO2 emissions for Future Aircraft Scenarios
* 
### Tools
The tools folder contains some additionally helpful files, such as plotting properties or dictionaries to match the aircraft names from the different sources.

## Quickstart
### Setup Repository
1. Clone this repository
```bash
git clone https://github.com/rohrerph/Master_Thesis_Codes.git
```
2. Install all needed Packages
3. Head over to the test_env.master.py File and execute the simulation