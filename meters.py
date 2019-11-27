#!/usr/bin/python
import RPi.GPIO as GPIO                              
import requests
from datetime import datetime
import time

#https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
def translate(sensor_val, in_from, in_to, out_from, out_to):
    out_range = out_to - out_from
    in_range = in_to - in_from
    in_val = sensor_val - in_from
    val=(float(in_val)/in_range)*out_range
    out_val = out_from+val
    return out_val

#https://stackoverflow.com/questions/5996881/how-to-limit-a-number-to-be-within-a-specified-range-python
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def getWeather():
  r = {}
  r['Retry'] = False  
  try:
    w = requests.get('http://forecast.weather.gov/MapClick.php?lat=38.9536&lon=-94.7335&unit=0&lg=english&FcstType=json')
  except: 
    w = None 
  try:
    r['Temp'] = int(w.json()['currentobservation']['Temp'])
  except: 
    r['Temp'] = 0 
    r['Retry'] = True  
  try: 
    r['Relh'] = int(w.json()['currentobservation']['Relh'])
  except: 
    r['Relh'] = 0
    r['Retry'] = True  
  return r

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)
hour = GPIO.PWM(25, 50)
hour.start(50)
GPIO.setup(18, GPIO.OUT)
minute = GPIO.PWM(18, 50)
minute.start(50)
GPIO.setup(23, GPIO.OUT)
temperature = GPIO.PWM(23, 50)
temperature.start(16)
GPIO.setup(24, GPIO.OUT)
humidity = GPIO.PWM(24, 50)
humidity.start(16)

weather = getWeather()
lastHour = int(datetime.now().strftime("%I"))

while True:
  hour.start(translate(int(datetime.now().strftime("%I")), 0, 12, 0, 100))
  minute.start(translate(int(datetime.now().strftime("%M")), 0, 60, 0, 100))
  temperature.start(translate(clamp(weather['Temp'], 0, 100), 0, 100, 0, 32))
  humidity.start(translate(clamp(weather['Relh'], 0, 100), 0, 100, 0, 32))
  time.sleep(60)
  if (lastHour != int(datetime.now().strftime("%I"))) or (weather['Retry']): 
    weather = getWeather()
    lastHour = int(datetime.now().strftime("%I"))

