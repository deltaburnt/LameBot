import socket, string, time
import util.logger_factory
from net.connection import Connection

class IRC(Connection):
	def __init__(self, name, host, port, nick, real_name, channels, extensions, allowed_channels):
		self.name = name
		self.logger = util.logger_factory.instance().getLogger('net.irc.'+name)
		
		self.host = host
		self.port = port
		self.nick = nick
		self.real_name = real_name
		self.chan_list = channels
		self.extensions = extensions
		self.allowed_channels = allowed_channels
	
	def connect(self):
		channels = ','.join(self.chan_list)
		
		super(IRC, self).connect()
		
		self._send_raw(Commands.NICK(self.nick))
		self._send_raw(Commands.USER(self.nick, self.real_name))
		
		self.logger.info(
		                 'Connected to %s on port %s in channels %s',
		                 self.host,
		                 self.port,
		                 self.chan_list
		)
		
	def disconnect(self, reason = 'cya nerds'):
		self._send_raw(Commands.QUIT(reason))
		super(IRC, self).disconnect()
	
	#Channels is comma delimited str
	def join(self, channels = None):
		if channels is None:
			channels = self.chan_list
			channels = ','.join(channels)
		else:
			channels = self.chan_list.append(channels)
		self.logger.debug('Joining channels %s', channels)
		self._send_raw(Commands.JOIN(channels))
		
	def msg(self, target, message):
		self._send_raw(Commands.PRIVMSG(target, message))
		
	def ctcp(self, target, message):
		self._send_raw(Commands.CTCP(target, message))
	
#Commonly called command syntax
class Commands():
	
	@staticmethod
	def PRIVMSG(target, message):
		return 'PRIVMSG %s :%s\r\n' % (target, message)
		
	@staticmethod
	def CTCP(target, message):
		return Commands.PRIVMSG(target, '\x01%s\x01' % message)
	
	@staticmethod
	def QUIT(message = 'Bye'):
		return 'QUIT %s\r\n' % (message)
	
	@staticmethod
	def JOIN(channels):
		return 'JOIN :%s\r\n' % (channels)
	
	@staticmethod
	def PONG(host):
		return 'PONG %s\r\n' % (host)
	
	@staticmethod
	def USER(nick, real_name):
		return 'USER %s * 8 :%s\r\n' % (nick, real_name)
	
	@staticmethod
	def NICK(nick):
		return 'NICK %s\r\n' % nick