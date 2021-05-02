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

class PlantCollection:
    """
    Models a plant owner's email, zip code and plant collection.
    """
    def __init__(self,email,zip_code, plants={},forecast=[]):
        self.email = email
        self.zip_code = zip_code
        self.plants = {}
        self.forecast = []

    def description(self):
        """
        Prints description of instantiated class in cli.
        """
        print("####################")
        print(f"User {self.email} at {self.zip_code} has {len(self.plants)} plants:")
        for plant in sorted (self.plants.keys()):
            print(f"    {plant}")
        print(f"    ===  7 Day Forecast===") #update with fstring to include city name
        self.get_forecast()

    def add_plants(self):
        """
        Updates dictionary with the user's plant collection
        """
        self.plants.update({plant_name:freeze_temp})
    
    def get_forecast(self):
        """
        Pulls 7 day forecast for the user's zipcode.
        """
        url = f"http://api.openweathermap.org/data/2.5/forecast/daily?zip={self.zip_code},us&units=imperial&appid={openweather_key}"
        response = requests.get(url)
        results = response.json()
        self.city = results['city']['name']
        print(f"    {self.city}")

        for day in results['list']:
            timestamp = datetime.datetime.fromtimestamp(day['dt'])
            print(f"    Date: {timestamp.strftime('%Y-%m-%d')} with min temp of: {day['temp']['min']}")


def sheets_array():
    """
    Scans the specified Google Sheet to gather all information needed for the PlantCollection class.
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


# Gets current Google Sheet contents
google_sheet_contents = sheets_array()

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
    # Instantiates class
    plant_class = PlantCollection(email,zipcode)

    # Adds user's plant collection to instantiated class.
    for i in google_sheet_contents:
        # Preparing variables and list
        plant_name = i['Plant Name']
        freeze_temp = i['Lowest temp (F°) to survive']
        plants = []
        
        if i['Email Address'] == email and plant_name in plants:
            continue
        elif i['Email Address'] == email and plant_name not in plants:
            plant_class.add_plants()
        plants.append(plant_name)
    
    # Prints description to CLI for debugging/sanity check.
    plant_class.description()


"""
PSEUDO CODE
---
1. Scan Google Sheet for plants and store array
2. Scan OpenWeather for 7 day forecast and log daily min temps
3. Filter array for any plant hadiness < min temps
4. Prep email payload (1 email per user)
5. Send email to each user with at risk plants notifying them of which plants to pull in and when.

"""