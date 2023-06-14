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
import subprocess
import RPi.GPIO as GPIO
#for convenience
#set SPOTIPY_CLIENT_ID='f677b01ff18f46f9a9e19044b00af5ad'
#set SPOTIPY_CLIENT_SECRET='057c14386cd541e984af51f55c6b9ab3'
#set  SPOTIPY_REDIRECT_URI='http://google.com/callback/'
#py api_calls.py 56n6jy66fjt1c199jq2fl5x44

#os.system('run_FFT_analyzer.py')
subprocess.Popen(['python', 'run_FFT_analyzer.py'])

#setting up GPIO PINS
GPIO.setmode(GPIO.BCM)
GPIO.setup(13,GPIO.IN)
GPIO.setup(19,GPIO.IN)
GPIO.setup(26,GPIO.IN)
GPIO.setup(4,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27,GPIO.IN, pull_up_down=GPIO.PUD_UP)
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

#Buttons and shiii
def next(channel):
    spotifyObject.next_track()


def back (channel):
    spotifyObject.previous()


def pause_play (channel):
    spotifyObject.pause_playback()
    
GPIO.add_event_detect(4, GPIO.FALLING, callback=next, bouncetime=600)
GPIO.add_event_detect(27, GPIO.FALLING, callback=back, bouncetime=600)
GPIO.add_event_detect(17, GPIO.FALLING, callback=pause_play, bouncetime=600)
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
current_track_id = track['item']['id']
#artist = spotifyObject.current_user_playing_track()
#print(json.dumps(track, sort_keys=True, indent=4))
artist = track['item']['artists'][0]['name']
track_name = track['item']['name']
print()
print("Currently playing " + artist + " - " + track_name)
print()

#output currently playing album art
#track = spotifyObject.current_user_playing_track()
link = track['item']['album']['images'][0]['url']
u = urllib.request.urlopen(link)
raw_data = u.read()
image = Image.open(io.BytesIO(raw_data))
image = image.resize((400,400), Image.ANTIALIAS)
image = ImageTk.PhotoImage(image)
img = image
label = Label(window, image=img)
label.pack()
#win.mainloop()
window.update()

while True:
    #Checking Switches
    if GPIO.input(13):
        spotifyObject.shuffle(state=True)
        print("reading")
    else:
        spotifyObject.shuffle(state=False)
        print("crying")

    if GPIO.input(19) and GPIO.input(26):
        spotifyObject.repeat(state = 'track')
    elif GPIO.input(26):
        spotifyObject.repeat(state = 'context')
    else:
        spotifyObject.repeat(state = 'off')
        
    new_track = spotifyObject.current_user_playing_track()
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
    
    if  new_track['item']['id'] != current_track_id:
        link = new_track['item']['album']['images'][0]['url']
        u = urllib.request.urlopen(link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        image = image.resize((400,400), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        img = image
        label.configure(image=img)
        label.image = img 
        window.update()
        current_track_id = new_track['item']['id']
    time.sleep(0.25)

displayName = user['display_name']
followers = user['followers']['total']


