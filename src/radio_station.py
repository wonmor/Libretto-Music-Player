import re
import urllib.request
import vlc
import time

class RadioStation:
    def __init__(self, url: str, streams_override: list[str]=[]):
        self.streams = []
        if not streams_override:
            self.url = url
            # Get radio streams from url
            self.streams = RadioStation.get_streams(url)
            self.set_default_stream()
        else:
            # Assign streams if streams are valid
            if RadioStation.check_stream_validity(streams_override[0])[0]:
                self.streams = streams_override
            self.set_default_stream()
    
    @staticmethod
    def is_stream_playlist(stream_url: str):
        # Create a list of playlist url extensions
        playlist_exts = ["pls", "m3u"]
        # Get url extension
        ext = stream_url.rpartition(".")[-1]
        # Determine if the stream is a playlist
        return ext in playlist_exts

    @staticmethod
    def check_stream_validity(stream_url: str):
        try:
            # Try opening the stream url
            urllib.request.urlopen(stream_url)
        except urllib.error.HTTPError as e:
            # Return the HTTP status code error that was sent with the response (e.g. 404, 501, ...)
            print(f"HTTP Error: {e.code}")
        except urllib.error.URLError as e:
            # Not an HTTP-specific error (e.g. connection refused)
            print(f"URL Error: {e.reason}")
        except Exception as e:
            # Not an HTTP-specific or URL error (e.g. unknow url type)
            print(f"Error: {e}")
        else:
            # Start a vlc instance and try playing the stream
            instance = vlc.Instance()
            player = instance.media_player_new()
            player.audio_set_mute(True)
            
            is_playlist = RadioStation.is_stream_playlist(stream_url)
            if is_playlist:
                player = instance.media_list_player_new()
                media = instance.media_list_new([stream_url])
                player.set_media_list(media)
            else:
                media = instance.media_new(stream_url)
                player.set_media(media)

            player.play()

            print("Checking the stream validity...")
            time.sleep(2)
            # Get the player state
            state = player.get_state()
            # Return true if the state is not an error
            if state != vlc.State.Error and state != vlc.State.Ended:
                player.stop()
                print("Stream is valid!")
                return True, state
            print(f"Stream is not valid! Player State: {state}")
            return False, state
        print("Stream is not valid!")
        return False, None

    def set_default_stream(self, stream_index: int=0):
        # Set the stream that will be played by default
        if stream_index < len(self.streams):
            self.default_stream = self.streams[stream_index]
            # Determine if the default stream is a playlist
            self.is_playlist = RadioStation.is_stream_playlist(self.default_stream)
        else:
            self.default_stream = None
            print("Stream index is out of range!")

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

    @staticmethod
    def get_streams(url: str):
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        raw_file = response.read().decode("utf-8")
        
        # Return the stream urls with regular expressions
        return re.findall(r"stream\":\"(.*?)\"", raw_file)

    def play_radio_stream(self):
        # Check if there is no default stream
        if not self.default_stream:
            print("Can't play radio stream; there is no default stream!")
            return

        # Create a vlc instance and player
        self.vlc_instace = vlc.Instance()
        self.player = self.vlc_instace.media_player_new()
        self.player.audio_set_mute(False)
        
        if self.is_playlist:
            # Set the default stream playlist as the playable media list
            self.player = self.vlc_instace.media_list_player_new()
            self.media = self.vlc_instace.media_list_new([self.default_stream])
            self.player.set_media_list(self.media)
        else:
            # Set the default stream as the playable media
            self.media = self.vlc_instace.media_new(self.default_stream)
            self.media.get_mrl()
            self.player.set_media(self.media)

        self.player.play()

        # Record the previously playing track
        previously_playing = None

        # While the stream is still playing
        while self.player.is_playing:
            time.sleep(1)
            if not self.is_playlist:
                now_playing = self.media.get_meta(12)
                
                if now_playing != previously_playing:
                    # Display the now playing track and record the previously playing track
                    print("Now playing", now_playing)
                    previously_playing = now_playing

                    # Display the currently playing track genre
                    genre = self.media.get_meta(2)
                    if genre:
                        print("Genre:", genre)
        return self.player.audio_get_track_description()


virgin_radio = RadioStation("https://www.iheart.com/live/999-virgin-radio-7481/")
virgin_radio.play_radio_stream()

iheart_radio = RadioStation("https://www.iheart.com/live/iheartradio-top-20-7556/")
iheart_radio.play_radio_stream()

mnm_radio = RadioStation("", ["http://icecast.vrtcdn.be/mnm-high.mp3"])
mnm_radio.play_radio_stream()

virgin_radio_broken = RadioStation("", ["https://www.iheart.com/live/999-virgin-radio-7481/"])
virgin_radio_broken.play_radio_stream()

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