from Components.GUIComponent import GUIComponent
from enigma import eWidget, eListbox, eListboxPythonMultiContent, eLabel, ePixmap, gFont, eSize, ePoint, BT_VALIGN_CENTER, BT_ALPHABLEND, BT_ALPHATEST, RT_HALIGN_RIGHT, RT_HALIGN_LEFT, RT_WRAP, RT_VALIGN_CENTER, RT_HALIGN_CENTER, BT_SCALE ,BT_KEEP_ASPECT_RATIO
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from skin import parseFont, parseColor
from Tools.Directories import resolveFilename , SCOPE_PLUGINS , fileExists
from Tools.LoadPixmap import LoadPixmap
from twisted.web.client import downloadPage
from Plugins.Extensions.MyFPL.components.tools import WebClientContextFactory
from Plugins.Extensions.MyFPL.FPlApi import FPlAPi
from .tools import MultiContentTemplateColor
import html

class MyFplPlayerLayout(GUIComponent):

    def __init__(self):
        GUIComponent.__init__(self)
        self.gkContent = eListboxPythonMultiContent()
        self.gkContent.setBuildFunc(self.buildEntry)
        self.dfContent = eListboxPythonMultiContent()
        self.dfContent.setBuildFunc(self.buildEntry)
        self.mdContent = eListboxPythonMultiContent()
        self.mdContent.setBuildFunc(self.buildEntry)
        self.atContent = eListboxPythonMultiContent()
        self.atContent.setBuildFunc(self.buildEntry)
        self.subsContent = eListboxPythonMultiContent()
        self.subsContent.setBuildFunc(self.buildEntry)

        self.gwDetailsContent = eListboxPythonMultiContent()
        self.gwDetailsContent.setBuildFunc(self.buildGwDetailsEntry)

        self.font = gFont("Myfpl-Regular", 23)
        self.font_bold = gFont("Myfpl-Bold", 23)
        self.backgroundColor = parseColor("white")
        self.foregroundColor = parseColor("#37003c")

        self.backgroundPixmap = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/pitch.png")
        self.totwIcon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/totw.png")
        self.captainIcon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/captain.png")
        self.tripleIcon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/triple.png")
        self.viceIcon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/vice.png")
        self.tripleViceIcon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/tripleVice.png")
        self.d75Icon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/75.png")
        self.d50Icon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/50.png")
        self.d25Icon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/25.png")
        self.d0Icon = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/images/icons/0.png")
        self.active_chip = None

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value) in self.skinAttributes:
            if attrib == "font":
                self.font = parseFont(value, ((1,1),(1,1)))
            elif attrib == "font_bold":
                self.font_bold = parseFont(value, ((1,1),(1,1)))
            elif attrib == "backgroundColor":
                self.backgroundColor = parseColor(value)
            elif attrib == "foregroundColor":
                self.foregroundColor = parseColor(value)
            elif attrib == "backgroundPixmap":
                self.backgroundPixmap = LoadPixmap(value)
            else:
                attribs.append((attrib, value))

        for _list in (self.gkContent, self.dfContent, self.mdContent, self.atContent, self.subsContent, self.gwDetailsContent):
            _list.setFont(0, self.font)
            _list.setFont(1, self.font_bold)
            _list.setFont(2, gFont("Myfpl-Bold", 95))
            _list.setFont(3, gFont("Myfpl-Bold", 15))
            _list.setFont(4, gFont("Myfpl-Regular", 18))
            _list.setFont(5, gFont("Myfpl-icons", 33))

        self.backPixamp.setAlphatest(BT_ALPHATEST)
        self.backPixamp.setScale(1)

        self.backPixamp.hide()
        self.skinAttributes = attribs
        return GUIComponent.applySkin(self, desktop, parent)

    GUI_WIDGET = eWidget

    def postWidgetCreate(self, instance):
        self.instance = instance
        self.instance.setBackgroundColor(self.backgroundColor)

        self.gwDetailsList = eListbox(self.instance)
        self.gwDetailsList.setSelectionEnable(0)
        self.gwDetailsList.resize(eSize(1450,175))
        self.gwDetailsList.move(ePoint(10,7))
        self.gwDetailsList.setBackgroundColor(parseColor('#5dd5fd'))
        self.gwDetailsList.setZPosition(1)
        self.gwDetailsList.setContent(self.gwDetailsContent)
        self.gwDetailsList.setItemHeight(175)
        self.gwDetailsList.setTransparent(1)

        self.gkList = eListbox(self.instance)
        self.gkList.setSelectionEnable(0)
        self.gkList.resize(eSize(1050,165))
        self.gkList.move(ePoint(195,200))
        self.gkList.setZPosition(1)
        self.gkList.setContent(self.gkContent)
        self.gkList.setItemHeight(165)
        self.gkList.setTransparent(1)

        self.dfList = eListbox(self.instance)
        self.dfList.setSelectionEnable(0)
        self.dfList.resize(eSize(1050,165))
        self.dfList.move(ePoint(self.gkList.position().x() + 7,self.gkList.size().height() + 195))
        self.dfList.setZPosition(1)
        self.dfList.setContent(self.dfContent)
        self.dfList.setItemHeight(165)
        self.dfList.setTransparent(1)

        self.mdList = eListbox(self.instance)
        self.mdList.setSelectionEnable(0)
        self.mdList.resize(eSize(1080,165))
        self.mdList.move(ePoint(self.dfList.position().x()-10,self.dfList.size().height() + 360))
        self.mdList.setZPosition(1)
        self.mdList.setContent(self.mdContent)
        self.mdList.setItemHeight(165)
        self.mdList.setTransparent(1)

        self.atList = eListbox(self.instance)
        self.atList.setSelectionEnable(0)
        self.atList.resize(eSize(1080,165))
        self.atList.move(ePoint(self.dfList.position().x()-10,self.dfList.size().height() + 525))
        self.atList.setZPosition(1)
        self.atList.setContent(self.atContent)
        self.atList.setItemHeight(165)
        self.atList.setTransparent(1)

        self.subsList = eListbox(self.instance)
        self.subsList.setSelectionEnable(0)
        self.subsList.resize(eSize(1400,165))
        self.subsList.move(ePoint(25,self.dfList.size().height() + 714))
        self.subsList.setZPosition(1)
        self.subsList.setContent(self.subsContent)
        self.subsList.setItemHeight(165)
        self.subsList.setTransparent(1)
        
        self.backPixamp = ePixmap(self.instance)

    def preWidgetRemove(self, instance):
        self.instance = None

    def showLayout(self, players_detail, curr_gw):
        if self.instance:
            self.backPixamp.resize(eSize(self.instance.size().width(),self.instance.size().height()))
            self.backPixamp.setPixmap(self.backgroundPixmap)
            self.backPixamp.show()

            self.active_chip = players_detail['active_chip']
            gw_detail = curr_gw
            gw_detail['UserPoints'] = players_detail['points']
            gw_detail['current_gw_rank'] = players_detail['rank']
            gw_detail['event_transfers'] = players_detail['event_transfers']
            gw_detail['event_transfers_cost'] = players_detail['event_transfers_cost']
            self.gwDetailsContent.setList([(gw_detail,)])

            _gk = []
            _def = []
            _med = []
            _for = []
            _subs = []
            for _,v in players_detail.items():
                if isinstance(v, dict):
                    if v['position'] < 12:
                        if v['element_type'] == 'Defender':
                            _def.append((v,))
                        elif v['element_type'] == 'Midfielder':
                            _med.append((v,))
                        elif v['element_type'] == 'Forward':
                            _for.append((v,))
                        elif v['element_type'] == 'Goalkeeper':
                            _gk.append((v,))
                    else:
                        _subs.append((v,))

            self.gkContent.setList([(_gk, )])
            self.dfContent.setList([(None,_def, )])
            self.mdContent.setList([(None,None, _med, )])
            self.atContent.setList([(None,None, None,_for, )])
            self.subsContent.setList([(None,None, None,None,_subs, )])


    def buildGwDetailsEntry(self, gw):
        res = [None]
        # print(gw)
        size = self.gwDetailsList.size()
        res.append(MultiContentEntryText(pos=(70, 100),size=(180,33),text='Average Points', font=4, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))
        res.append(MultiContentEntryText(pos=(70, 138),size=(180,33),text=str(gw['average_entry_score']), flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))

        res.append(MultiContentEntryText(pos=(340, 100),size=(180,33),text='Highest Points', font=1, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))
        res.append(MultiContentEntryText(pos=(340, 138),size=(180,33),text=str(gw['highest_score']), flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))

        res.append(MultiContentEntryText(pos=(520, 100),size=(33,33),text=str(html.unescape("&#xe941;")), font=5, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('green'), backcolor=MultiContentTemplateColor('white')))

        res.append(MultiContentEntryText(pos=(860, 100),size=(180,33),text='GW Rank', font=4, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))
        res.append(MultiContentEntryText(pos=(860, 138),size=(180,33),text=str(gw['current_gw_rank']), flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))

        res.append(MultiContentEntryText(pos=(1100, 100),size=(180,33),text='Transfers', font=1, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))
        # res.append(MultiContentEntryText(pos=(1250, 100),size=(33,33),text=str(html.unescape("&#xe941;")), font=5, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('yellow'), backcolor=MultiContentTemplateColor('white')))
        txt = f"{gw['event_transfers']} (-{gw['event_transfers_cost']} pts)" if gw['event_transfers_cost'] > 0 else str(gw['event_transfers'])
        res.append(MultiContentEntryText(pos=(1100, 138),size=(180,33),text=txt, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('white')))

        res.append(MultiContentEntryText(pos=((size.width() // 2) - 95, 0),size=(180,33),text=str(gw['name']), font=1, color=MultiContentTemplateColor('#37003c')))
        res.append(MultiContentEntryText(pos=((size.width() // 2) - 103, 55),size=(180,120),text=str(gw['UserPoints']), font=2, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#00ff87'), backcolor=MultiContentTemplateColor('#37003c')))
        if self.active_chip:
            txt = 'Triple Captain played' if self.active_chip == '3xc' else 'Wildcard played' if self.active_chip == 'wildcard' else 'Free Hit played' if self.active_chip == 'freehit' else 'Bench Boost played'
            res.append(MultiContentEntryText(pos=((size.width() // 2) - 103, 30),size=(180,33),text=txt, font=3, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor('#05fa87')))

        txt = 'Latest Points'
        if gw['finished']:
            txt = 'Final Points'
        res.append(MultiContentEntryText(pos=((size.width() // 2) - 103, 152),size=(180,22),text=txt, font=3, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, color=MultiContentTemplateColor('white'), backcolor=MultiContentTemplateColor('#37003c')))
        return res

    def buildEntry(self, gkData=None, defData=None, midData=None, ForData=None, subsData=None):
        if gkData:
            margin = 440
            res = self.entries(gkData, margin, self.gkList, self.gkContent)
        if defData:
            margin = 120 if len(defData) == 3 else 55 if len(defData) == 4 else 10
            res = self.entries(defData, margin, self.dfList, self.dfContent)
        if midData:
            margin = 123 if len(midData) == 3 else 57 if len(midData) == 4 else 232 if len(midData) == 2 else 17
            res = self.entries(midData, margin, self.mdList, self.mdContent)
        if ForData:
            margin = 123 if len(ForData) == 3 else 232 if len(ForData) == 2 else 440
            res = self.entries(ForData, margin, self.atList, self.atContent)
        if subsData:
            margin = 120
            res = self.entries(subsData, margin, self.subsList, self.subsContent)
        return res

    def entries(self, players_data, margin, eList, content):
        res = [None]
        x = margin
        for player in players_data:
            player = player[0]
            name_back_color = MultiContentTemplateColor("#37003c")
            name_text_color = MultiContentTemplateColor('white')
            ic_info = None
            if player['status'] in ('d', 'i', 's'):
                if player['chance_of_playing_next_round'] == 75:
                    name_back_color = MultiContentTemplateColor('#ffe65b')
                    name_text_color = MultiContentTemplateColor("#2f2f2f")
                    ic_info = self.d75Icon
                elif player['chance_of_playing_next_round'] < 75 and player['chance_of_playing_next_round'] > 26:
                    name_back_color = MultiContentTemplateColor('#ffab1b')
                    name_text_color = MultiContentTemplateColor("#2f2f2f")
                    ic_info = self.d50Icon
                elif player['chance_of_playing_next_round'] >= 25 and player['chance_of_playing_next_round'] > 0:
                    name_back_color = MultiContentTemplateColor('#d44401')
                    ic_info = self.d25Icon
                elif player['chance_of_playing_next_round'] == 0:
                    name_back_color = MultiContentTemplateColor('#c0020d')
                    ic_info = self.d0Icon

            shirt = f"shirt_{player['team_code']}_1-66.png" if player['element_type'] == 'Goalkeeper' else f"shirt_{player['team_code']}-66.png"
            s_path = resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/teams/")
            shirt_path = f"{s_path}/{shirt}"
            if fileExists(shirt_path):
                ptr = LoadPixmap(shirt_path)
                if ptr:
                    res.append(MultiContentEntryPixmapAlphaBlend(pos=(x+60,0),size=(100,75),png=ptr, flags=BT_SCALE|BT_KEEP_ASPECT_RATIO))
            else:
                index = eList.getCurrentIndex()
                self.downloadShirt(shirt_path, shirt, index, content)

            res.append(MultiContentEntryPixmapAlphaBlend(pos=(x+130,2),size=(24,24),png=ic_info, flags=BT_SCALE|BT_KEEP_ASPECT_RATIO))
            if player['is_captain']:
                c_icon = self.captainIcon 
                if self.active_chip and self.active_chip == '3xc':
                    c_icon = self.tripleIcon
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(x+130,28),size=(24,24),png=c_icon))
            elif player['is_vice_captain']:
                v_icon = self.viceIcon 
                if self.active_chip and self.active_chip == '3xc':
                    v_icon = self.tripleViceIcon
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(x+130,28),size=(24,24),png=v_icon))
            if player['stats']['in_dreamteam']:
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(x+130,55),size=(24,24),png=self.totwIcon))
            res.append(MultiContentEntryText(pos=(x, 80),size=(180,35),text=str(player['web_name']), font=1, flags=RT_VALIGN_CENTER|RT_HALIGN_CENTER, color=name_text_color, backcolor=name_back_color))
            
            score = player['stats']['total_points'] if player['multiplier'] == 0 else player['stats']['total_points'] * player['multiplier']
            if 'game_started' in player:
                if player['game_started'] is False:
                    # if player['game_finished'] is False:
                    if player['isPlayinsAway']:
                        score = f"{player['team_against']} (A)"
                    else:
                        score = f"{player['team_against']} (H)"
            res.append(MultiContentEntryText(pos=(x, 115),size=(180,35),text=str(score), font=1, flags=RT_VALIGN_CENTER|RT_HALIGN_CENTER, color=MultiContentTemplateColor('#37003c'), backcolor=MultiContentTemplateColor("#05fa87")))
            x += 200 + margin

        return res

    def downloadShirt(self, shirt_path, shirt, idx, _list):
        url = f'https://fantasy.premierleague.com/dist/img/shirts/standard/{shirt}'
        sniFactory = WebClientContextFactory(url)
        downloadPage(str.encode(url), shirt_path, contextFactory=sniFactory, timeout=10, agent=b'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2').addCallback(self.downloadCallback, idx, _list).addErrback(self.error)

    def downloadCallback(self, data, idx, _list):
        _list.invalidateEntry(idx)

    def error(self,error=None):
        if error:
            print(error)


class MyFplLeaguesLayout(GUIComponent):

    def __init__(self):
        GUIComponent.__init__(self)
        self.list = []
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildEntry)
        self.font = gFont("Myfpl-Regular", 23)
        self.font_bold = gFont("Myfpl-Bold", 23)
        self.backgroundColor = parseColor("white")
        self.backgroundColorSelected = parseColor("#37003c")
        self.foregroundColor = parseColor("#37003c")
        self.foregroundColorSelected = parseColor("white")
        self.upicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/up.png"))
        self.downicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/down.png"))
        self.sameicon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/icons/same.png"))

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value) in self.skinAttributes:
            if attrib == "font":
                self.font = parseFont(value, ((1,1),(1,1)))
            elif attrib == "font_bold":
                self.font_bold = parseFont(value, ((1,1),(1,1)))
            elif attrib == "backgroundColor":
                self.backgroundColor = parseColor(value)
            elif attrib == "foregroundColorSelected":
                self.foregroundColorSelected = parseColor(value)
            elif attrib == "backgroundColorSelected":
                self.backgroundColorSelected = parseColor(value)
            elif attrib == "backgroundPixmap":
                self.backgroundPixmap = LoadPixmap(value)
            elif attrib == "backgroundColorSelected":
                self.backgroundColorSelected = parseColor(value)
            else:
                attribs.append((attrib, value))

        self.l.setFont(0, self.font)
        self.l.setFont(1, self.font_bold)

        self.backPixamp.setAlphatest(BT_ALPHATEST)
        self.backPixamp.setZPosition(1)
        self.backPixamp.setScale(1)

        self.titleLabel.setFont(gFont("Myfpl-Bold", 23))
        self.titleLabel.setBackgroundColor(parseColor("#5dd5fd"))
        self.titleLabel.setForegroundColor(self.foregroundColor)
        self.titleLabel.setVAlign(eLabel.alignCenter)
        self.titleLabel.setHAlign(eLabel.alignLeft)
        self.titleLabel.setZPosition(2)
        self.titleLabel.setTransparent(1)

        self.backPixamp.hide()
        self.titleLabel.hide()
        self.skinAttributes = attribs
        return GUIComponent.applySkin(self, desktop, parent)

    GUI_WIDGET = eWidget

    def postWidgetCreate(self, instance):
        self.instance = instance
        self.instance.setBackgroundColor(self.backgroundColor)
        self.instance.setTransparent(1)
        self.backPixamp = ePixmap(self.instance)

        self.eList = eListbox(self.instance)
        self.eList.resize(eSize(400,450))
        self.eList.move(ePoint(16,75))
        self.eList.setZPosition(2)
        self.eList.setContent(self.l)
        self.eList.setItemHeight(64)
        self.eList.setTransparent(1)
        self.eList.setScrollbarMode(eListbox.showNever)
        self.eList.setWrapAround(1)

        self.titleLabel = eLabel(self.instance)

    def preWidgetRemove(self, instance):
        self.instance = None

    def buildEntries(self, list):
        if self.instance:
            self.backPixamp.resize(eSize(self.instance.size().width(),self.instance.size().height()))
            self.backPixamp.setPixmap(self.backgroundPixmap)
            self.backPixamp.show()

            self.titleLabel.resize(eSize(236, 36))
            self.titleLabel.move(ePoint(16,15))
            self.titleLabel.setText('Leagues')
            self.titleLabel.show()

            self.eList.setBackgroundColor(self.backgroundColor)
            self.eList.setBackgroundColorSelected(self.backgroundColorSelected)
            self.eList.setForegroundColor(self.foregroundColor)
            self.eList.setForegroundColorSelected(self.foregroundColorSelected)

            self.list = list
            self.l.setList(self.list)
            self.eList.moveSelectionTo(0)

    def buildEntry(self, league, league_type):
        res = [None]
        # res.append(MultiContentEntryText(pos=(0,0),size=(400,2), backcolor=MultiContentTemplateColor('#efefef')))
        if league_type:
            ptr = None
            if league_type == 'x':
                ptr = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/leagues/invite.png"))
            elif league_type == 's':
                ptr = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/leagues/general.png"))
            elif league_type == 'c':
                ptr = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/leagues/general.png"))
            if ptr:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(0,0),size=(300,32),png=ptr, flags=BT_SCALE|BT_VALIGN_CENTER|BT_KEEP_ASPECT_RATIO))
            res.append(MultiContentEntryText(pos=(60,37),size=(60,20),text="Rank", color=MultiContentTemplateColor("#7a7a7a")))
            res.append(MultiContentEntryText(pos=(190,37),size=(100,22),text="League", color=MultiContentTemplateColor("#7a7a7a")))
        if league:
            rank = FPlAPi.formatNb(league['entry_rank'])
            res.append(MultiContentEntryText(pos=(60,0),size=(120,64),text=str(rank),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT, color=MultiContentTemplateColor("#37003c"),color_sel=MultiContentTemplateColor("white"), backcolor_sel=MultiContentTemplateColor('#37003c')))
            res.append(MultiContentEntryText(pos=(190,0),size=(210,64),text=str(league['name']),flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT|RT_WRAP, font=1, color=MultiContentTemplateColor("#37003c"),color_sel=MultiContentTemplateColor("white"), backcolor_sel=MultiContentTemplateColor('#37003c')))
            icon = self.upicon if league['entry_rank'] < league['entry_last_rank'] else self.downicon if league['entry_rank'] > league['entry_last_rank'] else self.sameicon
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(17,1),size=(25,64),png=icon, flags=BT_SCALE|BT_VALIGN_CENTER|BT_KEEP_ASPECT_RATIO))
        return res

    def getCurrent(self):
        return self.l.getCurrentSelection()

    def up(self):
        if self.eList:
            self.eList.moveSelection(self.eList.moveUp)

    def down(self):
        if self.eList:
            self.eList.moveSelection(self.eList.moveDown)

    def pageUp(self):
        if self.eList:
            self.eList.moveSelection(self.eList.pageUp)

    def pageDown(self):
        if self.eList:
            self.eList.moveSelection(self.eList.pageDown)
            

class MyFpUserLayout(GUIComponent):

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildEntry)
        self.font = gFont("Myfpl-Regular", 23)
        self.font_bold = gFont("Myfpl-Bold", 23)
        self.backgroundColor = parseColor("white")
        self.backgroundColorSelected = parseColor("#37003c")
        self.foregroundColor = parseColor("#37003c")
        self.foregroundColorSelected = parseColor("white")

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value) in self.skinAttributes:
            if attrib == "backgroundPixmap":
                self.backgroundPixmap = LoadPixmap(value)
            else:
                attribs.append((attrib, value))

        self.l.setFont(0, self.font)
        self.l.setFont(1, self.font_bold)

        self.backPixamp.setAlphatest(BT_ALPHATEST)
        self.backPixamp.setZPosition(1)
        self.backPixamp.setScale(1)

        self.userCountry.setAlphatest(BT_ALPHABLEND)
        self.userCountry.setZPosition(2)
        self.userCountry.setScale(1)

        self.userName.setFont(gFont("Myfpl-Regular", 23))
        self.userName.setBackgroundColor(parseColor("#5dd5fd"))
        self.userName.setForegroundColor(self.foregroundColor)
        self.userName.setVAlign(eLabel.alignCenter)
        self.userName.setHAlign(eLabel.alignLeft)
        self.userName.setZPosition(2)
        self.userName.setTransparent(1)

        self.userClubName.setFont(gFont("Myfpl-Bold", 23))
        self.userClubName.setBackgroundColor(parseColor("#5dd5fd"))
        self.userClubName.setForegroundColor(self.foregroundColor)
        self.userClubName.setHAlign(eLabel.alignLeft)
        self.userClubName.setZPosition(2)
        self.userClubName.setTransparent(1)

        self.gwLabel.setFont(gFont("Myfpl-Bold", 23))
        self.gwLabel.setBackgroundColor(parseColor('white'))
        self.gwLabel.setForegroundColor(self.foregroundColor)
        self.gwLabel.setVAlign(eLabel.alignCenter)
        self.gwLabel.setHAlign(eLabel.alignLeft)
        self.gwLabel.setZPosition(2)
        self.gwLabel.setTransparent(1)
        self.gwLabel.setText('Gameweek History')
        self.gwLabel.resize(eSize(236, 36))
        self.gwLabel.move(ePoint(30,435))

        self.arrowLabel.setFont(gFont("Myfpl-icons", 33))
        self.arrowLabel.setBackgroundColor(parseColor('white'))
        self.arrowLabel.setForegroundColor(parseColor('blue'))
        self.arrowLabel.setVAlign(eLabel.alignCenter)
        self.arrowLabel.setHAlign(eLabel.alignLeft)
        self.arrowLabel.setZPosition(2)
        self.arrowLabel.setTransparent(1)
        self.arrowLabel.setText(str(html.unescape("&#xe941;")))
        self.arrowLabel.resize(eSize(33, 33))
        self.arrowLabel.move(ePoint(266,438))

        self.backPixamp.hide()
        self.userCountry.hide()
        self.gwLabel.hide()
        self.arrowLabel.hide()
        self.userName.hide()
        self.userClubName.hide()
        self.skinAttributes = attribs
        return GUIComponent.applySkin(self, desktop, parent)

    GUI_WIDGET = eWidget

    def postWidgetCreate(self, instance):
        self.instance = instance
        self.instance.setBackgroundColor(self.backgroundColor)
        self.instance.setTransparent(1)
        self.backPixamp = ePixmap(self.instance)
        self.userCountry = ePixmap(self.instance)

        self.eList = eListbox(self.instance)
        self.eList.setSelectionEnable(0)
        self.eList.resize(eSize(195,220))
        self.eList.move(ePoint(220,200))
        self.eList.setZPosition(2)
        self.eList.setContent(self.l)
        self.eList.setItemHeight(220)
        self.eList.setScrollbarMode(eListbox.showNever)
        self.eList.setTransparent(1)

        self.userName = eLabel(self.instance)
        self.userClubName = eLabel(self.instance)
        self.gwLabel = eLabel(self.instance)
        self.arrowLabel = eLabel(self.instance)

    def preWidgetRemove(self, instance):
        self.instance = None

    def setUserData(self, user_data):
        if self.instance:
            self.backPixamp.resize(eSize(self.instance.size().width(),self.instance.size().height()))
            self.backPixamp.setPixmap(self.backgroundPixmap)
            self.backPixamp.show()

            self.userName.setText(f"{user_data['player_first_name']} {user_data['player_last_name']}")
            self.userName.resize(eSize(236,36))
            self.userName.move(ePoint(20,15))
            self.userName.show()

            self.userClubName.setText(f"{user_data['club_name']}")
            self.userClubName.resize(eSize(236,60))
            self.userClubName.move(ePoint(20,53))
            self.userClubName.show()

            self.gwLabel.show()
            self.arrowLabel.show()

            flag_path = resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/flags/{}.png".format(user_data['country_code'].lower()))
            if fileExists(flag_path):
                ptr = LoadPixmap(flag_path)
                if ptr:
                    self.userCountry.resize(eSize(90,50))
                    self.userCountry.move(ePoint(315,25))
                    self.userCountry.setPixmap(ptr)
                    self.userCountry.show()

            self.l.setList([(user_data,)])

    def buildEntry(self, user_data):
        res = [None]
        res.append(MultiContentEntryText(pos=(0,15),size=(195,36),text=str(user_data['total_points']),flags=RT_VALIGN_CENTER|RT_HALIGN_RIGHT, color=MultiContentTemplateColor("#37003c"), backcolor=MultiContentTemplateColor('white')))
        res.append(MultiContentEntryText(pos=(0,66),size=(195,36),text=str(user_data['overall_rank']),flags=RT_VALIGN_CENTER|RT_HALIGN_RIGHT, color=MultiContentTemplateColor("#37003c"), backcolor=MultiContentTemplateColor('white')))
        res.append(MultiContentEntryText(pos=(0,122),size=(195,36),text=str(user_data['total_players']),flags=RT_VALIGN_CENTER|RT_HALIGN_RIGHT, color=MultiContentTemplateColor("#37003c"), backcolor=MultiContentTemplateColor('white')))
        res.append(MultiContentEntryText(pos=(0,175),size=(195,36),text=str(user_data['current_gw_points']),flags=RT_VALIGN_CENTER|RT_HALIGN_RIGHT, color=MultiContentTemplateColor("#37003c"), backcolor=MultiContentTemplateColor('white')))
        return res