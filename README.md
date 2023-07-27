# Aircraft Performance Modelling Tool 
## Repository Structure 
## [Database](./database)
This folder contains all the files executed by the [main.py](main.py). Further, the folder [rawdata](database/rawdata) contains all Input Data and in the 
folder [graphs](database/graphs), all created figures will be saved.

### [main.py](main.py) 
This is the main file, which executes the modelling pipeline. The Output Folder for all Graphs and all constants can be specified here. It will create a new output folder for the graphs for each day a simulation is carried out in order to not overwrite the existing ones. 
You can choose the Mach number and the Altitude for which the analysis should be carried out. 
As an output the Excel File Databank.xlsx will be produced. 

* [atmospheric_conditions](database/tools/atmospheric_conditions.py): Calculates the Air density, Flight velocity and Temperature
* [airtimeefficiency](database/operational/airtimeefficiency.py): Calculates the Airtime Efficiency
* [overallefficiency](database/overall/overallefficiency.py) : Uses US DOT Schedule T2 and Data from Lee et al. to calculate Overall Efficiency regarding MJ/ASK and creates the Databank
* [to_vs_cruise_sfc](database/emissions/to_vs_cruise_sfc.py) : Using different sources, Engines where both T/O and Cruise TSFC is known are gathered and a calibration between T/O and Cruise fuel consumption is made. 
* [icaoemssions](database/emissions/icaoemssions.py): Scales the T/O TSFC from the ICAO Emissions Databank to Cruise TSFC
* [aircraft_engine_configurations](database/overall/aircraft_engine_configurations.py) : [Aircraft Database](https://aircraft-database.com/) is used to gather all relevant Aircraft and engine parameters, and aswell Aircraft-Engine combinations. The Engines are then matched to the engine of the ICAO Emissions Databank to connect the Cruise TSFC to the Aircraft. Finally, all values are added to the Databank
* [engine_statistics](database/emissions/engine_statistics.py): Calculates and Plots some Engine Statistics regarding Dry Weight, Bypass Ratio, Pressure Ratio...
* [structuralefficiency](database/structural/structuralefficiency.py) : Calculates Structural Efficiency in OEW/Pax Exit Limit and adds it to the Databank
* [seats](database/operational/seats.py) : Based on Data from the US DOT, real seating capacities for Aircraft are averaged and added to the Databank
* [seatloadfactor](database/operational/seatloadfactor.py) : SLF measured by the US DOT and the ICAO are gathered. 
* [aerodynamicefficiency](database/aerodynamics/aerodynamicefficiency.py) : Using the Breguet Range Equation and Data regarding the Weight and Range of Aircraft from Airport Planning Manuals the Aerodynamic Efficiency is calculated. To do so, the TSFC calculated before is used. The results are then added to the Databank. 
* [therm_prop_eff](database/emissions/therm_prop_eff.py) : This File splits the Engine Efficiency into Propulsive and Thermal Efficiency by calculating the Propulsive Efficiency, assuming that Propulsive efficiency * Thermal efficiency = Engine efficiency. The values are then added to the Databank.   
* [thermal_efficiency](database/emissions/thermal_efficiency.py) : Calculates maximal thermal efficiency based on a Brayton Cycle
* [propulsive_efficiency](database/emissions/propulsive_efficiency.py) : Calculates maximal propulsive efficiency based on the fan diameter and the required thrust
* [aggregate_per_aircraft](database/overall/aggregate_per_aircraft.py) : The Databank contains now multiple entries for each Aircraft, accounting for different Engines, different OEW and MTOW series. This file groups all the data on Aircraft Level. 
* [aerodynamic_statistics](database/aerodynamics/aerodynamic_statistics.py) : Creates Plots regarding the FAA Box Limit and the evolution of AR
* [payload_range](database/aerodynamics/payload_range.py) : Creates Payload Range Diagrams for the A320 and the B777-200
* [index_decomposition](database/index_decomposition/technological.py) : Decomposes the Technical Efficiency Improvements MJ/ASK into Structural, Aerodynamic, Engine and Residual Efficiency.  
* [index_decomposition_operational](database/index_decomposition/technooperational.py) : Integrates the SLF to calculate MJ/RPK and decomposes the efficiency gains into Structural, Aerodynamic, Engine, Operational and Residual.
* [future_scen](./database/dashboard_prep/future_scen.py) : Calculate Efficiency and CO2 emissions for Future Aircraft Scenarios
### [Tools](database/tools)
The tools folder contains some additionally helpful files, such as plotting properties or dictionaries to match the aircraft names from the different sources.

## [Dashboard](./dashboard)
All the input files for the dashboard are generated during the modelling pipeline and will be directly saved in this folder. To generate the dashboard, the
[main_db.ipynb](dashboard/main_db.ipynb) file should be executed in Jupyter Notebook. 

The Dashboard contains the following sites: 

* Future Scenarios: Produces future CO2 emission scenarios based on the chosen technology, SLF and ATM improvements and annual growth rate. 
* Historical Efficiency Improvements: Shows the Results of the IDA
* Overall Efficiency: Shows the results for the historical overall efficiency improvements
* Data: DataFrame showing all Sub-Efficiencies for aircraft
* Author: Some infos about the Authors


## Quickstart
### Setup Repository
1. Clone this repository
```bash
git clone https://github.com/sustainableaviation/Aircraft-Performance.git
```
2. Install all needed Packages
### Run Code
3. Head over to the [main.py](main.py)  File and execute the simulation
4. Push the changes into the GitHub repository
4. Use the terminal and type 
```bash
start jupyter notebook
```
5. Head over to the [main_db.ipynb](dashboard/main_db.ipynb) and execute to see the dashboard