import subprocess
import sys
import secrets

def turn_on_livingroom():
#    aiy.audio.say('OK!')
    publish_all("ON","ON","OFF", "OFF", "OFF")

def turn_on_kitchen():
#    aiy.audio.say('OK!')
    publish_all("OFF","OFF","ON", "ON", "ON")
    
def turn_on_bathroom():
#    aiy.audio.say('OK!')
    publish_all("OFF","OFF","OFF", "ON", "ON")

def turn_off_everything():
    publish_all("OFF","OFF","OFF","OFF","OFF")

def turn_on_everything():
    publish_all("ON","ON","ON","ON","ON")

def publish_all(ceiling, drum, kitchenwall, bathroom, kitchen):
    subprocess.call('mosquitto_pub -h 192.168.1.145 -t cmnd/sonoff_ceiling/power -m '+ceiling+' -u '+secrets.uname+' -P '+secrets.pwd, shell=True)
    subprocess.call('mosquitto_pub -h 192.168.1.145 -t cmnd/sonoff_drum/power -m '+drum+' -u '+secrets.uname+' -P '+secrets.pwd, shell=True)
    subprocess.call('mosquitto_pub -h 192.168.1.145 -t cmnd/sonoff_kitchenwall/power -m '+kitchenwall+' -u '+secrets.uname+' -P '+secrets.pwd, shell=True)
    subprocess.call('mosquitto_pub -h 192.168.1.145 -t cmnd/sonoff_bathroom/power -m '+bathroom+' -u '+secrets.uname+' -P '+secrets.pwd, shell=True)
    subprocess.call('mosquitto_pub -h 192.168.1.145 -t cmnd/sonoff_kitchen/power -m '+kitchen+' -u '+secrets.uname+' -P '+secrets.pwd, shell=True)