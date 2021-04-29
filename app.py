import gspread
import requests
import os
import pprint
import datetime
from oauth2client.service_account import ServiceAccountCredentials

pp = pprint.PrettyPrinter(indent=4)

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

openweather_key = os.environ["openweather_key"]


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
    pp.pprint(google_sheet_contents)
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
            print(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} with min temp of: {day['temp']['min']}")

get_forecast()


"""
PSEUDO CODE
---
1. Scan Google Sheet for plants and store array
2. Scan OpenWeather for 7 day forecast and log daily min temps
3. Filter array for any plant hadiness < min temps
4. Prep email payload (1 email per user)
5. Send email to each user with at risk plants notifying them of which plants to pull in and when.

"""