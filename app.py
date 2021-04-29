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
    def __init__(self,email,zip_code):
        self.email = email
        self.zip_code = zip_code

    def description(self):
        print(f"User: {self.email} Zip: {self.zip_code}")    


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
emails = []

for i in google_sheet_contents:
    if i['Email Address'] in emails:
        continue
    else:
        emails.append(i['Email Address'])
        i = PlantCollection(i['Email Address'], i['Zip Code'])
        i.description()


plant_freeze = {}
for i in google_sheet_contents:
    name = i['Plant Name']
    freeze_temp = i['Lowest temp (F°) to survive']
    plant_freeze.update({name:freeze_temp})
    
#print(plant_freeze)

# testing dictionary as a thought to ditch creating a class. However when an email address has multiple plants to account for, the plants are overwritten leaving only one in the dictionary.
dict = {}
for i in google_sheet_contents:
    email = i['Email Address']
    freeze_temp = i['Lowest temp (F°) to survive']
    plant_name = i['Plant Name']
    zip = i['Zip Code']

    if i['Plant Name'] in dict:
        continue
    if i['Plant Name'] not in dict:
        dict[email]={'Zip Code':zip,plant_name:freeze_temp}

pp.pprint(google_sheet_contents)
print("***Dictionary***")
pp.pprint(dict)



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