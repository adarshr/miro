# Miro - an RSS based video player application
# Copyright (C) 2005-2009 Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

"""Menu handling code."""

from miro import app
from miro import prefs
from miro import signals
from miro import config

from miro.gtcache import gettext as _
from miro import config
from miro import prefs

(CTRL, ALT, SHIFT, CMD, RIGHT_ARROW, LEFT_ARROW, UP_ARROW,
 DOWN_ARROW, SPACE, ENTER, DELETE, BKSPACE, ESCAPE,
 F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12) = range(25)
platform = config.get(prefs.APP_PLATFORM)

MOD = CTRL

def set_mod(modifier):
    """Allows the platform to change the MOD key.  OSX and
    Windows have different mod keys.

    Examples:
    >>> set_mod(CTRL)
    >>> set_mod(CMD)
    """
    global MOD
    MOD = modifier

class Shortcut:
    """Defines a shortcut key combination used to trigger this
    menu item.

    The first argument is the shortcut key.  Other arguments are
    modifiers.

    Examples:

    >>> Shortcut("x", MOD)
    >>> Shortcut(BKSPACE, MOD)

    This is wrong:

    >>> Shortcut(MOD, "x")
    """
    def __init__(self, shortcut, *modifiers):
        self.shortcut = shortcut
        self.modifiers = modifiers

class MenuItem:
    """A menu item is a single item in the menu that can be clicked
    on that has an action.

    :param label: The label it has (must be internationalized)
    :param action: The action string for this menu item.
    :param shortcuts: None, the Shortcut, or tuple of Shortcut objects.
    :param enabled: Whether (True) or not (False) this menu item is
                    enabled by default.
    :param state_labels: If this menu item has states, then this is
                         the name/value pairs for all states.

    Example:

    >>> MenuItem(_("_Options"), "EditPreferences")
    >>> MenuItem(_("Cu_t"), "ClipboardCut", Shortcut("x", MOD))
    >>> MenuItem(_("_Update Feed"), "UpdateFeeds",
    ...          (Shortcut("r", MOD), Shortcut(F5)), enabled=False)
    >>> MenuItem(_("_Play"), "PlayPauseVideo", enabled=False,
    ...          play=_("_Play"), pause=_("_Pause"))
    """
    def __init__(self, label, action, shortcuts=None, enabled=True,
                 **state_labels):
        self.label = label
        self.action = action
        if shortcuts == None:
            shortcuts = ()
        if not isinstance(shortcuts, tuple):
            shortcuts = (shortcuts,)
        self.shortcuts = shortcuts
        self.enabled = enabled
        self.state_labels = state_labels

class Separator:
    """This denotes a separator in the menu.
    """
    def __init__(self):
        self.action = None

class Menu:
    """A Menu holds a list of MenuItems and Menus.

    Example:
    >>> Menu(_("P_layback"), "Playback", [
    ...      MenuItem(_("_Foo"), "Foo"),
    ...      MenuItem(_("_Bar"), "Bar")
    ...      ])
    >>> Menu("", "toplevel", [
    ...     Menu(_("_File"), "File", [ ... ])
    ...     ])
    """
    def __init__(self, label, action, menuitems):
        self.label = label
        self.action = action
        self.menuitems = list(menuitems)

    def __iter__(self):
        for mem in self.menuitems:
            yield mem
            if isinstance(mem, Menu):
                for mem2 in mem:
                    yield mem2

    def has(self, action):
        for mem in self.menuitems:
            if mem.action == action:
                return True
        return False

    def get(self, action, default=None):
        for mem in self.menuitems:
            if mem.action == action:
                return mem
            if isinstance(mem, Menu):
                try:
                    return mem.get(action)
                except ValueError:
                    pass

        if default is not None:
            return default

        raise ValueError("%s is not in this menu." % action)

    def index(self, action):
        for i, mem in enumerate(self.menuitems):
            if mem.action == action:
                return i
        raise ValueError("%s not in this menu." % action)

    def remove(self, action):
        # FIXME - this won't remove separators--probably should do
        # a pass to remove a separator for two separators in a row
        # or a separator at the beginning or end of the list
        self.menuitems = [m for m in self.menuitems if m.action != action]

    def count(self):
        return len(menuitems)

    def insert(self, index, menuitem):
        self.menuitems.insert(index, menuitem)

    def append(self, menuitem):
        self.menuitems.append(menuitem)

EditItems = [
    MenuItem(_("Cu_t"), "ClipboardCut", Shortcut("x", MOD)),
    MenuItem(_("_Copy"), "ClipboardCopy", Shortcut("c", MOD)),
    MenuItem(_("_Paste"), "ClipboardPaste", Shortcut("v", MOD)),
    MenuItem(_("Select _All"), "ClipboardSelectAll", Shortcut("a", MOD)),
]

def get_menu():
    mbar = Menu("", "TopLevel", [
            Menu(_("_Video"), "VideoMenu", [
                    MenuItem(_("_Open"), "Open", Shortcut("o", MOD)),
                    MenuItem(_("_Download Item"), "NewDownload"),
                    MenuItem(_("Check _Version"), "CheckVersion"),
                    Separator(),
                    MenuItem(_("_Remove Item"), "RemoveItems",
                             Shortcut(BKSPACE, MOD), enabled=False,
                             plural=_("_Remove Items")),
                    MenuItem(_("Re_name Item"), "RenameItem", enabled=False),
                    MenuItem(_("Save Item _As"), "SaveItem",
                             Shortcut("s", MOD), enabled=False,
                             plural=_("Save Items _As")),
                    MenuItem(_("Copy Item _URL"), "CopyItemURL",
                             Shortcut("u", MOD), enabled=False),
                    Separator(),
                    MenuItem(_("_Options"), "EditPreferences"),
                    MenuItem(_("_Quit"), "Quit", Shortcut("q", MOD)),
                    ]),

            Menu(_("_Sidebar"), "SidebarMenu", [
                    MenuItem(_("Add _Feed"), "NewFeed", Shortcut("n", MOD)),
                    MenuItem(_("Add Site"), "NewGuide"),
                    MenuItem(_("New Searc_h Feed"), "NewSearchFeed"),
                    MenuItem(_("New _Folder"), "NewFeedFolder",
                             Shortcut("n", MOD, SHIFT)),
                    Separator(),
                    MenuItem(_("Re_name"), "RenameFeed", enabled=False),
                    MenuItem(_("_Remove"), "RemoveFeeds",
                             Shortcut(BKSPACE, MOD), enabled=False,
                             folder=_("_Remove Folder"),
                             ),
                    MenuItem(_("_Update Feed"), "UpdateFeeds",
                             (Shortcut("r", MOD), Shortcut(F5)), enabled=False,
                             plural=_("_Update Feeds")),
                    MenuItem(_("Update _All Feeds"), "UpdateAllFeeds",
                             Shortcut("r", MOD, SHIFT)),
                    Separator(),
                    MenuItem(_("_Import Feeds (OPML)"), "ImportFeeds"),
                    MenuItem(_("E_xport Feeds (OPML)"), "ExportFeeds"),
                    Separator(),
                    MenuItem(_("_Share with a Friend"), "ShareFeed",
                             enabled=False),
                    MenuItem(_("Copy URL"), "CopyFeedURL", enabled=False),
                    ]),

            Menu(_("_Playlists"), "PlaylistsMenu", [
                    MenuItem(_("New _Playlist"), "NewPlaylist",
                             Shortcut("p", MOD)),
                    MenuItem(_("New Playlist Fol_der"), "NewPlaylistFolder",
                             Shortcut("p", MOD, SHIFT)),
                    Separator(),
                    MenuItem(_("Re_name Playlist"),"RenamePlaylist",
                             enabled=False),
                    MenuItem(_("_Remove Playlist"),"RemovePlaylists",
                             Shortcut(BKSPACE, MOD), enabled=False,
                             plural=_("_Remove Playlists"),
                             folders=_("_Remove Playlist Folders"),
                             folder=_("_Remove Playlist Folder"),
                             ),
                    ]),

            Menu(_("P_layback"), "PlaybackMenu", [
                    MenuItem(_("_Play"), "PlayPauseVideo", enabled=False,
                             play=_("_Play"),
                             pause=_("_Pause")),
                    MenuItem(_("_Stop"), "StopVideo", Shortcut("d", MOD),
                             enabled=False),
                    Separator(),
                    MenuItem(_("_Next Video"), "NextVideo",
                             Shortcut(RIGHT_ARROW, MOD), enabled=False),
                    MenuItem(_("_Previous Video"), "PreviousVideo",
                             Shortcut(LEFT_ARROW, MOD), enabled=False),
                    Separator(),
                    MenuItem(_("Skip _Forward"), "FastForward", enabled=False),
                    MenuItem(_("Skip _Back"), "Rewind", enabled=False),
                    Separator(),
                    MenuItem(_("Volume _Up"), "UpVolume",
                             Shortcut(UP_ARROW, MOD), enabled=False),
                    MenuItem(_("Volume _Down"), "DownVolume",
                             Shortcut(DOWN_ARROW,MOD), enabled=False),
                    Separator(),
                    MenuItem(_("_Fullscreen"), "Fullscreen",
                             (Shortcut("f", MOD), Shortcut(ENTER, ALT)),
                             enabled=False),
                    MenuItem(_("_Toggle Detached/Attached"), "ToggleDetach",
                             Shortcut("t", MOD), enabled=False),
                    Menu(_("S_ubtitles"), "SubtitlesMenu", 
                         [
                            MenuItem(_("None Available"), "NoneAvailable", enabled=False)
                            ]),
                    ]),

            Menu(_("_Help"), "HelpMenu", [
                    MenuItem(_("_About %(name)s",
                               {'name': config.get(prefs.SHORT_APP_NAME)}),
                             "About", ())
                    ])
            ])

    help_menu = mbar.get("HelpMenu")
    if config.get(prefs.DONATE_URL):
        help_menu.append(MenuItem(_("_Donate"), "Donate"))

    if config.get(prefs.HELP_URL):
        help_menu.append(MenuItem(_("_Help"), "Help", Shortcut(F1)))
    help_menu.append(Separator())
    help_menu.append(MenuItem(_("Diagnostics"), "Diagnostics"))
    if config.get(prefs.BUG_REPORT_URL):
        help_menu.append(MenuItem(_("Report a _Bug"), "ReportBug"))
    if config.get(prefs.TRANSLATE_URL):
        help_menu.append(MenuItem(_("_Translate"), "Translate"))
    if config.get(prefs.PLANET_URL):
        help_menu.append(MenuItem(_("_Planet Miro"), "Planet"))
    return mbar

action_handlers = {}
def lookup_handler(action_name):
    """For a given action name, get a callback to handle it.  Return
    None if no callback is found.
    """
    return action_handlers.get(action_name)

def action_handler(name):
    """Decorator for functions that handle menu actions."""
    def decorator(func):
        action_handlers[name] = func
        return func
    return decorator

# Video/File menu

@action_handler("Open")
def on_open():
    app.widgetapp.open_video()

@action_handler("NewDownload")
def on_new_download():
    app.widgetapp.new_download()

@action_handler("CheckVersion")
def on_check_version():
    app.widgetapp.check_version()

@action_handler("RemoveItems")
def on_remove_items():
    app.widgetapp.remove_items()

@action_handler("RenameItem")
def on_rename_item():
    app.widgetapp.rename_item()

@action_handler("SaveItem")
def on_save_item():
    app.widgetapp.save_item()

@action_handler("CopyItemURL")
def on_copy_item_url():
    app.widgetapp.copy_item_url()

@action_handler("EditPreferences")
def on_edit_preferences():
    app.widgetapp.preferences()

@action_handler("Quit")
def on_quit():
    app.widgetapp.quit()


# Feeds menu

@action_handler("NewFeed")
def on_new_feed():
    app.widgetapp.add_new_feed()

@action_handler("NewGuide")
def on_new_guidel():
    app.widgetapp.add_new_guide()

@action_handler("NewSearchFeed")
def on_new_search_feed():
    app.widgetapp.add_new_search_feed()

@action_handler("NewFeedFolder")
def on_new_feed_folder():
    app.widgetapp.add_new_feed_folder()

@action_handler("RenameFeed")
def on_rename_feed():
    app.widgetapp.rename_something()

@action_handler("RemoveFeeds")
def on_remove_feeds():
    app.widgetapp.remove_current_feed()

@action_handler("UpdateFeeds")
def on_update_feeds():
    app.widgetapp.update_selected_feeds()

@action_handler("UpdateAllFeeds")
def on_update_all_feeds():
    app.widgetapp.update_all_feeds()

@action_handler("ImportFeeds")
def on_import_feeds():
    app.widgetapp.import_feeds()

@action_handler("ExportFeeds")
def on_export_feeds():
    app.widgetapp.export_feeds()

@action_handler("ShareFeed")
def on_share_feed():
    app.widgetapp.share_feed()

@action_handler("CopyFeedURL")
def on_copy_feed_url():
    app.widgetapp.copy_feed_url()

# Playlists menu

@action_handler("NewPlaylist")
def on_new_playlist():
    app.widgetapp.add_new_playlist()

@action_handler("NewPlaylistFolder")
def on_new_playlist_folder():
    app.widgetapp.add_new_playlist_folder()

@action_handler("RenamePlaylist")
def on_rename_playlist():
    app.widgetapp.rename_something()

@action_handler("RemovePlaylists")
def on_remove_playlists():
    app.widgetapp.remove_current_playlist()

# Playback menu

@action_handler("PlayPauseVideo")
def on_play_pause_video():
    app.widgetapp.on_play_clicked()

@action_handler("StopVideo")
def on_play_pause_video():
    app.widgetapp.on_stop_clicked()

@action_handler("NextVideo")
def on_next_video():
    app.widgetapp.on_forward_clicked()

@action_handler("PreviousVideo")
def on_previous_video():
    app.widgetapp.on_previous_clicked()

@action_handler("FastForward")
def on_fast_forward():
    app.widgetapp.on_skip_forward()

@action_handler("Rewind")
def on_rewind():
    app.widgetapp.on_skip_backward()

@action_handler("UpVolume")
def on_up_volume():
    app.widgetapp.up_volume()

@action_handler("DownVolume")
def on_down_volume():
    app.widgetapp.down_volume()

@action_handler("Fullscreen")
def on_fullscreen():
    app.widgetapp.on_fullscreen_clicked()

@action_handler("ToggleDetach")
def on_toggle_detach():
    app.widgetapp.on_toggle_detach_clicked()

# Help menu

@action_handler("About")
def on_about():
    app.widgetapp.about()

@action_handler("Donate")
def on_donate():
    app.widgetapp.open_url(config.get(prefs.DONATE_URL))

@action_handler("Help")
def on_help():
    app.widgetapp.open_url(config.get(prefs.HELP_URL))

@action_handler("Diagnostics")
def on_diagnostics():
    app.widgetapp.diagnostics()

@action_handler("ReportBug")
def on_report_bug():
    app.widgetapp.open_url(config.get(prefs.BUG_REPORT_URL))

@action_handler("Translate")
def on_translate():
    app.widgetapp.open_url(config.get(prefs.TRANSLATE_URL))

@action_handler("Planet")
def on_planet():
    app.widgetapp.open_url(config.get(prefs.PLANET_URL))

# action_group name -> list of MenuItem labels belonging to action_group
action_groups = {
    # group for items that should never be enabled
    'FakeGroup': [
        'NoneAvailable'
        ],
    'NonPlaying': [
        'Open',
        'NewDownload',
        'NewFeed',
        'NewGuide',
        'NewSearchFeed',
        'NewFeedFolder',
        'UpdateAllFeeds',
        'ImportFeeds',
        'ExportFeeds',
        'NewPlaylist',
        'NewPlaylistFolder',
        ],
    'FeedSelected': [
        'ShareFeed',
        'CopyFeedURL'
        ],
    'FeedOrFolderSelected': [
        'RenameFeed',
        ],
    'FeedsSelected': [
        'RemoveFeeds',
        'UpdateFeeds',
        ],
    'PlaylistSelected': [
        'RenamePlaylist',
        ],
    'PlaylistsSelected': [
        'RemovePlaylists',
        ],
    'PlayableSelected': [
        'RenameItem',
        'CopyItemURL',
        'SaveItem',
        ],
    'PlayablesSelected': [
        'RemoveItems',
        ],
    'PlayableVideosSelected': [
        ],
    'PlayPause': [
        'PlayPauseVideo',
        ],
    'Playing': [
        'StopVideo',
        'NextVideo',
        'PreviousVideo',
        'Rewind',
        'FastForward',
        ],
    'PlayingVideo': [
        'Fullscreen',
        'ToggleDetach',
        ],
    }

action_group_map = {}
def recompute_action_group_map():
    for group, actions in action_groups.items():
        for action in actions:
            if action not in action_group_map:
                action_group_map[action] = list()
            action_group_map[action].append(group)
recompute_action_group_map()

def action_group_names():
    return action_groups.keys() + ['AlwaysOn']

def get_action_group_name(action):
    return action_group_map.get(action, ['AlwaysOn'])[0]

def get_all_action_group_name(action):
    return action_group_map.get(action, ['AlwaysOn'])

class MenuManager(signals.SignalEmitter):
    """Updates the menu based on the current selection.

    This includes enabling/disabling menu items, changing menu text for plural
    selection and enabling/disabling the play button.  The play button is
    obviously not a menu item, but it's pretty closely related

    Whenever code makes a change that could possibly affect which menu items
    should be enabled/disabled, it should call the update_menus() method.
    """
    def __init__(self):
        signals.SignalEmitter.__init__(self)
        self.create_signal('enabled-changed')
        self.enabled_groups = set(['AlwaysOn'])
        self.states = {}
        self.play_pause_state = "play"

    def reset(self):
        self.states = {"plural": [], "folder": [], "folders": []}
        self.enabled_groups = set(['AlwaysOn'])
        if app.playback_manager.is_playing:
            self.enabled_groups.add('PlayPause')
            self.enabled_groups.add('Playing')
            if not app.playback_manager.is_playing_audio:
                self.enabled_groups.add('PlayingVideo')
            if app.playback_manager.detached_window is not None:
                self.enabled_groups.add('NonPlaying')
        else:
            self.enabled_groups.add('NonPlaying')

    def _set_play_pause(self):
        if (not app.playback_manager.is_playing or
                app.playback_manager.is_paused):
            self.play_pause_state = 'play'
        else:
            self.play_pause_state = 'pause'

    def _handle_feed_selection(self, selected_feeds):
        """Handle the user selecting things in the feed list.  selected_feeds
        is a list of ChannelInfo objects
        """
        self.enabled_groups.add('FeedsSelected')
        if len(selected_feeds) == 1:
            if selected_feeds[0].is_folder:
                self.states["folder"].append("RemoveFeeds")
            else:
                self.enabled_groups.add('FeedSelected')
            self.enabled_groups.add('FeedOrFolderSelected')
        else:
            if len([s for s in selected_feeds if s.is_folder]) == len(selected_feeds):
                self.states["folders"].append("RemoveFeeds")
            else:
                self.states["plural"].append("RemoveFeeds")
            self.states["plural"].append("UpdateFeeds")

    def _handle_site_selection(self, selected_sites):
        """Handle the user selecting things in the site list.  selected_sites
        is a list of GuideInfo objects
        """
        pass # We don't change menu items for the site tab list

    def _handle_playlist_selection(self, selected_playlists):
        self.enabled_groups.add('PlaylistsSelected')
        if len(selected_playlists) == 1:
            if selected_playlists[0].is_folder:
                self.states["folder"].append("RemovePlaylists")
            self.enabled_groups.add('PlaylistSelected')
        else:
            if len([s for s in selected_playlists if s.is_folder]) == len(selected_playlists):
                self.states["folders"].append("RemovePlaylists")
            else:
                self.states["plural"].append("RemovePlaylists")

    def _handle_static_tab_selection(self, selected_static_tabs):
        """Handle the user selecting things in the static tab list.
        selected_sites is a list of GuideInfo objects
        """
        # we don't change menu items for the static tab list
        pass

    def _update_menus_for_selected_tabs(self):
        selection_type, selected_tabs = app.tab_list_manager.get_selection()
        if selection_type is None:
            pass
        elif selection_type in ('feed', 'audio-feed'):
            app.menu_manager._handle_feed_selection(selected_tabs)
        elif selection_type == 'playlist':
            app.menu_manager._handle_playlist_selection(selected_tabs)
        elif selection_type in ('static', 'library'):
            app.menu_manager._handle_static_tab_selection(selected_tabs)
        elif selection_type == 'site':
            app.menu_manager._handle_site_selection(selected_tabs)
        else:
            raise ValueError("Unknown tab list type: %s" % selection_type)

    def _update_menus_for_selected_items(self):
        """Update the menu items based on the current item list selection.
        """
        selected_items = app.item_list_controller_manager.get_selection()
        downloaded = False
        has_audio = False
        for item in selected_items:
            if item.downloaded:
                downloaded = True
            if item.file_type == 'audio':
                has_audio = True
        if downloaded:
            self.enabled_groups.add('PlayablesSelected')
            if not has_audio:
                self.enabled_groups.add('PlayableVideosSelected')
            if len(selected_items) == 1:
                self.enabled_groups.add('PlayableSelected')
            else:
                self.states["plural"].append("RemoveItems")

        if len(app.item_list_controller_manager.get_current_playlist()) > 0:
            self.enabled_groups.add('PlayPause')
            app.widgetapp.window.videobox.handle_new_selection(True)
        else:
            app.widgetapp.window.videobox.handle_new_selection(False)

    def update_menus(self):
        self.reset()
        self._update_menus_for_selected_tabs()
        self._update_menus_for_selected_items()
        self._set_play_pause()
        self.emit('enabled-changed')
