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
import time
import RPi.GPIO as GPIO
#for convenience
#set SPOTIPY_CLIENT_ID='f677b01ff18f46f9a9e19044b00af5ad'
#set SPOTIPY_CLIENT_SECRET='057c14386cd541e984af51f55c6b9ab3'
#set SPOTIPY_REDIRECT_URI='http://google.com/callback/'
#py api_calls.py 56n6jy66fjt1c199jq2fl5x44



def wait_for_press_next(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        GPIO.wait_for_edge(pin, GPIO.FALLING)
        current = SpotifyObject.next_track()
def main():

    #setting up GPIO PINS
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(13,GPIO.IN)
    GPIO.setup(19,GPIO.IN)
    GPIO.setup(26,GPIO.IN)
     
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

    #Switches toggling shuffle and replay
    if GPIO.input(13):
        self.spotifyObject.shuffle(1)
    
    
    #current playing track
    track = spotifyObject.current_user_playing_track()
    #artist = spotifyObject.current_user_playing_track()
    print(json.dumps(track, sort_keys=True, indent=4))
    print()
    artist = track['item']['artists'][0]['name']
    track = track['item']['name']
    print("Currently playing " + artist + " - " + track)

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

    #setting up the buttons to listen
    
    button_thread = threading.Thread(target=wait_for_button_press_next, args =(4,))
    button_thread.start()

   

    
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
