import json
import requests
from sqlite3 import connect
from datetime import datetime
from twisted.web.client import getPage
from twisted.internet.protocol import Factory
from twisted.internet.defer import inlineCallbacks
from .components.tools import WebClientContextFactory
from .components.commons import MyFplConfig as conf

head = {b"User-Agent": b"Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)"}

DB_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/MyFPL.db'

Factory.noisy = False

class FPlAPi:

    def __init__(self):
        self.baseApiUrl = 'https://fantasy.premierleague.com/api'
        self.bootstrapData = None
        self.playersPoints = None
        self.userData = None
        self.fplDB = MyfplDB()

    def login(self, email: str, password: str) -> dict:
        payload = {
            'login': email,
            'password': password,
            'app': 'plfpl-web',
            'redirect_uri': 'https://fantasy.premierleague.com/a/login'
        }
        with requests.Session() as session:
            try:
                rep = session.post('https://users.premierleague.com/accounts/login/', data=payload, headers=head)
                query = requests.utils.urlparse(rep.url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'state' in params:
                    if params['state'] == 'success':
                        account_detail = session.get('https://fantasy.premierleague.com/api/me/', headers=head).json()
                        if isinstance(account_detail, dict):
                            player_entry_id = account_detail['player']['entry']
                            return {'status': 'success', 'player_id': player_entry_id}
                        else:
                            return {'status': 'failed', 'reason': account_detail}
                    elif params['state'] == 'fail':
                        return {'status': 'failed', 'reason': params['reason']}
            except Exception as e:
                return {'status': 'failed', 'reason': e}

    @classmethod
    def formatNb(cls, number: int) -> int:
        if number:
            return f"{number:,}"
        return 0

    @classmethod
    def squadCost(cls, number: int) -> int:
        if number:
            return f"{number / 10.0}"
        return 0

    def errorCall(self,error=None):
        if error:
            #TODO handle errors
            print(error)

    @inlineCallbacks
    def getUserDetails(self, user_id, callback, gw=None):
        if self.userData and user_id in self.userData:
            if self.bootstrapData:
                if 'current_gw' not in self.userData:
                    curr_gw = next(event for event in self.bootstrapData['events'] if event['id'] == data['current_event'])
                    self.userData['current_gw'] = curr_gw
                if gw:
                    curr_gw = next(event for event in self.bootstrapData['events'] if event['id'] == gw)
                    self.userData['current_gw'] = curr_gw
            callback(self.userData, gw=gw)

        if not self.userData or not user_id in self.userData:
            url = f'{self.baseApiUrl}/entry/{user_id}/'
            sniFactory = WebClientContextFactory(url)
            data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=10).addErrback(self.errorCall)
            if data:
                data = json.loads(data)
                if self.userData is None:
                    self.userData = {}
                self.userData[data['id']] = {}
                self.userData[data['id']]['player_first_name'] = data['player_first_name']
                self.userData[data['id']]['player_last_name'] = data['player_last_name']
                self.userData[data['id']]['country_code'] = data['player_region_iso_code_short']
                self.userData[data['id']]['club_name'] = data['name']
                self.userData[data['id']]['started_event'] = data['started_event']
                self.userData[data['id']]['current_event'] = data['current_event']
                self.userData[data['id']]['total_points'] = self.formatNb(data['summary_overall_points'])
                self.userData[data['id']]['overall_rank'] = self.formatNb(data['summary_overall_rank'])
                self.userData[data['id']]['current_gw_points'] = self.formatNb(data['summary_event_points']) if data['summary_event_points'] else 0
                self.userData[data['id']]['current_gw_rank'] = self.formatNb(data['summary_event_rank']) if data['summary_event_rank'] else 0
                self.userData[data['id']]['leagues'] = data['leagues']
                if self.bootstrapData:
                    self.userData[data['id']]['total_players'] = self.formatNb(self.bootstrapData['total_players'])
                    self.userData['events'] = self.bootstrapData['events']
                    if 'current_gw' not in self.userData:
                        curr_gw = next(event for event in self.bootstrapData['events'] if event['id'] == data['current_event'])
                        self.userData['current_gw'] = curr_gw
                    if gw:
                        curr_gw = next(event for event in self.bootstrapData['events'] if event['id'] == gw)
                        self.userData['current_gw'] = curr_gw
                callback(self.userData, gw=gw)
            else:
                callback('The game is being updated.')

    @inlineCallbacks
    def getBootstrapData(self, callback, loadCurrentFixtures=False):
        data = self.getCachedBootstrapData()
        cache_data = False
        if data is None:
            url = f'{self.baseApiUrl}/bootstrap-static/'
            sniFactory = WebClientContextFactory(url)
            data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=25).addErrback(self.errorCall)
            cache_data = True
        if data:
            data = json.loads(data)
            if cache_data:
                self.fplDB.execQuery('delete from BOOTSTRAP')
                self.fplDB.execQuery('INSERT INTO BOOTSTRAP(BOOTSTRAP_DATA, LAST_UPDATE) values (?, ?)', (json.dumps(data, ensure_ascii=False), datetime.now().strftime('%d-%m-%Y %H:%M'), ))
            self.bootstrapData = data
            if loadCurrentFixtures:
                curr_gw = next(event for event in self.bootstrapData['events'] if event['is_current'])
                if curr_gw['finished'] is False:
                    self.getFixtures(curr_gw['id'], callback)
                else:
                    callback(True)
            else:
                callback(True)

    def getCachedBootstrapData(self):
        data = self.fplDB.queryData('select * from BOOTSTRAP')
        if data:
            data_date = datetime.strptime(data[1], '%d-%m-%Y %H:%M')
            diff = datetime.now() - data_date
            hours = diff.days * 24 + diff.seconds // 3600
            if hours < 1:
                return data[0]
        return None

    @inlineCallbacks
    def getFixtures(self, gw, callback):
        url = f'{self.baseApiUrl}/fixtures/?event={gw}'
        sniFactory = WebClientContextFactory(url)
        data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=10).addErrback(self.errorCall)
        if data:
            data = json.loads(data)
            if self.bootstrapData and data:
                self.bootstrapData['fixtures'] = data
            callback(True)

    @inlineCallbacks
    def getUserPlayers(self, user_id, gw, callback):
        cache_data = False
        if user_id == int(conf.user_id.value):
            if gw['finished']:
                ret = self.fplDB.queryData(f'SELECT * from USER where USER_ID=?', (user_id,))
                if ret:
                    data = self.fplDB.queryData(f'SELECT data from USER_GWS where GW=? and USER_ID=?', (gw['id'], user_id,))
                    if data:
                        data = json.loads(data[0])
                        callback(data)
                        return
                    else:
                        cache_data = True
                else:
                    cache_data = True
                    self.fplDB.execQuery('INSERT INTO USER(USER_ID) values (?)', (user_id, ))

        url = f"{self.baseApiUrl}/entry/{user_id}/event/{gw['id']}/picks/"
        sniFactory = WebClientContextFactory(url)
        data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=10).addErrback(self.errorCall)
        if data:
            data = json.loads(data)
            user_players = {player['element']: player for player in data['picks']}
            user_players['active_chip'] = data['active_chip']
            user_players['points'] = data['entry_history']['points']
            user_players['rank'] = self.formatNb(data['entry_history']['rank'])
            user_players['event_transfers'] = data['entry_history']['event_transfers']
            user_players['event_transfers_cost'] = data['entry_history']['event_transfers_cost']
            user_players['points_on_bench'] = data['entry_history']['points_on_bench']
            element_types = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
            if self.bootstrapData:
                for player in self.bootstrapData['elements']:
                    if player['id'] in user_players:
                        user_players[player['id']]['web_name'] = player['web_name']
                        user_players[player['id']]['element_type'] = element_types[player['element_type']]
                        user_players[player['id']]['team'] = player['team']
                        user_players[player['id']]['team_code'] = player['team_code']
                        user_players[player['id']]['status'] = player['status']
                        user_players[player['id']]['chance_of_playing_next_round'] = player['chance_of_playing_next_round']
                        if 'fixtures' in self.bootstrapData and gw['finished'] is False:
                            for team in self.bootstrapData['fixtures']:
                                if user_players[player['id']]['team'] in (team['team_a'], team['team_h']):
                                    if user_players[player['id']]['team'] == team['team_a']:
                                        user_players[player['id']]['team_against'] = self.getTeamName(team['team_h'])
                                        user_players[player['id']]['isPlayinsAway'] = True
                                    else:
                                        user_players[player['id']]['team_against'] = self.getTeamName(team['team_a'])
                                        user_players[player['id']]['isPlayinsAway'] = False
                                    user_players[player['id']]['game_started'] = team['started']
                                    user_players[player['id']]['game_finished'] = team['finished']
                if self.playersPoints:
                    for player in self.playersPoints['elements']:
                        if player['id'] in user_players:
                            user_players[player['id']]['stats'] = player['stats']
                if cache_data:
                    self.fplDB.execQuery('INSERT INTO USER_GWS(GW, DATA, USER_ID) values (?, ?, ?)', (gw['id'], json.dumps(user_players, ensure_ascii=False), user_id))
                callback(user_players)

    #TODO get user current team
    # @inlineCallbacks
    # def loadUserCurrentTeam(self, user_id, callback):
    #     url = f'{self.baseApiUrl}/my-team/{user_id}/'
    #     sniFactory = WebClientContextFactory(url)
    #     data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=10).addErrback(self.errorCall)
    #     print(data)

    def getTeamName(self, teamCode):
        teamName = '-'
        if self.bootstrapData and 'fixtures' in self.bootstrapData:
            teamName = next(team['short_name'] for team in self.bootstrapData['teams'] if team['id'] == teamCode)
        return teamName

    @inlineCallbacks
    def loadPlayerPoints(self, gw, callback):
        if gw['finished']:
            ret = self.fplDB.queryData(f'SELECT DATA from GWS_PLAYERS_POINTS where GW=?', (gw['id'],))
            if ret:
                self.playersPoints = json.loads(ret[0])
                callback()
                return
        url = f"{self.baseApiUrl}/event/{gw['id']}/live/"
        sniFactory = WebClientContextFactory(url)
        data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=10).addErrback(self.errorCall)
        if data:
            data = json.loads(data)
            self.fplDB.execQuery('INSERT INTO GWS_PLAYERS_POINTS(GW, DATA) values (?, ?)', (gw['id'], json.dumps(data, ensure_ascii=False), ))
            self.playersPoints = data
            callback()

    @inlineCallbacks
    def getUserHistory(self, user_id, callback):
        url = f'{self.baseApiUrl}/entry/{user_id}/history/'
        sniFactory = WebClientContextFactory(url)
        data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=10).addErrback(self.errorCall)
        if data:
            data = json.loads(data)
            callback(data)

    @inlineCallbacks
    def getLeagueStanding(self, league_id, callback, p=1):
        url = f'{self.baseApiUrl}/leagues-classic/{league_id}/standings/?page_standings={p}'
        sniFactory = WebClientContextFactory(url)
        data = yield getPage(str.encode(url), contextFactory=sniFactory, method=b"GET", headers=head, timeout=10).addErrback(self.errorCall)
        if data:
            data = json.loads(data)
            callback(data)


class MyfplDB:
    
    def __init__(self):
        self.createTables()

    def createTables(self):
        self.execQuery('CREATE TABLE IF NOT EXISTS `BOOTSTRAP` (`BOOTSTRAP_DATA` JSON , `LAST_UPDATE` DATE)')
        self.execQuery('CREATE TABLE IF NOT EXISTS `USER` (`USER_ID` INTEGER PRIMARY KEY)')
        self.execQuery('CREATE TABLE IF NOT EXISTS `USER_GWS` (`GW` INTEGER PRIMARY KEY, `DATA` JSON, `USER_ID` INTEGER, FOREIGN KEY(USER_ID) REFERENCES USER (USER_ID) ON DELETE CASCADE)')
        self.execQuery('CREATE TABLE IF NOT EXISTS `GWS_PLAYERS_POINTS` (`GW` INTEGER, `DATA` JSON)')

    def execQuery(self, cmd, params=()):
        with connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(cmd, params)

    def queryData(self, cmd, params=()):
        with connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(cmd, params)
            return cur.fetchone()