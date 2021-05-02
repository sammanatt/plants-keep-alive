import os
import pprint
import gspread
import requests
import datetime
from oauth2client.service_account import ServiceAccountCredentials

pp = pprint.PrettyPrinter(indent=4)

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

openweather_key = os.environ["openweather_key"]

#class that I cannot get to work without overwiting plant info.
class PlantCollection:
    """
    Models a plant owner's email, zip code and plant collection.
    """
    def __init__(self,email,zip_code,plants={}):
        self.email = email
        self.zip_code = zip_code
        self.plants = {}

    def description(self):
        print(f"User {self.email} at {self.zip_code} has {len(self.plants)} plants:")
        for plant in sorted (self.plants.keys()):
            print(f"    {plant}")    

    def add_plants(self):
        self.plants.update({plant_name:freeze_temp})


def sheets_array():
    """
    Scans the specified Google Sheet to create an array of all logged plants.
    """
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Keep my plants alive!").sheet1

    # Extract and print all of the values
    google_sheet_contents = sheet.get_all_records()

    #pp.pprint(google_sheet_contents)
    return google_sheet_contents

def get_forecast():
    """
    Pull 7 day forecast. 
    URL is hardcoded to US only. Updates can be made to include external countries if needed.
    """
    # Creates a unique list of zip codes from google_sheet_contents
    google_sheet_contents = sheets_array()
    zipcodes = []
    for i in google_sheet_contents:
        if i['Zip Code'] in zipcodes:
            continue
        else:
            zipcodes.append(i['Zip Code'])
    #print(zipcodes)

    # Gather temp_min for next 7 days in reported zip codes
    forecast = []
    for i in zipcodes:
        url = f"http://api.openweathermap.org/data/2.5/forecast/daily?zip={i},us&units=imperial&appid={openweather_key}"
        response = requests.get(url)
        forecast.append(response.json())

    for city in forecast:
        print(f"City: {city['city']['name']}")
        for day in city['list']:
            # Clean up variables
            timestamp = datetime.datetime.fromtimestamp(day['dt'])
            print(f"Date: {timestamp.strftime('%Y-%m-%d')} with min temp of: {day['temp']['min']}")


"""
Lines below this have just been setup for testing. Once I get them cleaned up, they should be moved into the appropriate function or class above.
"""

# Gets current Google Sheet contents
google_sheet_contents = sheets_array()
#pp.pprint(google_sheet_contents)

# Collect a unique dictionary of email addresses (keys) and zip codes (values)
user_info = {}

for i in google_sheet_contents:
    if i['Email Address'] in user_info:
        continue
    else:
        email = i['Email Address']
        zipcode = i['Zip Code']
        user_info.update({email:zipcode})

# Loops through all unique emails looking for plant ownership
for email,zipcode in user_info.items():
    plants = []
    #print(f"Working on {email}")
    # Instantiates class
    plant_class = PlantCollection(email,zipcode) #!!! Zipcode variable needs to get fixed

    for i in google_sheet_contents:
        # Preparing variables and list
        plant_name = i['Plant Name']
        freeze_temp = i['Lowest temp (F°) to survive']
        
        if i['Email Address'] == email and plant_name in plants:
            continue
        elif i['Email Address'] == email and plant_name not in plants:
            plant_class.add_plants()
        plants.append(plant_name)
    plant_class.description()


#pp.pprint(google_sheet_contents)
#get_forecast()
sheets_array()

"""
PSEUDO CODE
---
1. Scan Google Sheet for plants and store array
2. Scan OpenWeather for 7 day forecast and log daily min temps
3. Filter array for any plant hadiness < min temps
4. Prep email payload (1 email per user)
5. Send email to each user with at risk plants notifying them of which plants to pull in and when.

"""