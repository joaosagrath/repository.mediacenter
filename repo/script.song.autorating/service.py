import xbmc
import xbmcaddon
import json
import time

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')


class Monitor(xbmc.Monitor):
    def __init__(self):
        self.is_library_song = False        
        pass
        
    def status_check(self):
        # perform monitor status check
        pass
    
    def onPlayBackStarted(self):        
        self.is_library_song = True
    
    # When the song ends, either by user action, or when the song is
    # the last in the playlist and the "repeat" function is disabled.
    def onPlayBackStopped(self, new_rating, current_time):
        if self.is_library_song and current_time > 5:
            # Saving the new rating as the song stops.
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
            if show_notification == 'true':
                xbmc.executebuiltin("Notification(%s, %s)" % (addon_name, '{} rated to {}'.format(song_title, new_rating)))
            current_song = ''
            self.is_library_song = False

    def calculate_rating(self, new_rating, song_id, song_title, last_id):
        if last_id !=0 and song_id != last_id:
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
        if show_notification == 'true':
            if song_rating == 0:            
                xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, '{} rated to {}'.format(song_title, new_rating)))
            else: 
                xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, '{} rated to {}'.format(song_title, new_rating)))
        current_song = ''
        last_id=song_id
        
monitor             = Monitor()
player              = xbmc.Player()
calculated_rating   = 0
new_rating          = 0
current_time        = 0
total_time          = 0
# Variables to check song skipping
song_title          = ''
current_song        = ''
last_id             = ''
show_notification   = ''
real_show_notification   = ''

while not monitor.abortRequested():
    try:
        while True:
            if xbmc.Player().isPlayingAudio():
                if addon.getSetting("show_notification") == 'true':
                    show_notification = 'true' 
                else:
                    show_notification = 'false' 
                
                if addon.getSetting("real_show_notification") == 'true':
                    real_show_notification = 'true' 
                else:
                    real_show_notification = 'false' 
                    
                if not xbmc.getInfoLabel('MusicPlayer.Title') == '': 
                    
                    # Retrieve data from the currently playing song
                    song_title      = xbmc.getInfoLabel('MusicPlayer.Title')
                    song_rating     = xbmc.getInfoLabel('MusicPlayer.UserRating')
                    song_length     = int(xbmc.Player().getTotalTime())
                    current_time    = int(player.getTime())
                    song_parts      = int(song_length / 11)
                    
                    if song_rating == '':
                        song_rating = 0    
                    else:
                        song_rating = int(song_rating)
                    
                    if current_time > 0:
                        calculated_rating = int(current_time / song_parts)                
                        if song_rating == 0 or song_rating == '':
                            new_rating = int(current_time/song_parts)
                        if song_rating > 0:
                            new_rating = int((song_rating + calculated_rating) / 2)
                    
                    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.Introspect","id":1}')
                    result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":0,"properties":["userrating"]},"id":1}')
                    song_details = json.loads(result)["result"]["item"]
                    song_id = song_details["id"]

                    if current_song == '':
                        monitor.onPlayBackStarted()
                        current_song = song_title                    
                    
                    song_time_left = (song_length - current_time)
                    
                    # Resting only two seconds before the song finish.
                    if song_time_left <= 2:                
                        monitor.calculate_rating(new_rating, song_id, song_title, last_id)
                        current_song = xbmc.getInfoLabel('MusicPlayer.Title')
                        
                    # HERE NEED TO FIND A WAY TO SAVE THE NEW_RATING FROM LINE 66 OR 68
                    # IN THE SKIPPED SONG, NOT IN THE NEXT SONG
                    if song_time_left > 2 and current_song != song_title:                        
                        xbmc.executebuiltin("Notification(%s, %s, time=2000)" % ('{}'.format(current_song), 'Song Skipped'))                        
                        monitor.calculate_rating(new_rating, song_id, song_title, last_id)
                        current_song = xbmc.getInfoLabel('MusicPlayer.Title')
                    
                    if real_show_notification == 'true':
                        xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, '{} rated to {}'.format(song_title, new_rating)))                    
            else:
                monitor.onPlayBackStopped(new_rating, current_time)
            
            monitor.status_check()
            
            if monitor.waitForAbort(1): 
                break                  
    except Exception as e:
        xbmc.executebuiltin("Notification(%s, %s)" % ("An error occurred: ", e))