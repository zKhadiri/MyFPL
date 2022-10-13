# -*- coding: UTF-8 -*-
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from enigma import addFont, getDesktop
from .LoginInterface import MyFplLogin
from .FplUser import MyFplUserDetails
from .components.commons import MyFplConfig

addFont("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/fonts/Myfpl-icons.ttf", "Myfpl-icons", 100, 1)
addFont("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/fonts/PremierSans-Regular.ttf", "Myfpl-Regular", 100, 1)
addFont("/usr/lib/enigma2/python/Plugins/Extensions/MyFPL/assets/fonts/Premier-bold.ttf", "Myfpl-Bold", 100, 1)
addFont("/usr/lib/enigma2/python/Plugins/Extensions/DreamSat/assets/fonts/font_default.otf", "ArabicFont", 100, 1)

def getDesktopSize():
	s = getDesktop(0).size()
	return (s.width(), s.height())

def isFHD():
	desktopSize = getDesktopSize()
	if desktopSize[0] >= 1920:
		return True
	else:
		return False

def main(session, **kwargs):
    if isFHD():
        if MyFplConfig.isLoged.value:
            if MyFplConfig.user_id.value:
                session.open(MyFplUserDetails, int(MyFplConfig.user_id.value))
            else:
                session.open(MyFplLogin)
        else:
            session.open(MyFplLogin)
    else:
        session.open(MessageBox, _('Skin is not supported\nThis plugin works only with FHD skins'), MessageBox.TYPE_ERROR)

def Plugins(**kwargs):
    Descriptors=[]
    Descriptors.append(PluginDescriptor(name='My-FPL', description='Premier League Fantasy', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon='logo.png'))
    return Descriptors