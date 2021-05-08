# plants-keep-alive

![https://giphy.com/gifs/death-die-plant-XSTtrAN0rJfy](tryingnottodie.gif)

I decided to write this after losing a massive Basil plant last winter when our local temperatures dipped into the low 40's. I hope this helps save someone else's plants as well! At a high level, this script will: 

1. Read plant collection and user data from a Google Sheet
2. Instantiate a user's plant collection
3. Gather daily low temperatures from localized 7 day weather forecast
4. Send email notfications reporting which plants may be at risk of being damaged by cold weather 

You can run this with a cron job to run the script at your desired frequency.

**Example email**

At the moment, emails are sent in plain text. I've got a backlog item to use a Mailgun template for an improved look/feel.

```
=== Weekly Plant Alert ===

2021-05-07 has a low of 60
    The following plants are at risk:
        Shishito Peppers
        Basil
        Purple Basil
        Hindu Rope Plant
        Rat Tail Cactus

2021-05-08 has a low of 64
    The following plants are at risk:
        No plants are at risk!

2021-05-09 has a low of 70
    The following plants are at risk:
        No plants are at risk!

2021-05-10 has a low of 60
    The following plants are at risk:
        No plants are at risk!

2021-05-11 has a low of 58
    The following plants are at risk:
        Shishito Peppers
        Basil
        Purple Basil
        Hindu Rope Plant
        Rat Tail Cactus

2021-05-12 has a low of 63
    The following plants are at risk:
        No plants are at risk!

2021-05-13 has a low of 59
    The following plants are at risk:
        No plants are at risk!
```

---
# Setup

## Repo setup

1. Use your favorite method of cloning repos.
2. Run `pip3 install -r requirements.txt`
3. Within the repo, you'll have a file named `.env_EDIT_ME`. Rename this file to `.env`.

## Google Sheet template and permissions
The use of Google Sheets was selected as a quick option for close friends and family to add their plants and user data as well. Because the script will require email addresses and zip codes, I recommend you make your Google Sheet privitized.

**Create your sheet**
1. Make a copy of [this Google Sheet template](https://docs.google.com/spreadsheets/d/1cbqmThJJ4F66E_MKIg9KgNc7RwDWAOEpzKIU9mTgoKQ/edit?usp=sharing)
2. Replace the sample data with your own 


**Create a service account and grant it permissions to your sheet**

Twilio has a great tutorial on how to quickly set this up. Be sure to follow the instructions here: 
https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html


## Mailgun Setup
Rather than setting up an SMTP server, I opted to use Mailgun for this project to start sending emails via their API. If needed, sign up for an account [here](https://signup.mailgun.com/new/signup).

>At the time of writing this, you can sign up for an account and send up to 5,000 emails per month for the first three months. After that, pricing is pretty darn reasonable ($0.80 per month for 1,000 emails).

1. Log into your mailgun account at https://mailgun.com
2. Navigate to [the domains section](https://app.mailgun.com/app/sending/domains) under Sending
3. Select the domain you wish to send from
>Note: if you're sending from the sandbox domain, you can only email authorized recipients. These can be specified via the `Authorized Recipients` form on this page. 

4. Under `API` choose `Select` and copy the `API key` and `API base URL` into the mailgun variables in your .env file.


## OpenWeather
In order to gather local forecast data, this script leverages OpenWeather's API. This is a [free*](https://openweathermap.org/price) API with no ads. 

1. [Sign in](https://home.openweathermap.org/users/sign_in) and/or [create](https://home.openweathermap.org/users/sign_up) an OpenWeather account
2. Generate and create and API Key at: https://home.openweathermap.org/api_keys
3. Copy/paste your API key into your .env file

## Scheduling
Use your favorite method of scheduling python jobs (e.g. [python-crontab](https://pypi.org/project/python-crontab/), [schedule](https://schedule.readthedocs.io/en/stable/?__s=phkqu4iwbxbad117h1ey), et al.) to run this script as frequently as you wish.
