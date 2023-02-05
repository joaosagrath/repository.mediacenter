import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

addon = xbmcaddon.Addon()

def show_message(message):
    xbmc.executebuiltin("Notification(%s,%s,3000)" % (addon.getAddonInfo("name"), message))

def show_context_menu(params):
    li = xbmcgui.ListItem("Option 1")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url="", listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def run():
    params = dict(arg.split("=") for arg in sys.argv[2][1:].split("&"))
    if "info" in params:
        show_message("You selected: " + params["info"])
    else:
        show_context_menu(params)

run()
