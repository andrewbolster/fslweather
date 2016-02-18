#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import time, sleep
import math
from argparse import ArgumentParser

import json

#variable setup
count = 0
pin = 4 #GPIO 4
start_time = time()
last_time = 0
json_path = '/var/www/data.json'

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Custom Value and Rate generators for Rainfall
def calculate_rainfall_value():
    return count * 0.2764

def calculate_rainfall_rate():
    global count
    global start_time
    return count/(time()-start_time) * 3600 * calculate_rainfall_value() #mm/h

# Custom Value and Rate generators for Windspeed
r_cm = 9.0

interval = 1.0
calculate_interval = 5.0

def calculate_windspeed():
    global count
    c_cm = (2 * math.pi) * r_cm
    c_km = c_cm / 100000
    rot = count // 2
    d_km = c_km * rot
    km_per_sec = d_km / calculate_interval
    km_per_hour = km_per_sec * 3600
    return round (km_per_hour, 3)

def count_interval():
    global count
    this_count = count
    count = 0
    return this_count


def action(channel):
    global count
    global last_time
    last_time = time()
    count = count + 1


def main():
    GPIO.add_event_detect(pin, GPIO.RISING, callback=action, bouncetime=300)

    parser = ArgumentParser(prog='fslweather')
    parser.add_argument('--rainfall', action='store_true')
    parser.add_argument('--windspeed', action='store_true')
    parser.add_argument('--asservice', action='store_true')
    args = parser.parse_args()

    if not (args.rainfall or args.windspeed):
        raise ValueError("Must Use Either --rainfall or --windspeed")
    if args.rainfall and args.windspeed:
        raise ValueError("Must use EITHER --rainfall or --windspeed")

    if args.rainfall:
        template = "\rRainfall: {sum:6.3f} mm\t Est. Rate: {rate:6.3f} mm/hr"
        value = calculate_rainfall_value
        rate = calculate_rainfall_rate
    if args.windspeed:
        template = '\rThe current speed is: {rate:} km/h | Biggest so far: {max} km/h'
        value = count_interval
        rate = calculate_windspeed


    last_max = 0.0
    while True:
        r = rate()
        v = value()
        data = {
            'sum' : v,
            'rate' :  r,
            'max' : max(r, last_max),
            'last_action' : time()-last_time,
            'last_update' : time()
        }
        last_max = data['max']

        with open(json_path, 'w') as outfile:
            json.dump(data, outfile)
        if not args.asservice:
            print(template.format(**data), end='')
        sleep(calculate_interval)