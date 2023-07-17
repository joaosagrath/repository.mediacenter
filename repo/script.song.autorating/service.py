import xbmc
import xbmcaddon
import json
import time

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo("path")

class Monitor(xbmc.Monitor):
    def __init__(self):
        self.is_library_song = False
        pass

    def status_check(self):
        # perform monitor status check
        pass

    def onPlayBackStarted(self):
        # Music Library music is set to "True"
        if start_notification == 'true':
            xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, '{} Started'.format(song_title)))
        self.is_library_song = True

    def onPlayBackStopped(self, current_song, song_id, new_rating):
        # The song stops, the UserRating of the song is saved, then song ID is set to "0", 
        # and currentMusic to "empty" again. Library music is set to "False"
        if self.is_library_song and current_time > 5:            
            if show_notification == 'true' and addon_running == 'true':
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
            xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, ' {} rating is {}'.format(current_song, new_rating)))
            self.is_library_song = False


monitor             = Monitor()
player              = xbmc.Player()
current_song        = ''
song_count          = 0
new_rating          = 0
current_id          = 0 #  Add to match current song tracking
song_id             = 0 #  Add to match original song tracking
song_DBID           = ''

while not monitor.abortRequested():
    try:
        while True:
            
            if xbmc.Player().isPlayingAudio():            
                #  Variables to check if Notifications are ON/OF
                show_notification = 'true' if addon.getSetting("show_notification") == 'true' else 'false'
                start_notification = 'true' if addon.getSetting("start_notification") == 'true' else 'false'
                real_show_notification = 'true' if addon.getSetting("real_show_notification") == 'true' else 'false'
                # Variable to ON/OFF Auto Ratings.
                addon_running = 'true' if addon.getSetting("addon_running") == 'true' else 'false'
                # To check if Kodi is playing a song that is in the library
                song_DBID = xbmc.getInfoLabel('MusicPlayer.DBID') 
                
                if addon_running == 'true' and song_DBID != '':    
                    # Retrieve Song Data from the player
                    song_title      = xbmc.getInfoLabel('MusicPlayer.Title')
                    song_rating     = xbmc.getInfoLabel('MusicPlayer.UserRating')
                    song_length     = int(xbmc.Player().getTotalTime())
                    current_time    = int(player.getTime())
                    song_parts      = int(song_length / 11)
                    song_time_left  = (song_length - current_time)  
                    
                    # To to ensure UserRating is at least "0"
                    if song_rating == '':
                        song_rating = 0    
                    else:
                        song_rating = int(song_rating)
                    
                    # To avoid error "divided by zero"
                    if current_time > 0:
                        calculated_rating = int(current_time / song_parts)                
                        if song_rating == 0 or song_rating == '':
                            new_rating = int(current_time/song_parts)
                            if new_rating > 10:
                                new_rating = 10
                        if song_rating > 0:
                            new_rating = int((song_rating + calculated_rating) / 2)
                            if new_rating > 10:
                                new_rating = 10
                                
                    if current_song == '':
                        monitor.onPlayBackStarted()
                        
                        # Retrieve Song Data as player start:
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.Introspect","id":1}')
                        result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":0,"properties":["userrating"]},"id":1}')
                        song_details = json.loads(result)["result"]["item"]
                        song_id = song_details["id"]
                        current_id = xbmc.getInfoLabel('MusicPlayer.DBID')      #  Get database Id of new song
                        
                        # Set current song from player:
                        current_song = xbmc.getInfoLabel('MusicPlayer.Title')  
                    
                    # If song has changed, first will save current data in previous song,
                    # The will retrieve data for the new song:
                    if current_song != song_title:
                        # Save Song Data in previous song:
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
                        if show_notification == 'true':
                            xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, ' {} rating is {}'.format(current_song, new_rating)))
                        
                        # Retrieve Song Data from new song:
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.Introspect","id":1}')
                        result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":0,"properties":["userrating"]},"id":1}')
                        song_details = json.loads(result)["result"]["item"]
                        song_id = song_details["id"]
                        
                        # Set new current song from player:
                        current_song = xbmc.getInfoLabel('MusicPlayer.Title')
                    
                    # Show Real Time Rating
                    if real_show_notification == 'true':
                        xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, ' {} rating is {}'.format(current_song, new_rating)))
                        
            else:
                # For use when the user stops playback.
                monitor.onPlayBackStopped(current_song, song_id, new_rating)
                current_song = ''
                if song_DBID != '':
                    current_id = song_id = 0
                new_rating = 0
                
            monitor.status_check()

            if monitor.waitForAbort(1):
                break
    except Exception as e:
        xbmc.executebuiltin("Notification(%s, %s)" % ("An error occurred: ", e))