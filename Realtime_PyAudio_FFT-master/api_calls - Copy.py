import os
import sys
import json
import webbrowser
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError
import tkinter as tk
from tkinter import Toplevel, Tk, Label, PhotoImage
from PIL import ImageTk, Image
import io
import urllib.request
import argparse
from src.stream_analyzer import Stream_Analyzer
import time

#for convenience
#set SPOTIPY_CLIENT_ID='f677b01ff18f46f9a9e19044b00af5ad'
#set SPOTIPY_CLIENT_SECRET='057c14386cd541e984af51f55c6b9ab3'
#set  SPOTIPY_REDIRECT_URI='http://google.com/callback/'
#py api_calls.py 56n6jy66fjt1c199jq2fl5x44

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=None, dest='device',
                        help='pyaudio (portaudio) device index')
    parser.add_argument('--height', type=int, default=400, dest='height',
                        help='height, in pixels, of the visualizer window')
    parser.add_argument('--n_frequency_bins', type=int, default=400, dest='frequency_bins',
                        help='The FFT features are grouped in bins')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--window_ratio', default='22/10', dest='window_ratio',
                        help='float ratio of the visualizer window. e.g. 24/9')
    parser.add_argument('--sleep_between_frames', dest='sleep_between_frames', action='store_true',
                        help='when true process sleeps between frames to reduce CPU usage (recommended for low update rates)')
    return parser.parse_args()

def convert_window_ratio(window_ratio):
    if '/' in window_ratio:
        dividend, divisor = window_ratio.split('/')
        try:
            float_ratio = float(dividend) / float(divisor)
        except:
            raise ValueError('window_ratio should be in the format: float/float')
        return float_ratio
    raise ValueError('window_ratio should be in the format: float/float')

def run_FFT_analyzer():
    args = parse_args()
    window_ratio = convert_window_ratio(args.window_ratio)

    ear = Stream_Analyzer(
                    device = args.device,        # Pyaudio (portaudio) device index, defaults to first mic input
                    rate   = None,               # Audio samplerate, None uses the default source settings
                    FFT_window_size_ms  = 60,    # Window size used for the FFT transform
                    updates_per_second  = 100,  # How often to read the audio stream for new data
                    smoothing_length_ms = 50,    # Apply some temporal smoothing to reduce noisy features
                    #n_frequency_bins = args.frequency_bins, # The FFT features are grouped in bins
                    n_frequency_bins = 51,
                    visualize = 1,               # Visualize the FFT features with PyGame
                    verbose   = args.verbose,    # Print running statistics (latency, fps, ...)
                    height    = args.height,     # Height, in pixels, of the visualizer window,
                    window_ratio = window_ratio  # Float ratio of the visualizer window. e.g. 24/9
                    )

    fps = 60  #How often to update the FFT features + display
    last_update = time.time()
    while True:
        if (time.time() - last_update) > (1./fps):
            last_update = time.time()
            raw_fftx, raw_fft, binned_fftx, binned_fft = ear.get_audio_features()
        elif args.sleep_between_frames:
            time.sleep(((1./fps)-(time.time()-last_update)) * 0.99)

if __name__ == '__main__':
    api_calls-Copy()


#setting up art output
win = Tk()

win.attributes('-alpha', 0.0)
win.iconify()

window = Toplevel(win)
window.geometry("400x400")
window.overrideredirect(1)


# Get the username from terminal
username = sys.argv[1]
scope = 'user-read-private user-read-playback-state user-modify-playback-state' 
#https://open.spotify.com/user/56n6jy66fjt1c199jq2fl5x44?si=cd8bdfdf88c54ca2
#user id = '56n6jy66fjt1c199jq2fl5x44'
client_id = 'f677b01ff18f46f9a9e19044b00af5ad'
client_secrect = '057c14386cd541e984af51f55c6b9ab3'
redirect_uri = 'http://google.com/callback/'
#Erase cache and prompt for user permission



try:
    token = util.prompt_for_user_token(username, scope, client_id, client_secrect, redirect_uri)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id, client_secrect, redirect_uri)
#create our spotifyObject
spotifyObject = spotipy.Spotify(auth=token)
user = spotifyObject.current_user()
#print(json.dumps(user, sort_keys=True, indent=4))

#get current device
devices = spotifyObject.devices()
#print(json.dumps(devices, sort_keys=True, indent=4))
deviceID = devices['devices'][0]['id']

#check current_playback
playback = spotifyObject.current_playback()
#print(json.dumps(playback, sort_keys=True, indent=4))

total_time = playback['item']['duration_ms']
played_time = playback['progress_ms']
total_time = int(total_time)
played_time = int(played_time)

total_time_seconds = (total_time/1000)%60
total_time_minutes = (total_time/(1000*60))%60
total_time_seconds = int(total_time_seconds)
total_time_minutes = int(total_time_minutes)
if(total_time_seconds <= 9):
    t_s = '0' + str(total_time_seconds)
else:
    t_s = str(total_time_seconds)
    
played_time_seconds = (played_time/1000)%60
played_time_minutes = (played_time/(1000*60))%60
played_time_seconds = int(played_time_seconds)
played_time_minutes = int(played_time_minutes)
if(played_time_seconds <= 9):
    p_s = '0' + str(played_time_seconds)
    
else:
    p_s = str(played_time_seconds)
    


print("Total track time = " + str(total_time_minutes) + ":" + t_s)
print()
print("Played track time = " + str(played_time_minutes) + ":" + p_s)

#current playing track
track = spotifyObject.current_user_playing_track()
#artist = spotifyObject.current_user_playing_track()
#print(json.dumps(track, sort_keys=True, indent=4))
print()
artist = track['item']['artists'][0]['name']
track = track['item']['name']
print("Currently playing " + artist + " - " + track)
print()
#output currently playing album art
track = spotifyObject.current_user_playing_track()
link = track['item']['album']['images'][0]['url']
#art= track['item']['name']
u = urllib.request.urlopen(link)
raw_data = u.read()
image = Image.open(io.BytesIO(raw_data))
image = image.resize((400,400), Image.ANTIALIAS)
image = ImageTk.PhotoImage(image)
img = image
#img = ImageTk.PhotoImage(Image.open(path))
#photo = PhotoImage(file="C:/Users/Carter/ab67616d0000b273cdb645498cd3d8a2db4d05e1.jpg")
label = Label(window, image=img)
label.pack()
win.mainloop()
            

#if artist != "":
#    print("Currently playing " + artist + " - " + track)


displayName = user['display_name']
followers = user['followers']['total']
"""
while True:
    print()
    print(">>> Welcome to Spotipy " + displayName + "!")
    print(">>> You have " + str(followers) + " followers.")
    print()
    print("0 - search for an artist")
    print("1 - exit")
    print()
    choice = input("your choice: ")

    if choice == "0":
        print()
        searchQuery = input("Ok, whats their name: ")
        print()
        
        #search results
        searchResults = spotifyObject.search(searchQuery,1,0,"artist")
        #print(json.dumps(searchResults, sort_keys=True, indent=4))

        #artist details
        artist = searchResults['artists']['items'][0]
        print(artist['name'])
        print(str(artist['followers']['total']) + " followers")
        print(artist['genres'][0])
        print()
        webbrowser.open(artist['images'][0]['url'])
        artistID = artist['id']
        #album and track details
        trackURIs = []
        trackArt = []
        z = 0

        #extract album data
        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults['items']

        for item in albumResults:
            print("Album " + item['name'])
            albumID = item['id']
            albumArt = item['images'][0]['url']

            #extract track data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']

            for item in trackResults:
                print(str(z) + ": " + item['name'])
                trackURIs.append(item['uri'])
                trackArt.append(albumArt)
                z+=1
        print()

        # see album art

        while True:
            songSelection = input("Enter a song number to see the album art(x to exit): ")
            if songSelection == "x":
                break
            #webbrowser.open(trackArt[int(songSelection)])
            trackSelectionList = []
            trackSelectionList.append(trackURIs[int(songSelection)])
            spotifyObject.start_playback(deviceID, None, trackSelectionList)
            webbrowser.open(trackArt[int(songSelection)])
            #print(trackArt[int(songSelection)])
            link = trackArt[int(songSelection)]
            u = urllib.request.urlopen(link)

            raw_data = u.read()
            image = Image.open(io.BytesIO(raw_data))
            image = ImageTk.PhotoImage(image)


            img = image

            #img = ImageTk.PhotoImage(Image.open(path))
            #photo = PhotoImage(file="C:/Users/Carter/ab67616d0000b273cdb645498cd3d8a2db4d05e1.jpg")

            label = Label(window, image=img)
            label.pack()

            win.mainloop()
            
            
    if choice == "1":
        break

#print(json.dumps(VARIABLE, sort_keys=True, indent=4))
"""
