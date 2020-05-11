import sys
from time import sleep
import requests
import sqlite3
import datetime
import configparser
import os.path

class HWMissingData(Exception):
    pass


DEVICE_ID = ""
LOCATION_ID = ""

conn = sqlite3.connect("honeywell.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS hw_temp
             (record_time text, indoor_temp float, outdoor_temp float, outdoor_humidity float, is_heating int)"""
)

def get_device_location_id():
    if os.path.isfile("hw_device.txt"):
        config = configparser.ConfigParser()
        config.read("hw_device.txt")
        return config["DEFAULT"]["device_id"], config["DEFAULT"]["location_id"] 


def _refresh_token(refresh_token):
    """
    curl    -X POST 'https://api.honeywell.com/oauth2/token' 
            -H "Authorization: Basic Qm1DVlJ6bnBpaDA4NDdpNXhrYXVValV6aEszT0J5MTY6aElNOWR2cGRMZEJVVzVheQ==" 
            -H "Content-Type: application/x-www-form-urlencoded" 
            -d 'grant_type=refresh_token&refresh_token=7goS8iKkxnaG8Bx1NC2m4u5oIjVTtdGp'

    """
    headers = {
        "Authorization": "Basic Qm1DVlJ6bnBpaDA4NDdpNXhrYXVValV6aEszT0J5MTY6aElNOWR2cGRMZEJVVzVheQ==",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    r = requests.post(
        "https://api.honeywell.com/oauth2/token", data=data, headers=headers
    )
    token = r.json()["access_token"]
    refresh_token = r.json()["refresh_token"]
    config = configparser.ConfigParser()
    config.read("hw_tokens.txt")
    config.set("DEFAULT", "token", token)
    config.set("DEFAULT", "refresh_token", refresh_token)
    with open("hw_tokens.txt", "w") as configfile:
        config.write(configfile)
    return token, refresh_token

def get_token_info(hw_code):
    if os.path.isfile("hw_tokens.txt"):
        config = configparser.ConfigParser()
        config.read("hw_tokens.txt")
        token = config["DEFAULT"]["token"]
        refresh_token = config["DEFAULT"]["refresh_token"]
        return token, refresh_token

    headers = {
        "Authorization": "Basic Qm1DVlJ6bnBpaDA4NDdpNXhrYXVValV6aEszT0J5MTY6aElNOWR2cGRMZEJVVzVheQ==",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": f"{hw_code}",
        "scope": "",
        "redirect_uri": "none",
    }
    r = requests.post(
        "https://api.honeywell.com/oauth2/token", data=data, headers=headers
    )
    token = r.json()["access_token"]
    refresh_token = r.json()["refresh_token"]

    config = configparser.ConfigParser()
    config["DEFAULT"] = {"token": token, "refresh_token": refresh_token}
    with open("hw_tokens.txt", "w") as configfile:
        config.write(configfile)
    return token, refresh_token


def get_temp(token):
    """
    curl -X GET -H "Authorization: Bearer <token>" 
    "https://api.honeywell.com/v2/devices/thermostats/LCC-B82CA03FE296?apikey=BmCVRznpih0847i5xkauUjUzhK3OBy16&locationId=1473506"
    """
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"https://api.honeywell.com/v2/devices/thermostats/{DEVICE_ID}?apikey=BmCVRznpih0847i5xkauUjUzhK3OBy16&locationId={LOCATION_ID}",
        headers=headers,
    )
    if r.status_code == 401:
        return None, None, None, None, r.status_code
    data = r.json()
    try: 
        outdoor_humidity = data["displayedOutdoorHumidity"]
        indoor_temp = data["indoorTemperature"]
        outdoor_temp = data["outdoorTemperature"]
        is_heating = 1 if data["operationStatus"]["mode"] == "Heat" else 0
    except KeyError:
       raise HWMissingData
    return indoor_temp, outdoor_temp, outdoor_humidity, is_heating, r.status_code


def save_temp_db(indoor_temp, outdoor_temp, outdoor_humidity, is_heating):
    print(indoor_temp, outdoor_temp, outdoor_humidity, is_heating)
    date_now = str(datetime.datetime.now())
    q = f"INSERT INTO hw_temp VALUES ('{date_now}', {indoor_temp}, {outdoor_temp}, {outdoor_humidity}, {is_heating})"
    print(q)
    c.execute(q)
    conn.commit()


def process_temp(token, refresh_token):
    hw_token = token
    hw_refresh_token = refresh_token

    while True:
        try:
            indoor_temp, outdoor_temp, outdoor_humidity, is_heating, status_code = get_temp(
                hw_token
            )
        except HWMissingData:
            continue
        if status_code == 401:
            hw_token, hw_refresh_token = _refresh_token(hw_refresh_token)
            continue
        save_temp_db(indoor_temp, outdoor_temp, outdoor_humidity, is_heating)
        sleep(30)


if __name__ == "__main__":
    hw_code = sys.argv[1]
    DEVICE_ID, LOCATION_ID = get_device_location_id()
    token, refresh_token = get_token_info(hw_code)
    while True:
        try:
            process_temp(token, refresh_token)
        except:
            sleep(300)            
            continue


    
