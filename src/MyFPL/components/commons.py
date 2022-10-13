# -*- coding: UTF-8 -*-
from Components.config import config, ConfigSubsection, ConfigBoolean, ConfigDirectory
from .config import MyFplConfigText, MyFplConfigPassword

config.plugins.MyFPL = ConfigSubsection()
config.plugins.MyFPL.user_id = MyFplConfigText()
config.plugins.MyFPL.email = MyFplConfigText()
config.plugins.MyFPL.password = MyFplConfigPassword()
config.plugins.MyFPL.isLoged = ConfigBoolean(default=False)

MyFplConfig = config.plugins.MyFPL