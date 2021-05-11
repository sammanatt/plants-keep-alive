import os
import json
import pprint
import gspread
import argparse
import requests
import datetime

from oauth2client.service_account import ServiceAccountCredentials

pp = pprint.PrettyPrinter(indent=4)

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

openweather_key = os.environ["openweather_key"]
mailgun_apikey = os.environ["mailgun_apikey"]
mailgun_base_url = os.environ["mailgun_base_url"]
from_address = os.environ["from_address"]


class PlantCollection:
    """
    Models a plant owner's email, zip code and plant collection.
    """
    def __init__(self,email,zip_code, plants={},forecast={}):
        self.email = email
        self.zip_code = zip_code
        self.plants = {}
        self.forecast = {}

    def description(self):
        """
        Prints description of instantiated class in cli.
        """
        print("########################################")
        print(f"User {self.email} at {self.zip_code} has {len(self.plants)} plants:")
        for plant,freeze_temp in sorted (self.plants.items()):
            print(f"    {plant} (Damage at {freeze_temp}F)")
        
        self.get_forecast()
        print(f"    ===  {self.city} 7 Day Low Temp  ===") #update with fstring to include city name
        for day,min_temp in self.forecast.items():
            print(f"    {day} has a min temp of: {min_temp}F")

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

        for day in results['list']:
            timestamp = datetime.datetime.fromtimestamp(day['dt'])
            timestamp_formatted = timestamp.strftime('%Y-%m-%d')
            min_temp = day['temp']['min']
            self.forecast.update({timestamp_formatted:round(min_temp)})


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

def send_email(to_address,body_message):
    """
    Sends a plain-text email via Mailgun API.
    """

    message = requests.post(
        mailgun_base_url + "/messages",
        auth=("api", mailgun_apikey),
        data={"from": from_address,
              "to": to_address, 
              "subject": "Weekly Plant Alert",
              "text": body_message})
    print(f"message: {message.text}\n"
        f"status:{message.status_code}" )


def send_templated_message(to_address, body_message):
    return requests.post(
        mailgun_base_url + "/messages",
        auth=("api", mailgun_apikey),
        data={"from": from_address,
              "to": to_address,
              "subject": "Weekly Plant Alert",
              "template": "plantskeepalive",
              "h:X-Mailgun-Variables": json.dumps({"title": "API documentation", "body": body_message})})


# Gets current Google Sheet contents
google_sheet_contents = sheets_array()

# Collect a unique dictionary of email addresses (keys) and zip codes (values)
user_info = {}
for i in google_sheet_contents:
    if i['Email Address'] in user_info or bool(i['Email Address']) == False:
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

    plant_class.description()

    # Looks for plants with a freeze_temp < a daily min
    plant_class.get_forecast()
    daily_mintemp = plant_class.forecast        
    email_body = "=== Weekly Plant Alert ===\n"
    body_message = []
    current_indice = 0 
    for day,min_temp in daily_mintemp.items():
        plants_at_risk = []
        email_body += f"\n{day} has a low of {min_temp}\n"
        body_message.append({"date":day})
        body_message[current_indice].update({"plants_at_risk": plants_at_risk})
        current_indice += 1
        for plant,freeze_temp in plant_class.plants.items():
            if freeze_temp >= 10: 
                plants_at_risk.append(plant)
        if len(plants_at_risk) == 0:
            email_body += "    No plants are at risk!\n"
            #plants_at_risk = False
            plants_at_risk.append("No plants are at risk!")
        else: 
            email_body += "    The following plants are at risk:\n"
            for plant in plants_at_risk:
                email_body += f"        {plant}\n"
                #plants_at_risk.append(plant)
            #body_message["Dates"].append({"Plant_at_risk": plants_at_risk})

    # For loop for debugging
    print(json.dumps(body_message, indent=4))
    """
    for k,v in new_dict.items():
        print(f"Day is {k}")
        if bool(v) == False:
            print("    No plants are at risk!")
        else:
            print("    The followoing plants are at risk")
            for i in v:
                print(f"        {i}")"""
    
    send_templated_message(plant_class.email, body_message)

"""
if __name__ == "__main__":
    # Build argument parser
    parser = argparse.ArgumentParser(description='Send communcations to multiple customers via email.')
    parser.add_argument('-u',
                        '--user',
                        default=None,
                        help="Discogs user to import from.",
                        action='store_true')
    args = parser.parse_args()

    #if args.user is None:
    #    args.user = discogs_username
    main(args)
"""


"""
=== To Do ===
1. Add Debugger option to:
    a. Only email admin email
    b. Add optional argument to hard code min_temp
2. Add argument to specify if templatized emails will be used (default to plain text)
3. Test and fine-tune formatted emails using new_dict
4. Refactor plain text emails to use json in new_dict
"""


