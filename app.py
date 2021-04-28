import gspread
import requests
import os
import pprint
from oauth2client.service_account import ServiceAccountCredentials

pp = pprint.PrettyPrinter(indent=4)

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

openweather_key = os.environ["openweather_key"]

def create_array():
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
    list_of_hashes = sheet.get_all_records()
    return list
    pp.pprint(list_of_hashes)

def get_forecast():
    """
    Pull 7 day forecast. 
    URL is hardcoded to US only. Updates can be made to include external countries if needed.
    """
    url = "http://api.openweathermap.org/data/2.5/forecast?id=524901&appid=" + openweather_key
    # http://api.openweathermap.org/data/2.5/forecast?zip={zip code},{country code}&appid={API key}

    response = requests.get(url)

    pp.pprint(response.json())

create_array()
#get_forecast()


"""
PSEUDO CODE
---
1. Scan Google Sheet for plants and store array
2. Scan OpenWeather for 7 day forecast and log daily min temps
3. Filter array for any plant hadiness < min temps
4. Prep email payload (1 email per user)
5. Send email to each user with at risk plants notifying them of which plants to pull in and when.

"""