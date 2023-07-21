import pandas as pd

fuel_emissions = pd.read_excel(r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\database_creation\rawdata\emissions\ICAO_Carbon.xlsx', sheet_name='Tabelle1')
abbreviations = pd.read_excel(r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\database_creation\rawdata\emissions\ICAO_Carbon.xlsx', sheet_name='aircraftIcaoIata')
data = pd.read_excel(r'C:\Users\PRohr\Desktop\Masterarbeit\Python\test_env\Databank.xlsx')
data = data[['Name', 'Pax']]

new_header = fuel_emissions.iloc[1]
fuel_emissions = fuel_emissions[2:]  # Exclude the second row from the DataFrame

# Set the new header
fuel_emissions.columns = new_header

# Reset the index
fuel_emissions = fuel_emissions.reset_index(drop=True)

fuel_emissions = fuel_emissions.merge(abbreviations, left_on='Code', right_on='IATA')
fuel_emissions = fuel_emissions.drop(columns=['IATA', 'ICAO', 'Code'])
fuel_emissions = fuel_emissions.set_index('NAME')
fuel_emissions = fuel_emissions.div(fuel_emissions.columns.astype(float), axis=1)
fuel_emissions = fuel_emissions/1.852 # nautical miles to km
fuel_emissions = fuel_emissions*43.1 #MJ/kg of Jet fuel A
