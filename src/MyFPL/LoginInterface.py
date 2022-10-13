# -*- coding: UTF-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Tools.LoadPixmap import LoadPixmap
from Screens.MessageBox import MessageBox
from Tools.Directories import resolveFilename , SCOPE_PLUGINS , fileExists
from .FPlApi import FPlAPi
from .FplUser import MyFplUserDetails
from .components.FplVirtualKeyboard import MyFPlKeyboard
from .components.tools import readFromFile
from .components.commons import MyFplConfig as conf
import random, re


class MyFplLogin(Screen, ConfigListScreen):

    def __init__(self, session):
        self.list = []
        self.onChangedEntry = []
        self.session = session
        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        self.skin = readFromFile('assets/skin/LoginScreen.xml')
        self['players'] = Pixmap()
        self['status'] = Label()
        self['status'].hide()
        self['login_button'] = Pixmap()
        self['login_button'].hide()
        self.keyboardDlg = None
        self.inKeboard = False
        self.canLogin = False
        self['FPlActions'] = ActionMap(['FPlActions'], {
            'cancel': self.exit,
            "down": self.keyDown,
			"up": self.keyUp,
            'ok_long': self.toggleKeyboard,
            'green': self.ok,
            'ok': self.ok
        }, -1)
        for elem in ('configActions', 'menuConfigActions', 'charConfigActions', 'editConfigActions', 'virtualKeyBoardActions', 'config_actions', ):
            try:
                self[elem].setEnabled(False)
            except:pass
        self.fplApi = FPlAPi()
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        self.onChangedEntry.append(self.checkUserInfo)
        self.onLayoutFinish.append(self._onLayoutFinish)

    def _onLayoutFinish(self):
        player = random.choice(['haaland', 'james', 'maddison', 'raya', 'sancho'])
        player_icon_path = resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/assets/images/players/{}.png".format(player))
        if fileExists(player_icon_path):
            ptr = LoadPixmap(player_icon_path)
            self['players'].instance.setPixmap(ptr)
        self.createSetup()

    def checkUserInfo(self):
        if conf.email.value and conf.password.value:
            if re.match(r'[^@]+@[^@]+\.[^@]+', conf.email.value.replace('| ', '')) and conf.password.value.replace('| ',''):
                self['login_button'].show()
                self.canLogin = True
            else:
                self['login_button'].hide()
                self.canLogin = False
        else:
            self['login_button'].hide()
            self.canLogin = False

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def createSetup(self):
        self.list = [getConfigListEntry(_("Email:"), conf.email)]
        self.list.append(getConfigListEntry(_("Password:"), conf.password))
        self["config"].list = self.list
        self["config"].setList(self.list)

    def selectionChanged(self):
        if self["config"].getCurrent():
            self.removeGuiCursor()
            self.reBuildKeyboard(selected=-1)
            self.checkUserInfo()
            try:
                self["config"].getCurrent()[1].help_window.instance.hide()
            except:pass

    def ok(self):
        self['status'].hide()
        self.login()

    def keyDown(self):
        self["config"].instance.moveSelection(self["config"].instance.moveDown)

    def keyUp(self):
        self["config"].instance.moveSelection(self["config"].instance.moveUp)
        
    def login(self):
        if self.canLogin:
            ret = self.fplApi.login(conf.email.value, conf.password.value)
            if ret['status'] == 'success':
                self.closeKeyboard()
                if ret['player_id']:
                    conf.user_id.value = str(ret['player_id'])
                    self.session.openWithCallback(self.exit, MyFplUserDetails, conf.user_id.value)
                    conf.isLoged.value = True
                    conf.user_id.save()
                    conf.isLoged.save()
                    self._onSave()
                else:
                    self.session.open(MessageBox, 'Looks like you have a fresh account\nPlease go to fantasy.premierleague.com and build your team.', MessageBox.TYPE_ERROR)
            elif ret['status'] == 'failed':
                if ret['reason'] == 'credentials':
                    self['status'].setText('Incorrect email or password')
                    self['status'].show()
                else:
                    self['status'].setText(f"Login failed reason: {ret['reason']}")
                    self['status'].show()

    def toggleKeyboard(self):
        if not self.keyboardDlg:
            self.keyboardDlg = self.session.instantiateDialog(MyFPlKeyboard, text=self["config"].getCurrent()[1].getValue(), cb=self.keyboardCallBack)
            self.keyboardDlg.show()
        if not self.inKeboard:
            self['FPlActions'].execEnd()
            self.keyboardKeymap(activate=True)
            self.keyboardDlg.text = self["config"].getCurrent()[1].getValue() + self.keyboardDlg.cursor
            self.reBuildKeyboard()
            self.keyboardDlg.set_GUI_Text()
            self.inKeboard = True
        else:
            self['FPlActions'].execBegin()
            self.keyboardKeymap()
            self.removeGuiCursor()
            self.reBuildKeyboard(-1)
            self.inKeboard = False

    def reBuildKeyboard(self, selected=0):
        if self.keyboardDlg:
            self.keyboardDlg.nb_only = self["config"].getCurrent()[0] == _("User ID:")
            self.keyboardDlg.selectedKey = selected
            self.keyboardDlg.buildVirtualKeyBoard(selected)

    def keyboardKeymap(self, activate=False):
        for elem in ('actions', 'OkCancelActions', 'WizardActions', 'InputBoxActions', 'ShortcutActions', 'SeekActions'):
            if activate:
                self.keyboardDlg[elem].execBegin()
            else:
                self.keyboardDlg[elem].execEnd()

    def removeGuiCursor(self):
        txt = self["config"].getCurrent()[1].getValue().replace('| ', '')
        self.setText(txt)

    def setText(self, text):
        self["config"].getCurrent()[1].setValue(text)
        self["config"].invalidate(self["config"].getCurrent())
        self.checkUserInfo()

    def keyboardCallBack(self, text=None):
        if text:
            if text == 'CLEAR':
                text = ''
            self.setText(text)
        else:
            self.toggleKeyboard()

    def _onSave(self):
        for x in self["config"].list:
            x[1].save()

    def closeKeyboard(self):
        if self.keyboardDlg:
            self.keyboardKeymap()
            self.session.deleteDialog(self.keyboardDlg)
            self.keyboardDlg = None

    def exit(self, ret=None):
        if not ret:
            self.closeKeyboard()
            self.close()