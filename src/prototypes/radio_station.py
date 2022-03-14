import re
import urllib.request
import vlc
import time

class RadioStation:
    def __init__(self, url: str, streams_override: list[str]=[], check_default_stream_validity: bool=False):
        if not streams_override:
            self.url = url
            # Get radio streams from url
            self.streams = self.get_streams()
            self.set_default_stream()
        else:
            # Assign streams if streams are valid or check_default_stream_validity is set to False
            if (not check_default_stream_validity or self.check_stream_validity(streams_override[0])[0]):
                self.streams = streams_override
                self.set_default_stream()
            else:
                self.default_stream = None
    
    def set_default_stream(self, stream_index: int=0):
        # Set the stream that will be played by default
        if stream_index < len(self.streams):
            self.default_stream = self.streams[stream_index]
    
    def check_stream_validity(self, stream_url: str):
        # Returns the HTTP status code that was sent with the response
        code = str(urllib.request.urlopen(stream_url).getcode())
        # Check if the code starts with a 2 or 3 (not an error code)
        if code.startswith("2") or code.startswith("3"):
            # Start a vlc instance and try playing the stream
            instance = vlc.Instance()
            player = instance.media_player_new()
            media = instance.media_new(stream_url)
            player.set_media(media)
            player.audio_set_mute(True)
            player.play()

            print("Checking the stream validity...")
            time.sleep(3)
            # Get the player state
            state = player.get_state()
            # Return true if the state is not an error
            if state != vlc.State.Error:
                player.stop()
                print("Stream is valid!")
                return True, state
            print("Stream is not valid!")
            return False, state
        print("Stream is not valid!")
        return False, None

    def add_stream_manual(self, stream_url: str, default: bool=True):
        # Get the stream validity before trying to add the stream
        valid_stream = self.check_stream_validity(stream_url)[0]
        if not valid_stream:
            print("Could not add stream!")
            return 0

        if default:
            # Add as the first stream in the list
            index = 0
            self.streams.insert(index, stream_url)
            self.set_default_stream()
            # Return the added stream index
            return index
        else:
            # Add as the last stream in the list
            self.streams.append(stream_url)
            index = len(self.streams) - 1
            # Return the added stream index
            return index

    def get_streams(self):
        request = urllib.request.Request(self.url)
        response = urllib.request.urlopen(request)
        raw_file = response.read().decode("utf-8")
        
        # Return the stream urls with regular expressions
        return re.findall(r"stream\":\"(.*?)\"", raw_file)

'''
Finding the stream URL using Chrome Dev Tools or Mozilla Firefox Firebug:
- Right click
- View page source
- Find stream urls
'''

'''
99.9 Virgin Radio
"hls_stream":"http://playerservices.streamtheworld.com/api/livestream-redirect/CKFMFM_ADP.m3u8"
"secure_mp3_pls_stream":"https://playerservices.streamtheworld.com/pls/CKFMFM.pls"
"pls_stream":"http://playerservices.streamtheworld.com/pls/CKFMFMAAC.pls"
"secure_hls_stream":"https://playerservices.streamtheworld.com/api/livestream-redirect/CKFMFM_ADP.m3u8"
"secure_pls_stream":"https://playerservices.streamtheworld.com/pls/CKFMFMAAC.pls"

Belgian radio station (MNM) example: http://icecast.vrtcdn.be/mnm-high.mp3 (includes now playing info)

IHeart radio playlist: https://playerservices.streamtheworld.com/pls/ST13_S01.pls
'''