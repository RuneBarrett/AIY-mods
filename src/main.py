#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import subprocess
import sys

import aiy.assistant.auth_helpers
import aiy.audio
import aiy.voicehat
from google.assistant.library import Assistant
from google.assistant.library.event import EventType

import sonoffControl as sc
import youtubePlayer as ytp

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


def power_off_pi():
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def restart_homeassistant():
    aiy.audio.say('Restarting home assistant!')
    subprocess.call('sudo systemctl restart home-assistant@homeassistant.service', shell=True)

    
def process_event(assistant, event):
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        subprocess.Popen(["aplay", "/home/pi/sounds/R2D2Eureka.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        global yt
        yt = ytp.YouTubePlayer(aiy.audio.say)
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')
        subprocess.Popen(["aplay", "/home/pi/sounds/zippoO.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            subprocess.Popen(["aplay", "/home/pi/sounds/R2D2Laughing.wav"], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        elif text == 'restart home assistant':
            assistant.stop_conversation()
            restart_homeassistant()
        elif text in ['go to living room', 'living room']:
            assistant.stop_conversation()
            sc.turn_on_livingroom()
        elif text in ['go to kitchen', 'kitchen']:
            assistant.stop_conversation()
            sc.turn_on_kitchen()
        elif text in ['turn off lights', 'turn off everything', 'turn off the lights']:
            assistant.stop_conversation()
            sc.turn_off_everything()
        elif text in ['lights', 'turn on lights', 'turn on everything', 'turn on the lights']:
            assistant.stop_conversation()
            sc.turn_on_everything()
        elif text in ['go to bathroom', 'bathroom']:
            assistant.stop_conversation()
            sc.turn_on_bathroom()
        elif text.startswith('play'):
            assistant.stop_conversation()
            yt.run(text)
        elif text == 'stop music':
            assistant.stop_conversation()
            yt._stop()
        elif text == 'restart voice recognizer':
            subprocess.call('sudo systemctl restart voice-recognizer', shell=True)


    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)


if __name__ == '__main__':
    main()
