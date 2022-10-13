# -*- coding: UTF-8 -*-
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER, getPrevAsciiCode
from Screens.Screen import Screen
from Components.Language import language
from Components.ActionMap import ActionMap, HelpableActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Screens.HelpMenu import HelpableScreen
from Tools.NumericalTextInput import NumericalTextInput
import skin
from .tools import readFromFile
import html

class VirtualKeyBoardList(MenuList):
    def __init__(self, list, enableWrapAround=False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Myfpl-Regular', 28))
        self.l.setFont(1, gFont("Myfpl-icons", 28))
        self.l.setItemHeight(45)


def VirtualKeyBoardEntryComponent(keys, selectedKey, shiftMode=False):
    primaryColor = "#37003c"
    secondaryColor = "#5be2fe"
    res = [(keys)]
    bg = skin.parseColor("#00494949").argb()
    bgkey = skin.parseColor(primaryColor).argb()
    bgsel = skin.parseColor(secondaryColor).argb()
    bgok = skin.parseColor("#00009900").argb()
    bgcancel = skin.parseColor("#00990000").argb()
    bgselok = skin.parseColor("#00006600").argb()
    bgselcancel = skin.parseColor("#00660000").argb()
    shift = str(html.unescape("&#xe5d8;"))
    left = str(html.unescape("&#xe5cb;"))
    right = str(html.unescape("&#xe5cc;"))
    backspace = str(html.unescape("&#xe14a;"))
    

    height = 45
    width = int(1880/12)
    x = 0
    count = 0
    for key in keys:
        if key == "EXIT":
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="EXIT",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel, color=bgkey))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="EXIT",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
        elif key == "BACKSPACE":
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=backspace,
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgselcancel))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=backspace,
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgcancel))
        elif key == "CLEAR":
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="CLR",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel, color=bgkey))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="CLR",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
        elif key == "SHIFT":
            if shiftMode:
                if selectedKey == count:
                    res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=shift,
                                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel, color=bgkey))
                else:
                    res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=shift,
                                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bg))
            else:
                if selectedKey == count:
                    res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=shift,
                                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel, color=bgkey))
                else:
                    res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=shift,
                                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
        elif key == "SPACE":
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
        elif key == "OK":
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="OK",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgselok))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="OK",
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgok))
        elif key == "LEFT":
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=left,
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel, color=bgkey))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=left,
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
        elif key == "RIGHT":
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=right,
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel, color=bgkey))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text=right,
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
        else:
            if selectedKey == count:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text=key,
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel, color=bgkey))
            else:
                res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text=key,
                                                    flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
        x += width
        count += 1
    return res


class MyFPlKeyboard(Screen, NumericalTextInput, HelpableScreen):

    def __init__(self, session, title="", text="", nb_only=False, cb=None):
        Screen.__init__(self, session)
        NumericalTextInput.__init__(self, nextFunc=self.timeoutNI, handleTimeout=True)
        self.skin = readFromFile('assets/skin/keyboard.xml')
        self["list"] = VirtualKeyBoardList([])
        self.shiftMode = False
        self.nb_only = nb_only
        self.selectedKey = 0
        self.cursor = "XcursorX"
        self.gui_cursor = "| "
        self.text = text + self.cursor
        self.sms_txt = None
        self.cb = cb
        self.lang = language.getLanguage()
        self["actions"] = ActionMap(["KeyboardInputActions", "InputAsciiActions"],
        {
            "gotAsciiCode": self.keyGotAscii,
            "deleteBackward": self.backClicked,
        }, -2)
        self["InputBoxActions"] = HelpableActionMap(self, "InputBoxActions",
        {
            "deleteBackward": (self.cursorLeft, _("Move cursor left")),
            "deleteForward": (self.cursorRight, _("Move cursor right")),
        }, -2)
        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
        {
            "ok": (self.okClicked, _("Select key")),
            "cancel": (self.exit, _("Cancel")),
        }, -2)
        self["ShortcutActions"] = HelpableActionMap(self, "ShortcutActions",
        {
            "red": (self.backClicked, _("Delete (left of the cursor)")),
            "blue": (self.backSpace, _("Delete (right of the cursor)")),
            "green": (self.ok, _("Save")),
        }, -2)
        self["WizardActions"] = HelpableActionMap(self, "WizardActions",
        {
            "left": (self.left, _("Left")),
            "right": (self.right, _("Right")),
            "up": (self.up, _("Up")),
            "down": (self.down, _("Down")),
        }, -2)
        self["SeekActions"] = HelpableActionMap(self, "SeekActions",
        {
            "seekBack": (self.move_to_begin, _("Move to begin")),
            "seekFwd": (self.move_to_end, _("Move to end")),
        }, -2)
        self["NumberActions"] = NumberActionMap(["NumberActions"],
        {
            "1": self.keyNumberGlobal,
            "2": self.keyNumberGlobal,
            "3": self.keyNumberGlobal,
            "4": self.keyNumberGlobal,
            "5": self.keyNumberGlobal,
            "6": self.keyNumberGlobal,
            "7": self.keyNumberGlobal,
            "8": self.keyNumberGlobal,
            "9": self.keyNumberGlobal,
            "0": self.keyNumberGlobal
        })
        HelpableScreen.__init__(self)
        self.onExecBegin.append(self.setKeyboardModeAscii)
        self.onLayoutFinish.append(self.setLang)
        self.onLayoutFinish.append(self.buildVirtualKeyBoard)

    def setLang(self):
        if self.lang == 'de_DE':
            self.nbkeys_list = [u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0",
                u"CLEAR", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
            self.keys_list = [
                u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"-",
                u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"+", u"@",
                u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"#", u"\\", u"|",
                u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".",
                u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
            self.shiftkeys_list = [
                u"EXIT", u"!", u'"', u"$", u"%", u"&", u"/", u"(", u")", u"=", u"_",
                u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"*", u"[",
                u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"'", u"?", u"]",
                u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":",
                u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
            self.nextLang = 'en_EN'
        else:
            self.nbkeys_list = [u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0",
                u"CLEAR", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
            self.keys_list = [
                u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"-",
                u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"+", u"@",
                u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"#", u"\\", u"|",
                u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".",
                u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
            self.shiftkeys_list = [
                u"EXIT", u"!", u'"', u"$", u"%", u"&", u"/", u"(", u")", u"=", u"_",
                u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"*", u"[",
                u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"'", u"?", u"]",
                u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":",
                u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
            self.lang = 'en_EN'
            self.nextLang = 'de_DE'
        self.keys_list = self.buildKeyBoardLayout(self.keys_list)
        self.shiftkeys_list = self.buildKeyBoardLayout(self.shiftkeys_list)
        self.nbkeys_list = self.buildKeyBoardLayout(self.nbkeys_list)
        # self["country"].setText(self.lang)

    def buildVirtualKeyBoard(self, selectedKey=0):
        list = []
        self.max_key = -1
        self.setUseableChars(u'1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ')
        if self.nb_only:
            self.k_list = self.nbkeys_list
            self.setUseableChars(u'1234567890')
            for keys in self.k_list:
                keyslen = len(keys)
                self.max_key += keyslen
                if selectedKey < keyslen and selectedKey > -1:
                    list.append(VirtualKeyBoardEntryComponent(keys, selectedKey))
                else:
                    list.append(VirtualKeyBoardEntryComponent(keys, -1))
                selectedKey -= keyslen
        elif self.shiftMode:
            self.k_list = self.shiftkeys_list
            for keys in self.k_list:
                keyslen = len(keys)
                self.max_key += keyslen
                if selectedKey < keyslen and selectedKey > -1:
                    list.append(VirtualKeyBoardEntryComponent(keys, selectedKey, True))
                else:
                    list.append(VirtualKeyBoardEntryComponent(keys, -1, True))
                selectedKey -= keyslen
        else:
            self.k_list = self.keys_list
            for keys in self.k_list:
                keyslen = len(keys)
                self.max_key += keyslen
                if selectedKey < keyslen and selectedKey > -1:
                    list.append(VirtualKeyBoardEntryComponent(keys, selectedKey))
                else:
                    list.append(VirtualKeyBoardEntryComponent(keys, -1))
                selectedKey -= keyslen
        self.first_line_len = len(self.k_list[0])
        self.no_of_lines = len(self.k_list)
        self["list"].setList(list)

    def buildKeyBoardLayout(self, key_list):
        line_len = 12
        if self["list"].skinAttributes:
            for (attrib, value) in self["list"].skinAttributes:
                if attrib == "linelength":
                    line_len = int(value)
        k_list = []
        line = []
        i = 0
        for key in key_list:
            i += 1
            line.append(key)
            if i == line_len:
                k_list.append(line)
                i = 0
                line = []
        k_list.append(line)
        return k_list

    def toggleShift(self):
        if self.shiftMode:
            self.shiftMode = False
        else:
            self.shiftMode = True
        self.buildVirtualKeyBoard(self.selectedKey)

    def keyNumberGlobal(self, number):
        if number != self.lastKey and self.lastKey != -1:
            self.nextChar()
        txt = self.getKey(number)
        self.sms_txt = self.text.replace(self.cursor, txt + self.cursor)
        self.got_sms_key(txt)
        self.set_GUI_SMS_Text()

    def moveActiveKey(self, direction):
        self.selectedKey += direction
        for k in range(0, self.no_of_lines, 1):
            no_of_chars = k * self.first_line_len
            if direction == -1:
                if self.selectedKey == no_of_chars - 1:
                    self.selectedKey = no_of_chars - 1 + self.first_line_len
                    if self.selectedKey > self.max_key:
                        self.selectedKey = self.max_key
                    break
            elif direction == 1:
                if self.selectedKey == no_of_chars + self.first_line_len:
                    self.selectedKey = no_of_chars
                    break
                if self.selectedKey > self.max_key:
                    self.selectedKey = (self.no_of_lines - 1) * self.first_line_len
                    break
            elif direction == -self.first_line_len:
                if self.selectedKey < 0:
                    self.selectedKey = (
                                        self.no_of_lines - 1) * self.first_line_len + self.first_line_len + self.selectedKey
                    if self.selectedKey > self.max_key:
                        self.selectedKey = self.selectedKey - self.first_line_len
                break
            elif direction == self.first_line_len:
                tmp_key = self.selectedKey - self.first_line_len
                if self.selectedKey > self.max_key:
                    line_no = k + 1
                    if line_no * self.first_line_len > tmp_key:
                        self.selectedKey = tmp_key - (line_no - 1) * self.first_line_len
                        break
                elif self.selectedKey <= self.max_key:
                    break
        self.showActiveKey()

    def showActiveKey(self):
        self.buildVirtualKeyBoard(self.selectedKey)

    def left(self):
        self.moveActiveKey(-1)

    def right(self):
        self.moveActiveKey(+1)

    def up(self):
        self.moveActiveKey(-self.first_line_len)

    def down(self):
        self.moveActiveKey(+self.first_line_len)

    def move_to_begin(self):
        clean_txt = self.text.replace(self.cursor, "")
        self.text = self.cursor + clean_txt

    def move_to_end(self):
        clean_txt = self.text.replace(self.cursor, "")
        self.text = clean_txt + self.cursor

    def okClicked(self):
        if self.shiftMode:
            list = self.shiftkeys_list
        elif self.nb_only:
            list = self.nbkeys_list
        else:
            list = self.keys_list
        selectedKey = self.selectedKey
        
        text = None

        for x in list:
            xlen = len(x)
            if selectedKey < xlen:
                if selectedKey < len(x):
                    text = x[selectedKey]
                break
            else:
                selectedKey -= xlen

        if text is None:
            return
            
        if text == "EXIT":
            self.exit()
        elif text == "BACKSPACE":
            self.backClicked()
        elif text == "CLEAR":
            self.text = "" + self.cursor
            self.cb("CLEAR")
        elif text == "SHIFT":
            self.toggleShift()
        elif text == "SPACE":
            self.text = self.text.replace(self.cursor, " " + self.cursor)
            self.set_GUI_Text()
        elif text == "OK":
            self.ok()
            # self.cb()
        elif text == "LEFT":
            self.cursorLeft()
        elif text == "RIGHT":
            self.cursorRight()
        else:
            self.text = self.text.replace(self.cursor, text + self.cursor)
            self.set_GUI_Text()

    def cursorLeft(self):
        self.moveCursor(-1)

    def cursorRight(self):
        self.moveCursor(+1)

    def moveCursor(self, direction):
        txt = self.text.split(self.cursor)
        if direction < 0:
            direction *= self.checkUnicode(txt[0][-1:])
        elif direction > 0:
            direction *= self.checkUnicode(txt[1][:1])
        pos = self.text.find(self.cursor) + direction
        clean_txt = self.text.replace(self.cursor, "")
        if pos > len(clean_txt):
            self.text = self.cursor + clean_txt
        elif pos < 0:
            self.text = clean_txt + self.cursor
        else:
            self.text = clean_txt[:pos] + self.cursor + clean_txt[pos:]
        self.set_GUI_Text()

    def ok(self):
        text = self.text
        text = text.replace(self.cursor, "")
        self.cb(text)
        self.cb()

    def backClicked(self):
        txt = self.text.split(self.cursor)
        del_len = self.checkUnicode(txt[0][-1:])
        self.text = txt[0][:-del_len] + self.cursor + txt[1]
        self.set_GUI_Text()

    def backSpace(self):
        txt = self.text.split(self.cursor)
        del_len = self.checkUnicode(txt[1][:1])
        self.text = txt[0] + self.cursor + txt[1][del_len:]
        self.set_GUI_Text()

    def set_GUI_Text(self):
        if self.cb:
            txt = self.text.replace(self.cursor, "| ")
            if txt == '': txt = 'CLEAR'
            self.cb(txt)

    def set_GUI_SMS_Text(self):
        if self.cb:
            txt = self.sms_txt.replace(self.cursor, "| ")
            if txt == '': txt = 'CLEAR'
            self.cb(txt)

    def checkUnicode(self, char):
        try:
            len(u'%s' % char)
        except UnicodeDecodeError:
            return 2
        return 1

    def inShiftKeyList(self, key):
        for KeyList in self.shiftkeys_list:
            for char in KeyList:
                if char == key:
                    return True
        return False

    def got_sms_key(self, char):
        if self.inShiftKeyList(char):
            self.shiftMode = True
            list = self.shiftkeys_list
        else:
            self.shiftMode = False
            list = self.keys_list
        selkey = 0
        for keylist in list:
            for key in keylist:
                if key == char:
                    self.selectedKey = selkey
                    self.showActiveKey()
                    return
                else:
                    selkey += 1

    def keyGotAscii(self):
        from Components.config import getCharValue
        char = getCharValue(getPrevAsciiCode())
        if len(str(char)) == 1:
            char = char
        if self.inShiftKeyList(char):
            self.shiftMode = True
            list = self.shiftkeys_list
        else:
            self.shiftMode = False
            list = self.keys_list
        if char == " ":
            char = "SPACE"
        selkey = 0
        for keylist in list:
            for key in keylist:
                if key == char:
                    self.selectedKey = selkey
                    self.okClicked()
                    self.showActiveKey()
                    return
                else:
                    selkey += 1

    def timeoutNI(self):
        if self.sms_txt:
            self.text = self.sms_txt
        self.sms_txt = None
        self.set_GUI_Text()

    def exit(self):
        if self.cb:
            self.cb()
        else:
            self.close()