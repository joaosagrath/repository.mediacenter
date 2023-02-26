import xbmcaddon
import xbmcgui
import xml.etree.ElementTree as ET

# Load addon and get path to XML file
addon = xbmcaddon.Addon()
xml_path = xbmc.translatePath(addon.getAddonInfo('path') + '/resources/categories.xml')

# Parse XML file
tree = ET.parse(xml_path)
root = tree.getroot()

# Iterate through categories in XML file
for category in root.iter('category'):
    # Create list item for category
    list_item = xbmcgui.ListItem(label=category.find('m_title').text)
    list_item.setArt({'icon': xbmc.translatePath(addon.getAddonInfo('path') + '/resources/' + category.find('s_icon').text)})

    # Open category when selected
    list_item.setProperty('IsPlayable', 'false')
    list_item.setProperty('IsFolder', 'true')
    url = addon.getAddonInfo('id') + '://' + category.find('id').text
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item)

# End of directory
xbmcplugin.endOfDirectory(int(sys.argv[1]))
