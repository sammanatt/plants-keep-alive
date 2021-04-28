import gspread
import requests
import os
from oauth2client.service_account import ServiceAccountCredentials

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

rapidapi_key = os.environ["rapidapi_key"]

def get_forecast():
    """
    Pull 5 day forecast.
    """
    url = "https://community-open-weather-map.p.rapidapi.com/climate/month"

    querystring = {"q":"San Francisco"}

    headers = {
        'x-rapidapi-key':rapidapi_key,
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.json())

def scan_sheets():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Keep my plants alive!").sheet1

    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    print(list_of_hashes)


get_forecast()
#scan_sheets()


"""
PSEUDO CODE
---
1. Get low temps for next 7 days
2. Scan Google Sheet for plants:
    a. If low temp < min temp during next 7 days, add dictionary to list
3. Send email to each user with at risk plants notifying them of which plants to pull in and when.

"""