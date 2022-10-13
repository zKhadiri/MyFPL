from __future__ import print_function
from __future__ import absolute_import
from enigma import getPrevAsciiCode
from six import PY2
import six
from Components.config import ConfigElement
from Tools.NumericalTextInput import NumericalTextInput
# pyunichr = unichr if PY2 else chr

ACTIONKEY_LEFT = 0
ACTIONKEY_RIGHT = 1
ACTIONKEY_SELECT = 2
ACTIONKEY_DELETE = 3
ACTIONKEY_BACKSPACE = 4
ACTIONKEY_FIRST = 5
ACTIONKEY_LAST = 6
ACTIONKEY_TOGGLE = 7
ACTIONKEY_ASCII = 8
ACTIONKEY_TIMEOUT = 9
ACTIONKEY_NUMBERS = list(range(12, 12 + 10))
ACTIONKEY_0 = 12
ACTIONKEY_1 = 13
ACTIONKEY_2 = 14
ACTIONKEY_3 = 15
ACTIONKEY_4 = 16
ACTIONKEY_5 = 17
ACTIONKEY_6 = 18
ACTIONKEY_7 = 19
ACTIONKEY_8 = 20
ACTIONKEY_9 = 21
ACTIONKEY_PAGEUP = 22
ACTIONKEY_PAGEDOWN = 23
ACTIONKEY_PREV = 24
ACTIONKEY_NEXT = 25
ACTIONKEY_ERASE = 26

# Deprecated / Legacy action key names...
#
# (These should be removed when all Enigma2 uses the new and less confusing names.)
#
KEY_LEFT = ACTIONKEY_LEFT
KEY_RIGHT = ACTIONKEY_RIGHT
KEY_OK = ACTIONKEY_SELECT
KEY_DELETE = ACTIONKEY_DELETE
KEY_BACKSPACE = ACTIONKEY_BACKSPACE
KEY_HOME = ACTIONKEY_FIRST
KEY_END = ACTIONKEY_LAST
KEY_TOGGLEOW = ACTIONKEY_TOGGLE
KEY_ASCII = ACTIONKEY_ASCII
KEY_TIMEOUT = ACTIONKEY_TIMEOUT
KEY_NUMBERS = ACTIONKEY_NUMBERS
KEY_0 = ACTIONKEY_0
KEY_9 = ACTIONKEY_9


def getKeyNumber(key):
	assert key in ACTIONKEY_NUMBERS
	return key - ACTIONKEY_0

class MyFplConfigText(ConfigElement, NumericalTextInput):
	def __init__(self, default="", fixed_size=True, visible_width=False, show_help=True):
		ConfigElement.__init__(self)
		NumericalTextInput.__init__(self, nextFunc=self.nextFunc, handleTimeout=False)

		self.marked_pos = 0
		self.allmarked = (default != "")
		self.fixed_size = fixed_size
		self.visible_width = visible_width
		self.offset = 0
		self.overwrite = fixed_size
		self.help_window = None
		self.show_help = show_help
		self.value = self.last_value = self.default = default

	def validateMarker(self):
		textlen = len(self.text)
		if self.fixed_size:
			if self.marked_pos > textlen - 1:
				self.marked_pos = textlen - 1
		else:
			if self.marked_pos > textlen:
				self.marked_pos = textlen
		if self.marked_pos < 0:
			self.marked_pos = 0
		if self.visible_width:
			if self.marked_pos < self.offset:
				self.offset = self.marked_pos
			if self.marked_pos >= self.offset + self.visible_width:
				if self.marked_pos == textlen:
					self.offset = self.marked_pos - self.visible_width
				else:
					self.offset = self.marked_pos - self.visible_width + 1
			if self.offset > 0 and self.offset + self.visible_width > textlen:
				self.offset = max(0, len - self.visible_width)

	def insertChar(self, ch, pos, owr):
		if owr or self.overwrite:
			self.text = self.text[0:pos] + ch + self.text[pos + 1:]
		elif self.fixed_size:
			self.text = self.text[0:pos] + ch + self.text[pos:-1]
		else:
			self.text = self.text[0:pos] + ch + self.text[pos:]

	def deleteChar(self, pos):
		if not self.fixed_size:
			self.text = self.text[0:pos] + self.text[pos + 1:]
		elif self.overwrite:
			self.text = self.text[0:pos] + " " + self.text[pos + 1:]
		else:
			self.text = self.text[0:pos] + self.text[pos + 1:] + " "

	def deleteAllChars(self):
		if self.fixed_size:
			self.text = " " * len(self.text)
		else:
			self.text = ""
		self.marked_pos = 0

	def handleKey(self, key):
		# this will no change anything on the value itself
		# so we can handle it here in gui element
		if key == KEY_DELETE:
			self.timeout()
			if self.allmarked:
				self.deleteAllChars()
				self.allmarked = False
			else:
				self.deleteChar(self.marked_pos)
				if self.fixed_size and self.overwrite:
					self.marked_pos += 1
		elif key == KEY_BACKSPACE:
			self.timeout()
			if self.allmarked:
				self.deleteAllChars()
				self.allmarked = False
			elif self.marked_pos > 0:
				self.deleteChar(self.marked_pos - 1)
				if not self.fixed_size and self.offset > 0:
					self.offset -= 1
				self.marked_pos -= 1
		elif key == KEY_LEFT:
			self.timeout()
			if self.allmarked:
				self.marked_pos = len(self.text)
				self.allmarked = False
			else:
				self.marked_pos -= 1
		elif key == KEY_RIGHT:
			self.timeout()
			if self.allmarked:
				self.marked_pos = 0
				self.allmarked = False
			else:
				self.marked_pos += 1
		elif key == KEY_HOME:
			self.timeout()
			self.allmarked = False
			self.marked_pos = 0
		elif key == KEY_END:
			self.timeout()
			self.allmarked = False
			self.marked_pos = len(self.text)
		elif key == KEY_TOGGLEOW:
			self.timeout()
			self.overwrite = not self.overwrite
		elif key == KEY_ASCII:
			self.timeout()
			newChar = six.unichr(getPrevAsciiCode())
			if not self.useableChars or newChar in self.useableChars:
				if self.allmarked:
					self.deleteAllChars()
					self.allmarked = False
				self.insertChar(newChar, self.marked_pos, False)
				self.marked_pos += 1
		elif key in KEY_NUMBERS:
			owr = self.lastKey == getKeyNumber(key)
			newChar = self.getKey(getKeyNumber(key))
			if self.allmarked:
				self.deleteAllChars()
				self.allmarked = False
			self.insertChar(newChar, self.marked_pos, owr)
		elif key == KEY_TIMEOUT:
			self.timeout()
			if self.help_window:
				self.help_window.update(self)
			return

		if self.help_window:
			self.help_window.update(self)
		self.validateMarker()
		self.changed()

	def nextFunc(self):
		self.marked_pos += 1
		self.validateMarker()
		self.changed()

	def getValue(self):
		try:
			if PY2:
				return self.text.encode("utf-8")
			else:
				return six.ensure_str(self.text)
		except UnicodeDecodeError:
			print("Broken UTF8!")
			return self.text

	def setValue(self, val):
		try:
			if PY2:
				self.text = val.decode("utf-8")
			else:
				self.text = six.ensure_text(val)
		except UnicodeDecodeError:
			self.text = six.ensure_text(val, errors='ignore')
			print("Broken UTF8!")

	value = property(getValue, setValue)
	_value = property(getValue, setValue)

	def getText(self):
		if PY2:
			return self.text.encode("utf-8")
		else:
			return six.ensure_str(self.text)

	def getMulti(self, selected):
		if PY2:
			self.text = self.text.encode("utf-8")
		else:
			self.text = six.ensure_str(self.text)
		return "mtext"[1 - selected:], self.text

	def onSelect(self, session):
		self.allmarked = (self.value != "")
		# if session is not None:
		# 	from Screens.NumericalTextInputHelpDialog import NumericalTextInputHelpDialog
		# 	self.help_window = session.instantiateDialog(NumericalTextInputHelpDialog, self)
		# 	if self.show_help:
		# 		self.help_window.show()

	def onDeselect(self, session):
		self.marked_pos = 0
		self.offset = 0
		if self.help_window:
			session.deleteDialog(self.help_window)
			self.help_window = None
		if not self.last_value == self.value:
			self.changedFinal()
			self.last_value = self.value

	def getHTML(self, id):
		return '<input type="text" name="' + id + '" value="' + self.value + '" /><br>\n'

	def unsafeAssign(self, value):
		self.value = str(value)

class MyFplConfigPassword(MyFplConfigText):
	def __init__(self, default="", fixed_size=False, visible_width=False, censor=u"\u2022"):
		MyFplConfigText.__init__(self, default=default, fixed_size=fixed_size, visible_width=visible_width)
		if censor != "" and (isinstance(censor, str) and len(censor) != 1) and (isinstance(censor, unicode) and len(censor) != 1):
			raise ValueError("[Config] Error: Censor must be a single char (or \"\")!")
		self.censor = censor
		self.hidden = True

	def getMulti(self, selected):
		mtext, text = MyFplConfigText.getMulti(self, selected)
		if self.hidden:
			text = self.censor * len(text)  # For more security a fixed length string can be used!
		return (mtext, text)

	def onSelect(self, session):
		MyFplConfigText.onSelect(self, session)
		self.hidden = False

	def onDeselect(self, session):
		self.hidden = True
		MyFplConfigText.onDeselect(self, session)
