import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from pythonosc import udp_client
import logging
import json
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout

with open('app/color_codes.json', 'r') as f:

    COLOR_CODES_RAW = json.load(f)
    COLOR_CODES = {k: v.encode().decode('unicode_escape') for k, v in COLOR_CODES_RAW.items()}

with open('app/keys.json', 'r') as f:
    keys = json.load(f)
    
class MinecraftColorFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        return self.apply_color_codes(message)
    
    @staticmethod
    def apply_color_codes(text):
        i = 0
        while i < len(text) - 1:
            if text[i] == '&' and text[i + 1] in COLOR_CODES:
                color_code = COLOR_CODES[text[i + 1]]
                text = text[:i] + color_code + text[i + 2:]
                i += len(color_code) - 1
            else:
                i += 1
        return text + '\033[0m'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(MinecraftColorFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(console_handler)

SPOTIPY_CLIENT_ID = keys['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = keys['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = keys['SPOTIPY_REDIRECT_URI']
SCOPE = 'user-read-currently-playing user-read-playback-state'

VRCHAT_IP = '127.0.0.1'
VRCHAT_PORT = 9000

logger.info("&aOpening UDP port for OSC communication...")
osc_client = udp_client.SimpleUDPClient(VRCHAT_IP, VRCHAT_PORT)
logger.info("&aUDP port successfully opened!")

logger.info("&aPrompting Spotify login...")
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE),
                     requests_timeout=10,
                     retries=5)


def send_to_vrchat(message):
    """
    Sends a message to the VRChat chatbox.
    """
    logger.info(f"&bSending to VRChat: &r{message}")
    osc_client.send_message('/chatbox/input', [message, True])

def get_current_track():
    """
    Fetches the currently playing track from Spotify.
    Returns a tuple: (track_name, artist_name, is_playing, progress_ms, repeat_status)
    """
    try:

        current_track = sp.current_user_playing_track()
        current_playback = sp.current_playback()

        if current_track is not None:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            is_playing = current_track['is_playing']
            progress_ms = current_track['progress_ms']
            repeat_status = current_playback.get('repeat_state', 'unknown')
            return track_name, artist_name, is_playing, progress_ms, repeat_status
        return None, None, False, None, None
    except (ReadTimeoutError, ReadTimeout) as e:
        logger.warning("&eSpotify API request timed out. Retrying...")
        return None, None, False, None, None

def main():
    """
    Main loop to monitor the currently playing track and send updates to VRChat.
    """
    logger.info("&6Starting Spotify to VRChat OSC bridge...")
    last_track = None
    last_playing_state = False
    last_ms = 0

    while True:

        track_name, artist_name, is_playing, progress_ms, repeat_state = get_current_track()

        if track_name and artist_name:
            
            current_track = f"{track_name} - {artist_name}"
            
            if current_track != last_track:
                logger.info(f"&eSong changed: &r{current_track}")
                send_to_vrchat(current_track)
                last_track = current_track
                last_playing_state = is_playing

            if not last_playing_state and is_playing:
                logger.info(f"&eResumed playing: &r{current_track}")
                send_to_vrchat(current_track)
                last_playing_state = True

            if last_playing_state and not is_playing:
                logger.info("&cPlayback paused.")
                last_playing_state = False

            if (progress_ms + 10000) < last_ms and repeat_state == "track":
                logger.info(f"&eTrack looped: &r{current_track}")
                send_to_vrchat(current_track)

            last_ms = progress_ms
                
        time.sleep(1)
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("&cProgram terminated by user.")
    except Exception as e:
        logger.error(f"&4An error occurred: &r{e}")