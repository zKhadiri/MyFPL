from Tools.Directories import resolveFilename , SCOPE_PLUGINS , fileExists
from twisted.internet.ssl import ClientContextFactory
from twisted.internet._sslverify import ClientTLSOptions
try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse
from sys import version_info
from skin import parseColor


PY3 = version_info[0] == 3


def readFromFile(filename):
	_file = resolveFilename(SCOPE_PLUGINS, "Extensions/MyFPL/{}".format(filename))
	if fileExists(_file):
		with open(_file, 'r') as f:
			return f.read()

class WebClientContextFactory(ClientContextFactory):
	def __init__(self, url=None):
		domain = urlparse(url).netloc
		self.hostname = domain
	
	def getContext(self, hostname=None, port=None):
		ctx = ClientContextFactory.getContext(self)
		if self.hostname and ClientTLSOptions is not None: # workaround for TLS SNI
			ClientTLSOptions(self.hostname, ctx)
		return ctx

def MultiContentTemplateColor(n):
	if not isinstance(n, int):
		return parseColor(n).argb()
	return 0xff000000 | n