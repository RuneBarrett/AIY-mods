import subprocess
import logging

import re
import time
import urllib
import youtube_dl
import vlc

class YouTubePlayer(object):

    """Plays song from YouTube."""
    
    def __init__(self, say):
        self.say = say
        self._init_player()
        
    def run(self, voice_command):
    
        track = voice_command.lower().replace('play ', '', 1).strip()
        
        if not track:
            self.say('Please specify a song')
            return
        
        ydl_opts = {
            'default_search': 'ytsearch1:',
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }
        
        meta = None
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(track, download=False)
        except Exception as e:
            self.say('Failed to find ' + track)
            return
        
        if not meta:
            self.say('Failed to find ' + track)
            return
            
        track_info = meta['entries'][0]
        if not track_info:
            self.say('Failed to find ' + track)
            return
   
        url = track_info['url']
        logging.debug(url)
        media = self.instance.media_new(url)
        self.player.set_media(media)
   
        # Keep only words and use negative lookahead and lookbehind to remove '_'
        pattern = r'(?!_)\w+(?<!_)'
        self.now_playing = ' '.join(re.findall(pattern, track_info['title']))
        logging.info(self.now_playing)
        self.say('Now playing ' + self.now_playing)
        
        self.player.play()
            
    def _init_player(self):
        self.now_playing = None
        self.instance = vlc.Instance()#vlc.get_default_instance()
        self.player = self.instance.media_player_new()
        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_player_event)
        events.event_attach(vlc.EventType.MediaPlayerEncounteredError, self._on_player_event)

    def _stop(self):
        self.player.stop()

    def _on_player_event(self, event):
        if event.type == vlc.EventType.MediaPlayerEndReached:
            self._stop()
        elif event.type == vlc.EventType.MediaPlayerEncounteredError:
            self.say("Can't play " + self.now_playing)
            self._stop()