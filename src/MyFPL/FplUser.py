# -*- coding: UTF-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from enigma import gFont, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_VALIGN_CENTER,BT_SCALE ,BT_KEEP_ASPECT_RATIO, BT_VALIGN_CENTER
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename , SCOPE_PLUGINS
from .FPlApi import FPlAPi
from .components.FplComponents import MyFplPlayerLayout, MyFplLeaguesLayout, MyFpUserLayout
from .components.commons import MyFplConfig as conf
from .components.tools import readFromFile, MultiContentTemplateColor


class MyFplUserDetails(Screen):

    def __init__(self, session, user_id):
        Screen.__init__(self, session)
        self.session = session
        self.user_id = int(user_id)
        self.user_details = None
        self.gwHistoryDialog = None
        self.leaguesStandingDialog = None
        self.skin = readFromFile('assets/skin/FplUser.xml')
        self['UserLayout'] = MyFpUserLayout()
        self['PlayersLayout'] = MyFplPlayerLayout()
        self['LeaguesLayout'] = MyFplLeaguesLayout()
        self['FPlActions'] = ActionMap(['FPlActions'], {
            'cancel': self.exit,
            'up': self.up,
            'down': self.down,
            'left': self.left,
            'right': self.right,
            'ok': self.ok,
            'green': self.green,
            'blue': self.blue,
            'red': self.red
        }, -1)
        self.fplApi = FPlAPi()
        self.onLayoutFinish.append(self.loadBootstrapData)

    def loadBootstrapData(self, loaded=False):
        if loaded:
            self.fplApi.getUserDetails(self.user_id, self.getUserData)
        else:
            self.fplApi.getBootstrapData(self.loadBootstrapData, loadCurrentFixtures=True)

    def getUserData(self, data=None, gw=None):
        if data:
            if isinstance(data, dict):
                self.user_details = data
                self['UserLayout'].setUserData(self.user_details[self.user_id])
                self['UserLayout'].show()
                self.getUserPlayers(gw=gw)
                self.buildUserLeaguesList()
            else:
                self.session.openWithCallback(self.exit, MessageBox, data, MessageBox.TYPE_ERROR)
        else:
            self.fplApi.getUserDetails(self.user_id, self.getUserData, gw=gw)

    def getUserPlayers(self, data=None, gw=None):
        if not self.fplApi.playersPoints or gw is not None:
            curr_gw = self.user_details['current_gw']
            self.fplApi.loadPlayerPoints(curr_gw, self.getUserPlayers)
        else:
            if data:
                if isinstance(data, dict):
                    self.showUserPlayersDetails(data)
            else:
                if self.user_details:
                    curr_gw = self.user_details['current_gw']
                    self.fplApi.getUserPlayers(self.user_id, curr_gw, self.getUserPlayers)

    def showUserPlayersDetails(self, user_players=None):
        if user_players and self.user_details:
            self['PlayersLayout'].showLayout(user_players,  self.user_details['current_gw'])
            self['PlayersLayout'].show()

    def buildUserLeaguesList(self):
        if self.user_details:
            leagues = {}
            for league in self.user_details[self.user_id]['leagues']['classic']:
                if league['league_type'] not in leagues:
                    leagues[league['league_type']] = []
                    leagues[league['league_type']].append(league)
                else:
                    leagues[league['league_type']].append(league)
            _list = []
            for league_type in leagues:
                _list.append((None, league_type))
                for league in leagues[league_type]:
                    _list.append((league, None))
            self['LeaguesLayout'].buildEntries(_list)
            self['LeaguesLayout'].show()

    def ok(self):
        if self['LeaguesLayout'].getCurrent() is not None:
            self['FPlActions'].execEnd()
            league = self['LeaguesLayout'].getCurrent()[0]
            self.leaguesStandingDialog = self.session.instantiateDialog(UserLeaguesStandingDialog, self.user_id, league['id'], self.leaguesStandingCallback)
            self.leaguesStandingDialog.show()
            self.leaguesStandingDialog['FPlLeaguesActions'].execBegin()

    def green(self):
        if self.user_details:
            if self.user_details['current_gw']['highest_scoring_entry'] and self.user_id != self.user_details['current_gw']['highest_scoring_entry']:
                self.user_id = self.user_details['current_gw']['highest_scoring_entry']
                self['LeaguesLayout'].hide()
                self['PlayersLayout'].hide()
                self['UserLayout'].hide()
                self.getUserData()
            
    def blue(self):
        if self.user_details:
            self['FPlActions'].execEnd()
            self.gwHistoryDialog = self.session.instantiateDialog(UserGameWeeksDialog, self.user_id, self.gwHistoryCallback, self.user_details['current_gw']['id'])
            self.gwHistoryDialog.show()
            self.gwHistoryDialog['FPlGWActions'].execBegin()

    def gwHistoryCallback(self, gw=None, gw_rank=None):
        if gw:
            self['LeaguesLayout'].hide()
            self['PlayersLayout'].hide()
            self['UserLayout'].hide()
            self.getUserData(gw=gw)
        self['FPlActions'].execBegin()
        if self.gwHistoryDialog:
            self.gwHistoryDialog['FPlGWActions'].execEnd()
            self.session.deleteDialog(self.gwHistoryDialog)
            self.gwHistoryDialog = None

    def leaguesStandingCallback(self, user_id=None):
        if user_id:
            if self.user_id != user_id:
                gw = self.user_details[self.user_id]['current_event']
                self.user_id = user_id
                self['LeaguesLayout'].hide()
                self['PlayersLayout'].hide()
                self['UserLayout'].hide()
                self.getUserData(gw=gw)
        self['FPlActions'].execBegin()
        if self.leaguesStandingDialog:
            self.leaguesStandingDialog['FPlLeaguesActions'].execEnd()
            self.session.deleteDialog(self.leaguesStandingDialog)
            self.leaguesStandingDialog = None

    def up(self):
        self['LeaguesLayout'].up()

    def down(self):
        self['LeaguesLayout'].down()

    def left(self):
        self['LeaguesLayout'].pageUp()

    def right(self):
        self['LeaguesLayout'].pageDown()

    def red(self):
        if conf.isLoged.value:
            conf.isLoged.value = False
            conf.isLoged.save()
            self.close()

    def exit(self, ret=None):
        if not ret:
            if int(conf.user_id.value) != self.user_id:
                gw = self.user_details[self.user_id]['current_event']
                self.user_id = int(conf.user_id.value)
                self['LeaguesLayout'].hide()
                self['PlayersLayout'].hide()
                self['UserLayout'].hide()
                self.getUserData(gw=gw)
            else:
                self.close()


class UserGameWeeksDialog(Screen):

    def __init__(self, session, user_id, cb_func, curr_gw):
        Screen.__init__(self, session)
        self.user_id = user_id
        self.cb_func = cb_func
        self.curr_gw = curr_gw
        self.skin = readFromFile('assets/skin/FplGWDialog.xml')
        self['events'] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self['events'].l.setBuildFunc(self.buildEntry)
        self["events"].l.setFont(0, gFont("Myfpl-Regular", 23))
        self["events"].l.setFont(1, gFont("Myfpl-Bold", 23))
        self['FPlGWActions'] = ActionMap(['FPlActions'], {
            'cancel': self.exit,
            'ok': self.ok,
            'up': self.up,
            'down': self.down,
            'left': self.left,
            'right': self.right,
        }, -1)
        self.upicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/up.png"))
        self.downicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/down.png"))
        self.sameicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/same.png"))
        self.fplApi = FPlAPi()
        self.onLayoutFinish.append(self.loadUserHistory)

    def ok(self):
        if self['events'].getCurrent() is not None:
            event = self['events'].getCurrent()[0]
            if self.cb_func:
                self.cb_func(event['event'])

    def left(self):
        self['events'].pageUp()

    def right(self):
        self['events'].pageDown()

    def up(self):
        self['events'].up()

    def down(self):
        self['events'].down()

    def loadUserHistory(self, data=None):
        if data:
            if isinstance(data, dict):
                if data['current']:
                    self.buildHistoryList(data)
        else:
            self.fplApi.getUserHistory(self.user_id, self.loadUserHistory)

    def buildHistoryList(self, data):
        _list = [(None, ['GW', 'OR', '#', 'OP', 'GWR', 'GWP', 'PB', 'TM', 'TC', '£'])]
        idx_to = 0
        for idx,event in enumerate(data['current'][::-1]):
            if self.curr_gw == event['event']:
                idx_to = idx + 1
            _list.append((event, None))
        self['events'].l.setList(_list)
        self['events'].moveToIndex(idx_to)

    def buildEntry(self, event, head):
        res = [None]
        if head:
            res.append(MultiContentEntryText(pos=(20,52),size=(90,30),text=head[0],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(140,52),size=(90,30),text=head[1],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(295,52),size=(90,30),text=head[2],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(355,52),size=(90,30),text=head[3],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(515,52),size=(90,30),text=head[4],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(675,52),size=(90,30),text=head[5],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(835,52),size=(90,30),text=head[6],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(995,52),size=(90,30),text=head[7],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(1155,52),size=(90,30),text=head[8],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(1315,52),size=(90,30),text=head[9],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
        if event:
            res.append(MultiContentEntryText(pos=(0,0),size=(1485,2), backcolor=MultiContentTemplateColor('#efefef')))
            res.append(MultiContentEntryText(pos=(20,0),size=(90,85), font=1,text=f"GW{event['event']}",flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(140,0),size=(130,85),text=str(self.fplApi.formatNb(event['overall_rank'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))

            icon = self.sameicon
            if event['rank']:
                icon = self.upicon if event['rank'] < event['overall_rank'] else self.downicon if event['rank'] > event['overall_rank'] else self.sameicon
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(295,0),size=(25,85),png=icon, flags=BT_SCALE|BT_VALIGN_CENTER|BT_KEEP_ASPECT_RATIO))

            res.append(MultiContentEntryText(pos=(355,0),size=(130,85),text=str(self.fplApi.formatNb(event['total_points'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(515,0),size=(130,85),text=str(self.fplApi.formatNb(event['rank'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(675,0),size=(130,85),text=str(self.fplApi.formatNb(event['points'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(835,0),size=(130,85),text=str(self.fplApi.formatNb(event['points_on_bench'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(995,0),size=(130,85),text=str(self.fplApi.formatNb(event['event_transfers'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(1155,0),size=(130,85),text=str(self.fplApi.formatNb(event['event_transfers_cost'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(1315,0),size=(130,85),text=self.fplApi.squadCost(event['value']),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
        return res

    def exit(self):
        if self.cb_func:
            self.cb_func()
        else:
            self.close()

class UserLeaguesStandingDialog(Screen):

    def __init__(self, session, user_id, league_id, cb_func):
        Screen.__init__(self, session)
        self.league_id = league_id
        self.user_id = user_id
        self.cb_func = cb_func
        self.current_page = {'curr_page': 1, 'has_next': False}
        self.skin = readFromFile('assets/skin/FplLeaguesStandingDialog.xml')
        self['standing'] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self['standing'].l.setBuildFunc(self.buildEntry)
        self["standing"].l.setFont(0, gFont("Myfpl-Regular", 23))
        self["standing"].l.setFont(1, gFont("Myfpl-Bold", 23))
        self['title'] = Label()
        self['next'] = Pixmap()
        self['next'].hide()
        self['previous'] = Pixmap()
        self['previous'].hide()
        self['FPlLeaguesActions'] = ActionMap(['FPlActions'], {
            'cancel': self.exit,
            'ok': self.ok,
            'up': self.up,
            'down': self.down,
            'left': self.left,
            'right': self.right,
            'next': self.next,
            'previous': self.previous
        }, -1)
        self.upicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/up.png"))
        self.downicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/down.png"))
        self.sameicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/same.png"))
        self.fplApi = FPlAPi()
        self.onLayoutFinish.append(self.loadLeagueStanding)

    def ok(self):
        if self['standing'].getCurrent() is not None:
            entry = self['standing'].getCurrent()[0]
            if self.cb_func:
                self.cb_func(entry['entry'])

    def next(self):
        if self.current_page['has_next']:
            p = self.current_page['curr_page'] + 1
            self.fplApi.getLeagueStanding(self.league_id, self.loadLeagueStanding, p=p)
            self["standing"].hide()

    def previous(self):
        if self.current_page['curr_page'] >= 2:
            p = self.current_page['curr_page'] - 1
            self.fplApi.getLeagueStanding(self.league_id, self.loadLeagueStanding, p=p)
            self["standing"].hide()

    def left(self):
        self['standing'].pageUp()

    def right(self):
        self['standing'].pageDown()

    def up(self):
        self['standing'].up()

    def down(self):
        self['standing'].down()

    def loadLeagueStanding(self, data=None):
        if data:
            self.buildStandingList(data)
            self.current_page['curr_page'] = data['standings']['page']
            self.current_page['has_next'] = data['standings']['has_next']
            if data['standings']['page'] >= 2:
                self['previous'].show()
            else:
                self['previous'].hide()
            if data['standings']['has_next']:
                self['next'].show()
            else:
                self['next'].hide()
            self['title'].setText(f"League - {data['league']['name']}")
        else:
            self.fplApi.getLeagueStanding(self.league_id, self.loadLeagueStanding)

    def buildStandingList(self, data):
        if isinstance(data, dict):
            _list = [(None, ['Rank', 'Team & Manager', 'GW', 'TOT'])]
            for entry in data['standings']['results']:
                _list.append((entry, None))
            self['standing'].l.setList(_list)
            self['standing'].moveToIndex(0)
            self["standing"].show()

    def buildEntry(self, entry, head):
        res = [None]
        if head:
            res.append(MultiContentEntryText(pos=(20,38),size=(90,30),text=head[0],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(480,38),size=(200,30),text=head[1],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(1100,38),size=(200,30),text=head[2],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
            res.append(MultiContentEntryText(pos=(1300,38),size=(200,30),text=head[3],flags=RT_HALIGN_LEFT, color=MultiContentTemplateColor('#7a7a7a')))
        if entry:
            color = MultiContentTemplateColor('#37003c')
            color_sel = MultiContentTemplateColor('white')
            backcolor = MultiContentTemplateColor('white')
            res.append(MultiContentEntryText(pos=(0,0),size=(1485,2), backcolor=MultiContentTemplateColor('#efefef')))

            # if self.user_id == entry['entry']:
            #     color = color_sel = MultiContentTemplateColor('#00ff87')
            #     backcolor = MultiContentTemplateColor('#37003c')
            #     res.append(MultiContentEntryText(pos=(0,0),size=(1485,70), backcolor=MultiContentTemplateColor('#37003c')))

            res.append(MultiContentEntryText(pos=(20,0),size=(250,70),text=str(entry['rank']),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))

            icon = self.upicon if entry['rank'] < entry['last_rank'] else self.downicon if entry['rank'] > entry['last_rank'] else self.sameicon
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(295,0),size=(25,70),png=icon, flags=BT_SCALE|BT_VALIGN_CENTER|BT_KEEP_ASPECT_RATIO))
            
            res.append(MultiContentEntryText(pos=(480,2),size=(385,35),text=entry['entry_name'], font=1,flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(480,32),size=(385,35),text=entry['player_name'],flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))

            res.append(MultiContentEntryText(pos=(1100,0),size=(130,70),text=str(self.fplApi.formatNb(entry['event_total'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
            res.append(MultiContentEntryText(pos=(1300,0),size=(130,70),text=str(self.fplApi.formatNb(entry['total'])),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT))
        return res

    def exit(self):
        if self.cb_func:
            self.cb_func()
        else:
            self.close()