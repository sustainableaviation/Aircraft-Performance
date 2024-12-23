# %%

#All aircraft used for the extraction of the T2 Data.
class AirplaneModels:
    def __init__(self):
        self.models = {"Boeing 757-200": 1984,
                       "Boeing 767-300/300ER": 1987,
                       "Boeing 777-200ER/200LR/233LR": 1995,
                       "Airbus Industrie A320-100/200": 1988,
                       "Boeing 767-200/ER/EM": 1983,
                       "Boeing 737-800": 1998,
                       "Airbus Industrie A319": 1996,
                       "Boeing 737-300": 1984,
                       "McDonnell Douglas DC9 Super 80/MD81/82/83/88": 1980,
                       "Boeing 747-400": 1989,
                       "Boeing 737-700/700LR/Max 7": 1997,
                       "Boeing 727-200/231A": 1967,
                       "Airbus Industrie A330-200": 1998,
                       "Boeing 767-400/ER": 2000,
                       "McDonnell Douglas DC-10-30": 1972,
                       "Airbus Industrie A321/Lr": 1994,
                       "Boeing 737-400": 1988,
                       "Boeing 737-100/200": 1967,
                       "Boeing 737-500": 1990,
                       "Boeing 747-200/300": 1970,
                       "McDonnell Douglas MD-11": 1990,
                       "Boeing 757-300": 1999,
                       "Boeing 737-900": 2001,
                       "Boeing 747-100": 1970,
                       "Canadair RJ-700": 1999,
                       "B787-800 Dreamliner": 2011,
                       "McDonnell Douglas DC-9-30": 1966,
                       "Airbus Industrie A330-300/333": 1992,
                       "Embraer-145": 1996,
                       "Boeing 777-300/300ER/333ER": 1998,
                       "Embraer 190": 2004,
                       "B787-900 Dreamliner": 2014,
                       "McDonnell Douglas DC-10-10": 1970,
                       "Lockheed L-1011-1/100/200": 1973,
                       "Airbus Industrie A300-600/R/CF/RCF": 1984,
                       "Boeing 737-900ER": 2007,
                       "Canadair RJ-200ER /RJ-440": 1996,
                       "McDonnell Douglas MD-90": 1995,
                       "McDonnell Douglas DC-10-40": 1972,
                       "Boeing 717-200": 1999,
                       "Embraer ERJ-175": 2005,
                       "Boeing B737 Max 800": 2017,
                       "Boeing 787-10 Dreamliner": 2018,
                       "Airbus Industrie A330-900": 2018,
                       "Boeing B737 Max 900": 2018,
                       'Airbus Industrie A350-900': 2015,
                       'Airbus Industrie A320-200n': 2016,
                       'Airbus Industrie A-318': 2003,
                       'Airbus Industrie A300B/C/F-100/200': 1974,
                       'Airbus Industrie A310-200C/F' : 1983,
                       'Airbus Industrie A321-200n':2017,
                       'Boeing 727-100':1964,
                       'Boeing 737-200C':1968,
                       'Boeing 747SP':1976,
                       'Canadair CRJ 900':2001,
                       'Embraer-135':1999}

    def get_models(self):
        return self.models


#map names from the Aircraft-Database to the abbreviation names for my Database
class aircraftdata:
    def __init__(self):
        self.aircraftsfromdatabase = {'A340-500':'A340-500',
                                      '707-100B':'B707-100B/300',
                                      '707-300B':'B707-300',
                                      '717-200':'717-200',
                                      '720B': 'B720-000' ,
                                      '727-100': 'B727-100',
                                      '727-100RE Super 27': 'B727-100',
                                      '727-200':'B727-200/231A',
                                      '737-100':'B737-100/200',
                                      '737-200':'B737-100/200',
                                      '737-200C':'737-200C',
                                      '737-300':'B737-300',
                                      '737-400':'B737-400',
                                      '737-500':'B737-500/600',
                                      '737-600':'B737-500/600',
                                      '737-700':'737-700/700LR/Max 7',
                                      '737-700 IGW':'737-700/700LR/Max 7',
                                      '737-8':'B737 Max 800',
                                      '737-800':'737-800',
                                      '737-9':'B737 Max 900',
                                      '737-900':'737-900',
                                      '737-900ER':'737-900ER',
                                      '747-100':'747-100',
                                      '747-200B':'B747-200/300',
                                      '747-200C':'B747-200/300',
                                      '747-300':'B747-200/300',
                                      '747-400':'B747-400',
                                      '747-400D':'B747-400',
                                      '747SP':'747SP',
                                      '757-200':'B757-200',
                                      '757-200CB':'B757-200',
                                      '757-300':'757-300',
                                      '767-200':'B767-200/ER/EM',
                                      '767-300':'B767-300/300ER',
                                      '767-400ER':'767-400/ER',
                                      '777-200':'B777',
                                      '777-200LR':'B777',
                                      '777-300':'777-300/300ER/333ER',
                                      '777-300ER':'777-300/300ER/333ER',
                                      '787-10 Dreamliner': '787-10 Dreamliner',
                                      '787-8 Dreamliner':'B787-800 Dreamliner',
                                      '787-9 Dreamliner':'B787-900 Dreamliner',
                                      'A300 B1':'A300B/C/F-100/200',
                                      'A300 B2-100':'A300B/C/F-100/200',
                                      'A300 B2-200':'A300B/C/F-100/200',
                                      'A300 B4-100':'A300B/C/F-100/200',
                                      'A300 B4-200':'A300B/C/F-100/200',
                                      'A300 B4-600':'A300-600',
                                      'A300 B4-600R':'A300-600',
                                      'A300 C4-200':'A300B/C/F-100/200',
                                      'A300 C4-600':'A300-600',
                                      'A300 C4-600R':'A300-600',
                                      'A300 F4-200':'A300B/C/F-100/200',
                                      'A300 F4-600R':'A300-600',
                                      'A310-200':'A310-200C/F',
                                      'A310-200C':'A310-200C/F',
                                      'A310-300':'A310-300',
                                      'A318':'A-318',
                                      'A319':'A319',
                                      'A320':'A320-100/200',
                                      'A320neo':'A320-200n ',
                                      'A321-100':'A321/Lr',
                                      'A321-200':'A321/Lr',
                                      'A321neo':'A321-200n',
                                      'A330-200':'A330-200',
                                      'A330-300':'A330-300/333',
                                      'A330-900':'A330-900',
                                      'A350-900':'A350-900',
                                      'A380-800':'A380',
                                      'CRJ-200':'RJ-200ER /RJ-440',
                                      'CRJ-700':'RJ-700',
                                      'CRJ-900':'CRJ 900',
                                      'DC-10':'DC10-40',
                                      'DC-9-10':'DC9-10',
                                      'DC-9-30':'DC9-30',
                                      'DC-9-40':'DC9-40',
                                      'DC-9-50':'DC9-50',
                                      'EMB-135 (ERJ135 / ERJ140)':'Embraer-135',
                                      'EMB-135BJ Legacy':'Embraer-135',
                                      'EMB-145 (ERJ145)':'Embraer-145',
                                      'EMB-145XR (ERJ145 XR)':'Embraer-145',
                                      'ERJ 170-200 (E175)':'Embraer ERJ-175',
                                      'ERJ 190-100 (E190)':'Embraer 190',
                                      'ERJ 190-200 (E195)':'Embraer 190',
                                      'ERJ 190-300 (E190-E2)':'Embraer 190',
                                      'ERJ 190-400 (E195-E2)':'Embraer 190',
                                      'L-1011 TriStar':'L1011-1/100/200',
                                      'MD-11':'MD-11',
                                      'MD-81':'MD80/DC9-80',
                                      'MD-82':'MD80/DC9-80',
                                      'MD-83':'MD80/DC9-80',
                                      'MD-87':'MD80/DC9-80',
                                      'MD-88':'MD80/DC9-80',
                                      'MD-90':'MD-90',
                                      'DH.106 Comet': 'Comet 4'}
    def get_aircraftsfromdatabase(self):
        return self.aircraftsfromdatabase

#Classes to split the Seatloadfactor
class AirplaneTypes:
    def __init__(self):
        self.types = {"Boeing 757-200": 'Narrow',
                       "Boeing 767-300/300ER": 'Wide',
                       "Boeing 777-200ER/200LR/233LR": 'Wide',
                       "Airbus Industrie A320-100/200": 'Narrow',
                       "Boeing 767-200/ER/EM": 'Wide',
                       "Boeing 737-800": 'Narrow',
                       "Airbus Industrie A319": 'Narrow',
                       "Boeing 737-300": 'Narrow',
                       "McDonnell Douglas DC9 Super 80/MD81/82/83/88": 'Narrow',
                       "Boeing 747-400": 'Wide',
                       "Boeing 737-700/700LR/Max 7": 'Narrow',
                       "Boeing 727-200/231A": 'Narrow',
                       "Airbus Industrie A330-200": 'Wide',
                       "Boeing 767-400/ER": 'Wide',
                       "McDonnell Douglas DC-10-30": 'Wide',
                       "Airbus Industrie A321/Lr": 'Narrow',
                       "Boeing 737-400": 'Narrow',
                       "Boeing 737-100/200": 'Narrow',
                       "Boeing 737-500": 'Narrow',
                       "Boeing 747-200/300": 'Wide',
                       "McDonnell Douglas MD-11": 'Wide',
                       "Boeing 757-300": 'Narrow',
                       "Boeing 737-900": 'Narrow',
                       "Boeing 747-100": 'Wide',
                       "Canadair RJ-700": 'Regional',
                       "B787-800 Dreamliner": 'Wide',
                       "McDonnell Douglas DC-9-30": 'Narrow',
                       "Airbus Industrie A330-300/333": 'Wide',
                       "Embraer-145": 'Regional',
                       "Boeing 777-300/300ER/333ER": 'Wide',
                       "Embraer 190": 'Narrow',
                       "B787-900 Dreamliner": 'Wide',
                       "McDonnell Douglas DC-10-10": 'Wide',
                       "Lockheed L-1011-1/100/200": 'Wide',
                       "Airbus Industrie A300-600/R/CF/RCF": 'Wide',
                       "Boeing 737-900ER": 'Narrow',
                       "Canadair RJ-200ER /RJ-440": 'Regional',
                       "McDonnell Douglas MD-90": 'Narrow',
                       "McDonnell Douglas DC-10-40": 'Wide',
                       "Boeing 717-200": 'Narrow',
                       "Embraer ERJ-175": 'Regional',
                       "Boeing B737 Max 800": 'Narrow',
                       "Boeing 787-10 Dreamliner": 'Wide',
                       "Airbus Industrie A330-900": 'Wide',
                       "Boeing B737 Max 900": 'Narrow'
                       }

    def get_types(self):
        return self.types

#Map Full Aircraft names from Schedule T2 to abbreviations for the Databank
class fullname:
    def __init__(self):
        self.aircraftfullnames = {
                                "Airbus Industrie A300-600/R/CF/RCF": "A300-600",
                                "Airbus Industrie A319": "A319",
                                "Airbus Industrie A320-100/200": "A320-100/200",
                                "Airbus Industrie A321/Lr": "A321/Lr",
                                "Airbus Industrie A330-200": "A330-200",
                                "Airbus Industrie A330-300/333": "A330-300/333",
                                "Airbus Industrie A330-900": "A330-900",
                                "B787-800 Dreamliner": "B787-800 Dreamliner",
                                "B787-900 Dreamliner": "B787-900 Dreamliner",
                                "Boeing 717-200": "717-200",
                                "Boeing 727-200/231A": "B727-200/231A",
                                "Boeing 737-100/200": "B737-100/200",
                                "Boeing 737-300": "B737-300",
                                "Boeing 737-400": "B737-400",
                                "Boeing 737-500": "B737-500/600",
                                "Boeing 737-700/700LR/Max 7": "737-700/700LR/Max 7",
                                "Boeing 737-800": "737-800",
                                "Boeing 737-900": "737-900",
                                "Boeing 737-900ER": "737-900ER",
                                "Boeing 747-100": "747-100",
                                "Boeing 747-200/300": "B747-200/300",
                                "Boeing 747-400": "B747-400",
                                "Boeing 757-200": "B757-200",
                                "Boeing 757-300": "757-300",
                                "Boeing 767-200/ER/EM": "B767-200/ER/EM",
                                "Boeing 767-300/300ER": "B767-300/300ER",
                                "Boeing 767-400/ER": "767-400/ER",
                                "Boeing 777-200ER/200LR/233LR": "B777",
                                "Boeing 777-300/300ER/333ER": "777-300/300ER/333ER",
                                "Boeing 787-10 Dreamliner": "787-10 Dreamliner",
                                "Boeing B737 Max 800": "B737 Max 800",
                                "Boeing B737 Max 900": "B737 Max 900",
                                "Canadair RJ-200ER /RJ-440": "RJ-200ER /RJ-440",
                                "Canadair RJ-700": "RJ-700",
                                "Embraer 190": "Embraer 190",
                                "Embraer ERJ-175": "Embraer ERJ-175",
                                "Embraer-145": "Embraer-145",
                                "Lockheed L-1011-1/100/200": "L1011-1/100/200",
                                "McDonnell Douglas DC-10-10": "DC10-10",
                                "McDonnell Douglas DC-10-30": "DC10-30",
                                "McDonnell Douglas DC-10-40": "DC10-40",
                                "McDonnell Douglas DC-9-30": "DC9-30",
                                "McDonnell Douglas DC9 Super 80/MD81/82/83/88": "MD80/DC9-80",
                                "McDonnell Douglas MD-11": "MD-11",
                                "McDonnell Douglas MD-90": "MD-90",
                                'Airbus Industrie A350-900':'A350-900',
                                'Airbus Industrie A320-200n': 'A320-200n',
                                'Airbus Industrie A-318':'A-318',
                                'Airbus Industrie A300B/C/F-100/200':'A300B/C/F-100/200',
                                'Airbus Industrie A310-200C/F':'A310-200C/F',
                                'Airbus Industrie A321-200n':'A321-200n',
                                'Boeing 727-100':'727-100',
                                'Boeing 737-200C':'737-200C',
                                'Boeing 747SP':'747SP',
                                'Canadair CRJ 900':'CRJ 900',
                                'Embraer-135':'Embraer-135'}
    def get_aircraftfullnames(self):
        return self.aircraftfullnames

#Map the names from the Babikian input data to the names of the Schedule T2
# NO TO OUR
class AircraftNames:
    def __init__(self):
        self.aircraftnames = 
        {
        #    'B707-300':'B707-300',
        #    'B720-000':'B720-000',
        #    'DC9-10':'DC9-10',
        #    'DC9-30':'McDonnell Douglas DC-9-30',
        #    'B727-200/231A':'Boeing 727-200/231A',
        #    'B737-100/200':'Boeing 737-100/200',
        #    'DC9-40':'DC9-40',
        #    'DC10-10': 'McDonnell Douglas DC-10-10',
        #    'B747-200/300':'Boeing 747-200/300',
        #    'B747-100': 'Boeing 747-100',
        #    'DC10-40':'McDonnell Douglas DC-10-40',
        #    'DC10-30':'McDonnell Douglas DC-10-30',
        #    'L1011-1/100/200':'Lockheed L-1011-1/100/200',
        #    'DC9-50':'DC9-50',
        #    'L1011-500':'L1011-500',
        #    'MD80/DC9-80':'McDonnell Douglas DC9 Super 80/MD81/82/83/88',
        #    'B767-200/ER': 'Boeing 767-200/ER/EM',
        #    'A300-600':'Airbus Industrie A300-600/R/CF/RCF',
        #    'B757-200':'Boeing 757-200',
        #    'B737-300':'Boeing 737-300',
        #    'A310-300': 'A310-300',
        #    'B767-300/ER':'Boeing 767-300/300ER',
        #    'A320-100/200': 'Airbus Industrie A320-100/200',
        #    'B737-400':'Boeing 737-400',
        #    'B747-400':'Boeing 747-400',
        #    'MD11':'McDonnell Douglas MD-11',
        #    'B737-500/600':'Boeing 737-500',
        #    'B777': 'Boeing 777-200ER/200LR/233LR',
        #    'B707-100B/300': 'B707-100B/300'
        }

    def get_aircraftnames(self):
        return self.aircraftnames


class_aircraftfullnames = fullname()
aircraftfullnames = class_aircraftfullnames.aircraftfullnames
df_t2 = pd.DataFrame(list(aircraftfullnames.items()), columns=['T2', 'OUR'])

class_aircraftnames = AircraftNames()
aircraftnames = class_aircraftnames.aircraftnames
df_babikian_t2 = pd.DataFrame(list(aircraftnames.items()), columns=['Babikian', 'T2'])

df_t2 = pd.merge(
    left=df_t2,
    right=df_babikian_t2,
    left_on='T2',
    right_on='T2',
    how='left'
)

class_aircrafttypes = AirplaneTypes()
airplanetypes = class_aircrafttypes.types
df_types = pd.DataFrame(list(airplanetypes.items()), columns=['T2', 'Type'])

df_t2 = pd.merge(
    left=df_t2,
    right=df_types,
    left_on='T2',
    right_on='T2',
    how='left'
)

# YOI
class_models = AirplaneModels()
models = class_models.models
df_yoi = pd.DataFrame(list(models.items()), columns=['T2', 'YOI'])

df_t2 = pd.merge(
    left=df_t2,
    right=df_yoi,
    left_on='T2',
    right_on='T2',
    how='left'
)

# database.com
class_aircraftdata = aircraftdata()
aircraftdata = class_aircraftdata.aircraftsfromdatabase
df_aircraftdata = pd.DataFrame(list(aircraftdata.items()), columns=['aircraft-data.com', 'OUR'])
df_aircraftdata = df_aircraftdata.groupby('OUR')['aircraft-data.com'].apply(list).reset_index()

#df = pd.merge(
#    left=df_aircraftdata,
#    right=df_t2,
#    left_on='OUR',
#    right_on='OUR',
#    how='outer'
#)

# %%

"""
| OUR | data_1 | 
|-----|--------|
| A   | 1      |
| B   | 2      |

| OUR | data_2 |
|-----|--------|
| A   | 3      |
| C   | 4      |
"""

# Example dataframes
df_data_1 = pd.DataFrame({
    'OUR': ['A', 'B'],
    'data_1': [1, 2]
})

df_data_2 = pd.DataFrame({
    'OUR': ['A', 'C'],
    'data_2': [3, 4]
})

# Merging the dataframes
df_merged = pd.merge(
    left=df_data_1,
    right=df_data_2,
    left_on='OUR',
    right_on='OUR',
    how='left'
)

df_t2_dc = df_t2[df_t2['OUR'].str.contains("DC", na=False)]
df_com_dc = df_aircraftdata[df_aircraftdata['OUR'].str.contains("DC", na=False)]

