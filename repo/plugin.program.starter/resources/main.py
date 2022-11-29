# -*- coding: utf-8 -*-

# Copyright (c) 2016-2021 Wintermute0110 <wintermute0110@gmail.com>
# Portions (c) 2010-2015 Angelscry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# Starter main script file.

# First include modules in this package, then Kodi modules, finally standard library modules.

# --- Modules/packages in this plugin ---
from .constants import *
from .misc import *
from .utils import *
from .disk_IO import *
from .net_IO import *
from .assets import *
from .rom_audit import *
from .scrap import *
from .autoconfig import *
from .md import *

# --- Kodi stuff ---
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

# --- Python standard library ---
# Fix this: from collections import OrderedDict
import collections
import fnmatch
import hashlib
import os
import re
import shlex
import shutil
import socket
import string
import subprocess
import sys
import time
import traceback
if ADDON_RUNNING_PYTHON_2:
    import urlparse
elif ADDON_RUNNING_PYTHON_3:
    import urllib.parse
else:
    raise TypeError('Undefined Python runtime version.')

# --- Addon paths and constant definition ---
# _PATH is a filename | _DIR is a directory name (with trailing /).
class AEL_Paths:
    def __init__(self):
        # --- Kodi-related variables and data ---
        self.addon = kodi_addon_obj()

        # --- Base paths ---
        self.HOME_DIR = FileName('special://home')
        self.PROFILE_DIR = FileName('special://profile')
        self.ADDONS_DATA_DIR = FileName('special://profile/addon_data')
        self.ADDON_DATA_DIR = self.ADDONS_DATA_DIR.pjoin(self.addon.info_id)
        self.ADDONS_CODE_DIR = self.HOME_DIR.pjoin('addons')
        self.ADDON_CODE_DIR = self.ADDONS_CODE_DIR.pjoin(self.addon.info_id)
        self.ICON_FILE_PATH = self.ADDON_CODE_DIR.pjoin('media/icon.png')
        self.FANART_FILE_PATH = self.ADDON_CODE_DIR.pjoin('media/fanart.jpg')

        # --- Databases and reports ---
        self.CATEGORIES_FILE_PATH      = self.ADDON_DATA_DIR.pjoin('categories.xml')
        self.FAV_JSON_FILE_PATH        = self.ADDON_DATA_DIR.pjoin('favourites.json')
        self.COLLECTIONS_FILE_PATH     = self.ADDON_DATA_DIR.pjoin('collections.xml')
        self.VCAT_TITLE_FILE_PATH      = self.ADDON_DATA_DIR.pjoin('vcat_title.xml')
        self.VCAT_YEARS_FILE_PATH      = self.ADDON_DATA_DIR.pjoin('vcat_years.xml')
        self.VCAT_GENRE_FILE_PATH      = self.ADDON_DATA_DIR.pjoin('vcat_genre.xml')
        self.VCAT_DEVELOPER_FILE_PATH  = self.ADDON_DATA_DIR.pjoin('vcat_developers.xml')
        self.VCAT_NPLAYERS_FILE_PATH   = self.ADDON_DATA_DIR.pjoin('vcat_nplayers.xml')
        self.VCAT_ESRB_FILE_PATH       = self.ADDON_DATA_DIR.pjoin('vcat_esrb.xml')
        self.VCAT_RATING_FILE_PATH     = self.ADDON_DATA_DIR.pjoin('vcat_rating.xml')
        self.VCAT_CATEGORY_FILE_PATH   = self.ADDON_DATA_DIR.pjoin('vcat_category.xml')
        self.LAUNCH_LOG_FILE_PATH      = self.ADDON_DATA_DIR.pjoin('launcher.log')
        self.RECENT_PLAYED_FILE_PATH   = self.ADDON_DATA_DIR.pjoin('history.json')
        self.MOST_PLAYED_FILE_PATH     = self.ADDON_DATA_DIR.pjoin('most_played.json')

        # Reports
        self.BIOS_REPORT_FILE_PATH = self.ADDON_DATA_DIR.pjoin('report_BIOS.txt')
        self.LAUNCHER_REPORT_FILE_PATH = self.ADDON_DATA_DIR.pjoin('report_Launchers.txt')
        self.ROM_SYNC_REPORT_FILE_PATH = self.ADDON_DATA_DIR.pjoin('report_ROM_sync_status.txt')
        self.ROM_ART_INTEGRITY_REPORT_FILE_PATH = self.ADDON_DATA_DIR.pjoin('report_ROM_artwork_integrity.txt')

        # --- Offline scraper databases ---
        self.GAMEDB_INFO_DIR           = self.ADDON_CODE_DIR.pjoin('data-AOS')
        self.GAMEDB_JSON_BASE_NOEXT    = 'AOS_GameDB_info'
        # self.LAUNCHBOX_INFO_DIR        = self.ADDON_CODE_DIR.pjoin('LaunchBox')
        # self.LAUNCHBOX_JSON_BASE_NOEXT = 'LaunchBox_info'

        # --- Online scraper on-disk cache ---
        self.SCRAPER_CACHE_DIR = self.ADDON_DATA_DIR.pjoin('ScraperCache')

        # --- Artwork and NFO for Categories and Launchers ---
        self.DEFAULT_CAT_ASSET_DIR     = self.ADDON_DATA_DIR.pjoin('asset-categories')
        self.DEFAULT_COL_ASSET_DIR     = self.ADDON_DATA_DIR.pjoin('asset-collections')
        self.DEFAULT_LAUN_ASSET_DIR    = self.ADDON_DATA_DIR.pjoin('asset-launchers')
        self.DEFAULT_FAV_ASSET_DIR     = self.ADDON_DATA_DIR.pjoin('asset-favourites')
        self.VIRTUAL_CAT_TITLE_DIR     = self.ADDON_DATA_DIR.pjoin('db_title')
        self.VIRTUAL_CAT_YEARS_DIR     = self.ADDON_DATA_DIR.pjoin('db_year')
        self.VIRTUAL_CAT_GENRE_DIR     = self.ADDON_DATA_DIR.pjoin('db_genre')
        self.VIRTUAL_CAT_DEVELOPER_DIR = self.ADDON_DATA_DIR.pjoin('db_developer')
        self.VIRTUAL_CAT_NPLAYERS_DIR  = self.ADDON_DATA_DIR.pjoin('db_nplayer')
        self.VIRTUAL_CAT_ESRB_DIR      = self.ADDON_DATA_DIR.pjoin('db_esrb')
        self.VIRTUAL_CAT_RATING_DIR    = self.ADDON_DATA_DIR.pjoin('db_rating')
        self.VIRTUAL_CAT_CATEGORY_DIR  = self.ADDON_DATA_DIR.pjoin('db_category')
        self.ROMS_DIR                  = self.ADDON_DATA_DIR.pjoin('db_ROMs')
        self.COLLECTIONS_DIR           = self.ADDON_DATA_DIR.pjoin('db_Collections')
        self.REPORTS_DIR               = self.ADDON_DATA_DIR.pjoin('reports')

# --- Global variables ---
# This should not be a global variable. Use functional programming!
g_PATHS = AEL_Paths()

# For compatibility with the future (to easy the transition).
# See the code in AML. Global cfg variable to simulate function parameter.
cfg = g_PATHS

# Use functional programming as much as possible and avoid global variables.
# g_base_url must be a global variable because it is used in the misc_url_*() functions.
g_base_url = ''

# Module loading time. This variable is read only (only modified here).
g_time_str = text_type(datetime.datetime.now())

# Make AEL to run only 1 single instance
# See http://forum.kodi.tv/showthread.php?tid=310697
class SingleInstance:
    # Class variables
    monitor = xbmc.Monitor()
    window = xbmcgui.Window(10000)
    LOCK_PROPNAME = 'AEL_instance_lock'
    LOCK_VALUE = 'True'

    # def __init__(self): log_debug('SingleInstance::__init__() Begin...')

    # def __del__(self): log_debug('SingleInstance::__del__() Begin...')

    def __enter__(self):
        # --- If property is True then another instance of AEL is running ---
        prop_name = SingleInstance.window.getProperty(SingleInstance.LOCK_PROPNAME)
        if prop_name == SingleInstance.LOCK_VALUE:
            log_warning('SingleInstance::__enter__() Lock in use. Aborting AEL execution')
            # Apparently this message pulls the focus out of the launcher app. Disable it.
            # Has not effect. Kodi steals the focus from the launched app even if not message.
            kodi_dialog_OK('Another instance of AEL is running! Wait until the scraper finishes '
                'or close the launched application before launching a new one and try again.')
            raise SystemExit
        if SingleInstance.monitor.abortRequested():
            log_info('monitor.abortRequested() is True. Exiting plugin ...')
            raise SystemExit

        # --- Acquire lock for this instance ---
        log_debug('SingleInstance::__enter__() Lock not in use. Setting lock')
        SingleInstance.window.setProperty(SingleInstance.LOCK_PROPNAME, SingleInstance.LOCK_VALUE)
        return True

    def __exit__(self, type, value, traceback):
        # --- Print information about exception if any ---
        # If type == value == tracebak == None no exception happened
        if type:
            log_error('SingleInstance::__exit__() Unhandled excepcion in protected code')

        # --- Release lock even if an exception happened ---
        log_debug('SingleInstance::__exit__() Releasing lock')
        SingleInstance.window.setProperty(SingleInstance.LOCK_PROPNAME, '')

# ---------------------------------------------------------------------------------------------
# URL building functions. A set of functions to help making plugin URLs.
# g_base_url is plugin://plugin.program.AML/
# Normal URLs: plugin://plugin.program.AML/?command=xxxxx
# RunPlugin URLs: RunPlugin(plugin://plugin.program.AML/?command=xxxxx)
#
# Normal URLs are used in xbmcplugin.addDirectoryItem()
# RunPlugin URLs are used in listitem.addContextMenuItems()
#
# '&' must be scaped to '%26' in all URLs. What about other non-ASCII characters?
# ---------------------------------------------------------------------------------------------
# To speed up it could be interesting to add custom functions that do not check
# the number of arguments, specially for ROM rendering.
def aux_url(command, categoryID = None, launcherID = None, romID = None):
    if romID is not None:
        return '{}?com={}&catID={}&launID={}&romID={}'.format(g_base_url, command,
            categoryID, launcherID, romID)
    elif launcherID is not None:
        return '{}?com={}&catID={}&launID={}'.format(g_base_url, command, categoryID, launcherID)
    elif categoryID is not None:
        return '{}?com={}&catID={}'.format(g_base_url, command, categoryID)

    return '{}?com={}'.format(g_base_url, command)

# Kodi Matrix do not support XBMC.RunPlugin() anymore.
# Leia can run RunPlugin() commands w/o XBMC prefix.
# What about Krypton?
def aux_url_RP(command, categoryID = None, launcherID = None, romID = None):
    if romID is not None:
        return 'RunPlugin({}?com={}&catID={}&launID={}&romID={})'.format(g_base_url, command,
            categoryID, launcherID, romID)
    elif launcherID is not None:
        return 'RunPlugin({}?com={}&catID={}&launID={})'.format(g_base_url, command,
            categoryID, launcherID)
    elif categoryID is not None:
        return 'RunPlugin({}?com={}&catID={})'.format(g_base_url, command, categoryID)

    return 'RunPlugin({}?com={})'.format(g_base_url, command)

def aux_url_search(command, categoryID, launcherID, search_type, search_string):
    return '{}?com={}&catID={}&launID={}&search_type={}&search_string={}'.format(g_base_url,
        command, categoryID, launcherID, search_type, search_string)

# Edits a generic string using the GUI.
# 
# edict -> Dictionary to be edited. Category, Launcher or ROM.
# fname -> Field name in edict to be edited. Example: 'm_year'.
# prop_name -> Property name string. Example: 'Launcher Release Year'
#
# Returns True if edict was changed, false otherwise.
def aux_edit_str(edict, fname, prop_name):
    old_value_str = edict[fname]
    keyboard = KodiKeyboardDialog('Edit {}'.format(prop_name), old_value_str)
    keyboard.executeDialog()
    if not keyboard.isConfirmed():
        kodi_notify('{} not changed'.format(prop_name))
        return False
    if ADDON_RUNNING_PYTHON_2:
        new_value_str = keyboard.getData().strip().decode('utf-8')
    elif ADDON_RUNNING_PYTHON_3:
        new_value_str = keyboard.getData().strip()
    else:
        raise TypeError('Undefined Python runtime version.')
    new_value_str = new_value_str if new_value_str else old_value_str
    if old_value_str == new_value_str:
        kodi_notify('{} not changed'.format(prop_name))
        return False
    edict[fname] = new_value_str
    kodi_notify('{} is now {}'.format(prop_name, new_value_str))
    return True

class Main:
    # Main code. This is the plugin entry point.
    def run_plugin(self, addon_argv):
        global g_base_url

        # --- Initialise log system ---
        # Force DEBUG log level for development.
        # Place it before settings loading so settings can be dumped during debugging.
        # set_log_level(LOG_DEBUG)

        # --- Fill in settings dictionary using __addon_obj__.getSetting() ---
        self.settings = {}
        self._get_settings()
        set_log_level(self.settings['log_level'])

        # --- Some debug stuff for development ---
        log_debug('---------- Called AEL Main::run_plugin() constructor ----------')
        log_debug('sys.platform   "{}"'.format(sys.platform))
        # log_debug('WindowId       "{}"'.format(xbmcgui.getCurrentWindowId()))
        # log_debug('WindowName     "{}"'.format(xbmc.getInfoLabel('Window.Property(xmlfile)')))
        log_debug('Python version "' + sys.version.replace('\n', '') + '"')
        # log_debug('addon_name     "{}"'.format(g_PATHS.addon.info_name))
        log_debug('addon_id       "{}"'.format(g_PATHS.addon.info_id))
        log_debug('addon_version  "{}"'.format(g_PATHS.addon.info_version))
        # log_debug('addon_author   "{}"'.format(g_PATHS.addon.info_author))
        # log_debug('addon_profile  "{}"'.format(g_PATHS.addon.info_profile))
        # log_debug('addon_type     "{}"'.format(g_PATHS.addon.info_type))
        for i in range(len(addon_argv)): log_debug('addon_argv[{}] "{}"'.format(i, addon_argv[i]))
        # log_debug('PLUGIN_DATA_DIR OP "{}"'.format(g_PATHS.PLUGIN_DATA_DIR.getOriginalPath()))
        # log_debug('PLUGIN_DATA_DIR  P "{}"'.format(g_PATHS.PLUGIN_DATA_DIR.getPath()))
        # log_debug('ADDON_CODE_DIR OP "{}"'.format(g_PATHS.ADDON_CODE_DIR.getOriginalPath()))
        # log_debug('ADDON_CODE_DIR  P "{}"'.format(g_PATHS.ADDON_CODE_DIR.getPath()))

        # Print Python module path..
        # for i in range(len(sys.path)): log_debug('sys.path[{}] "{}"'.format(i, text_type(sys.path[i])))

        # --- Get DEBUG information for the log --
        if self.settings['log_level'] == LOG_DEBUG:
            json_rpc_start = time.time()

            # Properties: Kodi name and version
            p_dic = {'properties' : ['name', 'version']}
            response_props = kodi_jsonrpc_dict('Application.GetProperties', p_dic)
            # Skin in use
            p_dic = {'setting' : 'lookandfeel.skin'}
            response_skin = kodi_jsonrpc_dict('Settings.GetSettingValue', p_dic)

            # Print time consumed by JSON RPC calls
            json_rpc_end = time.time()
            # log_debug('JSON RPC time {0:.3f} ms'.format((json_rpc_end - json_rpc_start) * 1000))

            # Parse returned JSON and nice print.
            r_name = response_props['name']
            r_major = response_props['version']['major']
            r_minor = response_props['version']['minor']
            r_revision = response_props['version']['revision']
            r_tag = response_props['version']['tag']
            r_skin = response_skin['value']
            log_debug('JSON version "{}" "{}" "{}" "{}" "{}"'.format(
                r_name, r_major, r_minor, r_revision, r_tag))
            log_debug('JSON skin    "{}"'.format(r_skin))

            # --- Save all Kodi settings into a file for DEBUG ---
            # c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
            #          ' "method" : "Settings.GetSettings",'
            #          ' "params" : {"level":"expert"}}')
            # response = xbmc.executeJSONRPC(c_str)

        # Kiosk mode for skins.
        # Do not change context menus with listitem.addContextMenuItems() in Kiosk mode.
        # In other words, change the CM if Kiosk mode is disabled.
        self.g_kiosk_mode_disabled = xbmc.getCondVisibility('!Skin.HasSetting(KioskMode.Enabled)')

        # --- Addon data paths creation ---
        if not g_PATHS.ADDON_DATA_DIR.exists():            g_PATHS.ADDON_DATA_DIR.makedirs()
        if not g_PATHS.SCRAPER_CACHE_DIR.exists():         g_PATHS.SCRAPER_CACHE_DIR.makedirs()
        if not g_PATHS.DEFAULT_CAT_ASSET_DIR.exists():     g_PATHS.DEFAULT_CAT_ASSET_DIR.makedirs()
        if not g_PATHS.DEFAULT_COL_ASSET_DIR.exists():     g_PATHS.DEFAULT_COL_ASSET_DIR.makedirs()
        if not g_PATHS.DEFAULT_LAUN_ASSET_DIR.exists():    g_PATHS.DEFAULT_LAUN_ASSET_DIR.makedirs()
        if not g_PATHS.DEFAULT_FAV_ASSET_DIR.exists():     g_PATHS.DEFAULT_FAV_ASSET_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_TITLE_DIR.exists():     g_PATHS.VIRTUAL_CAT_TITLE_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_YEARS_DIR.exists():     g_PATHS.VIRTUAL_CAT_YEARS_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_GENRE_DIR.exists():     g_PATHS.VIRTUAL_CAT_GENRE_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_DEVELOPER_DIR.exists(): g_PATHS.VIRTUAL_CAT_DEVELOPER_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_NPLAYERS_DIR.exists():  g_PATHS.VIRTUAL_CAT_NPLAYERS_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_ESRB_DIR.exists():      g_PATHS.VIRTUAL_CAT_ESRB_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_RATING_DIR.exists():    g_PATHS.VIRTUAL_CAT_RATING_DIR.makedirs()
        if not g_PATHS.VIRTUAL_CAT_CATEGORY_DIR.exists():  g_PATHS.VIRTUAL_CAT_CATEGORY_DIR.makedirs()
        if not g_PATHS.ROMS_DIR.exists():                  g_PATHS.ROMS_DIR.makedirs()
        if not g_PATHS.COLLECTIONS_DIR.exists():           g_PATHS.COLLECTIONS_DIR.makedirs()
        if not g_PATHS.REPORTS_DIR.exists():               g_PATHS.REPORTS_DIR.makedirs()

        # --- Process URL ---
        g_base_url = addon_argv[0]
        self.addon_handle = int(addon_argv[1])
        if ADDON_RUNNING_PYTHON_2:
            args = urlparse.parse_qs(addon_argv[2][1:])
        elif ADDON_RUNNING_PYTHON_3:
            args = urllib.parse.parse_qs(addon_argv[2][1:])
        else:
            raise TypeError('Undefined Python runtime version.')
        # log_debug('args = {}'.format(args))
        # Interestingly, if plugin is called as type executable then args is empty.
        # However, if plugin is called as type video then Kodi adds the following
        # even for the first call: 'content_type': ['video']
        self.content_type = args['content_type'] if 'content_type' in args else None
        log_debug('content_type = {}'.format(self.content_type))

        # --- Addon first-time initialisation ---
        # >> When the addon is installed and the file categories.xml does not exist, just
        #    create an empty one with a default launcher.
        # >> NOTE Not needed anymore. Skins using shortcuts and/or widgets will call AEL concurrently
        #         and AEL should return an empty list with no GUI warnings or dialogs.
        # if not CATEGORIES_FILE_PATH.exists():
        #     kodi_dialog_OK('It looks it is the first time you run Starter! ' +
        #                    'A default categories.xml has been created. You can now customise it to your needs.')
        #     self._cat_create_default()
        #     fs_write_catfile(CATEGORIES_FILE_PATH, self.categories, self.launchers)

        # --- Load categories.xml and fill categories and launchers dictionaries ---
        self.categories = {}
        self.launchers = {}
        self.update_timestamp = fs_load_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)

        # --- Get addon command ---
        command = args['com'][0] if 'com' in args else 'SHOW_ADDON_ROOT'
        log_debug('command = "{}"'.format(command))

        # --- Commands that do not modify the databases are allowed to run concurrently ---
        concurrent_command_set = {
            'SHOW_ADDON_ROOT',
            'SHOW_VCATEGORIES_ROOT',
            'SHOW_AEL_OFFLINE_LAUNCHERS_ROOT',
            'SHOW_LB_OFFLINE_LAUNCHERS_ROOT',
            'SHOW_FAVOURITES',
            'SHOW_VIRTUAL_CATEGORY',
            'SHOW_RECENTLY_PLAYED',
            'SHOW_MOST_PLAYED',
            'SHOW_UTILITIES_VLAUNCHERS',
            'SHOW_GLOBALREPORTS_VLAUNCHERS',
            'SHOW_COLLECTIONS',
            'SHOW_COLLECTION_ROMS',
            'SHOW_LAUNCHERS',
            'SHOW_ROMS',
            'SHOW_VLAUNCHER_ROMS',
            'SHOW_AEL_SCRAPER_ROMS',
            'SHOW_LB_SCRAPER_ROMS',
            'EXEC_SHOW_CLONE_ROMS',
            'SHOW_CLONE_ROMS',
            'SHOW_ALL_CATEGORIES',
            'SHOW_ALL_LAUNCHERS',
            'SHOW_ALL_ROMS',
            'BUILD_GAMES_MENU',
        }
        if command in concurrent_command_set:
            self.run_concurrent(command, args)
        else:
            # Ensure AEL only runs one instance at a time
            with SingleInstance():
                self.run_protected(command, args)
        log_debug('Starter run_plugin() exit')

    # This function may run concurrently with other AEL instances.
    # Do not write files, only read stuff.
    def run_concurrent(self, command, args):
        log_debug('Starter run_concurrent() BEGIN')

        # --- Name says it all ---
        if command == 'SHOW_ADDON_ROOT':
            self._command_render_root_window()

        # --- Render launchers stuff ---
        elif command == 'SHOW_VCATEGORIES_ROOT':
            self._gui_render_vcategories_root()
        elif command == 'SHOW_AEL_OFFLINE_LAUNCHERS_ROOT':
            self._gui_render_AEL_scraper_launchers()
        elif command == 'SHOW_LB_OFFLINE_LAUNCHERS_ROOT':
            self._gui_render_LB_scraper_launchers()
        elif command == 'SHOW_FAVOURITES':
            self._command_render_favourites()
        elif command == 'SHOW_VIRTUAL_CATEGORY':
            self._command_render_virtual_category(args['catID'][0])
        elif command == 'SHOW_RECENTLY_PLAYED':
            self._command_render_recently_played()
        elif command == 'SHOW_MOST_PLAYED':
            self._command_render_most_played()
        elif command == 'SHOW_UTILITIES_VLAUNCHERS':
            self._gui_render_Utilities_vlaunchers()
        elif command == 'SHOW_GLOBALREPORTS_VLAUNCHERS':
            self._gui_render_GlobalReports_vlaunchers()

        elif command == 'SHOW_COLLECTIONS':
            self._command_render_collections()
        elif command == 'SHOW_COLLECTION_ROMS':
            self._command_render_collection_ROMs(args['catID'][0], args['launID'][0])
        elif command == 'SHOW_LAUNCHERS':
            self._command_render_launchers(args['catID'][0])

        # --- Show ROMs in launcher/virtual launcher ---
        elif command == 'SHOW_ROMS':
            self._command_render_roms(args['catID'][0], args['launID'][0])
        elif command == 'SHOW_VLAUNCHER_ROMS':
            self._command_render_virtual_launcher_roms(args['catID'][0], args['launID'][0])
        elif command == 'SHOW_AEL_SCRAPER_ROMS':
            self._command_render_AEL_scraper_roms(args['catID'][0])
        elif command == 'SHOW_LB_SCRAPER_ROMS':
            self._command_render_LB_scraper_roms(args['catID'][0])
        # Auxiliar command to render clone ROM list from context menu in Parent/Clone mode.
        elif command == 'EXEC_SHOW_CLONE_ROMS':
            url = aux_url('SHOW_CLONE_ROMS', args['catID'][0], args['launID'][0], args['romID'][0])
            xbmc.executebuiltin('Container.Update({})'.format(url))
        elif command == 'SHOW_CLONE_ROMS':
            self._command_render_clone_roms(args['catID'][0], args['launID'][0], args['romID'][0])

        # --- Skin commands ---
        # This commands render Categories/Launcher/ROMs and are used by skins to build shortcuts.
        # Do not render virtual launchers.
        # NOTE Renamed this to follow a scheme like in AML, _skin_zxczxcxzc()
        elif command == 'SHOW_ALL_CATEGORIES':
            self._command_render_all_categories()
        elif command == 'SHOW_ALL_LAUNCHERS':
            self._command_render_all_launchers()
        elif command == 'SHOW_ALL_ROMS':
            self._command_render_all_ROMs()

        # Command to build/fill the menu with categories or launcher using skinshortcuts
        elif command == 'BUILD_GAMES_MENU':
            self._command_buildMenu()

        else:
            kodi_dialog_OK('Unknown command {}'.format(args['com'][0]) )
        log_debug('Starter run_concurrent() END')

    # This function is guaranteed to run with no concurrency.
    def run_protected(self, command, args):
        log_debug('Starter run_protected() BEGIN')

        

        # --- Launcher management ---
        if command == 'ADD_LAUNCHER':
            self._command_add_new_launcher(args['catID'][0])
        elif command == 'ADD_LAUNCHER_ROOT':
            self._command_add_new_launcher(VCATEGORY_ADDONROOT_ID)
        elif command == 'EDIT_LAUNCHER':
            self._command_edit_launcher(args['catID'][0], args['launID'][0])

        # --- ROM management ---
        elif command == 'SCAN_ROMS':
            self._roms_import_roms(args['launID'][0])
        elif command == 'EDIT_ROM':
            self._command_edit_rom(args['catID'][0], args['launID'][0], args['romID'][0])

        # --- Launch ROM or standalone launcher ---
        elif command == 'LAUNCH_ROM':
            self._command_run_rom(args['catID'][0], args['launID'][0], args['romID'][0])
        elif command == 'LAUNCH_STANDALONE':
            self._command_run_standalone_launcher(args['catID'][0], args['launID'][0])

        # --- Favourite/ROM Collection management ---
        elif command == 'ADD_TO_FAV':
            self._command_add_to_favourites(args['catID'][0], args['launID'][0], args['romID'][0])
        elif command == 'ADD_TO_COLLECTION':
            self._command_add_ROM_to_collection(args['catID'][0], args['launID'][0], args['romID'][0])
        elif command == 'ADD_COLLECTION':
            self._command_add_collection()
        elif command == 'EDIT_COLLECTION':
            self._command_edit_collection(args['catID'][0], args['launID'][0])

        elif command == 'IMPORT_COLLECTION':
            self._command_import_collection()

        # Manages Favourites and ROM Collections.
        elif command == 'MANAGE_FAV':
            self._command_manage_favourites(args['catID'][0], args['launID'][0], args['romID'][0])

        elif command == 'MANAGE_RECENT_PLAYED':
            rom_ID  = args['romID'][0] if 'romID'  in args else ''
            self._command_manage_recently_played(rom_ID)

        elif command == 'MANAGE_MOST_PLAYED':
            rom_ID  = args['romID'][0] if 'romID'  in args else ''
            self._command_manage_most_played(rom_ID)

        # --- Searches ---
        # This command is issued when user clicks on "Search" on the context menu of a launcher
        # in the launchers view, or context menu inside a launcher. User is asked to enter the
        # search string and the field to search (name, category, etc.). Then, EXEC_SEARCH_LAUNCHER
        # command is called.
        elif command == 'SEARCH_LAUNCHER':
            self._command_search_launcher(args['catID'][0], args['launID'][0])
        elif command == 'EXECUTE_SEARCH_LAUNCHER':
            # >> Deal with empty search strings
            if 'search_string' not in args: args['search_string'] = [ '' ]
            self._command_execute_search_launcher(
                args['catID'][0], args['launID'][0],
                args['search_type'][0], args['search_string'][0])

        # >> Shows info about categories/launchers/ROMs and reports
        elif command == 'VIEW':
            catID  = args['catID'][0]                              # >> Mandatory
            launID = args['launID'][0] if 'launID' in args else '' # >> Optional
            romID  = args['romID'][0] if 'romID'  in args else ''  # >> Optional
            self._command_view_menu(catID, launID, romID)
        elif command == 'VIEW_OS_ROM':
            self._command_view_offline_scraper_rom(args['catID'][0], args['launID'][0], args['romID'][0])

        # >> Update virtual categories databases
        elif command == 'UPDATE_VIRTUAL_CATEGORY':
            self._command_update_virtual_category_db(args['catID'][0])
        elif command == 'UPDATE_ALL_VCATEGORIES':
            self._command_update_virtual_category_db_all()

        # Commands called from Utilities menu.
        elif command == 'EXECUTE_UTILS_IMPORT_LAUNCHERS': self._command_exec_utils_import_launchers()
        elif command == 'EXECUTE_UTILS_EXPORT_LAUNCHERS': self._command_exec_utils_export_launchers()

        elif command == 'EXECUTE_UTILS_CHECK_DATABASE': self._command_exec_utils_check_database()
        elif command == 'EXECUTE_UTILS_CHECK_LAUNCHERS': self._command_exec_utils_check_launchers()
        elif command == 'EXECUTE_UTILS_CHECK_LAUNCHER_SYNC_STATUS': self._command_exec_utils_check_launcher_sync_status()
        elif command == 'EXECUTE_UTILS_CHECK_ARTWORK_INTEGRITY': self._command_exec_utils_check_artwork_integrity()
        elif command == 'EXECUTE_UTILS_CHECK_ROM_ARTWORK_INTEGRITY': self._command_exec_utils_check_ROM_artwork_integrity()
        elif command == 'EXECUTE_UTILS_DELETE_REDUNDANT_ARTWORK': self._command_exec_utils_delete_redundant_artwork()
        elif command == 'EXECUTE_UTILS_DELETE_ROM_REDUNDANT_ARTWORK': self._command_exec_utils_delete_ROM_redundant_artwork()
        elif command == 'EXECUTE_UTILS_SHOW_DETECTED_DATS': self._command_exec_utils_show_DATs()
        elif command == 'EXECUTE_UTILS_CHECK_RETRO_LAUNCHERS': self._command_exec_utils_check_retro_launchers()
        elif command == 'EXECUTE_UTILS_CHECK_RETRO_BIOS': self._command_exec_utils_check_retro_BIOS()

        elif command == 'EXECUTE_UTILS_TGDB_CHECK': self._command_exec_utils_TGDB_check()
        elif command == 'EXECUTE_UTILS_MOBYGAMES_CHECK': self._command_exec_utils_MobyGames_check()
        elif command == 'EXECUTE_UTILS_SCREENSCRAPER_CHECK': self._command_exec_utils_ScreenScraper_check()
        elif command == 'EXECUTE_UTILS_ARCADEDB_CHECK': self._command_exec_utils_ArcadeDB_check()

        # Commands called from Global Reports menu.
        elif command == 'EXECUTE_GLOBAL_ROM_STATS': self._command_exec_global_rom_stats()
        elif command == 'EXECUTE_GLOBAL_AUDIT_STATS_ALL':
            self._command_exec_global_audit_stats(AUDIT_REPORT_ALL)
        elif command == 'EXECUTE_GLOBAL_AUDIT_STATS_NOINTRO':
            self._command_exec_global_audit_stats(AUDIT_REPORT_NOINTRO)
        elif command == 'EXECUTE_GLOBAL_AUDIT_STATS_REDUMP':
            self._command_exec_global_audit_stats(AUDIT_REPORT_REDUMP)

        # Unknown command
        else:
            kodi_dialog_OK('Unknown command {}'.format(args['com'][0]) )
        log_debug('Starter run_protected() END')

    # Get Addon Settings
    # In the future use the cfg = Configuration() class and not g_PATHS. See the AML code.
    def _get_settings(self):
        cfg = g_PATHS

        # --- ROM Scanner settings ---
        self.settings['scan_recursive'] = kodi_get_bool_setting(cfg, 'scan_recursive')
        self.settings['scan_ignore_bios'] = kodi_get_bool_setting(cfg, 'scan_ignore_bios')
        self.settings['scan_ignore_scrap_title'] = kodi_get_bool_setting(cfg, 'scan_ignore_scrap_title')
        self.settings['scan_ignore_scrap_title_MAME'] = kodi_get_bool_setting(cfg, 'scan_ignore_scrap_title_MAME')
        self.settings['scan_clean_tags'] = kodi_get_bool_setting(cfg, 'scan_clean_tags')
        self.settings['scan_update_NFO_files'] = kodi_get_bool_setting(cfg, 'scan_update_NFO_files')

        # --- ROM scraping ---
        # Scanner settings
        self.settings['scan_metadata_policy'] = kodi_get_int_setting(cfg, 'scan_metadata_policy')
        self.settings['scan_asset_policy'] = kodi_get_int_setting(cfg, 'scan_asset_policy')
        self.settings['game_selection_mode'] = kodi_get_int_setting(cfg, 'game_selection_mode')
        self.settings['asset_selection_mode'] = kodi_get_int_setting(cfg, 'asset_selection_mode')
        # Scanner scrapers
        self.settings['scraper_metadata'] = kodi_get_int_setting(cfg, 'scraper_metadata')
        self.settings['scraper_asset'] = kodi_get_int_setting(cfg, 'scraper_asset')
        self.settings['scraper_metadata_MAME'] = kodi_get_int_setting(cfg, 'scraper_metadata_MAME')
        self.settings['scraper_asset_MAME'] = kodi_get_int_setting(cfg, 'scraper_asset_MAME')

        # --- Misc settings ---
        self.settings['scraper_mobygames_apikey'] = kodi_get_str_setting(cfg, 'scraper_mobygames_apikey')
        self.settings['scraper_screenscraper_ssid'] = kodi_get_str_setting(cfg, 'scraper_screenscraper_ssid')
        self.settings['scraper_screenscraper_sspass'] = kodi_get_str_setting(cfg, 'scraper_screenscraper_sspass')

        self.settings['scraper_screenscraper_region'] = kodi_get_int_setting(cfg, 'scraper_screenscraper_region')
        self.settings['scraper_screenscraper_language'] = kodi_get_int_setting(cfg, 'scraper_screenscraper_language')

        self.settings['io_retroarch_sys_dir'] = kodi_get_str_setting(cfg, 'io_retroarch_sys_dir')
        self.settings['io_retroarch_only_mandatory'] = kodi_get_bool_setting(cfg, 'io_retroarch_only_mandatory')

        # --- ROM audit ---
        self.settings['audit_unknown_roms'] = kodi_get_int_setting(cfg, 'audit_unknown_roms')
        self.settings['audit_pclone_assets'] = kodi_get_bool_setting(cfg, 'audit_pclone_assets')
        self.settings['audit_nointro_dir'] = kodi_get_str_setting(cfg, 'audit_nointro_dir')
        self.settings['audit_redump_dir'] = kodi_get_str_setting(cfg, 'audit_redump_dir')

        # self.settings['audit_1G1R_first_region'] = kodi_get_int_setting(cfg, 'audit_1G1R_first_region')
        # self.settings['audit_1G1R_second_region'] = kodi_get_int_setting(cfg, 'audit_1G1R_second_region')
        # self.settings['audit_1G1R_third_region'] = kodi_get_int_setting(cfg, 'audit_1G1R_third_region')

        # --- Display ---
        self.settings['display_category_mode'] = kodi_get_int_setting(cfg, 'display_category_mode')
        self.settings['display_launcher_notify'] = kodi_get_bool_setting(cfg, 'display_launcher_notify')
        self.settings['display_hide_finished'] = kodi_get_bool_setting(cfg, 'display_hide_finished')
        self.settings['display_launcher_roms'] = kodi_get_bool_setting(cfg, 'display_launcher_roms')

        self.settings['display_rom_in_fav'] = kodi_get_bool_setting(cfg, 'display_rom_in_fav')
        self.settings['display_nointro_stat'] = kodi_get_bool_setting(cfg, 'display_nointro_stat')
        self.settings['display_fav_status'] = kodi_get_bool_setting(cfg, 'display_fav_status')

        self.settings['display_hide_add'] = kodi_get_bool_setting(cfg, 'display_hide_add')
        self.settings['display_hide_collections'] = kodi_get_bool_setting(cfg, 'display_hide_collections')
        self.settings['display_hide_vlaunchers'] = kodi_get_bool_setting(cfg, 'display_hide_vlaunchers')
        self.settings['display_hide_AEL_scraper'] = kodi_get_bool_setting(cfg, 'display_hide_AEL_scraper')
        self.settings['display_hide_recent'] = kodi_get_bool_setting(cfg, 'display_hide_recent')
        self.settings['display_hide_mostplayed'] = kodi_get_bool_setting(cfg, 'display_hide_mostplayed')
        self.settings['display_hide_utilities'] = kodi_get_bool_setting(cfg, 'display_hide_utilities')
        self.settings['display_hide_g_reports'] = kodi_get_bool_setting(cfg, 'display_hide_g_reports')

        # --- Paths ---
        self.settings['categories_asset_dir'] = kodi_get_str_setting(cfg, 'categories_asset_dir')
        self.settings['launchers_asset_dir'] = kodi_get_str_setting(cfg, 'launchers_asset_dir')
        self.settings['favourites_asset_dir'] = kodi_get_str_setting(cfg, 'favourites_asset_dir')
        self.settings['collections_asset_dir'] = kodi_get_str_setting(cfg, 'collections_asset_dir')

        # --- Advanced ---
        self.settings['media_state_action'] = kodi_get_int_setting(cfg, 'media_state_action')
        if ADDON_RUNNING_PYTHON_2:
            self.settings['delay_tempo'] = kodi_get_float_setting_as_int(cfg, 'delay_tempo')
        elif ADDON_RUNNING_PYTHON_3:
            self.settings['delay_tempo'] = kodi_get_int_setting(cfg, 'delay_tempo')
        else:
            raise TypeError('Undefined Python runtime version.')
        self.settings['suspend_audio_engine'] = kodi_get_bool_setting(cfg, 'suspend_audio_engine')
        self.settings['suspend_screensaver'] = kodi_get_bool_setting(cfg, 'suspend_screensaver')
        # self.settings['suspend_joystick_engine'] = kodi_get_bool_setting(cfg, 'suspend_joystick_engine')
        self.settings['escape_romfile'] = kodi_get_bool_setting(cfg, 'escape_romfile')
        self.settings['lirc_state'] = kodi_get_bool_setting(cfg, 'lirc_state')
        self.settings['show_batch_window'] = kodi_get_bool_setting(cfg, 'show_batch_window')
        self.settings['windows_close_fds'] = kodi_get_bool_setting(cfg, 'windows_close_fds')
        self.settings['windows_cd_apppath'] = kodi_get_bool_setting(cfg, 'windows_cd_apppath')
        self.settings['log_level'] = kodi_get_int_setting(cfg, 'log_level')

        # Check if user changed default artwork paths for categories/launchers. If not, set defaults.
        if self.settings['categories_asset_dir'] == '':
            self.settings['categories_asset_dir'] = g_PATHS.DEFAULT_CAT_ASSET_DIR.getOriginalPath()
        if self.settings['launchers_asset_dir'] == '':
            self.settings['launchers_asset_dir'] = g_PATHS.DEFAULT_LAUN_ASSET_DIR.getOriginalPath()
        if self.settings['favourites_asset_dir'] == '':
            self.settings['favourites_asset_dir'] = g_PATHS.DEFAULT_FAV_ASSET_DIR.getOriginalPath()
        if self.settings['collections_asset_dir'] == '':
            self.settings['collections_asset_dir'] = g_PATHS.DEFAULT_COL_ASSET_DIR.getOriginalPath()

        # Settings required by the scrapers (they are not really settings).
        self.settings['scraper_screenscraper_AEL_softname'] = 'AEL_{}'.format(cfg.addon.info_version)
        self.settings['scraper_aeloffline_addon_code_dir'] = g_PATHS.ADDON_CODE_DIR.getPath()
        self.settings['scraper_cache_dir'] = g_PATHS.SCRAPER_CACHE_DIR.getPath()

        # --- Dump settings for DEBUG ---
        # log_debug('Settings dump BEGIN')
        # for key in sorted(self.settings):
        #     log_debug('{} --> {:10s} {}'.format(key.rjust(21),
        #         text_type(self.settings[key]), type(self.settings[key])))
        # log_debug('Settings dump END')

    # Set Sorting methods
    def _misc_set_default_sorting_method(self):
        # This must be called only if self.addon_handle > 0, otherwise Kodi will complain in the log.
        if self.addon_handle < 0: return
        xbmcplugin.addSortMethod(handle = self.addon_handle, sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)

    def _misc_set_all_sorting_methods(self):
        # This must be called only if self.addon_handle > 0, otherwise Kodi will complain in the log.
        if self.addon_handle < 0: return
        xbmcplugin.addSortMethod(handle = self.addon_handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
        xbmcplugin.addSortMethod(handle = self.addon_handle, sortMethod = xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(handle = self.addon_handle, sortMethod = xbmcplugin.SORT_METHOD_STUDIO)
        xbmcplugin.addSortMethod(handle = self.addon_handle, sortMethod = xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.addSortMethod(handle = self.addon_handle, sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)

    # Set the AEL content type. It is a Window property used by skins to know if AEL is rendering
    # a Window that has categories/launchers or ROMs.
    def _misc_set_AEL_Content(self, AEL_Content_Value):
        if AEL_Content_Value == AEL_CONTENT_VALUE_LAUNCHERS:
            log_debug('_misc_set_AEL_Content() Setting Window({}) '.format(AEL_CONTENT_WINDOW_ID) +
                      'property "{}" = "{}"'.format(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_LAUNCHERS))
            xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_LAUNCHERS)
        elif AEL_Content_Value == AEL_CONTENT_VALUE_ROMS:
            log_debug('_misc_set_AEL_Content() Setting Window({}) '.format(AEL_CONTENT_WINDOW_ID) +
                      'property "{}" = "{}"'.format(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_ROMS))
            xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_ROMS)
        elif AEL_Content_Value == AEL_CONTENT_VALUE_NONE:
            log_debug('_misc_set_AEL_Content() Setting Window({}) '.format(AEL_CONTENT_WINDOW_ID) +
                      'property "{}" = "{}"'.format(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_NONE))
            xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_NONE)
        else:
            log_error('_misc_set_AEL_Content() Invalid AEL_Content_Value "{}"'.format(AEL_Content_Value))

    def _misc_set_AEL_Launcher_Content(self, launcher_dic):
        kodi_thumb     = 'DefaultFolder.png' if launcher_dic['rompath'] else 'DefaultProgram.png'
        icon_path      = asset_get_default_asset_Category(launcher_dic, 'default_icon', kodi_thumb)
        clearlogo_path = asset_get_default_asset_Category(launcher_dic, 'default_clearlogo')
        xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_LAUNCHER_NAME_LABEL, launcher_dic['m_name'])
        xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_LAUNCHER_ICON_LABEL, icon_path)
        xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_LAUNCHER_CLEARLOGO_LABEL, clearlogo_path)

    def _misc_clear_AEL_Launcher_Content(self):
        xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_LAUNCHER_NAME_LABEL, '')
        xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_LAUNCHER_ICON_LABEL, '')
        xbmcgui.Window(AEL_CONTENT_WINDOW_ID).setProperty(AEL_LAUNCHER_CLEARLOGO_LABEL, '')

    def _command_add_new_launcher(self, categoryID):
        LAUNCHER_STANDALONE  = 1
        LAUNCHER_ROM         = 2
        LAUNCHER_RETROPLAYER = 3
        LAUNCHER_LNK         = 4


        launcher_categoryID = VCATEGORY_ADDONROOT_ID
        launcher_type = LAUNCHER_STANDALONE
       
        # --- Standalone launcher ---
        mask_app = '.bat|.exe|.cmd|.lnk' if is_windows() else ''

        # Application.
        app = kodi_dialog_get_file('Find the program:', mask_app)
        if not app: return
        appPath = FileName(app)

        args = ''

        # Launcher title.
        title = appPath.getBaseNoExt()
        title_formatted = title.replace('.' + title.split('.')[-1], '').replace('.', ' ')
        keyboard = KodiKeyboardDialog('Program Name:', title_formatted)
        keyboard.executeDialog()
        if not keyboard.isConfirmed(): return
        title = keyboard.getData()
        title = title_formatted if title == '' else title

        launcher_platform = ''

        # Add launcher to the launchers dictionary (using name as index)
        launcherdata = fs_new_launcher()
        launcherdata['id']                 = title_formatted
        launcherdata['m_name']             = title
        launcherdata['platform']           = launcher_platform
        launcherdata['categoryID']         = launcher_categoryID
        launcherdata['application']        = appPath.getOriginalPath()
        launcherdata['args']               = args
        launcherdata['timestamp_launcher'] = time.time()
        self.launchers[title] = launcherdata
        kodi_notify('Program {} Added.'.format(title))

        # If this point is reached then changes to metadata/images were made.
        # Save categories and update container contents so user sees those changes inmediately.
        fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        kodi_refresh_container()

    def _command_edit_launcher(self, categoryID, launcherID):
        # Shows a select box with the options to edit
        finished_str = 'Finished' if self.launchers[launcherID]['finished'] == True else 'Unfinished'
        if self.launchers[launcherID]['categoryID'] == VCATEGORY_ADDONROOT_ID:
            category_name = 'Addon root (no category)'
        else:
            category_name = self.categories[self.launchers[launcherID]['categoryID']]['m_name']
        sDialog = KodiSelectDialog('Select action for Launcher {}'.format(self.launchers[launcherID]['m_name']))
        sDialog.setRows([
            'Edit Metadata',
            'Edit Arts',
            'Advanced Modifications',
            'Export Program configuration',
            'Delete Program',
        ])
        mindex = sDialog.executeDialog()
        if mindex is None: return

        # --- Edit Metadata---
        type_nb = 0
        if mindex == type_nb:
            # --- Metadata edit dialog ---
            NFO_FileName = fs_get_launcher_NFO_name(self.settings, self.launchers[launcherID])
            NFO_found_str = 'NFO found' if NFO_FileName.exists() else 'NFO not found'
            plot_str = text_limit_string(self.launchers[launcherID]['m_plot'], PLOT_STR_MAXSIZE)
            common_menu_list = [
                'Edit Title: "{}"'.format(self.launchers[launcherID]['m_name']),
                'Edit Release Year: "{}"'.format(self.launchers[launcherID]['m_year']),
                'Edit Genre: "{}"'.format(self.launchers[launcherID]['m_genre']),
                'Edit Developer: "{}"'.format(self.launchers[launcherID]['m_developer']),
                'Edit Rating: "{}"'.format(self.launchers[launcherID]['m_rating']),
                'Edit Plot: "{}"'.format(plot_str),
                'Import NFO file (default location, {})'.format(NFO_found_str),
                'Import NFO file (browse NFO file)...',
                'Save NFO file (default location)',
            ]
            sDialog = KodiSelectDialog('Edit Launcher Metadata')
            # For now disable scraping for all launchers, including standalone launchers.
            # ROM_launcher = True if self.launchers[launcherID]['rompath'] else False
            # if ROM_launcher:
            #     sDialog.setRows(common_menu_list)
            # else:
            #     sDialog.setRows(common_menu_list + scraper_menu_list)
            sDialog.setRows(common_menu_list)
            mindex2 = sDialog.executeDialog()
            if mindex2 is None: return

            # --- Edition of the launcher name ---
            if mindex2 == 0:
                old_value_str = self.launchers[launcherID]['m_name']
                keyboard = KodiKeyboardDialog('Edit Launcher Title', old_value_str)
                keyboard.executeDialog()
                if not keyboard.isConfirmed(): return
                new_value_str = keyboard.getData().strip()
                log_debug('_command_edit_launcher() Edit Title: old_value_str "{}"'.format(old_value_str))
                log_debug('_command_edit_launcher() Edit Title: new_value_str "{}"'.format(new_value_str))
                if old_value_str == new_value_str:
                    kodi_notify('Launcher Title not changed')
                    return

                # --- Rename ROMs XML/JSON file (if it exists) and change launcher ---
                launcher = self.launchers[launcherID]
                old_roms_base_noext = launcher['roms_base_noext']
                categoryID = launcher['categoryID']
                category_name = self.categories[categoryID]['m_name'] if categoryID in self.categories else VCATEGORY_ADDONROOT_ID
                new_roms_base_noext = fs_get_ROMs_basename(category_name, new_value_str, launcherID)
                fs_rename_ROMs_database(g_PATHS.ROMS_DIR, old_roms_base_noext, new_roms_base_noext)
                launcher['m_name'] = new_value_str
                launcher['roms_base_noext'] = new_roms_base_noext
                kodi_notify('Launcher Title is now {}'.format(new_value_str))

            # --- Selection of the launcher platform from AEL "official" list ---
            elif mindex2 == 1:
                p_idx = get_AEL_platform_index(self.launchers[launcherID]['platform'])
                sDialog = KodiSelectDialog('Select the platform', AEL_platform_list, preselect = p_idx)
                sel_platform = sDialog.executeDialog()
                if sel_platform is None: return
                if p_idx == sel_platform:
                    kodi_notify('Launcher Platform not changed')
                    return
                self.launchers[launcherID]['platform'] = AEL_platform_list[sel_platform]
                kodi_notify('Launcher Platform is now {}'.format(AEL_platform_list[sel_platform]))

            # --- Edition of the launcher release date (year) ---
            elif mindex2 == 2:
                save_DB = aux_edit_str(self.launchers[launcherID], 'm_year', 'Launcher Release Year')
                if not save_DB: return

            # --- Edition of the launcher genre ---
            elif mindex2 == 3:
                save_DB = aux_edit_str(self.launchers[launcherID], 'm_genre', 'Launcher Genre')
                if not save_DB: return

            # --- Edition of the launcher developer ---
            elif mindex2 == 4:
                save_DB = aux_edit_str(self.launchers[launcherID], 'm_developer', 'Launcher Developer')
                if not save_DB: return

            # --- Edition of the launcher rating ---
            elif mindex2 == 5:
                sDialog = KodiSelectDialog('Edit Category Rating')
                sDialog.setRows([
                    'Not set',  'Rating 0', 'Rating 1', 'Rating 2', 'Rating 3', 'Rating 4',
                    'Rating 5', 'Rating 6', 'Rating 7', 'Rating 8', 'Rating 9', 'Rating 10',
                ])
                rating = sDialog.executeDialog()
                if rating is None:
                    kodi_notify('Launcher Rating not changed')
                    return
                elif rating == 0:
                    self.launchers[launcherID]['m_rating'] = ''
                    kodi_notify('Launcher Rating changed to Not Set')
                elif rating >= 1 and rating <= 11:
                    self.launchers[launcherID]['m_rating'] = '{}'.format(rating - 1)
                    kodi_notify('Launcher Rating is now {}'.format(self.launchers[launcherID]['m_rating']))

            # --- Edit launcher description (plot) ---
            elif mindex2 == 6:
                save_DB = aux_edit_str(self.launchers[launcherID], 'm_plot', 'Launcher Plot')
                if not save_DB: return

            # --- Import launcher metadata from NFO file (default location) ---
            elif mindex2 == 7:
                # Returns True if changes were made.
                NFO_FN = fs_get_launcher_NFO_name(self.settings, self.launchers[launcherID])
                save_DB = fs_import_launcher_NFO(NFO_FN, self.launchers, launcherID)
                if not save_DB: return
                kodi_notify('Imported Launcher NFO file {}'.format(NFO_FN.getPath()))

            # --- Browse for NFO file ---
            elif mindex2 == 8:
                NFO_file_str = kodi_dialog_get_file('Select Launcher NFO file', '.nfo')
                log_debug('_command_edit_launcher() kodi_dialog_get_file() -> "{}"'.format(NFO_file_str))
                if not NFO_file_str: return
                NFO_FN = FileName(NFO_file_str)
                if not NFO_FN.exists(): return
                save_DB = fs_import_launcher_NFO(NFO_FN, self.launchers, launcherID)
                if not save_DB: return
                kodi_notify('Imported Launcher NFO file {}'.format(NFO_FN.getPath()))

            # --- Export launcher metadata to NFO file ---
            elif mindex2 == 9:
                NFO_FileName = fs_get_launcher_NFO_name(self.settings, self.launchers[launcherID])
                success = fs_export_launcher_NFO(NFO_FileName, self.launchers[launcherID])
                if not success: return
                kodi_notify('Exported Launcher NFO file {}'.format(NFO_FileName.getPath()))
                return # No need to save launchers so return

            # --- Scrape launcher metadata ---
            elif mindex2 >= 10:
                # --- Use the scraper chosen by user ---
                scraper_index = mindex2 - len(common_menu_list)
                scraper_ID = g_scrap_factory.get_metadata_scraper_ID_from_menu_idx(scraper_index)
                scrap_strategy = g_scrap_factory.create_CM_metadata(scraper_ID)

                # --- Grab data ---
                object_dic = self.launchers[launcherID]
                platform = self.launchers[launcherID]['platform']
                data_dic = {
                    'rom_base_noext' : self.launchers[launcherID]['m_name'],
                    'platform' : platform,
                }

                # --- Scrape! ---
                # If this returns False there were no changes so no need to save database.
                op_dic = scrap_strategy.scrap_CM_metadata_Launcher(object_dic, data_dic)
                kodi_display_user_message(op_dic)
                if not op_dic['status']: return

        # --- Edit Arts ---
        type_nb = type_nb + 1
        if mindex == type_nb:
            launcher = self.launchers[launcherID]

            # Create ListItems and label2
            label2_icon       = launcher['s_icon']       if launcher['s_icon']      else 'Not set'
            label2_fanart     = launcher['s_fanart']     if launcher['s_fanart']    else 'Not set'
            label2_banner     = launcher['s_banner']     if launcher['s_banner']    else 'Not set'
            label2_clearlogo  = launcher['s_clearlogo']  if launcher['s_clearlogo'] else 'Not set'
            label2_poster     = launcher['s_poster']     if launcher['s_poster']     else 'Not set'

            icon_listitem       = xbmcgui.ListItem(label = 'Edit Icon ...', label2 = label2_icon)
            fanart_listitem     = xbmcgui.ListItem(label = 'Edit Fanart ...', label2 = label2_fanart)
            banner_listitem     = xbmcgui.ListItem(label = 'Edit Banner ...', label2 = label2_banner)
            clearlogo_listitem  = xbmcgui.ListItem(label = 'Edit Clearlogo ...', label2 = label2_clearlogo)
            poster_listitem     = xbmcgui.ListItem(label = 'Edit Poster ...', label2 = label2_poster)

            # Set artwork with setArt()
            img_icon       = launcher['s_icon']       if launcher['s_icon']     else 'DefaultAddonNone.png'
            img_fanart     = launcher['s_fanart']     if launcher['s_fanart']    else 'DefaultAddonNone.png'
            img_banner     = launcher['s_banner']     if launcher['s_banner']    else 'DefaultAddonNone.png'
            img_clearlogo  = launcher['s_clearlogo']  if launcher['s_clearlogo'] else 'DefaultAddonNone.png'
            img_poster     = launcher['s_poster']     if launcher['s_poster']     else 'DefaultAddonNone.png'

            icon_listitem.setArt({'icon' : img_icon})
            fanart_listitem.setArt({'icon' : img_fanart})
            banner_listitem.setArt({'icon' : img_banner})
            clearlogo_listitem.setArt({'icon' : img_clearlogo})
            poster_listitem.setArt({'icon' : img_poster})

            # Execute select dialog
            sDialog = KodiSelectDialog('Edit Launcher Assets/Artwork', useDetails = True)
            sDialog.setRows([
                icon_listitem,
                fanart_listitem,
                banner_listitem,
                clearlogo_listitem,
                poster_listitem,
            ])
            mindex2 = sDialog.executeDialog()
            if mindex2 is None: return

            # --- Edit Assets ---
            # If this function returns False no changes were made. No need to save categories
            # XML and update container.
            asset_kind = LAUNCHER_ASSET_ID_LIST[mindex2]
            if not self._gui_edit_asset(KIND_LAUNCHER, asset_kind, launcher): return

        # --- Launcher Advanced Modifications menu option ---
        type_nb = type_nb + 1
        if mindex == type_nb:
            toggle_window_str = 'ON' if self.launchers[launcherID]['toggle_window'] else 'OFF'
            non_blocking_str = 'ON' if self.launchers[launcherID]['non_blocking'] else 'OFF'
            multidisc_str = 'ON' if self.launchers[launcherID]['multidisc'] else 'OFF'
            filter_str = '.bat|.exe|.cmd' if sys.platform == 'win32' else ''

            launcher_str = "'{}'".format(self.launchers[launcherID]['application'])

            # Standalone launcher menu.
            sDialog = KodiSelectDialog('Launcher Advanced Modifications')
            sDialog.setRows([
                "Change Program'{}'".format(self.launchers[launcherID]['args']),
                "Insert Aditional arguments",
                "Toggle Kodi into windowed mode (now {})".format(toggle_window_str),
                "Non-blocking Program (now {})".format(non_blocking_str),
            ])
            # ROMS launcher menu.
            mindex2 = sDialog.executeDialog()
            if mindex2 is None: return

            # --- Launcher application path menu option ---
            type2_nb = 0
            if mindex2 == type2_nb:                
                app = kodi_dialog_get_file('Find the new program:')
                if not app: return
                self.launchers[launcherID]['application'] = app
                kodi_notify('Changed launcher application')

            # --- Edition of the launcher arguments ---
            type2_nb = type2_nb + 1
            if mindex2 == type2_nb:
                keyboard = KodiKeyboardDialog('Edit Program arguments', self.launchers[launcherID]['args'])
                keyboard.executeDialog()
                if not keyboard.isConfirmed(): return
                self.launchers[launcherID]['args'] = keyboard.getData().strip()
                kodi_notify('Changed launcher arguments')

            # --- Launcher Additional arguments ---
            type2_nb = type2_nb + 1
            if mindex2 == type2_nb:
                launcher = self.launchers[launcherID]
                additional_args_list = []
                for extra_arg in launcher['args_extra']:
                    additional_args_list.append("Modify '{}'".format(extra_arg))
                sDialog = KodiSelectDialog('Program additional arguments')
                sDialog.setRows(['Add new additional arguments ...'] + additional_args_list)
                type_aux = sDialog.executeDialog()
                if type_aux is None: return

                # Add new additional arguments
                if type_aux == 0:
                    new_value_str = kodi_get_keyboard_text('Edit launcher additional arguments')
                    launcher['args_extra'].append(new_value_str)
                    log_debug('_command_edit_launcher() Appending extra_args to launcher {}'.format(launcherID))
                    kodi_notify('Added additional arguments in position {}'.format(len(launcher['args_extra'])))
                elif type_aux >= 1:
                    arg_index = type_aux - 1
                    sDialog = KodiSelectDialog('Modify extra arguments {}'.format(type_aux), [
                        'Edit "{}"...'.format(launcher['args_extra'][arg_index]),
                        'Delete extra arguments',
                    ])
                    type_aux_2 = sDialog.executeDialog()
                    if type_aux_2 is None: return
                    if type_aux_2 == 0:
                        new_value_str = kodi_get_keyboard_text('Edit application arguments',
                            launcher['args_extra'][arg_index])
                        launcher['args_extra'][arg_index] = new_value_str
                        log_debug('_command_edit_launcher() Edited args_extra[{}] to "{}"'.format(
                            arg_index, launcher['args_extra'][arg_index]))
                        kodi_notify('Changed launcher extra arguments {}'.format(type_aux))
                    elif type_aux_2 == 1:
                        ret = kodi_dialog_yesno('Are you sure you want to delete Launcher '
                            'additional arguments {}?'.format(type_aux))
                        if not ret: return
                        del launcher['args_extra'][arg_index]
                        log_debug("_command_edit_launcher() Deleted launcher['args_extra'][{}]".format(arg_index))
                        kodi_notify('Changed launcher extra arguments {}'.format(type_aux))

            if self.launchers[launcherID]['rompath'] != '':
                # --- Launcher ROM path menu option (Only ROM launchers) ---
                type2_nb = type2_nb + 1
                if mindex2 == type2_nb:
                    rom_path = kodi_dialog_get_directory('Select ROM directory', self.launchers[launcherID]['rompath'])
                    self.launchers[launcherID]['rompath'] = rom_path
                    kodi_notify('Changed ROM path')

                # --- Edition of the launcher ROM extension (Only ROM launchers) ---
                type2_nb = type2_nb + 1
                if mindex2 == type2_nb:
                    t = 'Edit ROM extension, use "|" as separator. (e.g lnk|cbr)'
                    new_value_str = kodi_get_keyboard_text(t, self.launchers[launcherID]['romext'])
                    self.launchers[launcherID]['romext'] = new_value_str
                    kodi_notify('Changed ROM extensions')

            # --- Minimise Kodi window flag ---
            type2_nb = type2_nb + 1
            if mindex2 == type2_nb:
                p_idx = 1 if self.launchers[launcherID]['toggle_window'] else 0
                sDialog = KodiSelectDialog('Toggle Kodi into windowed mode', ['OFF (default)', 'ON'], p_idx)
                s_idx = sDialog.executeDialog()
                if s_idx is None: return
                self.launchers[launcherID]['toggle_window'] = True if s_idx == 1 else False
                minimise_str = 'ON' if self.launchers[launcherID]['toggle_window'] else 'OFF'
                kodi_notify('Toggle Kodi into windowed mode {}'.format(minimise_str))

            # --- Non-blocking launcher flag ---
            type2_nb = type2_nb + 1
            if mindex2 == type2_nb:
                p_idx = 1 if self.launchers[launcherID]['non_blocking'] else 0
                sDialog = KodiSelectDialog('Non-blocking launcher', ['OFF (default)', 'ON'], p_idx)
                s_idx = sDialog.executeDialog()
                if s_idx is None: return
                self.launchers[launcherID]['non_blocking'] = True if s_idx == 1 else False
                non_blocking_str = 'ON' if self.launchers[launcherID]['non_blocking'] else 'OFF'
                kodi_notify('Launcher Non-blocking is now {}'.format(non_blocking_str))

        # --- Export Launcher XML configuration ---
        type_nb = type_nb + 1
        if mindex == type_nb:
            launcher = self.launchers[launcherID]
            launcher_fn_str = 'Launcher_' + text_title_to_filename_str(launcher['m_name']) + '.xml'
            log_debug('_command_edit_launcher() Exporting Launcher configuration')
            log_debug('_command_edit_launcher() Name     "{}"'.format(launcher['m_name']))
            log_debug('_command_edit_launcher() ID       {}'.format(launcher['id']))
            log_debug('_command_edit_launcher() l_fn_str "{}"'.format(launcher_fn_str))

            # Ask user for a path to export the launcher configuration
            dir_path = kodi_dialog_get_directory('Select XML export directory')
            if not dir_path: return
            export_FN = FileName(dir_path).pjoin(launcher_fn_str)
            if export_FN.exists():
                ret = kodi_dialog_yesno('Overwrite file {}?'.format(export_FN.getPath()))
                if not ret:
                    kodi_notify_warn('Export of Launcher XML cancelled')
                    return

            # --- Print error message is something goes wrong writing file ---
            try:
                autoconfig_export_launcher(launcher, export_FN, self.categories)
            except KodiAddonError as ex:
                kodi_notify_warn('{}'.format(ex))
            else:
                kodi_notify('Exported Launcher "{}" XML config'.format(launcher['m_name']))
            return # No need to update categories.xml and timestamps so return now.

        # --- Remove Launcher menu option ---
        type_nb = type_nb + 1
        if mindex == type_nb:
            rompath = self.launchers[launcherID]['rompath']
            launcher_name = self.launchers[launcherID]['m_name']
            # ROMs launcher
            if rompath:
                roms = fs_load_ROMs_JSON(g_PATHS.ROMS_DIR, self.launchers[launcherID])
                ret = kodi_dialog_yesno('Launcher "{}" has {} ROMs. '.format(launcher_name, len(roms)) +
                    'Are you sure you want to delete it?')
            # Standalone launcher
            else:
                ret = kodi_dialog_yesno('Launcher "{}" is standalone. '.format(launcher_name) +
                    'Are you sure you want to delete it?')
            if not ret:
                kodi_notify('Delete Launcher cancelled')
                return

            # Remove JSON/XML file if exist
            # Remove launcher from database. Categories.xml will be saved at the end of function
            if rompath:
                fs_unlink_ROMs_database(g_PATHS.ROMS_DIR, self.launchers[launcherID])
            self.launchers.pop(launcherID)
            kodi_notify('Deleted Launcher {}'.format(launcher_name))

        # If this point is reached then changes to launcher metadata/assets were made.
        # Save categories and update container contents so user sees those changes inmediately.
        # NOTE Update edited launcher timestamp only if launcher was not deleted!
        if launcherID in self.launchers: self.launchers[launcherID]['timestamp_launcher'] = time.time()
        fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        kodi_refresh_container()

    # -----------------------------------------------------------------------------------------
    # Categories LisItem rendering
    # ---------------------------------------------------------------------------------------------
    # Renders the addon Root window.
    def _command_render_root_window(self):
        self._misc_set_all_sorting_methods()
        self._misc_set_AEL_Content(AEL_CONTENT_VALUE_LAUNCHERS)
        self._misc_clear_AEL_Launcher_Content()

        # --- Render categories in classic mode or in flat mode ---
        # This code must never fail. If categories.xml cannot be read because an upgrade
        # is necessary the user must be able to go to the "Utilities" menu.
        # <setting id="display_category_mode" values="Standard|Flat"/>
        if self.settings['display_category_mode'] == 0:
            # For every category, add it to the listbox. Order alphabetically by name.
            for cat_id in sorted(self.categories, key = lambda x : self.categories[x]['m_name']):
                self._gui_render_category_row(self.categories[cat_id], cat_id)
        else:
            # Traverse categories and sort alphabetically.
            for cat_id in sorted(self.categories, key = lambda x : self.categories[x]['m_name']):
                # Get launchers in this category alphabetically sorted.
                launcher_list = []
                for launcher_id in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
                    launcher = self.launchers[launcher_id]
                    if launcher['categoryID'] == cat_id: launcher_list.append(launcher)
                # Render list of launchers for this category.
                cat_name = self.categories[cat_id]['m_name']
                for launcher in launcher_list:
                    launcher_name = '[COLOR thistle]{}[/COLOR] - {}'.format(cat_name, launcher['m_name'])
                    self._gui_render_launcher_row(launcher, launcher_name)

        # --- Render categoryless launchers. Order alphabetically by name ---
        catless_launchers = {}
        for launcher_id in self.launchers:
            launcher = self.launchers[launcher_id]
            if launcher['categoryID'] == VCATEGORY_ADDONROOT_ID:
                catless_launchers[launcher_id] = launcher
        for launcher_id in sorted(catless_launchers, key = lambda x : catless_launchers[x]['m_name']):
            self._gui_render_launcher_row(catless_launchers[launcher_id])

        # --- AEL Favourites special category ---
        if not self.settings['display_hide_add']:
            self._gui_render_add_row()
            
        xbmcplugin.endOfDirectory(self.addon_handle, succeeded = True, cacheToDisc = False)

    def _gui_render_add_row(self):
        # --- Create listitem row ---
        vcategory_name   = '[COLOR silver]Add Program[/COLOR]'
        vcategory_plot   = 'Add your first program.'
        vcategory_icon   = 'DefaultProgram.png'
        # vcategory_icon   = g_PATHS.ADDON_CODE_DIR.pjoin('media/theme/Add_icon.png').getPath()
        vcategory_fanart = g_PATHS.FANART_FILE_PATH.getPath()
        vcategory_poster = 'DefaultProgram.png'
        # vcategory_poster = g_PATHS.ADDON_CODE_DIR.pjoin('media/theme/Add_poster.png').getPath()
        listitem = xbmcgui.ListItem(vcategory_name)
        listitem.setInfo('video', {
            'title' : vcategory_name,
            'plot' : vcategory_plot,
            'overlay' : KODI_ICON_OVERLAY_UNWATCHED,
        })
        listitem.setArt({'icon' : vcategory_icon, 'fanart' : vcategory_fanart, 'poster' : vcategory_poster})
        listitem.setProperty(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_ROM_LAUNCHER)

        # Create context menu if Kiosk mode is disabled (normal mode).
        if self.g_kiosk_mode_disabled:
            commands = [
                ('Add New Launcher', aux_url_RP('ADD_LAUNCHER_ROOT')),
                ('Kodi File Manager', 'ActivateWindow(filemanager)'),
                ('AEL addon settings', 'Addon.OpenSettings({})'.format(cfg.addon.info_id)),
            ]
            listitem.addContextMenuItems(commands, replaceItems = True)
        url_str = aux_url('ADD_LAUNCHER_ROOT')
        xbmcplugin.addDirectoryItem(self.addon_handle, url_str, listitem, True)

    # ---------------------------------------------------------------------------------------------
    # Launcher LisItem rendering
    # ---------------------------------------------------------------------------------------------
    #
    # Renders the launchers for a given category
    #
    def _command_render_launchers(self, categoryID):
        # >> Set content type
        self._misc_set_all_sorting_methods()
        self._misc_set_AEL_Content(AEL_CONTENT_VALUE_LAUNCHERS)
        self._misc_clear_AEL_Launcher_Content()

        # --- If the category has no launchers then render nothing ---
        launcher_IDs = []
        for launcher_id in self.launchers:
            if self.launchers[launcher_id]['categoryID'] == categoryID: launcher_IDs.append(launcher_id)
        if not launcher_IDs:
            category_name = self.categories[categoryID]['m_name']
            kodi_notify('Category {} has no launchers. Add launchers first.'.format(category_name))
            # NOTE If we return at this point Kodi produces and error:
            # ERROR: GetDirectory - Error getting plugin://plugin.program.advanced.emulator.launcher/?catID=8...f&com=SHOW_LAUNCHERS
            # ERROR: CGUIMediaWindow::GetDirectory(plugin://plugin.program.advanced.emulator.launcher/?catID=8...2f&com=SHOW_LAUNCHERS) failed
            #
            # How to avoid that? Rendering the categories again? If I call _command_render_categories() it does not work well, categories
            # are displayed in wrong alphabetical order and if go back clicking on .. the categories window is rendered again (instead of
            # exiting the addon).
            # self._command_render_categories()
            #
            # What about replacewindow? I also get the error, still not clear why...
            # xbmc.executebuiltin('ReplaceWindow(Programs,{})'.format(g_base_url)) # Does not work
            # xbmc.executebuiltin('ReplaceWindow({})'.format(g_base_url)) # Does not work
            #
            # Container.Refresh does not work either...
            # kodi_refresh_container()
            #
            # SOLUTION: call xbmcplugin.endOfDirectory(). It will create an empty ListItem wiht only '..' entry.
            #           User cannot open a context menu and the only option is to go back to categories display.
            #           No errors in Kodi log!
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # Render launcher rows of this launcher
        for key in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
            if self.launchers[key]['categoryID'] == categoryID:
                self._gui_render_launcher_row(self.launchers[key])
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    # Renders all launchers belonging to all categories.
    # This function is called by skins to create shortcuts.
    def _command_render_all_launchers(self):
        # If no launchers render nothing
        if not self.launchers:
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Render all launchers
        for key in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
            self._gui_render_launcher_row(self.launchers[key])
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _gui_render_launcher_row(self, launcher_dic, launcher_raw_name = None):
        # --- Do not render row if launcher finished ---
        if launcher_dic['finished'] and self.settings['display_hide_finished']:
            return

        # --- Launcher tags ---
        # >> Do not plot ROM count on standalone launchers! Launcher is standalone if rompath = ''
        if launcher_raw_name is None: launcher_raw_name = launcher_dic['m_name']

        launcher_name = launcher_raw_name

        # --- Create listitem row ---
        ICON_OVERLAY = 5 if launcher_dic['finished'] else 4
        listitem = xbmcgui.ListItem(launcher_name)
        # BUG in Jarvis/Krypton skins. If 'year' is set to empty string a 0 is displayed on the
        #     skin. If year is not set then the correct icon is shown.
        if launcher_dic['m_year']:
            listitem.setInfo('video', {
                'title'   : launcher_name,             'year'    : launcher_dic['m_year'],
                'genre'   : launcher_dic['m_genre'],   'studio'  : launcher_dic['m_developer'],
                'rating'  : launcher_dic['m_rating'],  'plot'    : launcher_dic['m_plot'],
                'trailer' : launcher_dic['s_trailer'], 'overlay' : ICON_OVERLAY })
        else:
            listitem.setInfo('video', {
                'title'   : launcher_name,
                'genre'   : launcher_dic['m_genre'],   'studio'  : launcher_dic['m_developer'],
                'rating'  : launcher_dic['m_rating'],  'plot'    : launcher_dic['m_plot'],
                'trailer' : launcher_dic['s_trailer'], 'overlay' : ICON_OVERLAY })
        listitem.setProperty('platform', launcher_dic['platform'])
        if launcher_dic['rompath']:
            listitem.setProperty(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_ROM_LAUNCHER)
            listitem.setProperty(AEL_NUMITEMS_LABEL, text_type(launcher_dic['num_roms']))
        else:
            listitem.setProperty(AEL_CONTENT_LABEL, AEL_CONTENT_VALUE_STD_LAUNCHER)

        # --- Set ListItem artwork ---
        kodi_thumb     = 'DefaultFolder.png' if launcher_dic['rompath'] else 'DefaultProgram.png'
        icon_path      = asset_get_default_asset_Category(launcher_dic, 'default_icon', kodi_thumb)
        fanart_path    = asset_get_default_asset_Category(launcher_dic, 'default_fanart')
        banner_path    = asset_get_default_asset_Category(launcher_dic, 'default_banner')
        poster_path    = asset_get_default_asset_Category(launcher_dic, 'default_poster')
        clearlogo_path = asset_get_default_asset_Category(launcher_dic, 'default_clearlogo')
        listitem.setArt({
            'icon' : icon_path, 'fanart' : fanart_path, 'banner' : banner_path,
            'poster' : poster_path, 'clearlogo' : clearlogo_path,
            'controller' : launcher_dic['s_controller'],
        })

        # --- Create context menu ---
        # Categories/Launchers/ROMs context menu order
        #  1) View XXXXX
        #  2) Edit XXXXX
        #  3) Add launcher (Categories) | Add ROMs (Launchers)
        #  4) Search XXXX
        #  5) Create new XXXX
        commands = []
        launcherID = launcher_dic['id']
        categoryID = launcher_dic['categoryID']
        commands.append(('Edit Program', aux_url_RP('EDIT_LAUNCHER', categoryID, launcherID)))
        

        commands.append(('Add New Program', aux_url_RP('ADD_LAUNCHER', categoryID)))
        # Launchers in addon root should be able to create a new category
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)'))
        commands.append(('Starter settings', 'Addon.OpenSettings({})'.format(cfg.addon.info_id)))
        if xbmc.getCondVisibility('!Skin.HasSetting(KioskMode.Enabled)'):
            listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add Launcher row to ListItem ---
        if launcher_dic['rompath']:
            url_str = aux_url('SHOW_ROMS', categoryID, launcherID)
            folder_flag = True
        else:
            url_str = aux_url('LAUNCH_STANDALONE', categoryID, launcherID)
            folder_flag = False
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = url_str, listitem = listitem, isFolder = folder_flag)

    # Launchs a standalone application.
    def _command_run_standalone_launcher(self, categoryID, launcherID):
        # --- Check launcher is OK ---
        if launcherID not in self.launchers:
            kodi_dialog_OK('launcherID not found in self.launchers')
            return
        launcher = self.launchers[launcherID]
        minimize_flag = launcher['toggle_window']
        log_info('_run_standalone_launcher() categoryID {}'.format(categoryID))
        log_info('_run_standalone_launcher() launcherID {}'.format(launcherID))

        # --- Execute Kodi built-in function under certain conditions ---
        # Application is "xbmc", "xbmc.exe" or starts with "xbmc-fav-" or "xbmc-sea-".
        # Upgraded to support kodi.
        # Arguments is the builtin function to execute, for example:
        # ActivateWindow(10821,"plugin://plugin.program.iagl/game_list/list_all/Dreamcast_Downloaded/1",return)
        application_str = launcher['application']
        arguments_str = launcher['args']
        app_cleaned = application_str.lower().replace('.exe' , '')
        if app_cleaned == 'xbmc' or app_cleaned == 'kodi' or \
            'xbmc-fav-' in app_cleaned or 'xbmc-sea-' in app_cleaned or \
            'kodi-fav-' in app_cleaned or 'kodi-sea-' in app_cleaned:
            log_info('_run_standalone_launcher() Executing Kodi builtin function')
            log_info('_run_standalone_launcher() application "{}"'.format(application_str))
            log_info('_run_standalone_launcher() app_cleaned "{}"'.format(app_cleaned))
            log_info('_run_standalone_launcher() arguments   "{}"'.format(arguments_str))
            if self.settings['display_launcher_notify']: kodi_notify('Launching Kodi builtin')
            xbmc.executebuiltin('{}'.format(arguments_str))
            log_info('_run_standalone_launcher() Exiting function.')
            return

        # ----- External application -----
        application = FileName(launcher['application'])
        app_basename = application.getBase()
        app_ext = application.getExt()
        launcher_title = launcher['m_name']
        log_info('_run_standalone_launcher() application   "{}"'.format(application.getPath()))
        log_info('_run_standalone_launcher() apppath       "{}"'.format(application.getDir()))
        log_info('_run_standalone_launcher() app_basename  "{}"'.format(app_basename))
        log_info('_run_standalone_launcher() app_ext       "{}"'.format(app_ext))
        log_info('_run_standalone_launcher() launcher name "{}"'.format(launcher_title))

        # --- Argument substitution ---
        arguments = launcher['args']
        log_info('_run_standalone_launcher() raw arguments   "{}"'.format(arguments))
        arguments = arguments.replace('$apppath$' , application.getDir())
        log_info('_run_standalone_launcher() final arguments "{}"'.format(arguments))

        # --- Check for errors and abort if errors found ---
        if not application.exists():
            log_error('Launching app not found "{}"'.format(application.getPath()))
            kodi_notify_warn('App {} not found.'.format(application.getOriginalPath()))
            return

        # --- Execute external application ---
        non_blocking_flag = False
        self._run_before_execution(launcher_title, minimize_flag)
        self._run_process(application.getPath(), arguments, application.getDir(), app_ext, non_blocking_flag)
        self._run_after_execution(minimize_flag)

    # Launches a ROM launcher or standalone launcher
    # For standalone launchers romext is the extension of the application (only used in Windoze)
    def _run_process(self, application, arguments, apppath, romext, non_blocking_flag):
        # Determine platform and launch application
        # See http://stackoverflow.com/questions/446209/possible-values-from-sys-platform

        # Decompose arguments to call subprocess module
        arg_list = shlex.split(arguments, posix = True)
        exec_list = [application] + arg_list
        log_debug('_run_process() arguments = "{}"'.format(arguments))
        log_debug('_run_process() arg_list  = {}'.format(arg_list))
        log_debug('_run_process() exec_list = {}'.format(exec_list))

        # NOTE subprocess24_hack.py was hacked to always set CreateProcess() bInheritHandles to 0.
        # bInheritHandles [in] If this parameter TRUE, each inheritable handle in the calling
        # process is inherited by the new process. If the parameter is FALSE, the handles are not
        # inherited. Note that inherited handles have the same value and access rights as the original handles.
        # See https://msdn.microsoft.com/en-us/library/windows/desktop/ms682425(v=vs.85).aspx
        #
        # Same behavior can be achieved in current version of subprocess with close_fds.
        # If close_fds is true, all file descriptors except 0, 1 and 2 will be closed before the
        # child process is executed. (Unix only). Or, on Windows, if close_fds is true then no handles
        # will be inherited by the child process. Note that on Windows, you cannot set close_fds to
        # true and also redirect the standard handles by setting stdin, stdout or stderr.
        #
        # If I keep old launcher behavior in Windows (close_fds = True) then program output cannot
        # be redirected to a file.
        #
        if is_windows():
            app_ext = application.split('.')[-1]
            log_debug('_run_process() (Windows) application = "{}"'.format(application))
            log_debug('_run_process() (Windows) arguments   = "{}"'.format(arguments))
            log_debug('_run_process() (Windows) apppath     = "{}"'.format(apppath))
            log_debug('_run_process() (Windows) romext      = "{}"'.format(romext))
            log_debug('_run_process() (Windows) app_ext     = "{}"'.format(app_ext))

            # Standalone launcher where application is a LNK file
            if app_ext == 'lnk' or app_ext == 'LNK':
                # Remove initial and trailing quotes to avoid double quotation.
                application = misc_strip_quotes(application)
                if ADDON_RUNNING_PYTHON_2:
                    c = 'start "AEL" /b "{}"'.format(application).encode('utf-8')
                elif ADDON_RUNNING_PYTHON_3:
                    c = 'start "AEL" /b "{}"'.format(application)
                else:
                    raise TypeError('Undefined Python runtime version.')
                log_debug('_run_process() (Windows) Launching LNK application')
                retcode = subprocess.call(c, shell = True)
                log_info('_run_process() (Windows) LNK app retcode = {}'.format(retcode))

            # ROM launcher where ROMs are LNK files
            elif romext == 'lnk' or romext == 'LNK':
                # Remove initial and trailing quotes to avoid double quotation.
                arguments = misc_strip_quotes(arguments)
                if ADDON_RUNNING_PYTHON_2:
                    c = 'start "AEL" /b "{}"'.format(arguments).encode('utf-8')
                elif ADDON_RUNNING_PYTHON_3:
                    c = 'start "AEL" /b "{}"'.format(arguments)
                else:
                    raise TypeError('Undefined Python runtime version.')
                log_debug('_run_process() (Windows) Launching LNK ROM')
                retcode = subprocess.call(c, shell = True)
                log_info('_run_process() (Windows) LNK ROM retcode = {}'.format(retcode))

            # CMD/BAT applications in Windows.
            elif app_ext == 'bat' or app_ext == 'BAT' or app_ext == 'cmd' or app_ext == 'CMD':
                # Workaround to run UNC paths in Windows.
                # Retroarch now support ROMs in UNC paths (Samba remotes)
                new_exec_list = list(exec_list)
                for i in range(len(exec_list)):
                    if exec_list[i][0] != '\\': continue
                    new_exec_list[i] = '\\' + exec_list[i]
                    log_debug('_run_process() (Windows) Before arg #{} = "{}"'.format(i, exec_list[i]))
                    log_debug('_run_process() (Windows) Now    arg #{} = "{}"'.format(i, new_exec_list[i]))
                exec_list = list(new_exec_list)
                log_debug('_run_process() (Windows) exec_list = {}'.format(exec_list))
                log_debug('_run_process() (Windows) Launching BAT/CMD application')
                log_debug('_run_process() (Windows) Ignoring setting windows_cd_apppath')
                log_debug('_run_process() (Windows) Ignoring setting windows_close_fds')
                log_debug('_run_process() (Windows) show_batch_window = {}'.format(self.settings['show_batch_window']))
                info = subprocess.STARTUPINFO()
                info.dwFlags = 1
                info.wShowWindow = 5 if self.settings['show_batch_window'] else 0
                if ADDON_RUNNING_PYTHON_2:
                    apppath_t = apppath.encode('utf-8')
                elif ADDON_RUNNING_PYTHON_3:
                    apppath_t = apppath
                else:
                    raise TypeError('Undefined Python runtime version.')
                retcode = subprocess.call(exec_list, cwd = apppath_t, close_fds = True, startupinfo = info)
                log_info('_run_process() (Windows) Process BAT/CMD retcode = {}'.format(retcode))

            # Normal Windows application.
            else:
                # --- Workaround to run UNC paths in Windows ---
                # Retroarch now support ROMs in UNC paths (Samba remotes)
                new_exec_list = list(exec_list)
                for i in range(len(exec_list)):
                    if exec_list[i][0] != '\\': continue
                    new_exec_list[i] = '\\' + exec_list[i]
                    log_debug('_run_process() (Windows) Before arg #{} = "{}"'.format(i, exec_list[i]))
                    log_debug('_run_process() (Windows) Now    arg #{} = "{}"'.format(i, new_exec_list[i]))
                exec_list = list(new_exec_list)
                log_debug('_run_process() (Windows) exec_list = {}'.format(exec_list))

                # cwd = apppath.encode('utf-8') fails if application path has Unicode on Windows
                # A workaraound is to use cwd = apppath.encode(sys.getfilesystemencoding()) --> DOES NOT WORK
                # For the moment AEL cannot launch executables on Windows having Unicode paths.
                windows_cd_apppath = self.settings['windows_cd_apppath']
                windows_close_fds  = self.settings['windows_close_fds']
                log_debug('_run_process() (Windows) Launching regular application')
                log_debug('_run_process() (Windows) windows_cd_apppath = {}'.format(windows_cd_apppath))
                log_debug('_run_process() (Windows) windows_close_fds  = {}'.format(windows_close_fds))
                # In Python 3 use Unicode to call functions in the subprocess module.
                if ADDON_RUNNING_PYTHON_2:
                    apppath_t = apppath.encode('utf-8')
                elif ADDON_RUNNING_PYTHON_3:
                    apppath_t = apppath
                else:
                    raise TypeError('Undefined Python runtime version.')
                # Note that on Windows, you cannot set close_fds to true and also redirect the
                # standard handles by setting stdin, stdout or stderr.
                if windows_cd_apppath and windows_close_fds:
                    retcode = subprocess.call(exec_list, cwd = apppath_t, close_fds = True)
                elif windows_cd_apppath and not windows_close_fds:
                    with open(g_PATHS.LAUNCH_LOG_FILE_PATH.getPath(), 'w') as f:
                        retcode = subprocess.call(exec_list, cwd = apppath_t, close_fds = False,
                            stdout = f, stderr = subprocess.STDOUT)
                elif not windows_cd_apppath and windows_close_fds:
                    retcode = subprocess.call(exec_list, close_fds = True)
                elif not windows_cd_apppath and not windows_close_fds:
                    with open(g_PATHS.LAUNCH_LOG_FILE_PATH.getPath(), 'w') as f:
                        retcode = subprocess.call(exec_list, close_fds = False,
                            stdout = f, stderr = subprocess.STDOUT)
                else:
                    raise Exception('Logical error')
                log_info('_run_process() (Windows) Process retcode = {}'.format(retcode))

        elif is_android():
            if ADDON_RUNNING_PYTHON_2:
                c = '{} {}'.format(application, arguments).encode('utf-8')
            elif ADDON_RUNNING_PYTHON_3:
                c = '{} {}'.format(application, arguments)
            else:
                raise TypeError('Undefined Python runtime version.')
            retcode = os.system(c)
            log_info('_run_process() Process retcode = {}'.format(retcode))

        # New in 0.9.7: always close all file descriptions except 0, 1 and 2 on the child
        # process. This is to avoid Kodi open sockets be inherited by the child process. A
        # wrapper script may terminate Kodi using JSON RPC and if file descriptors are not
        # closed Kodi will complain that the remote interface cannot be initialised. I believe
        # the cause is that the listening socket is kept open by the wrapper script.
        elif is_linux():
            # os.system() is deprecated and should not be used anymore, use subprocess module.
            # Also, save child process stdout to a file.
            if non_blocking_flag:
                # In a non-blocking launch stdout/stderr of child process cannot be recorded.
                log_info('_run_process() (Linux) Launching non-blocking process subprocess.Popen()')
                p = subprocess.Popen(exec_list, close_fds = True)
            else:
                if self.settings['lirc_state']: xbmc.executebuiltin('LIRC.stop')
                log_info('_run_process() (Linux) Launching blocking process subprocess.call()')
                with open(g_PATHS.LAUNCH_LOG_FILE_PATH.getPath(), 'w') as f:
                    retcode = subprocess.call(exec_list, stdout = f, stderr = subprocess.STDOUT, close_fds = True)
                log_info('_run_process() Process retcode = {}'.format(retcode))
                if self.settings['lirc_state']: xbmc.executebuiltin('LIRC.start')

        elif is_osx():
            with open(g_PATHS.LAUNCH_LOG_FILE_PATH.getPath(), 'w') as f:
                retcode = subprocess.call(exec_list, stdout = f, stderr = subprocess.STDOUT)
            log_info('_run_process() Process retcode = {}'.format(retcode))

        else:
            kodi_notify_warn('Cannot determine the running platform.')

    # These two functions do things like stopping music before lunch, toggling full screen, etc.
    # Variables set in this function:
    # self.kodi_was_playing      True if Kodi player was ON, False otherwise
    # self.kodi_audio_suspended  True if Kodi audio suspended before launching
    def _run_before_execution(self, rom_title, toggle_screen_flag):
        # --- User notification ---
        if self.settings['display_launcher_notify']:
            kodi_notify('Launching {}'.format(rom_title))

        # --- Stop/Pause Kodi mediaplayer if requested in settings ---
        self.kodi_was_playing = False
        # id="media_state_action" default="0" values="Stop|Pause|Let Play"
        media_state_action = self.settings['media_state_action']
        media_state_str = ['Stop', 'Pause', 'Let Play'][media_state_action]
        log_debug('_run_before_execution() media_state_action is "{}" ({})'.format(media_state_str, media_state_action))
        if media_state_action == 0 and xbmc.Player().isPlaying():
            log_debug('_run_before_execution() Calling xbmc.Player().stop()')
            xbmc.Player().stop()
            xbmc.sleep(100)
            self.kodi_was_playing = True
        elif media_state_action == 1 and xbmc.Player().isPlaying():
            log_debug('_run_before_execution() Calling xbmc.Player().pause()')
            xbmc.Player().pause()
            xbmc.sleep(100)
            self.kodi_was_playing = True

        # --- Force audio suspend if requested in "Settings" --> "Advanced"
        # See http://forum.kodi.tv/showthread.php?tid=164522
        self.kodi_audio_suspended = False
        if self.settings['suspend_audio_engine']:
            log_debug('_run_before_execution() Suspending Kodi audio engine')
            xbmc.audioSuspend()
            xbmc.enableNavSounds(False)
            xbmc.sleep(100)
            self.kodi_audio_suspended = True
        else:
            log_debug('_run_before_execution() DO NOT suspend Kodi audio engine')

        # --- Force joystick suspend if requested in "Settings" --> "Advanced"
        # See https://forum.kodi.tv/showthread.php?tid=287826&pid=2627128#pid2627128
        # See https://forum.kodi.tv/showthread.php?tid=157499&pid=1722549&highlight=input.enablejoystick#pid1722549
        # See https://forum.kodi.tv/showthread.php?tid=313615
        self.kodi_joystick_suspended = False
        # if self.settings['suspend_joystick_engine']:
            # log_debug('_run_before_execution() Suspending Kodi joystick engine')
            # >> Research. Get the value of the setting first
            # >> Apparently input.enablejoystick is not supported on Kodi Krypton anymore.
            # c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
            #          ' "method" : "Settings.GetSettingValue",'
            #          ' "params" : {"setting":"input.enablejoystick"}}')
            # response = xbmc.executeJSONRPC(c_str)
            # log_debug('JSON      ''{}'''.format(c_str))
            # log_debug('Response  ''{}'''.format(response))

            # c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
            #          ' "method" : "Settings.SetSettingValue",'
            #          ' "params" : {"setting" : "input.enablejoystick", "value" : false} }')
            # response = xbmc.executeJSONRPC(c_str)
            # log_debug('JSON      ''{}'''.format(c_str))
            # log_debug('Response  ''{}'''.format(response))
            # self.kodi_joystick_suspended = True

            # log_error('_run_before_execution() Suspending Kodi joystick engine not supported on Kodi Krypton!')
        # else:
            # log_debug('_run_before_execution() DO NOT suspend Kodi joystick engine')

        # --- Toggle Kodi windowed/fullscreen if requested ---
        if toggle_screen_flag:
            log_debug('_run_before_execution() Toggling Kodi fullscreen')
            kodi_toogle_fullscreen()
        else:
            log_debug('_run_before_execution() Toggling Kodi fullscreen DEACTIVATED in Launcher')

        # Disable screensaver
        if self.settings['suspend_screensaver']:
            kodi_disable_screensaver()
        else:
            screensaver_mode = kodi_get_screensaver_mode()
            log_debug('_run_before_execution() Screensaver status "{}"'.format(screensaver_mode))

        # --- Pause Kodi execution some time ---
        delay_tempo_ms = self.settings['delay_tempo']
        log_debug('_run_before_execution() Pausing {} ms'.format(delay_tempo_ms))
        xbmc.sleep(delay_tempo_ms)
        log_debug('_run_before_execution() function ENDS')

    def _run_after_execution(self, toggle_screen_flag):
        # --- Stop Kodi some time ---
        delay_tempo_ms = self.settings['delay_tempo']
        log_debug('_run_after_execution() Pausing {} ms'.format(delay_tempo_ms))
        xbmc.sleep(delay_tempo_ms)

        # --- Toggle Kodi windowed/fullscreen if requested ---
        if toggle_screen_flag:
            log_debug('_run_after_execution() Toggling Kodi fullscreen')
            kodi_toogle_fullscreen()
        else:
            log_debug('_run_after_execution() Toggling Kodi fullscreen DEACTIVATED in Launcher')

        # --- Resume audio engine if it was suspended ---
        # Calling xmbc.audioResume() takes a loong time (2/4 secs) if audio was not properly suspended!
        # Also produces this in Kodi's log:
        # WARNING: CActiveAE::StateMachine - signal: 0 from port: OutputControlPort not handled for state: 7
        #   ERROR: ActiveAE::Resume - failed to init
        if self.kodi_audio_suspended:
            log_debug('_run_after_execution() Kodi audio engine was suspended before launching')
            log_debug('_run_after_execution() Resuming Kodi audio engine')
            xbmc.audioResume()
            xbmc.enableNavSounds(True)
            xbmc.sleep(100)
        else:
            log_debug('_run_after_execution() DO NOT resume Kodi audio engine')

        # --- Resume joystick engine if it was suspended ---
        if self.kodi_joystick_suspended:
            log_debug('_run_after_execution() Kodi joystick engine was suspended before launching')
            log_debug('_run_after_execution() Resuming Kodi joystick engine')
            # response = xbmc.executeJSONRPC(c_str)
            # log_debug('JSON      ''{}'''.format(c_str))
            # log_debug('Response  ''{}'''.format(response))
            log_debug('_run_before_execution() Not supported on Kodi Krypton!')
        else:
            log_debug('_run_after_execution() DO NOT resume Kodi joystick engine')

        # Restore screensaver status.
        if self.settings['suspend_screensaver']:
            kodi_restore_screensaver()
        else:
            screensaver_mode = kodi_get_screensaver_mode()
            log_debug('_run_after_execution() Screensaver status "{}"'.format(screensaver_mode))

        # --- Resume Kodi playing if it was paused. If it was stopped, keep it stopped. ---
        media_state_action = self.settings['media_state_action']
        media_state_str = ['Stop', 'Pause', 'Let Play'][media_state_action]
        log_debug('_run_after_execution() media_state_action is "{}" ({})'.format(media_state_str, media_state_action))
        log_debug('_run_after_execution() self.kodi_was_playing is {}'.format(self.kodi_was_playing))
        if self.kodi_was_playing and media_state_action == 1:
            log_debug('_run_after_execution() Calling xbmc.Player().play()')
            xbmc.Player().play()
        log_debug('_run_after_execution() function ENDS')

    # Check if Launcher reports must be created/regenrated
    def _roms_regenerate_launcher_reports(self, categoryID, launcherID, roms):
        # --- Get report filename ---
        if categoryID in self.categories: category_name = self.categories[categoryID]['m_name']
        else:                             category_name = VCATEGORY_ADDONROOT_ID
        roms_base_noext  = fs_get_ROMs_basename(category_name, self.launchers[launcherID]['m_name'], launcherID)
        report_stats_FN  = g_PATHS.REPORTS_DIR.pjoin(roms_base_noext + '_stats.txt')
        log_debug('_command_view_menu() Stats  OP "{}"'.format(report_stats_FN.getOriginalPath()))

        # --- If report doesn't exists create it automatically ---
        log_debug('_command_view_Launcher_Report() Testing report file "{}"'.format(report_stats_FN.getPath()))
        if not report_stats_FN.exists():
            kodi_dialog_OK('Report file not found. Will be generated now.')
            self._roms_create_launcher_reports(categoryID, launcherID, roms)
            self.launchers[launcherID]['timestamp_report'] = time.time()
            # DO NOT update the timestamp of categories/launchers or report will always be obsolete!!!
            # Keep same timestamp as before.
            fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers, self.update_timestamp)

        # --- If report timestamp is older than launchers last modification, recreate it ---
        if self.launchers[launcherID]['timestamp_report'] <= self.launchers[launcherID]['timestamp_launcher']:
            kodi_dialog_OK('Report is outdated. Will be regenerated now.')
            self._roms_create_launcher_reports(categoryID, launcherID, roms)
            self.launchers[launcherID]['timestamp_report'] = time.time()
            fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers, self.update_timestamp)

    # Creates a Launcher report having:
    #  1) Launcher statistics
    #  2) Report of ROM metadata
    #  3) Report of ROM artwork
    #  4) If No-Intro file, then No-Intro audit information.
    def _roms_create_launcher_reports(self, categoryID, launcherID, roms):
        ROM_NAME_LENGHT = 50

        # Report file name.
        if categoryID in self.categories: category_name = self.categories[categoryID]['m_name']
        else:                             category_name = VCATEGORY_ADDONROOT_ID
        launcher = self.launchers[launcherID]
        roms_base_noext  = fs_get_ROMs_basename(category_name, launcher['m_name'], launcherID)
        report_stats_FN  = g_PATHS.REPORTS_DIR.pjoin(roms_base_noext + '_stats.txt')
        report_meta_FN   = g_PATHS.REPORTS_DIR.pjoin(roms_base_noext + '_metadata.txt')
        report_assets_FN = g_PATHS.REPORTS_DIR.pjoin(roms_base_noext + '_assets.txt')
        log_debug('_roms_create_launcher_reports() Stats  OP "{}"'.format(report_stats_FN.getOriginalPath()))
        log_debug('_roms_create_launcher_reports() Meta   OP "{}"'.format(report_meta_FN.getOriginalPath()))
        log_debug('_roms_create_launcher_reports() Assets OP "{}"'.format(report_assets_FN.getOriginalPath()))
        roms_base_noext = fs_get_ROMs_basename(category_name, launcher['m_name'], launcherID)
        report_file_name = g_PATHS.REPORTS_DIR.pjoin(roms_base_noext + '.txt')
        log_debug('_roms_create_launcher_reports() Report filename "{}"'.format(report_file_name.getOriginalPath()))

        # >> Step 1: Build report data
        num_roms = len(roms)
        missing_m_year      = missing_m_genre    = missing_m_developer = missing_m_nplayers  = 0
        missing_m_esrb      = missing_m_rating   = missing_m_plot      = 0
        missing_s_title     = missing_s_snap     = missing_s_fanart    = missing_s_banner    = 0
        missing_s_clearlogo = missing_s_boxfront = missing_s_boxback   = missing_s_cartridge = 0
        missing_s_flyer     = missing_s_map      = missing_s_manual    = missing_s_trailer   = 0
        audit_none = audit_have = audit_miss = audit_unknown = 0
        audit_num_parents = audit_num_clones = 0
        check_list = []
        path_title_P = FileName(launcher['path_title']).getPath()
        path_snap_P = FileName(launcher['path_snap']).getPath()
        path_boxfront_P = FileName(launcher['path_boxfront']).getPath()
        path_boxback_P = FileName(launcher['path_boxback']).getPath()
        path_cartridge_P = FileName(launcher['path_cartridge']).getPath()
        for rom_id in sorted(roms, key = lambda x : roms[x]['m_name']):
            rom = roms[rom_id]
            rom_info = {}
            rom_info['m_name'] = rom['m_name']
            rom_info['m_nointro_status'] = rom['nointro_status']
            rom_info['m_pclone_status'] = rom['pclone_status']
            # --- Metadata ---
            if rom['m_year']:                 rom_info['m_year']      = 'YES'
            else:                             rom_info['m_year']      = '---'; missing_m_year += 1
            if rom['m_genre']:                rom_info['m_genre']     = 'YES'
            else:                             rom_info['m_genre']     = '---'; missing_m_genre += 1
            if rom['m_developer']:            rom_info['m_developer'] = 'YES'
            else:                             rom_info['m_developer'] = '---'; missing_m_developer += 1
            if rom['m_nplayers']:             rom_info['m_nplayers']  = 'YES'
            else:                             rom_info['m_nplayers']  = '---'; missing_m_nplayers += 1
            if rom['m_esrb'] == ESRB_PENDING: rom_info['m_esrb']      = '---'; missing_m_esrb += 1
            else:                             rom_info['m_studio']    = 'YES'
            if rom['m_rating']:               rom_info['m_rating']    = 'YES'
            else:                             rom_info['m_rating']    = '---'; missing_m_rating += 1
            if rom['m_plot']:                 rom_info['m_plot']      = 'YES'
            else:                             rom_info['m_plot']      = '---'; missing_m_plot += 1
            # --- Assets ---
            # >> Y means the asset exists and has the Base_noext of the ROM.
            # >> S means the asset exists and is a PClone group substitution.
            # >> C means the asset exists and is a user customised asset.
            # >> X means the asset exists, getDir() is same but Base_noext() is different
            # path_* and art getDir() different ==> Custom asset (user customised it) C
            # path_* and art getDir() equal and Base_noext() equal ==> Own artwork Y
            # path_* and art getDir() equal and Base_noext() different ==> Maybe S or maybe C => O
            # To differentiate between S and C a test in the PClone group must be done.
            #
            romfile_FN = FileName(rom['filename'])
            romfile_getBase_noext = romfile_FN.getBaseNoExt()
            if rom['s_title']:
                rom_info['s_title'] = self._aux_get_info(FileName(rom['s_title']), path_title_P, romfile_getBase_noext)
            else:
                rom_info['s_title'] = '-'
                missing_s_title += 1
            if rom['s_snap']:
                rom_info['s_snap'] = self._aux_get_info(FileName(rom['s_snap']), path_snap_P, romfile_getBase_noext)
            else:
                rom_info['s_snap'] = '-'
                missing_s_snap += 1
            if rom['s_boxfront']:
                rom_info['s_boxfront'] = self._aux_get_info(FileName(rom['s_boxfront']), path_boxfront_P, romfile_getBase_noext)
            else:
                rom_info['s_boxfront'] = '-'
                missing_s_boxfront += 1
            if rom['s_boxback']:
                rom_info['s_boxback'] = self._aux_get_info(FileName(rom['s_boxback']), path_boxback_P, romfile_getBase_noext)
            else:
                rom_info['s_boxback'] = '-'
                missing_s_boxback += 1
            if rom['s_cartridge']:
                rom_info['s_cartridge'] = self._aux_get_info(FileName(rom['s_cartridge']), path_cartridge_P, romfile_getBase_noext)
            else:
                rom_info['s_cartridge'] = '-'
                missing_s_cartridge += 1
            if rom['s_fanart']:    rom_info['s_fanart']    = 'Y'
            else:                  rom_info['s_fanart']    = '-'; missing_s_fanart += 1
            if rom['s_banner']:    rom_info['s_banner']    = 'Y'
            else:                  rom_info['s_banner']    = '-'; missing_s_banner += 1
            if rom['s_clearlogo']: rom_info['s_clearlogo'] = 'Y'
            else:                  rom_info['s_clearlogo'] = '-'; missing_s_clearlogo += 1
            if rom['s_flyer']:     rom_info['s_flyer']     = 'Y'
            else:                  rom_info['s_flyer']     = '-'; missing_s_flyer += 1
            if rom['s_map']:       rom_info['s_map']       = 'Y'
            else:                  rom_info['s_map']       = '-'; missing_s_map += 1
            if rom['s_manual']:    rom_info['s_manual']    = 'Y'
            else:                  rom_info['s_manual']    = '-'; missing_s_manual += 1
            if rom['s_trailer']:   rom_info['s_trailer']   = 'Y'
            else:                  rom_info['s_trailer']   = '-'; missing_s_trailer += 1
            # --- ROM audit ---
            if   rom['nointro_status'] == AUDIT_STATUS_NONE:    audit_none += 1
            elif rom['nointro_status'] == AUDIT_STATUS_HAVE:    audit_have += 1
            elif rom['nointro_status'] == AUDIT_STATUS_MISS:    audit_miss += 1
            elif rom['nointro_status'] == AUDIT_STATUS_UNKNOWN: audit_unknown += 1
            else:
                log_error('Unknown audit status {}.'.format(rom['nointro_status']))
                kodi_dialog_OK('Unknown audit status {}. This is a bug, please report it.'.format(rom['nointro_status']))
                return
            if   rom['pclone_status'] == PCLONE_STATUS_PARENT: audit_num_parents += 1
            elif rom['pclone_status'] == PCLONE_STATUS_CLONE:  audit_num_clones += 1
            elif rom['pclone_status'] == PCLONE_STATUS_NONE:   pass
            else:
                log_error('Unknown pclone status {}.'.format(rom['pclone_status']))
                kodi_dialog_OK('Unknown pclone status {}. This is a bug, please report it.'.format(rom['pclone_status']))
                return

            # Add to list
            check_list.append(rom_info)

        # Math
        have_m_year = num_roms - missing_m_year
        have_m_genre = num_roms - missing_m_genre
        have_m_developer = num_roms - missing_m_developer
        have_m_nplayers = num_roms - missing_m_nplayers
        have_m_esrb = num_roms - missing_m_esrb
        have_m_rating = num_roms - missing_m_rating
        have_m_plot = num_roms - missing_m_plot

        have_s_year_pcent = float(have_m_year*100) / num_roms
        have_s_genre_pcent = float(have_m_genre*100) / num_roms
        have_s_developer_pcent = float(have_m_developer*100) / num_roms
        have_s_nplayers_pcent = float(have_m_nplayers*100) / num_roms
        have_s_esrb_pcent = float(have_m_esrb*100) / num_roms
        have_s_rating_pcent = float(have_m_rating*100) / num_roms
        have_s_plot_pcent = float(have_m_plot*100) / num_roms

        miss_s_year_pcent = float(missing_m_year*100) / num_roms
        miss_s_genre_pcent = float(missing_m_genre*100) / num_roms
        miss_s_developer_pcent = float(missing_m_developer*100) / num_roms
        miss_s_nplayers_pcent = float(missing_m_nplayers*100) / num_roms
        miss_s_esrb_pcent = float(missing_m_esrb*100) / num_roms
        miss_s_rating_pcent = float(missing_m_rating*100) / num_roms
        miss_s_plot_pcent = float(missing_m_plot*100) / num_roms

        have_s_title = num_roms - missing_s_title
        have_s_snap = num_roms - missing_s_snap
        have_s_boxfront = num_roms - missing_s_boxfront
        have_s_boxback = num_roms - missing_s_boxback
        have_s_cartridge = num_roms - missing_s_cartridge
        have_s_fanart = num_roms - missing_s_fanart
        have_s_banner = num_roms - missing_s_banner
        have_s_clearlogo = num_roms - missing_s_clearlogo
        have_s_flyer = num_roms - missing_s_flyer
        have_s_map = num_roms - missing_s_map
        have_s_manual = num_roms - missing_s_manual
        have_s_trailer = num_roms - missing_s_trailer

        have_s_title_pcent = float(have_s_title*100) / num_roms
        have_s_snap_pcent = float(have_s_snap*100) / num_roms
        have_s_boxfront_pcent = float(have_s_boxfront*100) / num_roms
        have_s_boxback_pcent = float(have_s_boxback*100) / num_roms
        have_s_cartridge_pcent = float(have_s_cartridge*100) / num_roms
        have_s_fanart_pcent = float(have_s_fanart*100) / num_roms
        have_s_banner_pcent = float(have_s_banner*100) / num_roms
        have_s_clearlogo_pcent = float(have_s_clearlogo*100) / num_roms
        have_s_flyer_pcent = float(have_s_flyer*100) / num_roms
        have_s_map_pcent = float(have_s_map*100) / num_roms
        have_s_manual_pcent = float(have_s_manual*100) / num_roms
        have_s_trailer_pcent = float(have_s_trailer*100) / num_roms

        miss_s_title_pcent = float(missing_s_title*100) / num_roms
        miss_s_snap_pcent = float(missing_s_snap*100) / num_roms
        miss_s_boxfront_pcent = float(missing_s_boxfront*100) / num_roms
        miss_s_boxback_pcent = float(missing_s_boxback*100) / num_roms
        miss_s_cartridge_pcent = float(missing_s_cartridge*100) / num_roms
        miss_s_fanart_pcent = float(missing_s_fanart*100) / num_roms
        miss_s_banner_pcent = float(missing_s_banner*100) / num_roms
        miss_s_clearlogo_pcent = float(missing_s_clearlogo*100) / num_roms
        miss_s_flyer_pcent = float(missing_s_flyer*100) / num_roms
        miss_s_map_pcent = float(missing_s_map*100) / num_roms
        miss_s_manual_pcent = float(missing_s_manual*100) / num_roms
        miss_s_trailer_pcent = float(missing_s_trailer*100) / num_roms

        # --- Step 2: Statistics report ---
        # Launcher name printed on window title
        # Audit statistics
        str_list = []
        str_list.append('<No-Intro Audit Statistics>\n')
        str_list.append('Number of ROMs   {:5d}\n'.format(num_roms))
        str_list.append('Not checked ROMs {:5d}\n'.format(audit_none))
        str_list.append('Have ROMs        {:5d}\n'.format(audit_have))
        str_list.append('Missing ROMs     {:5d}\n'.format(audit_miss))
        str_list.append('Unknown ROMs     {:5d}\n'.format(audit_unknown))
        str_list.append('Parent           {:5d}\n'.format(audit_num_parents))
        str_list.append('Clones           {:5d}\n'.format(audit_num_clones))
        # Metadata
        str_list.append('\n<Metadata statistics>\n')
        str_list.append('Year      {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_m_year, missing_m_year, have_s_year_pcent, miss_s_year_pcent))
        str_list.append('Genre     {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_m_genre, missing_m_genre, have_s_genre_pcent, miss_s_genre_pcent))
        str_list.append('Developer {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_m_developer, missing_m_developer, have_s_developer_pcent, miss_s_developer_pcent))
        str_list.append('NPlayers  {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_m_nplayers, missing_m_nplayers, have_s_nplayers_pcent, miss_s_nplayers_pcent))
        str_list.append('ESRB      {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_m_esrb, missing_m_esrb, have_s_esrb_pcent, miss_s_esrb_pcent))
        str_list.append('Rating    {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_m_rating, missing_m_rating, have_s_rating_pcent, miss_s_rating_pcent))
        str_list.append('Plot      {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_m_plot, missing_m_plot, have_s_plot_pcent, miss_s_plot_pcent))
        # Assets statistics
        str_list.append('\n<Asset statistics>\n')
        str_list.append('Title     {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_title, missing_s_title, have_s_title_pcent, miss_s_title_pcent))
        str_list.append('Snap      {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_snap, missing_s_snap, have_s_snap_pcent, miss_s_snap_pcent))
        str_list.append('Boxfront  {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_boxfront, missing_s_boxfront, have_s_boxfront_pcent, miss_s_boxfront_pcent))
        str_list.append('Boxback   {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_boxback, missing_s_boxback, have_s_boxback_pcent, miss_s_boxback_pcent))
        str_list.append('Cartridge {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_cartridge, missing_s_cartridge, have_s_cartridge_pcent, miss_s_cartridge_pcent))
        str_list.append('Fanart    {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_fanart, missing_s_fanart, have_s_fanart_pcent, miss_s_fanart_pcent))
        str_list.append('Banner    {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_banner, missing_s_banner, have_s_banner_pcent, miss_s_banner_pcent))
        str_list.append('Clearlogo {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_clearlogo, missing_s_clearlogo, have_s_clearlogo_pcent, miss_s_clearlogo_pcent))
        str_list.append('Flyer     {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_flyer, missing_s_flyer, have_s_flyer_pcent, miss_s_flyer_pcent))
        str_list.append('Map       {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_map, missing_s_map, have_s_map_pcent, miss_s_map_pcent))
        str_list.append('Manual    {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_manual, missing_s_manual, have_s_manual_pcent, miss_s_manual_pcent))
        str_list.append('Trailer   {0:5d} have / {1:5d} miss  ({2:5.1f}%, {3:5.1f}%)\n'.format(
            have_s_trailer, missing_s_trailer, have_s_trailer_pcent, miss_s_trailer_pcent))

        # Step 3: Metadata report
        str_meta_list = []
        str_meta_list.append('{} Year Genre Developer Rating Plot Audit    PClone\n'.format('Name'.ljust(ROM_NAME_LENGHT)))
        str_meta_list.append('{}\n'.format('-' * 99))
        for m in check_list:
            # Limit ROM name string length
            name_str = text_limit_string(m['m_name'], ROM_NAME_LENGHT)
            str_meta_list.append('{} {}  {}   {}       {}    {}  {:<7}  {}\n'.format(
                name_str.ljust(ROM_NAME_LENGHT),
                m['m_year'], m['m_genre'], m['m_developer'],
                m['m_rating'], m['m_plot'], m['m_nointro_status'], m['m_pclone_status']))

        # Step 4: Asset report
        str_asset_list = []
        str_asset_list.append('{} Tit Sna Fan Ban Clr Bxf Bxb Car Fly Map Man Tra\n'.format('Name'.ljust(ROM_NAME_LENGHT)))
        str_asset_list.append('{}\n'.format('-' * 98))
        for m in check_list:
            # Limit ROM name string length
            name_str = text_limit_string(m['m_name'], ROM_NAME_LENGHT)
            str_asset_list.append('{}  {}   {}   {}   {}   {}   {}   {}   {}   {}   {}   {}   {}\n'.format(
                name_str.ljust(ROM_NAME_LENGHT),
                m['s_title'],     m['s_snap'],     m['s_fanart'],  m['s_banner'],
                m['s_clearlogo'], m['s_boxfront'], m['s_boxback'], m['s_cartridge'],
                m['s_flyer'],     m['s_map'],      m['s_manual'],  m['s_trailer']))

        # Step 5: Join string and write TXT reports
        try:
            # Stats report
            full_string = ''.join(str_list).encode('utf-8')
            file = open(report_stats_FN.getPath(), 'w')
            file.write(full_string)
            file.close()

            # Metadata report
            full_string = ''.join(str_meta_list).encode('utf-8')
            file = open(report_meta_FN.getPath(), 'w')
            file.write(full_string)
            file.close()

            # Asset report
            full_string = ''.join(str_asset_list).encode('utf-8')
            file = open(report_assets_FN.getPath(), 'w')
            file.write(full_string)
            file.close()
        except OSError:
            log_error('Cannot write Launcher Report file (OSError)')
            kodi_notify_warn('Cannot write Launcher Report (OSError)')
        except IOError:
            log_error('Cannot write categories.xml file (IOError)')
            kodi_notify_warn('Cannot write Launcher Report (IOError)')


    def _aux_get_info(self, asset_FN, path_asset_P, romfile_getBase_noext):
        # log_debug('title_FN.getDir() "{}"'.format(title_FN.getDir()))
        # log_debug('path_title_P      "{}"'.format(path_title_P))
        if path_asset_P != asset_FN.getDir():
            ret_str = 'C'
        else:
            if romfile_getBase_noext == asset_FN.getBaseNoExt():
                ret_str = 'Y'
            else:
                ret_str = 'O'

        return ret_str

    # Chooses a No-Intro/Redump DAT.
    # Return FileName object if a valid DAT was found.
    # Return None if error (DAT file not found).
    def _roms_set_NoIntro_DAT(self, launcher):
        has_custom_DAT = True if launcher['audit_custom_dat_file'] else False
        if has_custom_DAT:
            log_debug('Using user-provided custom DAT file.')
            nointro_xml_FN = FileName(launcher['audit_custom_dat_file'])
        else:
            log_debug('Trying to autolocating DAT file...')
            # --- Auto search for a DAT file ---
            NOINTRO_PATH_FN = FileName(self.settings['audit_nointro_dir'])
            if not NOINTRO_PATH_FN.exists():
                kodi_dialog_OK('No-Intro DAT directory not found. '
                    'Please set it up in AEL addon settings.')
                return None
            REDUMP_PATH_FN = FileName(self.settings['audit_redump_dir'])
            if not REDUMP_PATH_FN.exists():
                kodi_dialog_OK('No-Intro DAT directory not found. '
                    'Please set it up in AEL addon settings.')
                return None
            NOINTRO_DAT_list = NOINTRO_PATH_FN.scanFilesInPath('*.dat')
            REDUMP_DAT_list = REDUMP_PATH_FN.scanFilesInPath('*.dat')
            # Locate platform object.
            if launcher['platform'] in platform_long_to_index_dic:
                p_index = platform_long_to_index_dic[launcher['platform']]
                platform = AEL_platforms[p_index]
            else:
                kodi_dialog_OK(
                    'Unknown platform "{}". '.format(launcher['platform']) +
                    'ROM Audit cancelled.')
                return None
            # Autolocate DAT file
            if platform.DAT == DAT_NOINTRO:
                log_debug('Autolocating No-Intro DAT')
                fname = misc_look_for_NoIntro_DAT(platform, NOINTRO_DAT_list)
                if fname:
                    launcher['audit_auto_dat_file'] = fname
                    nointro_xml_FN = FileName(fname)
                else:
                    kodi_dialog_OK('No-Intro DAT cannot be auto detected.')
                    return None
            elif platform.DAT == DAT_REDUMP:
                log_debug('Autolocating Redump DAT')
                fname = misc_look_for_Redump_DAT(platform, REDUMP_DAT_list)
                if fname:
                    launcher['audit_auto_dat_file'] = fname
                    nointro_xml_FN = FileName(fname)
                else:
                    kodi_dialog_OK('Redump DAT cannot be auto detected.')
                    return None
            else:
                log_warning('platform.DAT {} unknown'.format(platform.DAT))
                return None

        return nointro_xml_FN

    # Deletes missing ROMs, probably added by the ROM Audit.
    def _roms_delete_missing_ROMs(self, roms):
        num_removed_roms = 0
        num_roms = len(roms)
        log_info('_roms_delete_missing_ROMs() Launcher has {} ROMs'.format(num_roms))
        if num_roms == 0:
            log_info('_roms_delete_missing_ROMs() Launcher is empty. No dead ROM check.')
            return num_removed_roms
        log_debug('_roms_delete_missing_ROMs() Starting dead items scan')
        for rom_id in sorted(roms, key = lambda x : roms[x]['m_name']):
            if not roms[rom_id]['filename']:
                # log_debug('_roms_delete_missing_ROMs() Skip "{}"'.format(roms[rom_id]['m_name']))
                continue
            ROMFileName = FileName(roms[rom_id]['filename'])
            # log_debug('_roms_delete_missing_ROMs() Test "{}"'.format(ROMFileName.getBase()))
            # --- Remove missing ROMs ---
            if not ROMFileName.exists():
                # log_debug('_roms_delete_missing_ROMs() RM   "{}"'.format(ROMFileName.getBase()))
                del roms[rom_id]
                num_removed_roms += 1
        if num_removed_roms > 0:
            log_info('_roms_delete_missing_ROMs() {} dead ROMs removed successfully'.format(
                num_removed_roms))
        else:
            log_info('_roms_delete_missing_ROMs() No dead ROMs found.')

        return num_removed_roms

    # Resets the No-Intro status
    # 1) Remove all ROMs which does not exist.
    # 2) Set status of remaining ROMs to nointro_status = AUDIT_STATUS_NONE
    # Both launcher and roms dictionaries edited by reference.
    def _roms_reset_NoIntro_status(self, launcher, roms):
        log_info('_roms_reset_NoIntro_status() Launcher has {} ROMs'.format(len(roms)))
        if len(roms) < 1: return

        # Step 1) Delete missing/dead ROMs
        num_removed_roms = self._roms_delete_missing_ROMs(roms)
        log_info('_roms_reset_NoIntro_status() Removed {} dead/missing ROMs'.format(num_removed_roms))

        # Step 2) Set Audit status to AUDIT_STATUS_NONE and
        #         set PClone status to PCLONE_STATUS_NONE
        log_info('_roms_reset_NoIntro_status() Resetting No-Intro status of all ROMs to None')
        for rom_id in sorted(roms, key = lambda x : roms[x]['m_name']):
            roms[rom_id]['nointro_status'] = AUDIT_STATUS_NONE
            roms[rom_id]['pclone_status']  = PCLONE_STATUS_NONE
        log_info('_roms_reset_NoIntro_status() Now launcher has {} ROMs'.format(len(roms)))

        # Step 3) Delete PClone index and Parent ROM list.
        roms_base_noext = launcher['roms_base_noext']
        CParent_roms_base_noext = roms_base_noext + '_index_CParent'
        PClone_roms_base_noext  = roms_base_noext + '_index_PClone'
        parents_roms_base_noext = roms_base_noext + '_parents'
        CParent_FN = g_PATHS.ROMS_DIR.pjoin(CParent_roms_base_noext + '.json')
        PClone_FN  = g_PATHS.ROMS_DIR.pjoin(PClone_roms_base_noext + '.json')
        parents_FN = g_PATHS.ROMS_DIR.pjoin(parents_roms_base_noext + '.json')
        if CParent_FN.exists():
            log_info('_roms_reset_NoIntro_status() Deleting {}'.format(CParent_FN.getPath()))
            CParent_FN.unlink()
        if PClone_FN.exists():
            log_info('_roms_reset_NoIntro_status() Deleting {}'.format(PClone_FN.getPath()))
            PClone_FN.unlink()
        if parents_FN.exists():
            log_info('_roms_reset_NoIntro_status() Deleting {}'.format(parents_FN.getPath()))
            parents_FN.unlink()

        # Step 4) Update launcher statistics and status.
        launcher['num_roms']    = len(roms)
        launcher['num_parents'] = 0
        launcher['num_clones']  = 0
        launcher['num_have']    = 0
        launcher['num_miss']    = 0
        launcher['num_unknown'] = 0
        launcher['audit_state'] = AUDIT_STATE_OFF

    # Helper function to update ROMs No-Intro status if user configured a No-Intro DAT file.
    # Dictionaries are mutable, so roms can be changed because passed by assigment.
    # This function also creates the Parent/Clone indices:
    #   1) ADDON_DATA_DIR/db_ROMs/roms_base_noext_PClone_index.json
    #   2) ADDON_DATA_DIR/db_ROMs/roms_base_noext_parents.json
    #
    # A) If there are Unkown ROMs, a fake rom with name [Unknown ROMs] and
    #    id UNKNOWN_ROMS_PARENT_ID is created. This fake ROM is the parent of all Unknown ROMs.
    #    This fake ROM is added to roms_base_noext_parents.json database.
    #    This fake ROM is not present in the main JSON ROM database.
    #
    # Both launcher and roms dictionaries updated by reference.
    #
    # Returns:
    #   True  -> ROM audit was OK
    #   False -> There was a problem with the audit.
    def _roms_update_NoIntro_status(self, launcher, roms, DAT_FN):
        __debug_progress_dialogs = False
        __debug_time_step = 0.0005

        # --- Reset the No-Intro status and removed No-Intro missing ROMs ---
        audit_have = audit_miss = audit_unknown = audit_extra = 0
        pDialog = KodiProgressDialog()
        pDialog.startProgress('Deleting Missing/Dead ROMs and clearing flags...')
        self._roms_reset_NoIntro_status(launcher, roms)
        pDialog.endProgress()
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Check if DAT file exists ---
        if not DAT_FN.exists():
            log_warning('_roms_update_NoIntro_status() Not found {}'.format(DAT_FN.getPath()))
            return False
        pDialog.startProgress('Loading No-Intro/Redump XML DAT file...')
        roms_nointro = audit_load_NoIntro_XML_file(DAT_FN)
        pDialog.endProgress()
        if __debug_progress_dialogs: time.sleep(0.5)
        if not roms_nointro:
            log_warning('_roms_update_NoIntro_status() Error loading {}'.format(DAT_FN.getPath()))
            return False

        # --- Remove BIOSes from No-Intro ROMs ---
        if self.settings['scan_ignore_bios']:
            log_info('_roms_update_NoIntro_status() Removing BIOSes from No-Intro ROMs ...')
            pDialog.startProgress('Removing BIOSes from No-Intro ROMs...', len(roms_nointro))
            filtered_roms_nointro = {}
            for rom_id in roms_nointro:
                pDialog.updateProgressInc()
                if __debug_progress_dialogs: time.sleep(__debug_time_step)

                rom = roms_nointro[rom_id]
                BIOS_str_list = re.findall('\[BIOS\]', rom['name'])
                if not BIOS_str_list:
                    filtered_roms_nointro[rom_id] = rom
                else:
                    log_debug('_roms_update_NoIntro_status() Removed BIOS "{}"'.format(rom['name']))
            pDialog.endProgress()
            roms_nointro = filtered_roms_nointro
        else:
            log_info('_roms_update_NoIntro_status() User wants to include BIOSes.')

        # --- Put No-Intro ROM names in a set ---
        # Set is the fastest Python container for searching elements (implements hashed search).
        # No-Intro names include tags
        roms_nointro_set = set(roms_nointro.keys())
        roms_set = set()
        pDialog.startProgress('Creating No-Intro and ROM sets...')
        for rom_id in roms:
            ROMFileName = FileName(roms[rom_id]['filename'])
            roms_set.add(ROMFileName.getBaseNoExt()) # Use the ROM basename.
        pDialog.endProgress()
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Traverse Launcher ROMs and check if they are in the No-Intro ROMs list ---
        pDialog.startProgress('Audit Step 1/4: Checking Have and Unknown ROMs...', len(roms))
        for rom_id in roms:
            pDialog.updateProgressInc()
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
            ROMFileName = FileName(roms[rom_id]['filename'])
            if roms[rom_id]['i_extra_ROM']:
                roms[rom_id]['nointro_status'] = AUDIT_STATUS_EXTRA
                audit_extra += 1
                # log_debug('_roms_update_NoIntro_status() EXTRA   "{}"'.format(ROMFileName.getBaseNoExt()))
            elif ROMFileName.getBaseNoExt() in roms_nointro_set:
                roms[rom_id]['nointro_status'] = AUDIT_STATUS_HAVE
                audit_have += 1
                # log_debug('_roms_update_NoIntro_status() HAVE    "{}"'.format(ROMFileName.getBaseNoExt()))
            else:
                roms[rom_id]['nointro_status'] = AUDIT_STATUS_UNKNOWN
                audit_unknown += 1
                # log_debug('_roms_update_NoIntro_status() UNKNOWN "{}"'.format(ROMFileName.getBaseNoExt()))
        pDialog.endProgress()

        # --- Mark Launcher dead ROMs as Missing ---
        pDialog.startProgress('Audit Step 2/4: Checking Missing ROMs...', len(roms))
        for rom_id in roms:
            pDialog.updateProgressInc()
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
            ROMFileName = FileName(roms[rom_id]['filename'])
            if not ROMFileName.exists():
                roms[rom_id]['nointro_status'] = AUDIT_STATUS_MISS
                audit_miss += 1
                # log_debug('_roms_update_NoIntro_status() MISSING "{}"'.format(ROMFileName.getBaseNoExt()))
        pDialog.endProgress()

        # --- Now add Missing ROMs to Launcher ---
        # Traverse the No-Intro set and add the No-Intro ROM if it's not in the Launcher
        # Added/Missing ROMs have their own romID.
        ROMPath = FileName(launcher['rompath'])
        pDialog.startProgress('Audit Step 3/4: Adding Missing ROMs...', len(roms_nointro_set))
        for nointro_rom in sorted(roms_nointro_set):
            pDialog.updateProgressInc()
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
            # log_debug('_roms_update_NoIntro_status() Checking "{}"'.format(nointro_rom))
            if nointro_rom not in roms_set:
                # Add new "fake" missing ROM. This ROM cannot be launched!
                # Added ROMs have special extension .nointro
                rom = fs_new_rom()
                rom_id                = misc_generate_random_SID()
                rom['id']             = rom_id
                rom['filename']       = ROMPath.pjoin(nointro_rom + '.nointro').getOriginalPath()
                rom['m_name']         = nointro_rom
                rom['nointro_status'] = AUDIT_STATUS_MISS
                roms[rom_id] = rom
                audit_miss += 1
                # log_debug('_roms_update_NoIntro_status() ADDED   "{}"'.format(rom['m_name']))
                # log_debug('_roms_update_NoIntro_status()    OP   "{}"'.format(rom['filename']))
        pDialog.endProgress()

        # --- Detect if the DAT file has PClone information or not ---
        dat_pclone_dic = audit_make_NoIntro_PClone_dic(roms_nointro)
        num_dat_clones = 0
        for parent_name in dat_pclone_dic: num_dat_clones += len(dat_pclone_dic[parent_name])
        log_debug('No-Intro/Redump DAT has {} clone ROMs'.format(num_dat_clones))

        # --- Generate main pclone dictionary ---
        # audit_unknown_roms is an int of list = ['Parents', 'Clones']
        # log_debug("settings['audit_unknown_roms'] = {}".format(self.settings['audit_unknown_roms']))
        unknown_ROMs_are_parents = True if self.settings['audit_unknown_roms'] == 0 else False
        log_debug('unknown_ROMs_are_parents = {}'.format(unknown_ROMs_are_parents))
        # if num_dat_clones == 0 and self.settings['audit_create_pclone_groups']:
        #     # --- If DAT has no PClone information and user want then generate filename-based PClone groups ---
        #     # This feature is taken from NARS (NARS Advanced ROM Sorting)
        #     log_debug('Generating filename-based Parent/Clone groups')
        #     pDialog.startProgress('Building filename-based Parent/Clone index...')
        #     roms_pclone_index = audit_generate_filename_PClone_index(roms, roms_nointro, unknown_ROMs_are_parents)
        #     pDialog.endProgress()
        #     if __debug_progress_dialogs: time.sleep(0.5)
        # else:
        #     # --- Make a DAT-based Parent/Clone index ---
        #     # Here we build a roms_pclone_index with info from the DAT file. 2 issues:
        #     # A) Redump DATs do not have cloneof information.
        #     # B) Also, it is at this point where a region custom parent may be chosen instead of
        #     #    the default one.
        #     log_debug('Generating DAT-based Parent/Clone groups')
        #     pDialog.startProgress('Building DAT-based Parent/Clone index...')
        #     roms_pclone_index = audit_generate_DAT_PClone_index(roms, roms_nointro, unknown_ROMs_are_parents)
        #     pDialog.endProgress()
        #     if __debug_progress_dialogs: time.sleep(0.5)

        # --- Make a DAT-based Parent/Clone index ---
        # For 0.9.7 only use the DAT to make the PClone groups. In 0.9.8 decouple the audit
        # code from the PClone generation code.
        log_debug('Generating DAT-based Parent/Clone groups')
        pDialog.startProgress('Building DAT-based Parent/Clone index...')
        roms_pclone_index = audit_generate_DAT_PClone_index(roms, roms_nointro, unknown_ROMs_are_parents)
        pDialog.endProgress()
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Make a Clone/Parent index ---
        # This is made exclusively from the Parent/Clone index
        pDialog.startProgress('Building Clone/Parent index...')
        clone_parent_dic = {}
        for parent_id in roms_pclone_index:
            for clone_id in roms_pclone_index[parent_id]:
                clone_parent_dic[clone_id] = parent_id
        pDialog.endProgress()
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Set ROMs pclone_status flag and update launcher statistics ---
        pDialog.startProgress('Audit Step 4/4: Setting Parent/Clone status and cloneof fields...', len(roms))
        audit_parents, audit_clones = 0, 0
        for rom_id in roms:
            pDialog.updateProgressInc()
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
            if rom_id in roms_pclone_index:
                roms[rom_id]['pclone_status'] = PCLONE_STATUS_PARENT
                audit_parents += 1
            else:
                roms[rom_id]['cloneof'] = clone_parent_dic[rom_id]
                roms[rom_id]['pclone_status'] = PCLONE_STATUS_CLONE
                audit_clones += 1
        pDialog.endProgress()
        launcher['num_roms']    = len(roms)
        launcher['num_parents'] = audit_parents
        launcher['num_clones']  = audit_clones
        launcher['num_have']    = audit_have
        launcher['num_miss']    = audit_miss
        launcher['num_unknown'] = audit_unknown
        launcher['num_extra']   = audit_extra
        launcher['audit_state'] = AUDIT_STATE_ON

        # --- Make a Parent only ROM list and save JSON ---
        # This is to speed up rendering of launchers in Parent/Clone display mode.
        pDialog.startProgress('Building Parent/Clone index and Parent dictionary...')
        parent_roms = audit_generate_parent_ROMs_dic(roms, roms_pclone_index)
        pDialog.endProgress()
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Save JSON databases ---
        pDialog.startProgress('Saving NO-Intro/Redump JSON databases...', 3)
        f_FN = g_PATHS.ROMS_DIR.pjoin(launcher['roms_base_noext'] + '_index_PClone.json')
        utils_write_JSON_file(f_FN.getPath(), roms_pclone_index)
        pDialog.updateProgressInc()
        f_FN = g_PATHS.ROMS_DIR.pjoin(launcher['roms_base_noext'] + '_index_CParent.json')
        utils_write_JSON_file(f_FN.getPath(), clone_parent_dic)
        pDialog.updateProgressInc()
        f_FN = g_PATHS.ROMS_DIR.pjoin(launcher['roms_base_noext'] + '_parents.json')
        utils_write_JSON_file(f_FN.getPath(), parent_roms)
        pDialog.endProgress()

        # --- Update launcher number of ROMs ---
        self.audit_have    = audit_have
        self.audit_miss    = audit_miss
        self.audit_unknown = audit_unknown
        self.audit_extra   = audit_extra
        self.audit_total   = len(roms)
        self.audit_parents = audit_parents
        self.audit_clones  = audit_clones

        # --- Report ---
        log_info('********** No-Intro/Redump audit finished. Report ***********')
        log_info('Have ROMs    {:6d}'.format(self.audit_have))
        log_info('Miss ROMs    {:6d}'.format(self.audit_miss))
        log_info('Unknown ROMs {:6d}'.format(self.audit_unknown))
        log_info('Extra ROMs   {:6d}'.format(self.audit_extra))
        log_info('Total ROMs   {:6d}'.format(self.audit_total))
        log_info('Parent ROMs  {:6d}'.format(self.audit_parents))
        log_info('Clone ROMs   {:6d}'.format(self.audit_clones))

        return True

    # DEPRCATED FUNCTION. Not used anymore and will be removed soon.
    #
    # Manually add a new ROM instead of a recursive scan.
    #   A) User chooses a ROM file
    #   B) Title is formatted. No metadata scraping.
    #   C) Thumb and fanart are searched locally only.
    # Later user can edit this ROM if he wants.
    def _roms_add_new_rom(self, launcherID):
        # --- Grab launcher information ---
        launcher = self.launchers[launcherID]
        romext   = launcher['romext']
        rompath  = launcher['rompath']
        log_debug('_roms_add_new_rom() launcher name "{}"'.format(launcher['m_name']))

        # --- Load ROMs for this launcher ---
        roms = fs_load_ROMs_JSON(g_PATHS.ROMS_DIR, launcher)

        # --- Choose ROM file ---
        extensions = '.' + romext.replace('|', '|.')
        romfile = kodi_dialog_get_file('Select the ROM file', extensions, rompath)
        if not romfile: return
        log_debug('_roms_add_new_rom() romfile "{}"'.format(romfile))

        # --- Format title ---
        scan_clean_tags = self.settings['scan_clean_tags']
        ROMFile = FileName(romfile)
        rom_name = text_format_ROM_title(ROMFile.getBaseNoExt(), scan_clean_tags)

        # ~~~ Check asset dirs and disable scanning for unset dirs ~~~
        # >> Do not warn about unconfigured dirs here
        (enabled_asset_list, unconfigured_name_list) = asset_get_configured_dir_list(launcher)

        # ~~~ Ensure there is no duplicate asset dirs ~~~
        duplicated_name_list = asset_get_duplicated_dir_list(launcher)
        if duplicated_name_list:
            duplicated_asset_srt = ', '.join(duplicated_name_list)
            log_debug('_roms_add_new_rom() Duplicated asset dirs: {}'.format(duplicated_asset_srt))
            kodi_dialog_OK('Duplicated asset directories: {}. '.format(duplicated_asset_srt) +
                'Change asset directories before continuing.')
            return
        else:
            log_debug('_roms_add_new_rom() No duplicated asset dirs found')

        # ~~~ Search for local artwork/assets ~~~
        local_asset_list = assets_search_local_assets(launcher, ROMFile, enabled_asset_list)

        # --- Create ROM data structure ---
        romdata = fs_new_rom()
        romdata['id']          = misc_generate_random_SID()
        romdata['filename']    = ROMFile.getOriginalPath()
        romdata['m_name']      = rom_name
        for index, asset_kind in enumerate(ROM_ASSET_ID_LIST):
            A = assets_get_info_scheme(asset_kind)
            romdata[A.key] = local_asset_list[index]
        roms[romdata['id']] = romdata
        log_info('_roms_add_new_rom() Added a new ROM')
        log_info('_roms_add_new_rom() romID       "{}"'.format(romdata['id']))
        log_info('_roms_add_new_rom() filename    "{}"'.format(romdata['filename']))
        log_info('_roms_add_new_rom() m_name      "{}"'.format(romdata['m_name']))
        log_debug('_roms_add_new_rom() s_title     "{}"'.format(romdata['s_title']))
        log_debug('_roms_add_new_rom() s_snap      "{}"'.format(romdata['s_snap']))
        log_debug('_roms_add_new_rom() s_fanart    "{}"'.format(romdata['s_fanart']))
        log_debug('_roms_add_new_rom() s_banner    "{}"'.format(romdata['s_banner']))
        log_debug('_roms_add_new_rom() s_clearlogo "{}"'.format(romdata['s_clearlogo']))
        log_debug('_roms_add_new_rom() s_boxfront  "{}"'.format(romdata['s_boxfront']))
        log_debug('_roms_add_new_rom() s_boxback   "{}"'.format(romdata['s_boxback']))
        log_debug('_roms_add_new_rom() s_cartridge "{}"'.format(romdata['s_cartridge']))
        log_debug('_roms_add_new_rom() s_flyer     "{}"'.format(romdata['s_flyer']))
        log_debug('_roms_add_new_rom() s_map       "{}"'.format(romdata['s_map']))
        log_debug('_roms_add_new_rom() s_manual    "{}"'.format(romdata['s_manual']))
        log_debug('_roms_add_new_rom() s_trailer   "{}"'.format(romdata['s_trailer']))

        # --- If there is a No-Intro XML configured audit ROMs ---
        if launcher['audit_state'] == AUDIT_STATE_ON:
            log_info('ROM Audit is ON. Refreshing ROM audit ...')
            nointro_xml_FN = self._roms_set_NoIntro_DAT(launcher)
            if not self._roms_update_NoIntro_status(launcher, roms, nointro_xml_FN):
                kodi_dialog_OK('Error auditing ROMs. XML DAT file unset.')
        else:
            log_info('ROM Audit if OFF. Do not refresh ROM Audit.')

        # ~~~ Save ROMs XML file ~~~
        # Also save categories/launchers to update timestamp.
        launcher['num_roms'] = len(roms)
        launcher['timestamp_launcher'] = time.time()
        fs_write_ROMs_JSON(g_PATHS.ROMS_DIR, launcher, roms)
        fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        kodi_refresh_container()
        kodi_notify('Added ROM. Launcher has now {} ROMs'.format(len(roms)))

    # ROM scanner. Called when user chooses Launcher CM, "Add ROMs" -> "Scan for new ROMs"
    def _roms_import_roms(self, launcherID):
        log_debug('========== _roms_import_roms() BEGIN ==================================================')

        # --- Get information from launcher ---
        launcher = self.launchers[launcherID]
        rom_path = FileName(launcher['rompath'])
        launcher_exts = launcher['romext']
        rom_extra_path = FileName(launcher['romextrapath'])
        launcher_multidisc = launcher['multidisc']
        log_info('_roms_import_roms() Starting ROM scanner ...')
        log_info('Launcher name  "{}"'.format(launcher['m_name']))
        log_info('Launcher ID    "{}"'.format(launcher['id']))
        log_info('ROM path       "{}"'.format(rom_path.getPath()))
        log_info('ROM extra path "{}"'.format(rom_extra_path.getPath()))
        log_info('ROM exts       "{}"'.format(launcher_exts))
        log_info('Platform       "{}"'.format(launcher['platform']))
        log_info('Multidisc      {}'.format(launcher_multidisc))

        # --- Open ROM scanner report file ---
        launcher_report_FN = g_PATHS.REPORTS_DIR.pjoin(launcher['roms_base_noext'] + '_report.txt')
        log_info('Report file OP "{}"'.format(launcher_report_FN.getOriginalPath()))
        log_info('Report file  P "{}"'.format(launcher_report_FN.getPath()))
        report_slist = []
        report_slist.append('*** Starting ROM scanner ***')
        report_slist.append('Launcher name  "{}"'.format(launcher['m_name']))
        report_slist.append('Launcher ID    "{}"'.format(launcher['id']))
        report_slist.append('ROM path       "{}"'.format(rom_path.getPath()))
        report_slist.append('ROM extra path "{}"'.format(rom_extra_path.getPath()))
        report_slist.append('ROM ext        "{}"'.format(launcher_exts))
        report_slist.append('Platform       "{}"'.format(launcher['platform']))

        # Check if there is an XML for this launcher. If so, load it.
        # If file does not exist or is empty then return an empty dictionary.
        report_slist.append('Loading launcher ROMs...')
        roms = fs_load_ROMs_JSON(g_PATHS.ROMS_DIR, launcher)
        num_roms = len(roms)
        report_slist.append('{} ROMs currently in database'.format(num_roms))
        log_info('Launcher ROM database contain {} items'.format(num_roms))

        # --- Progress dialog ---
        pdialog_verbose = True
        pdialog = KodiProgressDialog()

        # --- Load metadata/asset scrapers --------------------------------------------------------
        g_scraper_factory = ScraperFactory(g_PATHS, self.settings)
        scraper_strategy = g_scraper_factory.create_scanner(launcher)
        scraper_strategy.scanner_set_progress_dialog(pdialog, pdialog_verbose)
        # Check if scraper is ready for operation. Otherwise disable it internally.
        scraper_strategy.scanner_check_before_scraping()

        # Create ROMFilter object. Loads filter databases for MAME.
        romfilter = FilterROM(g_PATHS, self.settings, launcher['platform'])

        # --- Assets/artwork stuff ----------------------------------------------------------------
        # Ensure there is no duplicate asset dirs. Abort scanning of assets if duplicate dirs found.
        log_debug('Checking for duplicated artwork directories...')
        duplicated_name_list = asset_get_duplicated_dir_list(launcher)
        if duplicated_name_list:
            duplicated_asset_srt = ', '.join(duplicated_name_list)
            log_info('Duplicated asset dirs: {}'.format(duplicated_asset_srt))
            kodi_dialog_OK('Duplicated asset directories: {}. '.format(duplicated_asset_srt) +
                'Change asset directories before continuing.')
            return
        else:
            log_info('No duplicated asset dirs found')

        # --- Check asset dirs and disable scanning for unset dirs ---
        log_debug('Checking for unset artwork directories...')
        scraper_strategy.scanner_check_launcher_unset_asset_dirs()
        if scraper_strategy.unconfigured_name_list:
            unconfigured_asset_srt = ', '.join(scraper_strategy.unconfigured_name_list)
            kodi_dialog_OK('Assets directories not set: {}. '.format(unconfigured_asset_srt) +
                'Asset scanner will be disabled for this/those.')

        # --- Create a cache of assets ---
        # utils_file_cache_add_dir() creates a set with all files in a given directory.
        # That set is stored in a function internal cache associated with the path.
        # Files in the cache can be searched with utils_file_cache_search()
        log_info('Scanning and caching files in asset directories...')
        pdialog.startProgress('Scanning files in asset directories...', len(ROM_ASSET_ID_LIST))
        for i, asset_kind in enumerate(ROM_ASSET_ID_LIST):
            pdialog.updateProgress(i)
            AInfo = assets_get_info_scheme(asset_kind)
            utils_file_cache_add_dir(launcher[AInfo.path_key])
        pdialog.endProgress()

        # --- Remove dead ROM entries ------------------------------------------------------------
        log_info('Removing dead ROMs...'.format())
        report_slist.append('Removing dead ROMs...')
        num_removed_roms = 0
        if num_roms > 0:
            pdialog.startProgress('Checking for dead ROMs...', num_roms)
            i = 0
            for key in sorted(roms, key = lambda x : roms[x]['m_name']):
                pdialog.updateProgress(i)
                i += 1
                log_debug('Searching {}'.format(roms[key]['filename']))
                fileName = FileName(roms[key]['filename'])
                if not fileName.exists():
                    log_debug('Deleting from DB {}'.format(roms[key]['filename']))
                    del roms[key]
                    num_removed_roms += 1
            pdialog.endProgress()
            if num_removed_roms > 0:
                kodi_notify('{} dead ROMs removed successfully'.format(num_removed_roms))
                log_info('{} dead ROMs removed successfully'.format(num_removed_roms))
            else:
                log_info('No dead ROMs found')
        else:
            log_info('Launcher is empty. No dead ROM check.')

        # --- Scan all files in ROM path (mask *.*) and put them in a list -----------------------
        pdialog.startProgress('Scanning and caching files in ROM path ...')
        files = []
        log_info('Scanning files in {}'.format(rom_path.getPath()))
        report_slist.append('Scanning files ...')
        report_slist.append('Directory {}'.format(rom_path.getPath()))
        if self.settings['scan_recursive']:
            log_info('Recursive scan activated')
            files = rom_path.recursiveScanFilesInPath('*.*')
        else:
            log_info('Recursive scan not activated')
            files = rom_path.scanFilesInPath('*.*')
        log_info('File scanner found {} files'.format(len(files)))
        report_slist.append('File scanner found {} files'.format(len(files)))
        pdialog.endProgress()

        # --- Scan all files in extra ROM path ---------------------------------------------------
        extra_files = []
        if launcher['romextrapath']:
            log_info('Scanning files in extra ROM path.')
            pdialog.startProgress('Scanning and caching files in extra ROM path ...')
            log_info('Scanning files in {}'.format(rom_extra_path.getPath()))
            report_slist.append('Scanning files...')
            report_slist.append('Directory {}'.format(rom_extra_path.getPath()))
            if self.settings['scan_recursive']:
                log_info('Recursive scan activated')
                extra_files = rom_extra_path.recursiveScanFilesInPath('*.*')
            else:
                log_info('Recursive scan not activated')
                extra_files = rom_extra_path.scanFilesInPath('*.*')
            log_info('File scanner found {} files'.format(len(extra_files)))
            report_slist.append('File scanner found {} files'.format(len(extra_files)))
            pdialog.endProgress()
        else:
            log_info('Extra ROM path empty. Skipping scanning.')

        # --- Prepare list of files to be processed ----------------------------------------------
        # List has tuples (filename, extra_ROM_flag). List already sorted alphabetically.
        file_list = []
        for f_path in sorted(files): file_list.append((f_path, False))
        for f_path in sorted(extra_files): file_list.append((f_path, True))

        # --- Now go processing file by file -----------------------------------------------------
        pdialog.startProgress('Processing ROMs...', len(file_list))
        log_info('============================== Processing ROMs ===============================')
        report_slist.append('\n*** Processing files ***')
        num_new_roms = 0
        num_files_checked = 0
        for f_path, extra_ROM_flag in file_list:
            # --- Get all file name combinations ---
            ROM = FileName(f_path)
            log_debug('------------------------------ Processing cached file -------------------')
            log_debug('ROM.getPath()         "{}"'.format(ROM.getPath()))
            log_debug('ROM.getOriginalPath() "{}"'.format(ROM.getOriginalPath()))
            # log_debug('ROM.getPathNoExt()    "{}"'.format(ROM.getPathNoExt()))
            # log_debug('ROM.getDir()          "{}"'.format(ROM.getDir()))
            # log_debug('ROM.getBase()         "{}"'.format(ROM.getBase()))
            # log_debug('ROM.getBaseNoExt()    "{}"'.format(ROM.getBaseNoExt()))
            # log_debug('ROM.getExt()          "{}"'.format(ROM.getExt()))
            report_slist.append('File "{}"'.format(ROM.getPath()))

            # Update progress dialog.
            file_text = 'ROM [COLOR orange]{}[/COLOR]'.format(ROM.getBase())
            if pdialog_verbose: file_text += '\nChecking if has ROM extension...'
            pdialog.updateProgress(num_files_checked, file_text)
            # if not pdialog_verbose:
            #     pdialog.updateProgress(num_files_checked, file_text)
            # else:
            #     pdialog.updateProgress(num_files_checked, file_text, 'Checking if has ROM extension...')
            num_files_checked += 1

            # --- Check if filename matchs ROM extensions ---
            # The recursive scan has scanned all files. Check if this file matches some of
            # the ROM extensions. If this file isn't a ROM skip it and go for next one in the list.
            processROM = False
            for ext in launcher_exts.split("|"):
                if ROM.getExt() == '.' + ext:
                    log_debug("Expected '{}' extension detected".format(ext))
                    report_slist.append("Expected '{}' extension detected".format(ext))
                    processROM = True
            if not processROM:
                log_debug('File has not an expected extension. Skipping file.')
                report_slist.append('File has not an expected extension. Skipping file.')
                report_slist.append('')
                continue

            # --- Check if ROM belongs to a multidisc set ---
            MultiDiscInROMs = False
            MDSet = get_multidisc_info(ROM)
            if MDSet.isMultiDisc and launcher_multidisc:
                log_debug('ROM belongs to a multidisc set.')
                log_debug('isMultiDisc "{}"'.format(MDSet.isMultiDisc))
                log_debug('setName     "{}"'.format(MDSet.setName))
                log_debug('discName    "{}"'.format(MDSet.discName))
                log_debug('extension   "{}"'.format(MDSet.extension))
                log_debug('order       "{}"'.format(MDSet.order))
                report_slist.append('ROM belongs to a multidisc set.')

                # Check if the set is already in launcher ROMs.
                MultiDisc_rom_id = None
                for rom_id in roms:
                    temp_FN = FileName(roms[rom_id]['filename'])
                    if temp_FN.getBase() == MDSet.setName:
                        MultiDiscInROMs  = True
                        MultiDisc_rom_id = rom_id
                        break
                log_debug('MultiDiscInROMs is {}'.format(MultiDiscInROMs))

                # If the set is not in the ROMs then this ROM is the first of the set.
                # Add the set
                if not MultiDiscInROMs:
                    log_debug('First ROM in the multidisc set.')
                    # Manipulate ROM so filename is the name of the set.
                    ROM_original = ROM
                    ROM_dir = FileName(ROM.getDir())
                    ROM_temp = ROM_dir.pjoin(MDSet.setName)
                    log_debug('ROM_temp OP "{}"'.format(ROM_temp.getOriginalPath()))
                    log_debug('ROM_temp  P "{}"'.format(ROM_temp.getPath()))
                    log_debug('ROM_original OP "{}"'.format(ROM_original.getOriginalPath()))
                    log_debug('ROM_original  P "{}"'.format(ROM_original.getPath()))
                    ROM = ROM_temp
                # If set already in ROMs, just add this disk into the set disks field.
                else:
                    log_debug('Adding additional disk "{}" to set'.format(MDSet.discName))
                    roms[MultiDisc_rom_id]['disks'].append(MDSet.discName)
                    # Reorder disks like Disk 1, Disk 2, ...

                    # Process next file
                    log_debug('Processing next file ...')
                    continue
            elif MDSet.isMultiDisc and not launcher_multidisc:
                log_debug('ROM belongs to a multidisc set but Multidisc support is disabled.')
                report_slist.append('ROM belongs to a multidisc set but Multidisc support is disabled.')
            else:
                log_debug('ROM does not belong to a multidisc set.')
                report_slist.append('ROM does not belong to a multidisc set.')

            # --- If ROM already in DB then skip it ---
            # Linear search is slow but I don't care for now.
            ROM_in_launcher_DB = False
            for rom_id in roms:
                if roms[rom_id]['filename'] == f_path:
                    ROM_in_launcher_DB = True
                    break
            if ROM_in_launcher_DB:
                log_debug('File already into launcher ROM list. Skipping file.')
                report_slist.append('File already into launcher ROM list. Skipping file.')
                report_slist.append('')
                continue
            else:
                log_debug('File not in launcher ROM list. Processing...')
                report_slist.append('File not in launcher ROM list. Processing...')

            # --- Ignore BIOS ROMs ---
            if romfilter.ROM_is_filtered(ROM.getBaseNoExt()):
                log_debug('ROM filtered. Skipping ROM processing.')
                report_slist.append('ROM filtered. Skipping ROM processing.')
                report_slist.append('')
                continue

            # --- Create new ROM and process metadata and assets ---------------------------------
            romdata = fs_new_rom()
            romdata['id'] = misc_generate_random_SID()
            romdata['filename'] = ROM.getOriginalPath()
            romdata['i_extra_ROM'] = extra_ROM_flag
            ROM_checksums = ROM_original if MDSet.isMultiDisc and launcher_multidisc else ROM
            scraper_strategy.scanner_process_ROM_begin(romdata, ROM, ROM_checksums)
            scraper_strategy.scanner_process_ROM_metadata(romdata, ROM)
            scraper_strategy.scanner_process_ROM_assets(romdata, ROM)

            # --- Add ROM to database ------------------------------------------------------------
            roms[romdata['id']] = romdata
            num_new_roms += 1

            # --- This was the first ROM in a multidisc set ---
            if launcher_multidisc and MDSet.isMultiDisc and not MultiDiscInROMs:
                log_info('Adding to ROMs dic first disk "{}"'.format(MDSet.discName))
                roms[romdata['id']]['disks'].append(MDSet.discName)

            # --- Check if user pressed the cancel button ---
            if pdialog.isCanceled():
                pdialog.endProgress()
                kodi_dialog_OK('Stopping ROM scanning. No changes have been made.')
                log_info('User pressed Cancel button when scanning ROMs. ROM scanning stopped.')
                # Flush scraper disk caches.
                g_scraper_factory.destroy_scanner(pdialog)
                # Flush report
                report_head_sl.append('WARNING ROM Scanner interrupted (cancel button pressed).')
                report_head_sl.append('')
                r_all_sl = []
                r_all_sl.extend(report_head_sl)
                r_all_sl.extend(report_slist)
                utils_write_slist_to_file(launcher_report_FN.getPath(), r_all_sl)
                return
            report_slist.append('')
        pdialog.endProgress()
        # Flush scraper disk caches.
        g_scraper_factory.destroy_scanner(pdialog)

        # --- Scanner report ---
        log_info('******************** ROM scanner finished. Report ********************')
        log_info('Removed dead ROMs {:6d}'.format(num_removed_roms))
        log_info('Files checked     {:6d}'.format(num_files_checked))
        log_info('New added ROMs    {:6d}'.format(num_new_roms))
        log_info('ROMs in Launcher  {:6d}'.format(len(roms)))
        report_head_sl = []
        report_head_sl.append('***** ROM scanner summary *****')
        report_head_sl.append('Removed dead ROMs {:6d}'.format(num_removed_roms))
        report_head_sl.append('Files checked     {:6d}'.format(num_files_checked))
        report_head_sl.append('New added ROMs    {:6d}'.format(num_new_roms))
        report_head_sl.append('ROMs in Launcher  {:6d}'.format(len(roms)))
        report_head_sl.append('')

        if not roms:
            report_head_sl.append('WARNING The ROM scanner found no ROMs. Launcher is empty.')
            report_head_sl.append('')
            r_all_sl = []
            r_all_sl.extend(report_head_sl)
            r_all_sl.extend(report_slist)
            utils_write_slist_to_file(launcher_report_FN.getPath(), r_all_sl)
            kodi_dialog_OK('The scanner found no ROMs! Make sure launcher directory and file '
                'extensions are correct.')
            return

        # --- If we have a No-Intro XML then audit roms after scanning ----------------------------
        if launcher['audit_state'] == AUDIT_STATE_ON:
            log_info('No-Intro/Redump is ON. Starting ROM audit...')
            nointro_xml_FN = self._roms_set_NoIntro_DAT(launcher)
            # Error printed with a OK dialog inside this function.
            if nointro_xml_FN is not None:
                log_debug('Using DAT "{}"'.format(nointro_xml_FN.getPath()))
                if self._roms_update_NoIntro_status(launcher, roms, nointro_xml_FN):
                    fs_write_ROMs_JSON(g_PATHS.ROMS_DIR, self.launchers[launcherID], roms)
                    kodi_notify('ROM scanner and audit finished. '
                        'Have {} / Miss {} / Unknown {}'.format(self.audit_have, self.audit_miss, self.audit_unknown))
                    # _roms_update_NoIntro_status() already prints and audit report on Kodi log
                    report_head_sl.append('***** No-Intro/Redump audit finished. Report *****')
                    report_head_sl.append('Have ROMs    {:6d}'.format(self.audit_have))
                    report_head_sl.append('Miss ROMs    {:6d}'.format(self.audit_miss))
                    report_head_sl.append('Unknown ROMs {:6d}'.format(self.audit_unknown))
                    report_head_sl.append('Total ROMs   {:6d}'.format(self.audit_total))
                    report_head_sl.append('Parent ROMs  {:6d}'.format(self.audit_parents))
                    report_head_sl.append('Clone ROMs   {:6d}'.format(self.audit_clones))
                else:
                    kodi_notify_warn('Error auditing ROMs')
            else:
                log_error('Error finding No-Intro/Redump DAT file.')
                log_error('Audit not done.')
                kodi_notify_warn('Error finding No-Intro/Redump DAT file')
        else:
            log_info('ROM Audit state is OFF. Do not audit ROMs.')
            report_head_sl.append('ROM Audit state is OFF. Do not audit ROMs.')
            if num_new_roms == 0:
                kodi_notify('Added no new ROMs. Launcher has {} ROMs'.format(len(roms)))
            else:
                kodi_notify('Added {} new ROMs'.format(num_new_roms))
        report_head_sl.append('')

        # --- Close ROM scanner report file ---
        r_all_sl = []
        r_all_sl.extend(report_head_sl)
        r_all_sl.extend(report_slist)
        utils_write_slist_to_file(launcher_report_FN.getPath(), r_all_sl)

        # --- Save ROMs XML file ---
        # Also save categories/launchers to update timestamp.
        # Update Launcher timestamp to update VLaunchers and reports.
        self.launchers[launcherID]['num_roms'] = len(roms)
        self.launchers[launcherID]['timestamp_launcher'] = time.time()
        pdialog.startProgress('Saving ROM JSON database ...', 100)
        fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        pdialog.updateProgress(25)
        fs_write_ROMs_JSON(g_PATHS.ROMS_DIR, launcher, roms)
        pdialog.endProgress()
        kodi_refresh_container()

    # Edit category/launcher/rom asset.
    #
    # When editing ROMs optional parameter launcher_dic is required.
    # Caller is responsible for saving the Categories/Launchers/ROMs.
    # If image is changed container should be updated so the user sees new image instantly.
    # object_dic is edited by assigment.
    # A ROM in Favourites has categoryID = VCATEGORY_FAVOURITES_ID.
    # A ROM in a collection categoryID = VCATEGORY_COLLECTIONS_ID.
    #
    # --- Returns ---
    # True   Changes made. Categories/Launchers/ROMs must be saved and container updated
    # False  No changes were made. No necessary to refresh container
    def _gui_edit_asset(self, object_kind, asset_ID, object_dic, categoryID = '', launcherID = ''):
        # --- Get asset object information ---
        AInfo = assets_get_info_scheme(asset_ID)
        if object_kind == KIND_CATEGORY:
            # --- Grab asset information for editing ---
            object_name = 'Category'
            asset_dir_FN = FileName(self.settings['categories_asset_dir'])
            asset_path_noext_FN = assets_get_path_noext_SUFIX(AInfo, asset_dir_FN,
                object_dic['m_name'], object_dic['id'])
            log_info('_gui_edit_asset() Editing Category "{}"'.format(AInfo.name))
            log_info('_gui_edit_asset() ID {}'.format(object_dic['id']))
            if not asset_dir_FN.isdir():
                kodi_dialog_OK('Directory to store Category artwork not configured or not found. '
                    'Configure it before you can edit artwork.')
                return False

        elif object_kind == KIND_COLLECTION:
            # --- Grab asset information for editing ---
            object_name = 'Collection'
            asset_dir_FN = FileName(self.settings['collections_asset_dir'])
            asset_path_noext_FN = assets_get_path_noext_SUFIX(AInfo, asset_dir_FN,
                object_dic['m_name'], object_dic['id'])
            log_info('_gui_edit_asset() Editing Collection "{}"'.format(AInfo.name))
            log_info('_gui_edit_asset() ID {}'.format(object_dic['id']))
            if not asset_dir_FN.isdir():
                kodi_dialog_OK('Directory to store Collection artwork not configured or not found. '
                    'Configure it before you can edit artwork.')
                return False

        elif object_kind == KIND_LAUNCHER:
            # --- Grab asset information for editing ---
            object_name = 'Launcher'
            asset_dir_FN = FileName(self.settings['launchers_asset_dir'])
            asset_path_noext_FN = assets_get_path_noext_SUFIX(AInfo, asset_dir_FN,
                object_dic['m_name'], object_dic['id'])
            log_info('_gui_edit_asset() Editing Launcher "{}"'.format(AInfo.name))
            log_info('_gui_edit_asset() ID {}'.format(object_dic['id']))
            if not asset_dir_FN.isdir():
                kodi_dialog_OK('Directory to store Launcher artwork not configured or not found. '
                    'Configure it before you can edit artwork.')
                return False

        elif object_kind == KIND_ROM:
            # --- Grab asset information for editing ---
            object_name = 'ROM'
            ROM_FN = FileName(object_dic['filename'])
            if object_dic['disks']:
                ROM_hash_FN = FileName(ROM_FN.getDir()).pjoin(object_dic['disks'][0])
            else:
                ROM_hash_FN = ROM_FN
            if categoryID == VCATEGORY_FAVOURITES_ID:
                log_info('_gui_edit_asset() ROM is in Favourites')
                platform = object_dic['platform']
                asset_dir_FN = FileName(self.settings['favourites_asset_dir'])
                asset_path_noext_FN = assets_get_path_noext_SUFIX(AInfo, asset_dir_FN,
                    ROM_FN.getBaseNoExt(), object_dic['id'])
            elif categoryID == VCATEGORY_COLLECTIONS_ID:
                log_info('_gui_edit_asset() ROM is in Collection')
                platform = object_dic['platform']
                asset_dir_FN = FileName(self.settings['collections_asset_dir'])
                new_asset_basename = assets_get_collection_asset_basename(AInfo,
                    ROM_FN.getBaseNoExt(), platform, '.png')
                new_asset_basename_FN = FileName(new_asset_basename)
                asset_path_noext_FN = asset_dir_FN.pjoin(new_asset_basename_FN.getBaseNoExt())
            else:
                log_info('_gui_edit_asset() ROM is in Launcher id {}'.format(launcherID))
                launcher = self.launchers[launcherID]
                platform = launcher['platform']
                asset_dir_FN = FileName(launcher[AInfo.path_key])
                asset_path_noext_FN = assets_get_path_noext_DIR(AInfo, asset_dir_FN, ROM_FN)
            log_info('_gui_edit_asset() Editing ROM {}'.format(AInfo.name))
            log_info('_gui_edit_asset() ROM ID {}'.format(object_dic['id']))
            log_debug('_gui_edit_asset() platform "{}"'.format(platform))

            # --- Do not edit asset if asset directory not configured ---
            if not asset_dir_FN.isdir():
                kodi_dialog_OK('Directory to store {} not configured or not found. '.format(AInfo.name) + \
                    'Configure it before you can edit artwork.')
                return False

        else:
            log_error('_gui_edit_asset() Unknown object_kind = {}'.format(object_kind))
            kodi_notify_warn("Unknown object_kind '{}'".format(object_kind))
            return False
        # Debug info
        log_debug('_gui_edit_asset() asset_dir_FN "{}"'.format(asset_dir_FN.getOriginalPath()))
        log_debug('_gui_edit_asset() asset_path_noext_FN "{}"'.format(asset_path_noext_FN.getOriginalPath()))

        # --- Only enable scraper if support the asset ---
        # Scrapers only loaded if editing a ROM.
        if object_kind == KIND_ROM:
            g_scrap_factory = ScraperFactory(g_PATHS, self.settings)
            scraper_menu_list = g_scrap_factory.get_asset_scraper_menu_list(asset_ID)
        else:
            scraper_menu_list = []

        # --- Show image editing options ---
        # Scrapers only supported for ROMs (for the moment)
        common_menu_list = [
            'Select local {}'.format(AInfo.kind_str),
            'Import local {} (copy and rename)'.format(AInfo.kind_str),
            'Unset artwork/asset',
        ]
        sDialog = KodiSelectDialog('Change {} {}'.format(AInfo.name, AInfo.kind_str))
        sDialog.setRows(common_menu_list + scraper_menu_list)
        mindex = sDialog.executeDialog()
        if mindex is None: return False

        # --- Link to a local image ---
        if mindex == 0:
            log_debug('_gui_edit_asset() Linking local image...')
            image_dir = FileName(object_dic[AInfo.key]).getDir() if object_dic[AInfo.key] else ''
            log_debug('_gui_edit_asset() Initial path "{}"'.format(image_dir))
            if asset_ID == ASSET_MANUAL_ID or asset_ID == ASSET_TRAILER_ID:
                image_file = kodi_dialog_get_file('Select {} {}'.format(AInfo.name, AInfo.kind_str),
                    AInfo.exts_dialog, image_dir)
            else:
                image_file = kodi_dialog_get_image('Select {} {}'.format(AInfo.name, AInfo.kind_str),
                    AInfo.exts_dialog, image_dir)
            if not image_file: return False
            image_file_path = FileName(image_file)
            if not image_file or not image_file_path.exists(): return False

            # --- Update object by assigment. XML/JSON will be save by parent ---
            log_debug('_gui_edit_asset() AInfo.key "{}"'.format(AInfo.key))
            object_dic[AInfo.key] = image_file_path.getOriginalPath()
            kodi_notify('{} {} has been updated'.format(object_name, AInfo.name))
            log_info('_gui_edit_asset() Linked {} {} "{}"'.format(object_name,
                AInfo.name, image_file_path.getOriginalPath()))

            # Update Kodi image cache.
            # TODO Only update mtime for local files and not for Kodi VFS files.
            utils_update_file_mtime(image_file_path.getPath())

        # --- Import an image ---
        # Copy and rename a local image into asset directory.
        elif mindex == 1:
            log_debug('_gui_edit_asset() Importing image...')
            # If assets exists start file dialog from current asset directory
            image_dir = ''
            if object_dic[AInfo.key]: image_dir = FileName(object_dic[AInfo.key]).getDir()
            log_debug('_gui_edit_asset() Initial path "{}"'.format(image_dir))
            t = 'Select {} image'.format(AInfo.name)
            image_path_str = kodi_dialog_get_image(t, AInfo.exts_dialog, image_dir)
            image_FN = FileName(image_path_str)
            if not image_FN.exists(): return False

            # Determine image extension and dest filename. Check for errors.
            dest_image_FN = asset_path_noext_FN.pappend(image_FN.getExt())
            log_debug('_gui_edit_asset() image_FN      "{}"'.format(image_FN.getOriginalPath()))
            log_debug('_gui_edit_asset() img_ext       "{}"'.format(image_FN.getExt()))
            log_debug('_gui_edit_asset() dest_image_FN "{}"'.format(dest_image_FN.getOriginalPath()))
            if image_FN.getPath() == dest_image_FN.getPath():
                log_info('_gui_edit_asset() image_FN and dest_image_FN are the same. Returning.')
                kodi_notify_warn('image_FN and dest_image_FN are the same. Returning')
                return False

            try:
                utils_copy_file(image_FN.getPath(), dest_image_FN.getPath())
            except OSError:
                log_error('_gui_edit_asset() OSError exception copying image')
                kodi_notify_warn('OSError exception copying image')
                return False
            except IOError:
                log_error('_gui_edit_asset() IOError exception copying image')
                kodi_notify_warn('IOError exception copying image')
                return False

            # Update object by assigment. XML will be save by parent.
            # Always store original/raw paths in database.
            object_dic[AInfo.key] = dest_image_FN.getOriginalPath()
            kodi_notify('{} {} has been updated'.format(object_name, AInfo.name))
            log_info('_gui_edit_asset() Copied file  "{}"'.format(image_FN.getOriginalPath()))
            log_info('_gui_edit_asset() Into         "{}"'.format(dest_image_FN.getOriginalPath()))
            log_info('_gui_edit_asset() Selected {} {} "{}"'.format(object_name,
                AInfo.name, dest_image_FN.getOriginalPath()))

            # Update Kodi image cache.
            utils_update_file_mtime(dest_image_FN.getPath())

        # --- Unset asset ---
        elif mindex == 2:
            log_debug('_gui_edit_asset() Unsetting asset...')
            object_dic[AInfo.key] = ''
            kodi_notify('{} {} has been unset'.format(object_name, AInfo.name))
            log_info('_gui_edit_asset() Unset {} {}'.format(object_name, AInfo.name))

        # --- Manual scrape and choose from a list of images ---
        elif mindex >= 3:
            log_debug('_gui_edit_asset() Scraping image...')

            # Create ScrapeFactory object.
            scraper_index = mindex - len(common_menu_list)
            log_debug('_gui_edit_asset() Scraper index {}'.format(scraper_index))
            scraper_ID = g_scrap_factory.get_asset_scraper_ID_from_menu_idx(scraper_index)

            # Scrape!
            data_dic = {
                'ROM_FN' : ROM_FN,
                'ROM_hash_FN' : ROM_hash_FN,
                'platform' : platform,
                # These vars are to compute asset_path_noext_FN
                'categoryID' : categoryID,
                'launcherID' : launcherID,
                'settings' : self.settings,
                'launchers' : self.launchers,
            }
            # If this function return False there were no changes so no need to save the
            # ROMs JSON on the caller function.
            # Scraper disk caches are flushed (written to disk) even if there is a message
            # to be printed here. A message here could be that no images were found, network
            # error when downloading image, etc., however the caches (internal, etc.) may have
            # valid data that needs to be saved.
            st_dic = kodi_new_status_dic()
            scraper_strategy = g_scrap_factory.create_CM_asset(scraper_ID)
            scraper_strategy.scrap_CM_asset(object_dic, asset_ID, data_dic, st_dic)
            # Flush caches
            pDialog = KodiProgressDialog()
            pDialog.startProgress('Flushing scraper disk caches...')
            g_scrap_factory.destroy_CM()
            pDialog.endProgress()
            # Display notification or error. If error return and do not save ROMs database.
            if kodi_display_status_message(st_dic): return False

        # If we reach this point, changes were made.
        # Categories/Launchers/ROMs must be saved, container must be refreshed.
        return True

    # Creates default categories data struct.
    # CAREFUL deletes current categories!
    def _cat_create_default(self):
        # The key in the categories dictionary is an MD5 hash generate with current time plus some
        # random number. This will make it unique and different for every category created.
        category = fs_new_category()
        category_key = misc_generate_random_SID()
        category['id'] = category_key
        category['m_name']  = 'Emulators'
        category['m_genre'] = 'Emulators'
        category['m_plot']  = 'Initial AEL category.'
        self.categories = {}
        self.launchers = {}
        self.categories[category_key] = category

    # Checks if a category is empty (no launchers defined)
    # Returns True if the category is empty. Returns False if non-empty.
    def _cat_is_empty(self, categoryID):
        for launcherID in self.launchers:
            if self.launchers[launcherID]['categoryID'] == categoryID:
                return False
        return True

    def _command_exec_utils_import_launchers(self):
        # If enableMultiple = True this function always returns a list of strings in UTF-8
        file_list = kodi_dialog_get_file_multiple('Select XML category/launcher configuration file', '.xml')
        # Process file by file
        for xml_file in file_list:
            log_debug('_command_exec_utils_import_launchers() Importing "{}"'.format(xml_file))
            import_FN = FileName(xml_file)
            if not import_FN.exists(): continue
            # This function edits self.categories, self.launchers dictionaries
            autoconfig_import_launchers(g_PATHS.CATEGORIES_FILE_PATH, g_PATHS.ROMS_DIR,
                self.categories, self.launchers, import_FN)
        # Save Categories/Launchers, update timestamp and notify user.
        fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        kodi_refresh_container()
        kodi_notify('Finished importing Categories/Launchers')

    # Export AEL launcher configuration.
    def _command_exec_utils_export_launchers(self):
        log_debug('_command_exec_utils_export_launchers() Exporting Category/Launcher XML configuration')

        # --- Ask path to export XML configuration ---
        dir_path = kodi_dialog_get_directory('Select XML export directory')
        if not dir_path: return

        # --- If XML exists then warn user about overwriting it ---
        export_FN = FileName(dir_path).pjoin('AEL_configuration.xml')
        if export_FN.exists():
            ret = kodi_dialog_yesno('AEL_configuration.xml found in the selected directory. Overwrite?')
            if not ret:
                kodi_notify_warn('Category/Launcher XML exporting cancelled')
                return

        # --- Export stuff ---
        try:
            autoconfig_export_all(self.categories, self.launchers, export_FN)
        except KodiAddonError as ex:
            kodi_notify_warn('{}'.format(ex))
        else:
            kodi_notify('Exported AEL Categories and Launchers XML configuration')

    # Checks all databases and updates to newer version if possible
    def _command_exec_utils_check_database(self):
        log_debug('_command_exec_utils_check_database() Beginning...')
        pDialog = KodiProgressDialog()

        # Open Categories/Launchers XML. XML should be updated automatically on load.
        pDialog.startProgress('Checking Categories/Launchers...')
        self.categories = {}
        self.launchers = {}
        self.update_timestamp = fs_load_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        for category_id in self.categories:
            category = self.categories[category_id]
            # Fix s_thumb -> s_icon renaming
            if category['default_icon'] == 's_thumb':      category['default_icon'] = 's_icon'
            if category['default_fanart'] == 's_thumb':    category['default_fanart'] = 's_icon'
            if category['default_banner'] == 's_thumb':    category['default_banner'] = 's_icon'
            if category['default_poster'] == 's_thumb':    category['default_poster'] = 's_icon'
            if category['default_clearlogo'] == 's_thumb': category['default_clearlogo'] = 's_icon'

            # Fix s_flyer -> s_poster renaming
            if category['default_icon'] == 's_flyer':      category['default_icon'] = 's_poster'
            if category['default_fanart'] == 's_flyer':    category['default_fanart'] = 's_poster'
            if category['default_banner'] == 's_flyer':    category['default_banner'] = 's_poster'
            if category['default_poster'] == 's_flyer':    category['default_poster'] = 's_poster'
            if category['default_clearlogo'] == 's_flyer': category['default_clearlogo'] = 's_poster'

        # Traverse and fix Launchers.
        for launcher_id in self.launchers:
            launcher = self.launchers[launcher_id]
            # Fix s_thumb -> s_icon renaming
            if launcher['default_icon'] == 's_thumb':       launcher['default_icon'] = 's_icon'
            if launcher['default_fanart'] == 's_thumb':     launcher['default_fanart'] = 's_icon'
            if launcher['default_banner'] == 's_thumb':     launcher['default_banner'] = 's_icon'
            if launcher['default_poster'] == 's_thumb':     launcher['default_poster'] = 's_icon'
            if launcher['default_clearlogo'] == 's_thumb':  launcher['default_clearlogo'] = 's_icon'
            if launcher['default_controller'] == 's_thumb': launcher['default_controller'] = 's_icon'
            # Fix s_flyer -> s_poster renaming
            if launcher['default_icon'] == 's_flyer':       launcher['default_icon'] = 's_poster'
            if launcher['default_fanart'] == 's_flyer':     launcher['default_fanart'] = 's_poster'
            if launcher['default_banner'] == 's_flyer':     launcher['default_banner'] = 's_poster'
            if launcher['default_poster'] == 's_flyer':     launcher['default_poster'] = 's_poster'
            if launcher['default_clearlogo'] == 's_flyer':  launcher['default_clearlogo'] = 's_poster'
            if launcher['default_controller'] == 's_flyer': launcher['default_controller'] = 's_poster'
        # Save categories.xml to update timestamp.
        fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        pDialog.endProgress()

        # Traverse all launchers. Load ROMs and check every ROMs.
        pDialog.startProgress('Checking Launcher ROMs...', len(self.launchers))
        for launcher_id in self.launchers:
            pDialog.updateProgressInc()
            s = '_command_edit_rom() Checking Launcher "{}"'
            log_debug(s.format(self.launchers[launcher_id]['m_name']))
            # Load and fix standard ROM database.
            roms = fs_load_ROMs_JSON(g_PATHS.ROMS_DIR, self.launchers[launcher_id])
            for rom_id in roms: self._misc_fix_rom_object(roms[rom_id])
            fs_write_ROMs_JSON(g_PATHS.ROMS_DIR, self.launchers[launcher_id], roms)

            # If exists, load and fix Parent ROM database.
            parents_FN = g_PATHS.ROMS_DIR.pjoin(self.launchers[launcher_id]['roms_base_noext'] + '_parents.json')
            if parents_FN.exists():
                roms = utils_load_JSON_file(parents_FN.getPath())
                for rom_id in roms: self._misc_fix_rom_object(roms[rom_id])
                utils_write_JSON_file(parents_FN.getPath(), roms)

            # This updates timestamps and forces regeneration of Virtual Launchers.
            self.launchers[launcher_id]['timestamp_launcher'] = time.time()
        # Save categories.xml because launcher timestamps changed.
        fs_write_catfile(g_PATHS.CATEGORIES_FILE_PATH, self.categories, self.launchers)
        pDialog.endProgress()

        # Load Favourite ROMs and update JSON
        roms_fav = fs_load_Favourites_JSON(g_PATHS.FAV_JSON_FILE_PATH)
        pDialog.startProgress('Checking Favourite ROMs...', len(roms_fav))
        for rom_id in roms_fav:
            pDialog.updateProgressInc()
            rom = roms_fav[rom_id]
            self._misc_fix_Favourite_rom_object(rom)
        fs_write_Favourites_JSON(g_PATHS.FAV_JSON_FILE_PATH, roms_fav)
        pDialog.endProgress()

        # Traverse every ROM Collection database and check/update Favourite ROMs.
        COL = fs_load_Collection_index_XML(g_PATHS.COLLECTIONS_FILE_PATH)
        pDialog.startProgress('Checking Collection ROMs...', len(COL['collections']))
        for collection_id in COL['collections']:
            pDialog.updateProgressInc()

            # Fix collection
            collection = COL['collections'][collection_id]
            if 'default_thumb' in collection:
                collection['default_icon'] = collection['default_thumb']
                collection.pop('default_thumb')
            if 's_thumb' in collection:
                collection['s_icon'] = collection['s_thumb']
                collection.pop('s_thumb')
            if 's_flyer' in collection:
                collection['s_poster'] = collection['s_flyer']
                collection.pop('s_flyer')
            # Fix s_thumb -> s_icon renaming
            if collection['default_icon'] == 's_thumb':      collection['default_icon'] = 's_icon'
            if collection['default_fanart'] == 's_thumb':    collection['default_fanart'] = 's_icon'
            if collection['default_banner'] == 's_thumb':    collection['default_banner'] = 's_icon'
            if collection['default_poster'] == 's_thumb':    collection['default_poster'] = 's_icon'
            if collection['default_clearlogo'] == 's_thumb': collection['default_clearlogo'] = 's_icon'
            # Fix s_flyer -> s_poster renaming
            if collection['default_icon'] == 's_flyer':      collection['default_icon'] = 's_poster'
            if collection['default_fanart'] == 's_flyer':    collection['default_fanart'] = 's_poster'
            if collection['default_banner'] == 's_flyer':    collection['default_banner'] = 's_poster'
            if collection['default_poster'] == 's_flyer':    collection['default_poster'] = 's_poster'
            if collection['default_clearlogo'] == 's_flyer': collection['default_clearlogo'] = 's_poster'

            # Fix collection ROMs
            roms_json_file = g_PATHS.COLLECTIONS_DIR.pjoin(collection['roms_base_noext'] + '.json')
            collection_rom_list = fs_load_Collection_ROMs_JSON(roms_json_file)
            for rom in collection_rom_list: self._misc_fix_Favourite_rom_object(rom)
            fs_write_Collection_ROMs_JSON(roms_json_file, collection_rom_list)
        fs_write_Collection_index_XML(g_PATHS.COLLECTIONS_FILE_PATH, COL['collections'])
        pDialog.endProgress()

        # Load Most Played ROMs and check/update.
        pDialog.startProgress('Checking Most Played ROMs...')
        most_played_roms = fs_load_Favourites_JSON(g_PATHS.MOST_PLAYED_FILE_PATH)
        for rom_id in most_played_roms:
            rom = most_played_roms[rom_id]
            self._misc_fix_Favourite_rom_object(rom)
        fs_write_Favourites_JSON(g_PATHS.MOST_PLAYED_FILE_PATH, most_played_roms)
        pDialog.endProgress()

        # Load Recently Played ROMs and check/update.
        pDialog.startProgress('Checking Recently Played ROMs...')
        recent_roms_list = fs_load_Collection_ROMs_JSON(g_PATHS.RECENT_PLAYED_FILE_PATH)
        for rom in recent_roms_list: self._misc_fix_Favourite_rom_object(rom)
        fs_write_Collection_ROMs_JSON(g_PATHS.RECENT_PLAYED_FILE_PATH, recent_roms_list)
        pDialog.endProgress()

        # So long and thanks for all the fish.
        kodi_notify('All databases checked')
        log_debug('_command_check_database() Exiting')

    # ROM dictionary is edited by Python passing by assigment
    def _misc_fix_rom_object(self, rom):
        # Add new fields if not present
        if 'm_nplayers'    not in rom: rom['m_nplayers']    = ''
        if 'm_esrb'        not in rom: rom['m_esrb']        = ESRB_PENDING
        if 'disks'         not in rom: rom['disks']         = []
        if 'pclone_status' not in rom: rom['pclone_status'] = PCLONE_STATUS_NONE
        if 'cloneof'       not in rom: rom['cloneof']       = ''
        if 's_3dbox'       not in rom: rom['s_3dbox']       = ''
        if 'i_extra_ROM'   not in rom: rom['i_extra_ROM']   = False
        # Delete unwanted/obsolete stuff
        if 'nointro_isClone' in rom: rom.pop('nointro_isClone')
        # DB field renamings
        if 'm_studio' in rom:
            rom['m_developer'] = rom['m_studio']
            rom.pop('m_studio')

    def _misc_fix_Favourite_rom_object(self, rom):
        # Fix standard ROM fields
        self._misc_fix_rom_object(rom)

        # Favourite ROMs additional stuff
        if 'args_extra' not in rom: rom['args_extra'] = []
        if 'non_blocking' not in rom: rom['non_blocking'] = False
        if 'roms_default_thumb' in rom:
            rom['roms_default_icon'] = rom['roms_default_thumb']
            rom.pop('roms_default_thumb')
        if 'minimize' in rom:
            rom['toggle_window'] = rom['minimize']
            rom.pop('minimize')

    def _command_exec_utils_check_launchers(self):
        log_info('_command_exec_utils_check_launchers() Checking all Launchers configuration ...')

        main_slist = []
        main_slist.append('Number of launchers: {}\n'.format(len(self.launchers)))
        for launcher_id in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
            launcher = self.launchers[launcher_id]
            l_str = []
            main_slist.append('[COLOR orange]Launcher "{}"[/COLOR]'.format(launcher['m_name']))

            # Check that platform is on AEL official platform list
            platform = launcher['platform']
            if platform not in platform_long_to_index_dic:
                l_str.append('Unrecognised platform "{}"'.format(platform))

            # Check that category exists
            categoryID = launcher['categoryID']
            if categoryID != VCATEGORY_ADDONROOT_ID and categoryID not in self.categories:
                l_str.append('Category not found (unlinked launcher)')

            # Check that application exists
            app_FN = FileName(launcher['application'])
            if not app_FN.exists():
                l_str.append('Application "{}" not found'.format(app_FN.getPath()))

            # Check that rompath exists if rompath is not empty
            # Empty rompath means standalone launcher
            rompath = launcher['rompath']
            rompath_FN = FileName(rompath)
            if rompath and not rompath_FN.exists():
                l_str.append('ROM path "{}" not found'.format(rompath_FN.getPath()))

            # Check that DAT file exists if not empty
            audit_custom_dat_file = launcher['audit_custom_dat_file']
            audit_custom_dat_FN = FileName(audit_custom_dat_file)
            if audit_custom_dat_file and not audit_custom_dat_FN.exists():
                l_str.append('Custom DAT file "{}" not found'.format(audit_custom_dat_FN.getPath()))

            # audit_auto_dat_file = launcher['audit_auto_dat_file']
            # audit_auto_dat_FN = FileName(audit_auto_dat_file)
            # if audit_auto_dat_file and not audit_auto_dat_FN.exists():
            #     l_str.append('Custom DAT file "{}" not found\n'.format(audit_auto_dat_FN.getPath()))

            # Test that artwork files exist if not empty (s_* fields)
            self._aux_check_for_file(l_str, 's_icon', launcher)
            self._aux_check_for_file(l_str, 's_fanart', launcher)
            self._aux_check_for_file(l_str, 's_banner', launcher)
            self._aux_check_for_file(l_str, 's_poster', launcher)
            self._aux_check_for_file(l_str, 's_clearlogo', launcher)
            self._aux_check_for_file(l_str, 's_controller', launcher)
            self._aux_check_for_file(l_str, 's_trailer', launcher)

            # Test that ROM_asset_path exists if not empty
            ROM_asset_path = launcher['ROM_asset_path']
            ROM_asset_path_FN = FileName(ROM_asset_path)
            if ROM_asset_path and not ROM_asset_path_FN.exists():
                l_str.append('ROM_asset_path "{}" not found'.format(ROM_asset_path_FN.getPath()))

            # Test that ROM asset paths exist if not empty (path_* fields)
            self._aux_check_for_file(l_str, 'path_3dbox', launcher)
            self._aux_check_for_file(l_str, 'path_title', launcher)
            self._aux_check_for_file(l_str, 'path_snap', launcher)
            self._aux_check_for_file(l_str, 'path_boxfront', launcher)
            self._aux_check_for_file(l_str, 'path_boxback', launcher)
            self._aux_check_for_file(l_str, 'path_cartridge', launcher)
            self._aux_check_for_file(l_str, 'path_fanart', launcher)
            self._aux_check_for_file(l_str, 'path_banner', launcher)
            self._aux_check_for_file(l_str, 'path_clearlogo', launcher)
            self._aux_check_for_file(l_str, 'path_flyer', launcher)
            self._aux_check_for_file(l_str, 'path_map', launcher)
            self._aux_check_for_file(l_str, 'path_manual', launcher)
            self._aux_check_for_file(l_str, 'path_trailer', launcher)

            # Check for duplicate asset paths

            # If l_str is empty is because no problems were found.
            if l_str:
                main_slist.extend(l_str)
            else:
                main_slist.append('No problems found')
            main_slist.append('')

        # Stats report
        log_info('Writing report file "{}"'.format(g_PATHS.LAUNCHER_REPORT_FILE_PATH.getPath()))
        utils_write_slist_to_file(g_PATHS.LAUNCHER_REPORT_FILE_PATH.getPath(), main_slist)
        full_string = '\n'.join(main_slist)
        kodi_display_text_window_mono('Launchers report', full_string)

    def _aux_check_for_file(self, str_list, dic_key_name, launcher):
        path = launcher[dic_key_name]
        path_FN = FileName(path)
        if path and not path_FN.exists():
            problems_found = True
            str_list.append('{} "{}" not found'.format(dic_key_name, path_FN.getPath()))

    # For every ROM launcher scans the ROM path and check 1) if there are dead ROMs and 2) if
    # there are ROM files not in AEL database. If either 1) or 2) is true launcher must be
    # updated with the ROM scanner.
    def _command_exec_utils_check_launcher_sync_status(self):
        log_debug('_command_exec_utils_check_launcher_sync_status() Checking ROM Launcher sync status...')
        main_slist = []
        short_slist = [ ['left', 'left'] ]
        detailed_slist = []
        pdialog = KodiProgressDialog()
        d_msg = 'Checking ROM sync status'
        pdialog.startProgress(d_msg, len(self.launchers))
        for launcher_id in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
            pdialog.updateProgressInc(d_msg)
            launcher = self.launchers[launcher_id]
            # Skip non-ROM launchers.
            if not launcher['rompath']: continue
            log_debug('Checking ROM Launcher "{}"'.format(launcher['m_name']))
            detailed_slist.append('[COLOR orange]Launcher "{}"[/COLOR]'.format(launcher['m_name']))
            # Load ROMs.
            pdialog.updateMessage('{}\n{}'.format(d_msg, 'Loading ROMs...'))
            roms = fs_load_ROMs_JSON(g_PATHS.ROMS_DIR, launcher)
            num_roms = len(roms)
            R_str = 'ROM' if num_roms == 1 else 'ROMs'
            log_debug('Launcher has {} DB {}'.format(num_roms, R_str))
            detailed_slist.append('Launcher has {} DB {}'.format(num_roms, R_str))
            # For now skip multidisc ROMs until multidisc support is fixed. I think for
            # every ROM in the multidisc set there should be a normal ROM not displayed
            # in listings, and then the special multidisc ROM that points to the ROMs
            # in the set.
            has_multidisc_ROMs = False
            for rom_id in roms:
                if roms[rom_id]['disks']:
                    has_multidisc_ROMs = True
                    break
            if has_multidisc_ROMs:
                log_debug('Launcher has multidisc ROMs. Skipping launcher')
                detailed_slist.append('Launcher has multidisc ROMs.')
                detailed_slist.append('[COLOR yellow]Skipping launcher[/COLOR]')
                continue
            # Get real ROMs (remove Missing, Multidisc, etc., ROMs).
            # Remove ROM Audit Missing ROMs (fake ROMs).
            real_roms = {}
            for rom_id in roms:
                if roms[rom_id]['nointro_status'] == AUDIT_STATUS_MISS: continue
                real_roms[rom_id] = roms[rom_id]
            num_real_roms = len(real_roms)
            R_str = 'ROM' if num_real_roms == 1 else 'ROMs'
            log_debug('Launcher has {} real {}'.format(num_real_roms, R_str))
            detailed_slist.append('Launcher has {} real {}'.format(num_real_roms, R_str))
            # If Launcher is empty there is nothing to do.
            if num_real_roms < 1:
                log_debug('Launcher is empty')
                detailed_slist.append('Launcher is empty')
                detailed_slist.append('[COLOR yellow]Skipping launcher[/COLOR]')
                continue
            # Make a dictionary for fast indexing.
            romfiles_dic = {real_roms[rom_id]['filename'] : rom_id for rom_id in real_roms}

            # Scan files in rompath directory.
            pdialog.updateMessage('{}\n{}'.format(d_msg, 'Scanning files in ROM paths...'))
            launcher_path = FileName(launcher['rompath'])
            log_debug('Scanning files in {}'.format(launcher_path.getPath()))
            if self.settings['scan_recursive']:
                log_debug('Recursive scan activated')
                files = launcher_path.recursiveScanFilesInPath('*.*')
            else:
                log_debug('Recursive scan not activated')
                files = launcher_path.scanFilesInPath('*.*')
            num_files = len(files)
            f_str = 'file' if num_files == 1 else 'files'
            log_debug('File scanner found {} files'.format(num_files, f_str))
            detailed_slist.append('File scanner found {} files'.format(num_files, f_str))

            # Check for dead ROMs (ROMs in AEL DB not on disk).
            pdialog.updateMessage('{}\n{}'.format(d_msg, 'Checking dead ROMs...'))
            log_debug('Checking for dead ROMs...')
            num_dead_roms = 0
            for rom_id in real_roms:
                fileName = FileName(real_roms[rom_id]['filename'])
                if not fileName.exists(): num_dead_roms += 1
            if num_dead_roms > 0:
                R_str = 'ROM' if num_dead_roms == 1 else 'ROMs'
                detailed_slist.append('Found {} dead {}'.format(num_dead_roms, R_str))
            else:
                detailed_slist.append('No dead ROMs found')

            # Check for unsynced ROMs (ROMS on disk not in AEL DB).
            pdialog.updateMessage('{}\n{}'.format(d_msg, 'Checking unsynced ROMs...'))
            log_debug('Checking for unsynced ROMs...')
            num_unsynced_roms = 0
            for f_path in sorted(files):
                ROM_FN = FileName(f_path)
                processROM = False
                for ext in launcher['romext'].split("|"):
                    if ROM_FN.getExt() == '.' + ext: processROM = True
                if not processROM: continue
                # Ignore BIOS ROMs, like the ROM Scanner does.
                if self.settings['scan_ignore_bios']:
                    BIOS_re = re.findall('\[BIOS\]', ROM_FN.getBase())
                    if len(BIOS_re) > 0:
                        log_debug('BIOS detected. Skipping ROM "{}"'.format(ROM_FN.getBase()))
                        continue
                ROM_in_launcher_DB = True if f_path in romfiles_dic else False
                if not ROM_in_launcher_DB: num_unsynced_roms += 1
            if num_unsynced_roms > 0:
                R_str = 'ROM' if num_unsynced_roms == 1 else 'ROMs'
                detailed_slist.append('Found {} unsynced {}'.format(num_unsynced_roms, R_str))
            else:
                detailed_slist.append('No unsynced ROMs found')
            update_launcher_flag = True if num_dead_roms > 0 or num_unsynced_roms > 0 else False
            if update_launcher_flag:
                short_slist.append([launcher['m_name'], '[COLOR red]Update launcher[/COLOR]'])
                detailed_slist.append('[COLOR red]Launcher should be updated[/COLOR]')
            else:
                short_slist.append([launcher['m_name'], '[COLOR green]Launcher OK[/COLOR]'])
                detailed_slist.append('[COLOR green]Launcher OK[/COLOR]')
            detailed_slist.append('')
        pdialog.endProgress()

        # Generate, save and display report.
        log_info('Writing report file "{}"'.format(g_PATHS.ROM_SYNC_REPORT_FILE_PATH.getPath()))
        pdialog.startProgress('Saving report')
        main_slist.append('*** Summary ***')
        main_slist.append('There are {} ROM launchers.'.format(len(self.launchers)))
        main_slist.append('')
        main_slist.extend(text_render_table_NO_HEADER(short_slist, trim_Kodi_colours = True))
        main_slist.append('')
        main_slist.append('*** Detailed report ***')
        main_slist.extend(detailed_slist)
        utils_write_slist_to_file(g_PATHS.ROM_SYNC_REPORT_FILE_PATH.getPath(), main_slist)
        pdialog.endProgress()
        full_string = '\n'.join(main_slist)
        kodi_display_text_window_mono('ROM sync status report', full_string)

    def _command_exec_utils_check_artwork_integrity(self):
        kodi_dialog_OK('EXECUTE_UTILS_CHECK_ARTWORK_INTEGRITY not implemented yet.')

    def _command_exec_utils_check_ROM_artwork_integrity(self):
        log_debug('_command_exec_utils_check_ROM_artwork_integrity() Beginning...')
        main_slist = []
        detailed_slist = []
        sum_table_slist = [
            ['left', 'right', 'right', 'right', 'right'],
            ['Launcher', 'ROMs', 'Images', 'Missing', 'Problematic'],
        ]
        pdialog = KodiProgressDialog()
        d_msg = 'Checking ROM artwork integrity...'
        pdialog.startProgress(d_msg, len(self.launchers))
        total_images = 0
        missing_images = 0
        processed_images = 0
        problematic_images = 0
        for launcher_id in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
            pdialog.updateProgressInc(d_msg)

            launcher = self.launchers[launcher_id]
            # Skip non-ROM launcher.
            if not launcher['rompath']: continue
            log_debug('Checking ROM Launcher "{}"...'.format(launcher['m_name']))
            detailed_slist.append(KC_ORANGE + 'Launcher "{}"'.format(launcher['m_name']) + KC_END)
            # Load ROMs.
            pdialog.updateMessage('{}\n{}'.format(d_msg, 'Loading ROMs'))
            roms = fs_load_ROMs_JSON(g_PATHS.ROMS_DIR, launcher)
            num_roms = len(roms)
            R_str = 'ROM' if num_roms == 1 else 'ROMs'
            log_debug('Launcher has {} DB {}'.format(num_roms, R_str))
            detailed_slist.append('Launcher has {} DB {}'.format(num_roms, R_str))
            # If Launcher is empty there is nothing to do.
            if num_roms < 1:
                log_debug('Launcher is empty')
                detailed_slist.append('Launcher is empty')
                detailed_slist.append(KC_YELLOW + 'Skipping launcher' + KC_END)
                continue

            # Traverse all ROMs in Launcher.
            # For every asset check the artwork file.
            # First check if the image has the correct extension.
            problems_detected = False
            launcher_images = 0
            launcher_missing_images = 0
            launcher_problematic_images = 0
            pdialog.updateMessage('{}\n{}'.format(d_msg, 'Checking image files'))
            for rom_id in roms:
                rom = roms[rom_id]
                # detailed_slist.append('\nProcessing ROM {}'.format(rom['filename']))
                for asset_id in ROM_ASSET_ID_LIST:
                    A = assets_get_info_scheme(asset_id)
                    asset_fname = rom[A.key]
                    # detailed_slist.append('\nProcessing asset {}'.format(A.name))
                    # Skip empty assets
                    if not asset_fname: continue
                    # Skip manuals and trailers
                    if asset_id == ASSET_MANUAL_ID: continue
                    if asset_id == ASSET_TRAILER_ID: continue
                    launcher_images += 1
                    total_images += 1
                    # If asset file does not exits that's an error.
                    if not os.path.exists(asset_fname):
                        detailed_slist.append('Not found {}'.format(asset_fname))
                        launcher_missing_images += 1
                        missing_images += 1
                        problems_detected = True
                        continue
                    # Process asset
                    processed_images += 1
                    asset_root, asset_ext = os.path.splitext(asset_fname)
                    asset_ext = asset_ext[1:] # Remove leading dot '.png' -> 'png'
                    img_id_ext = misc_identify_image_id_by_ext(asset_fname)
                    img_id_real = misc_identify_image_id_by_contents(asset_fname)
                    # detailed_slist.append('img_id_ext "{}" | img_id_real "{}"'.format(img_id_ext, img_id_real))
                    # Unrecognised or corrupted image.
                    if img_id_ext == IMAGE_UKNOWN_ID:
                        detailed_slist.append('Unrecognised extension {}'.format(asset_fname))
                        problems_detected = True
                        problematic_images += 1
                        launcher_problematic_images += 1
                        continue
                    # Corrupted image.
                    if img_id_real == IMAGE_CORRUPT_ID:
                        detailed_slist.append('Corrupted {}'.format(asset_fname))
                        problems_detected = True
                        problematic_images += 1
                        launcher_problematic_images += 1
                        continue
                    # Unrecognised or corrupted image.
                    if img_id_real == IMAGE_UKNOWN_ID:
                        detailed_slist.append('Bin unrecog or corrupted {}'.format(asset_fname))
                        problems_detected = True
                        problematic_images += 1
                        launcher_problematic_images += 1
                        continue
                    # At this point the image is recognised but has wrong extension
                    if img_id_ext != img_id_real:
                        detailed_slist.append('Wrong extension ({}) {}'.format(
                            IMAGE_EXTENSIONS[img_id_real][0], asset_fname))
                        problems_detected = True
                        problematic_images += 1
                        launcher_problematic_images += 1
                        continue
                # On big setups this can take forever. Allow the user to cancel.
                if pdialog.isCanceled(): break
            else:
                # only executed if the inner loop did NOT break
                sum_table_slist.append([
                    launcher['m_name'], '{:,d}'.format(num_roms), '{:,d}'.format(launcher_images),
                    '{:,d}'.format(launcher_missing_images), '{:,d}'.format(launcher_problematic_images),
                ])
                detailed_slist.append('Number of images    {:6,d}'.format(launcher_images))
                detailed_slist.append('Missing images      {:6,d}'.format(launcher_missing_images))
                detailed_slist.append('Problematic images  {:6,d}'.format(launcher_problematic_images))
                if problems_detected:
                    detailed_slist.append(KC_RED + 'Launcher should be updated' + KC_END)
                else:
                    detailed_slist.append(KC_GREEN + 'Launcher OK' + KC_END)
                detailed_slist.append('')
                continue
            # only executed if the inner loop DID break
            detailed_slist.append('Interrupted by user (pDialog cancelled).')
            break
        pdialog.endProgress()

        # Generate, save and display report.
        log_info('Writing report file "{}"'.format(g_PATHS.ROM_ART_INTEGRITY_REPORT_FILE_PATH.getPath()))
        pdialog.startProgress('Saving report')
        main_slist.append('*** Summary ***')
        main_slist.append('There are {:,} ROM launchers.'.format(len(self.launchers)))
        main_slist.append('Total images        {:7,d}'.format(total_images))
        main_slist.append('Missing images      {:7,d}'.format(missing_images))
        main_slist.append('Processed images    {:7,d}'.format(processed_images))
        main_slist.append('Problematic images  {:7,d}'.format(problematic_images))
        main_slist.append('')
        main_slist.extend(text_render_table(sum_table_slist))
        main_slist.append('')
        main_slist.append('*** Detailed report ***')
        main_slist.extend(detailed_slist)
        utils_write_slist_to_file(g_PATHS.ROM_ART_INTEGRITY_REPORT_FILE_PATH.getPath(), main_slist)
        pdialog.endProgress()
        full_string = '\n'.join(main_slist)
        kodi_display_text_window_mono('ROM artwork integrity report', full_string)

    def _command_exec_utils_delete_redundant_artwork(self):
        kodi_dialog_OK('EXECUTE_UTILS_DELETE_REDUNDANT_ARTWORK not implemented yet.')

    def _command_exec_utils_delete_ROM_redundant_artwork(self):
        kodi_dialog_OK('EXECUTE_UTILS_DELETE_ROM_REDUNDANT_ARTWORK not implemented yet.')
        return

        log_info('_command_exec_utils_delete_ROM_redundant_artwork() Beginning...')
        main_slist = []
        detailed_slist = []
        pdialog = KodiProgressDialog()
        pdialog.startProgress('Checking ROM sync status', len(self.launchers))
        for launcher_id in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
            pdialog.updateProgressInc()
            launcher = self.launchers[launcher_id]
            # Skip non-ROM launcher.
            if not launcher['rompath']: continue
            log_debug('Checking ROM Launcher "{}"'.format(launcher['m_name']))
            detailed_slist.append('[COLOR orange]Launcher "{}"[/COLOR]'.format(launcher['m_name']))
            # Load ROMs.
            roms = fs_load_ROMs_JSON(g_PATHS.ROMS_DIR, launcher)
            num_roms = len(roms)
            R_str = 'ROM' if num_roms == 1 else 'ROMs'
            log_debug('Launcher has {} DB {}'.format(num_roms, R_str))
            detailed_slist.append('Launcher has {} DB {}'.format(num_roms, R_str))
            # For now skip multidisc ROMs until multidisc support is fixed. I think for
            # every ROM in the multidisc set there should be a normal ROM not displayed
            # in listings, and then the special multidisc ROM that points to the ROMs
            # in the set.
            has_multidisc_ROMs = False
            for rom_id in roms:
                if roms[rom_id]['disks']:
                    has_multidisc_ROMs = True
                    break
            if has_multidisc_ROMs:
                log_debug('Launcher has multidisc ROMs. Skipping launcher')
                detailed_slist.append('Launcher has multidisc ROMs.')
                detailed_slist.append('[COLOR yellow]Skipping launcher[/COLOR]')
                continue
            # Get real ROMs (remove Missing, Multidisc, etc., ROMs).
            # Remove ROM Audit Missing ROMs (fake ROMs).
            real_roms = {}
            for rom_id in roms:
                if roms[rom_id]['nointro_status'] == AUDIT_STATUS_MISS: continue
                real_roms[rom_id] = roms[rom_id]
            num_real_roms = len(real_roms)
            R_str = 'ROM' if num_real_roms == 1 else 'ROMs'
            log_debug('Launcher has {} real {}'.format(num_real_roms, R_str))
            detailed_slist.append('Launcher has {} real {}'.format(num_real_roms, R_str))
            # If Launcher is empty there is nothing to do.
            if num_real_roms < 1:
                log_debug('Launcher is empty')
                detailed_slist.append('Launcher is empty')
                detailed_slist.append('[COLOR yellow]Skipping launcher[/COLOR]')
                continue
            # Make a dictionary for fast indexing.
            # romfiles_dic = {real_roms[rom_id]['filename'] : rom_id for rom_id in real_roms}

            # Process all asset directories one by one.


            # Complete detailed report.
            detailed_slist.append('')
        pdialog.endProgress()

        # Generate, save and display report.
        log_info('Writing report file "{}"'.format(g_PATHS.ROM_SYNC_REPORT_FILE_PATH.getPath()))
        pdialog.startProgress('Saving report')
        main_slist.append('*** Summary ***')
        main_slist.append('There are {} ROM launchers.'.format(len(self.launchers)))
        main_slist.append('')
        # main_slist.extend(text_render_table_NO_HEADER(short_slist, trim_Kodi_colours = True))
        # main_slist.append('')
        main_slist.append('*** Detailed report ***')
        main_slist.extend(detailed_slist)
        utils_write_str_to_file(g_PATHS.ROM_SYNC_REPORT_FILE_PATH.getPath(), main_slist)
        pdialog.endProgress()
        full_string = '\n'.join(main_slist)
        kodi_display_text_window_mono('ROM redundant artwork report', full_string)

    # Shows a report of the auto-detected No-Intro/Redump DAT files.
    # This simplifies a lot the ROM Audit of launchers and other things like the
    # Offline Scraper database generation.
    def _command_exec_utils_show_DATs(self):
        log_debug('_command_exec_utils_show_DATs() Starting...')
        DAT_STRING_LIMIT_CHARS = 75

        # --- Get files in No-Intro and Redump DAT directories ---
        NOINTRO_PATH_FN = FileName(self.settings['audit_nointro_dir'])
        if not NOINTRO_PATH_FN.exists():
            kodi_dialog_OK('No-Intro DAT directory not found. Please set it up in AEL addon settings.')
            return
        REDUMP_PATH_FN = FileName(self.settings['audit_redump_dir'])
        if not REDUMP_PATH_FN.exists():
            kodi_dialog_OK('No-Intro DAT directory not found. Please set it up in AEL addon settings.')
            return

        # --- Table header ---
        table_str = [
            ['left', 'left', 'left'],
            ['Platform', 'DAT type', 'DAT file'],
        ]

        # --- Scan files in DAT dirs ---
        NOINTRO_DAT_list = NOINTRO_PATH_FN.scanFilesInPath('*.dat')
        REDUMP_DAT_list = REDUMP_PATH_FN.scanFilesInPath('*.dat')
        # Some debug code
        # for fname in NOINTRO_DAT_list: log_debug(fname)

        # --- Autodetect files ---
        # 1) Traverse all platforms.
        # 2) Autodetect DATs for No-Intro or Redump platforms only.
        # AEL_platforms_t = AEL_platforms[0:4]
        for platform in AEL_platforms:
            if platform.DAT == DAT_NOINTRO:
                fname = misc_look_for_NoIntro_DAT(platform, NOINTRO_DAT_list)
                if fname:
                    DAT_str = FileName(fname).getBase()
                    DAT_str = text_limit_string(DAT_str, DAT_STRING_LIMIT_CHARS)
                    # DAT_str = '[COLOR=orange]' + DAT_str + '[/COLOR]'
                else:
                    DAT_str = '[COLOR=yellow]No-Intro DAT not found[/COLOR]'
                table_str.append([platform.compact_name, platform.DAT, DAT_str])
            elif platform.DAT == DAT_REDUMP:
                fname = misc_look_for_Redump_DAT(platform, REDUMP_DAT_list)
                if fname:
                    DAT_str = FileName(fname).getBase()
                    DAT_str = text_limit_string(DAT_str, DAT_STRING_LIMIT_CHARS)
                    # DAT_str = '[COLOR=orange]' + DAT_str + '[/COLOR]'
                else:
                    DAT_str = '[COLOR=yellow]Redump DAT not found[/COLOR]'
                table_str.append([platform.compact_name, platform.DAT, DAT_str])

        # Print report
        slist = text_render_table(table_str)
        full_string = '\n'.join(slist)
        kodi_display_text_window_mono('No-Intro/Redump DAT files report', full_string)

    def _command_exec_utils_check_retro_launchers(self):
        log_debug('_command_exec_utils_check_retro_launchers() Starting...')
        slist = []

        # Resolve category IDs to names
        for launcher_id in self.launchers:
            category_id = self.launchers[launcher_id]['categoryID']
            if category_id == 'root_category':
                self.launchers[launcher_id]['category'] = 'No category'
            else:
                self.launchers[launcher_id]['category'] = self.categories[category_id]['m_name']

        # Traverse list of launchers. If launcher uses Retroarch then check the
        # arguments and check that the core pointed with argument -L exists.
        # Sort launcher by category and then name.
        num_retro_launchers = 0
        for launcher_id in sorted(self.launchers,
            key = lambda x: (self.launchers[x]['category'], self.launchers[x]['m_name'])):
            launcher = self.launchers[launcher_id]
            m_name = launcher['m_name']
            # Skip Standalone Launchers
            if not launcher['rompath']:
                log_debug('Skipping launcher "{}"'.format(m_name))
                continue
            log_debug('Checking launcher "{}"'.format(m_name))
            application = launcher['application']
            arguments_list = [launcher['args']]
            arguments_list.extend(launcher['args_extra'])
            if not application.lower().find('retroarch'):
                log_debug('Not a Retroarch launcher "{}"'.format(application))
                continue
            clist = []
            flag_retroarch_launcher = False
            for index, arg_str in enumerate(arguments_list):
                arg_list = shlex.split(arg_str, posix = True)
                log_debug('[index {}] arg_str "{}"'.format(index, arg_str))
                log_debug('[index {}] arg_list {}'.format(index, arg_list))
                for i, arg in enumerate(arg_list):
                    if arg != '-L': continue
                    flag_retroarch_launcher = True
                    num_retro_launchers += 1
                    core_FN = FileName(arg_list[i+1])
                    if core_FN.exists():
                        s = '[COLOR=green]Found[/COLOR] core "{}"'.format(core_FN.getPath())
                    else:
                        s = '[COLOR=red]Missing[/COLOR] core "{}"'.format(core_FN.getPath())
                    log_debug(s)
                    clist.append(s)
                    break
            # Build report
            if flag_retroarch_launcher:
                t = 'Category [COLOR orange]{}[/COLOR] - Launcher [COLOR orange]{}[/COLOR]'.format(
                    self.launchers[launcher_id]['category'], m_name)
                slist.append(t)
                slist.extend(clist)
                slist.append('')
        # Print report
        title = 'Retroarch launchers report'
        if num_retro_launchers > 0:
            kodi_display_text_window_mono(title, '\n'.join(slist))
        else:
            kodi_display_text_window_mono(title, 'No Retroarch launchers found.')

    def _command_exec_utils_check_retro_BIOS(self):
        log_debug('_command_exec_utils_check_retro_BIOS() Checking Retroarch BIOSes ...')
        check_only_mandatory = self.settings['io_retroarch_only_mandatory']
        log_debug('_command_exec_utils_check_retro_BIOS() check_only_mandatory = {}'.format(check_only_mandatory))

        # If Retroarch System dir not configured or found abort.
        sys_dir_FN = FileName(self.settings['io_retroarch_sys_dir'])
        if not sys_dir_FN.exists():
            kodi_dialog_OK('Retroarch System directory not found. Please configure it.')
            return

        # Algorithm:
        # 1) Traverse list of BIOS. For every BIOS:
        # 2) Check if file exists. If not exists -> missing BIOS.
        # 3) If BIOS exists check file size.
        # 3) If BIOS exists check MD5
        # 4) Unknwon files in Retroarch System dir are ignored and non-reported.
        # 5) Write results into a report TXT file.
        BIOS_status_dic = {}
        BIOS_status_dic_colour = {}
        pDialog = KodiProgressDialog()
        pDialog.startProgress('Checking Retroarch BIOSes...', len(Libretro_BIOS_list))
        for BIOS_dic in Libretro_BIOS_list:
            pDialog.updateProgressInc()

            if check_only_mandatory and not BIOS_dic['mandatory']:
                log_debug('BIOS "{}" is not mandatory. Skipping check.'.format(BIOS_dic['filename']))
                continue

            BIOS_file_FN = sys_dir_FN.pjoin(BIOS_dic['filename'])
            log_debug('Testing BIOS "{}"'.format(BIOS_file_FN.getPath()))

            if not BIOS_file_FN.exists():
                log_info('Not found "{}"'.format(BIOS_file_FN.getPath()))
                BIOS_status_dic[BIOS_dic['filename']] = 'Not found'
                BIOS_status_dic_colour[BIOS_dic['filename']] = '[COLOR orange]Not found[/COLOR]'
                continue

            BIOS_stat = BIOS_file_FN.stat()
            file_size = BIOS_stat.st_size
            if file_size != BIOS_dic['size']:
                log_info('Wrong size "{}"'.format(BIOS_file_FN.getPath()))
                log_info('It is {} and must be {}'.format(file_size, BIOS_dic['size']))
                BIOS_status_dic[BIOS_dic['filename']] = 'Wrong size'
                BIOS_status_dic_colour[BIOS_dic['filename']] = '[COLOR orange]Wrong size[/COLOR]'
                continue

            hash_md5 = hashlib.md5()
            with open(BIOS_file_FN.getPath(), "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            file_MD5 = hash_md5.hexdigest()
            log_debug('MD5 is "{}"'.format(file_MD5))
            if file_MD5 != BIOS_dic['md5']:
                log_info('Wrong MD5 "{}"'.format(BIOS_file_FN.getPath()))
                log_info('It is       "{}"'.format(file_MD5))
                log_info('and must be "{}"'.format(BIOS_dic['md5']))
                BIOS_status_dic[BIOS_dic['filename']] = 'Wrong MD5'
                BIOS_status_dic_colour[BIOS_dic['filename']] = '[COLOR orange]Wrong MD5[/COLOR]'
                continue
            log_info('BIOS OK "{}"'.format(BIOS_file_FN.getPath()))
            BIOS_status_dic[BIOS_dic['filename']] = 'OK'
            BIOS_status_dic_colour[BIOS_dic['filename']] = '[COLOR lime]OK[/COLOR]'
        pDialog.endProgress()

        # Output format:
        #    BIOS name             Mandatory  Status      Cores affected
        #    -------------------------------------------------
        #    5200.rom              YES        OK          ---
        #    7800 BIOS (E).rom     NO         Wrong MD5   core a name
        #                                                 core b name
        #    7800 BIOS (U).rom     YES        OK          ---
        max_size_BIOS_filename = 0
        for BIOS_dic in Libretro_BIOS_list:
            if len(BIOS_dic['filename']) > max_size_BIOS_filename:
                max_size_BIOS_filename = len(BIOS_dic['filename'])

        max_size_status = 0
        for key in BIOS_status_dic:
            if len(BIOS_status_dic[key]) > max_size_status:
                max_size_status = len(BIOS_status_dic[key])

        slist = []
        slist.append('Retroarch system dir "{}"'.format(sys_dir_FN.getPath()))
        if check_only_mandatory:
            slist.append('Checking only mandatory BIOSes.\n')
        else:
            slist.append('Checking mandatory and optional BIOSes.\n')
        bios_str      = '{}{}'.format('BIOS name', ' ' * (max_size_BIOS_filename - len('BIOS name')))
        mandatory_str = 'Mandatory'
        status_str    = '{}{}'.format('Status', ' ' * (max_size_status - len('Status')))
        cores_str     = 'Cores affected'
        size_total = len(bios_str) + len(mandatory_str) + len(status_str) + len(cores_str) + 6
        slist.append('{}  {}  {}  {}'.format(bios_str, mandatory_str, status_str, cores_str))
        slist.append('{}'.format('-' * size_total))

        for BIOS_dic in Libretro_BIOS_list:
            BIOS_filename = BIOS_dic['filename']
            # If BIOS was skipped continue loop
            if BIOS_filename not in BIOS_status_dic: continue
            status_text = BIOS_status_dic[BIOS_filename]
            status_text_colour = BIOS_status_dic_colour[BIOS_filename]
            filename_str = '{}{}'.format(BIOS_filename, ' ' * (max_size_BIOS_filename - len(BIOS_filename)))
            mandatory_str = 'YES      ' if BIOS_dic['mandatory'] else 'NO       '
            status_str = '{}{}'.format(status_text_colour, ' ' * (max_size_status - len(status_text)))
            len_status_str = len('{}{}'.format(status_text, ' ' * (max_size_status - len(status_text))))

            # Print affected core list
            core_list = BIOS_dic['cores']
            if len(core_list) == 0:
                line_str = '{}  {}  {}'.format(filename_str, mandatory_str, status_str)
                slist.append(line_str)
            else:
                num_spaces = len(filename_str) + 9 + len_status_str + 4
                for i, core_name in enumerate(core_list):
                    beautiful_core_name = Retro_core_dic[core_name] if core_name in Retro_core_dic else core_name
                    if i == 0:
                        line_str = '{}  {}  {}  {}'.format(filename_str, mandatory_str,
                            status_str, beautiful_core_name)
                        slist.append(line_str)
                    else:
                        line_str = '{}  {}'.format(' ' * num_spaces, beautiful_core_name)
                        slist.append(line_str)

        # Stats report
        log_info('Writing report file "{}"'.format(g_PATHS.BIOS_REPORT_FILE_PATH.getPath()))
        utils_write_slist_to_file(g_PATHS.BIOS_REPORT_FILE_PATH.getPath(), slist)
        full_string = '\n'.join(slist)
        kodi_display_text_window_mono('Retroarch BIOS report', full_string)

    # Use TGDB scraper to get the monthly allowance and report to the user.
    # TGDB API docs https://api.thegamesdb.net/
    def _command_exec_utils_TGDB_check(self):
        # --- Get scraper object and retrieve information ---
        # Treat any error message returned by the scraper as an OK dialog.
        st_dic = kodi_new_status_dic()
        g_scraper_factory = ScraperFactory(g_PATHS, self.settings)
        TGDB = g_scraper_factory.get_scraper_object(SCRAPER_THEGAMESDB_ID)
        TGDB.check_before_scraping(st_dic)
        if kodi_display_status_message(st_dic): return

        # To check the scraper monthly allowance, get the list of platforms as JSON. This JSON
        # data contains the monthly allowance.
        pdialog = KodiProgressDialog()
        pdialog.startProgress('Retrieving info from TheGamesDB...')
        json_data = TGDB.debug_get_genres(st_dic)
        pdialog.endProgress()
        if kodi_display_status_message(st_dic): return
        extra_allowance = json_data['extra_allowance']
        remaining_monthly_allowance = json_data['remaining_monthly_allowance']
        allowance_refresh_timer = json_data['allowance_refresh_timer']
        allowance_refresh_timer_str = text_type(datetime.timedelta(seconds = allowance_refresh_timer))

        # --- Print and display report ---
        window_title = 'TheGamesDB scraper information'
        sl = []
        sl.append('extra_allowance              {}'.format(extra_allowance))
        sl.append('remaining_monthly_allowance  {}'.format(remaining_monthly_allowance))
        sl.append('allowance_refresh_timer      {}'.format(allowance_refresh_timer))
        sl.append('allowance_refresh_timer_str  {}'.format(allowance_refresh_timer_str))
        sl.append('')
        sl.append('TGDB scraper seems to be working OK.')
        kodi_display_text_window_mono(window_title, '\n'.join(sl))

    # MobyGames API docs https://www.mobygames.com/info/api
    # Currently there is no way to check the MobyGames allowance.
    def _command_exec_utils_MobyGames_check(self):
        # --- Get scraper object and retrieve information ---
        # Treat any error message returned by the scraper as an OK dialog.
        st_dic = kodi_new_status_dic()
        g_scraper_factory = ScraperFactory(g_PATHS, self.settings)
        MobyGames = g_scraper_factory.get_scraper_object(SCRAPER_MOBYGAMES_ID)
        MobyGames.check_before_scraping(st_dic)
        if kodi_display_status_message(st_dic): return

        # TTBOMK, there is no way to know the current limits of MobyGames scraper.
        # Just get the list of platforms and report to the user.
        pdialog = KodiProgressDialog()
        pdialog.startProgress('Retrieving info from MobyGames...')
        json_data = MobyGames.debug_get_platforms(st_dic)
        pdialog.endProgress()
        if kodi_display_status_message(st_dic): return

        # --- Print and display report ---
        window_title = 'MobyGames scraper information'
        sl = []
        sl.append('The API allowance of MobyGames cannot be currently checked.')
        sl.append('')
        sl.append('MobyGames has {} platforms.'.format(len(json_data['platforms'])))
        sl.append('')
        sl.append('MobyGames scraper seems to be working OK.')
        kodi_display_text_window_mono(window_title, '\n'.join(sl))

    # ScreenScraper API docs https://www.screenscraper.fr/webapi.php
    def _command_exec_utils_ScreenScraper_check(self):
        # --- Get scraper object and retrieve information ---
        # Treat any error message returned by the scraper as an OK dialog.
        st_dic = kodi_new_status_dic()
        g_scraper_factory = ScraperFactory(g_PATHS, self.settings)
        ScreenScraper = g_scraper_factory.get_scraper_object(SCRAPER_SCREENSCRAPER_ID)
        ScreenScraper.check_before_scraping(st_dic)
        if kodi_display_status_message(st_dic): return

        # Get ScreenScraper user information
        pdialog = KodiProgressDialog()
        pdialog.startProgress('Retrieving info from ScreenScraper...')
        json_data = ScreenScraper.debug_get_user_info(st_dic)
        pdialog.endProgress()
        if kodi_display_status_message(st_dic): return

        # --- Print and display report ---
        header = json_data['header']
        serveurs = json_data['response']['serveurs']
        ssuser = json_data['response']['ssuser']
        window_title = 'ScreenScraper scraper information'
        sl = [
            'APIversion           {}'.format(header['APIversion']),
            'dateTime             {}'.format(header['dateTime']),
            'cpu1 load            {}%'.format(serveurs['cpu1']),
            'cpu2 load            {}%'.format(serveurs['cpu2']),
            'nbscrapeurs          {}'.format(serveurs['nbscrapeurs']),
            '',
            'id                   {}'.format(ssuser['id']),
            'niveau               {}'.format(ssuser['niveau']),
            'maxthreads           {}'.format(ssuser['maxthreads']),
            'maxdownloadspeed     {}'.format(ssuser['maxdownloadspeed']),
            'requeststoday        {}'.format(ssuser['requeststoday']),
            'requestskotoday      {}'.format(ssuser['requestskotoday']),
            'maxrequestspermin    {}'.format(ssuser['maxrequestspermin']),
            'maxrequestsperday    {}'.format(ssuser['maxrequestsperday']),
            'maxrequestskoperday  {}'.format(ssuser['maxrequestskoperday']),
            'visites              {}'.format(ssuser['visites']),
            'datedernierevisite   {}'.format(ssuser['datedernierevisite']),
            'favregion            {}'.format(ssuser['favregion']),
            '',
            'ScreenScraper scraper seems to be working OK.',
        ]
        kodi_display_text_window_mono(window_title, '\n'.join(sl))

    # Retrieve an example game to test if ArcadeDB works.
    # TTBOMK there are not API retrictions at the moment (August 2019).
    def _command_exec_utils_ArcadeDB_check(self):
        st_dic = kodi_new_status_dic()
        g_scraper_factory = ScraperFactory(g_PATHS, self.settings)
        ArcadeDB = g_scraper_factory.get_scraper_object(SCRAPER_ARCADEDB_ID)
        ArcadeDB.check_before_scraping(st_dic)
        if kodi_display_status_message(st_dic): return

        search_str = 'atetris'
        rom_FN = FileName('atetris.zip')
        rom_checksums_FN = FileName('atetris.zip')
        platform = 'MAME'

        pdialog = KodiProgressDialog()
        pdialog.startProgress('Retrieving info from ArcadeDB...')
        ArcadeDB.check_candidates_cache(rom_FN, platform)
        ArcadeDB.clear_cache(rom_FN, platform)
        candidates = ArcadeDB.get_candidates(search_str, rom_FN, rom_checksums_FN, platform, st_dic)
        pdialog.endProgress()
        if kodi_display_status_message(st_dic): return
        if len(candidates) != 1:
            kodi_dialog_OK('There is a problem with ArcadeDB scraper.')
            return
        json_response_dic = ArcadeDB.debug_get_QUERY_MAME_dic(candidates[0])

        # --- Print and display report ---
        num_games = len(json_response_dic['result'])
        window_title = 'ArcadeDB scraper information'
        sl = [
            'num_games      {}'.format(num_games),
            'game_name      {}'.format(json_response_dic['result'][0]['game_name']),
            'title          {}'.format(json_response_dic['result'][0]['title']),
            'emulator_name  {}'.format(json_response_dic['result'][0]['emulator_name']),
        ]
        if num_games == 1:
            sl.append('')
            sl.append('ArcadeDB scraper seems to be working OK.')
            sl.append('Remember this scraper only works with platform MAME.')
            sl.append('It will only return valid data for MAME games.')
        kodi_display_text_window_mono(window_title, '\n'.join(sl))

    def _command_exec_global_rom_stats(self):
        log_debug('_command_exec_global_rom_stats() BEGIN')
        window_title = 'Global ROM statistics'
        sl = []
        # sl.append('[COLOR violet]Launcher ROM report.[/COLOR]')
        # sl.append('')

        # --- Table header ---
        table_str = [
            ['left', 'left', 'left'],
            ['Category', 'Launcher', 'ROMs'],
        ]

        # Traverse categories and sort alphabetically.
        log_debug('Number of categories {}'.format(len(self.categories)))
        log_debug('Number of launchers {}'.format(len(self.launchers)))
        for cat_id in sorted(self.categories, key = lambda x : self.categories[x]['m_name']):
            # Get launchers of this category alphabetically sorted.
            launcher_list = []
            for launcher_id in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
                launcher = self.launchers[launcher_id]
                # Skip Standalone Launchers
                if not launcher['rompath']: continue
                if launcher['categoryID'] == cat_id: launcher_list.append(launcher)
            # Render list of launchers for this category.
            cat_name = self.categories[cat_id]['m_name']
            for launcher in launcher_list:
                table_str.append([cat_name, launcher['m_name'], text_type(launcher['num_roms'])])
        # Traverse launchers with no category.
        catless_launchers = {}
        for launcher_id in self.launchers:
            launcher = self.launchers[launcher_id]
            if launcher['categoryID'] == VCATEGORY_ADDONROOT_ID:
                catless_launchers[launcher_id] = launcher
        for launcher_id in sorted(catless_launchers, key = lambda x : catless_launchers[x]['m_name']):
            launcher = self.launchers[launcher_id]
            # Skip Standalone Launchers
            if not launcher['rompath']: continue
            table_str.append(['', launcher['m_name'], text_type(launcher['num_roms'])])

        # Generate table and print report
        # log_debug(text_type(table_str))
        sl.extend(text_render_table(table_str))
        kodi_display_text_window_mono(window_title, '\n'.join(sl))

    # TODO Add a table columnd to tell user if the DAT is automatic or custom.
    def _command_exec_global_audit_stats(self, report_type):
        log_debug('_command_exec_global_audit_stats() Report type {}'.format(report_type))
        window_title = 'Global ROM Audit statistics'
        sl = []

        # --- Table header ---
        # Table cell padding: left, right
        table_str = [
            ['left', 'left', 'left', 'left', 'left', 'left', 'left', 'left'],
            ['Category', 'Launcher', 'Platform', 'Type', 'ROMs', 'Have', 'Miss', 'Unknown'],
        ]

        # Traverse categories and sort alphabetically.
        log_debug('Number of categories {}'.format(len(self.categories)))
        log_debug('Number of launchers {}'.format(len(self.launchers)))
        for cat_id in sorted(self.categories, key = lambda x : self.categories[x]['m_name']):
            # Get launchers of this category alphabetically sorted.
            launcher_list = []
            for launcher_id in sorted(self.launchers, key = lambda x : self.launchers[x]['m_name']):
                launcher = self.launchers[launcher_id]
                # Skip Standalone Launchers and Launcher with no ROM Audit.
                if not launcher['rompath']: continue
                if launcher['audit_state'] == AUDIT_STATE_OFF: continue
                if launcher['categoryID'] == cat_id: launcher_list.append(launcher)
            # Render list of launchers for this category.
            cat_name = self.categories[cat_id]['m_name']
            for launcher in launcher_list:
                p_index = get_AEL_platform_index(launcher['platform'])
                p_obj = AEL_platforms[p_index]
                # Skip launchers depending on user settings.
                if report_type == AUDIT_REPORT_NOINTRO and p_obj.DAT != DAT_NOINTRO: continue
                if report_type == AUDIT_REPORT_REDUMP and p_obj.DAT != DAT_REDUMP: continue
                table_str.append([
                    cat_name, launcher['m_name'], p_obj.compact_name, p_obj.DAT,
                    text_type(launcher['num_roms']), text_type(launcher['num_have']),
                    text_type(launcher['num_miss']), text_type(launcher['num_unknown']),
                ])
        # Traverse launchers with no category.
        catless_launchers = {}
        for launcher_id in self.launchers:
            launcher = self.launchers[launcher_id]
            if launcher['categoryID'] == VCATEGORY_ADDONROOT_ID:
                catless_launchers[launcher_id] = launcher
        for launcher_id in sorted(catless_launchers, key = lambda x : catless_launchers[x]['m_name']):
            launcher = self.launchers[launcher_id]
            # Skip Standalone Launchers
            if not launcher['rompath']: continue

            p_index = get_AEL_platform_index(launcher['platform'])
            p_obj = AEL_platforms[p_index]
            # Skip launchers depending on user settings.
            if report_type == AUDIT_REPORT_NOINTRO and p_obj.DAT != DAT_NOINTRO: continue
            if report_type == AUDIT_REPORT_REDUMP and p_obj.DAT != DAT_REDUMP: continue
            table_str.append([
                ' ', launcher['m_name'], p_obj.compact_name, text_type(p_obj.DAT),
                text_type(launcher['num_roms']), text_type(launcher['num_have']),
                text_type(launcher['num_miss']), text_type(launcher['num_unknown']),
            ])

        # Generate table and print report
        # log_debug(text_type(table_str))
        log_debug(text_type(table_str))
        sl.extend(text_render_table(table_str))
        kodi_display_text_window_mono(window_title, '\n'.join(sl))

    def _command_buildMenu(self):
        log_debug('_command_buildMenu() Starting...')

        hasSkinshortcuts = xbmc.getCondVisibility('System.HasAddon(script.skinshortcuts)') == 1
        if hasSkinshortcuts == False:
            log_warning("Addon skinshortcuts is not installed, cannot build games menu")
            kodi_notify('Addon skinshortcuts is not installed')
            return

        path = ""
        try:
            skinshortcutsAddon = xbmcaddon.Addon('script.skinshortcuts')
            path = FileName(skinshortcutsAddon.getAddonInfo('path'))

            libPath = path.pjoin('resources', 'lib')
            sys.path.append(libPath.getPath())

            unidecodeModule = xbmcaddon.Addon('script.module.unidecode')
            libPath = FileName(unidecodeModule.getAddonInfo('path'))
            libPath = libPath.pjoin('lib')
            sys.path.append(libPath.getPath())

            sys.modules[ "__main__" ].ADDON    = skinshortcutsAddon
            sys.modules[ "__main__" ].ADDONID  = text_type(skinshortcutsAddon.getAddonInfo('id'))
            sys.modules[ "__main__" ].CWD      = path.getPath()
            sys.modules[ "__main__" ].LANGUAGE = skinshortcutsAddon.getLocalizedString

            import gui, datafunctions

        except Exception as ex:
            log_error("(Exception) Failed to load skinshortcuts addon")
            log_error("(Exception) {}".format(ex))
            traceback.print_exc()
            kodi_notify_warn('Could not load skinshortcuts addon')
            return
        log_debug('_command_buildMenu() Loaded SkinsShortCuts addon')

        startToBuild = kodi_dialog_yesno('Want to automatically fill the menu?', 'Games menu')
        if not startToBuild: return

        menuStore = datafunctions.DataFunctions()
        ui = gui.GUI( "script-skinshortcuts.xml", path, "default", group="mainmenu", defaultGroup=None,
            nolabels="false", groupname="" )
        ui.currentWindow = xbmcgui.Window()

        mainMenuItems = []
        mainMenuItemLabels = []
        shortcuts = menuStore._get_shortcuts( "mainmenu", defaultGroup =None )
        for shortcut in shortcuts.getroot().findall( "shortcut" ):
            item = ui._parse_shortcut( shortcut )
            mainMenuItemLabels.append(item[1].getLabel())
            mainMenuItems.append(item[1])

        selectedMenuIndex = KodiSelectDialog('Select menu', mainMenuItemLabels).executeDialog()
        selectedMenuItem = mainMenuItems[selectedMenuIndex]

        sDialog = KodiSelectDialog("Select content to create in {}".format(selectedMenuItem.getLabel()))
        sDialog.setRows(['Categories', 'Launchers'])
        typeOfContent = sDialog.executeDialog()

        selectedMenuID = selectedMenuItem.getProperty("labelID")
        selectedMenuItems = []

        selectedMenuItemsFromStore = menuStore._get_shortcuts(selectedMenuID, defaultGroup =None )
        amount = len(selectedMenuItemsFromStore.getroot().findall( "shortcut" ))

        if amount < 1:
            selectedDefaultID = selectedMenuItem.getProperty("defaultID")
            selectedMenuItemsFromStore = menuStore._get_shortcuts(selectedDefaultID, defaultGroup =None )

        for shortcut in selectedMenuItemsFromStore.getroot().findall( "shortcut" ):
            item = ui._parse_shortcut( shortcut )
            selectedMenuItems.append(item[1])

        ui.group = selectedMenuID
        count = len(selectedMenuItems)

        if typeOfContent == 0:
            for key in sorted(self.categories, key = lambda x : self.categories[x]['m_name']):
                category_dic = self.categories[key]
                name = category_dic['m_name']
                url_str = 'ActivateWindow(Programs,"{}",return)'.format(aux_url('SHOW_LAUNCHERS', key))
                fanart = asset_get_default_asset_Category(category_dic, 'default_fanart')
                thumb = asset_get_default_asset_Category(category_dic, 'default_thumb', 'DefaultFolder.png')

                log_debug('_command_buildMenu() Adding Category "{}"'.format(name))
                listitem = self._buildMenuItem(key, name, url_str, thumb, fanart, count, ui)
                selectedMenuItems.append(listitem)

        if typeOfContent == 1:
            for key in sorted(self.launchers, key = lambda x : self.launchers[x]['application']):
                launcher_dic = self.launchers[key]
                name = launcher_dic['m_name']
                launcherID = launcher_dic['id']
                categoryID = launcher_dic['categoryID']
                url_str = 'ActivateWindow(Programs,"%s",return)'.format(aux_url('SHOW_ROMS', categoryID, launcherID))
                fanart = asset_get_default_asset_Category(launcher_dic, 'default_fanart')
                thumb = asset_get_default_asset_Category(launcher_dic, 'default_thumb', 'DefaultFolder.png')

                log_debug('_command_buildMenu() Adding Launcher "{}"'.format(name))
                listitem = self._buildMenuItem(key, name, url_str, thumb, fanart, count, ui)
                selectedMenuItems.append(listitem)

        ui.changeMade = True
        ui.allListItems = selectedMenuItems
        ui._save_shortcuts()
        ui.close()
        log_info("Saved shortcuts for AEL")
        kodi_notify('The menu has been updated with AEL content')

        # xmlfunctions.ADDON = xbmcaddon.Addon('script.skinshortcuts')
        # xmlfunctions.ADDONVERSION = xmlfunctions.ADDON.getAddonInfo('version')
        # xmlfunctions.LANGUAGE = xmlfunctions.ADDON.getLocalizedString
        # xml = XMLFunctions()
        # xml.buildMenu("9000","","0",None,"","0")
        # log_info("Done building menu for AEL")

    def _buildMenuItem(self, key, name, action, thumb, fanart, count, ui):
        listitem = xbmcgui.ListItem(name)
        listitem.setProperty("defaultID", key)
        listitem.setProperty("Path", action)
        listitem.setProperty("displayPath", action)
        listitem.setProperty("icon", thumb)
        listitem.setProperty("skinshortcuts-orderindex", text_type(count))
        listitem.setProperty("additionalListItemProperties", "[]")
        ui._add_additional_properties(listitem)
        ui._add_additionalproperty(listitem, "background", fanart)
        ui._add_additionalproperty(listitem, "backgroundName", fanart)

        return listitem
