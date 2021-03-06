import os, importlib, inspect
import api.plugin, util.logger_factory

class Loader():
	
	def __init__(self, scheduler, bot, sql_conn):
		filenames = os.listdir(os.path.abspath(__file__+'/../../ext'))
		self.ext_names = [x[:-3] for x in filenames if x[-3:] == '.py' and x != '__init__.py']
		self.scheduler = scheduler
		self.bot = bot
		self.sql_conn = sql_conn
		self.sql = sql_conn.cursor()
		self.logger = util.logger_factory.instance().getLogger('api.loader')
		
		self.sql.execute('CREATE TABLE IF NOT EXISTS `__plugins` (name)')
		self.sql_conn.commit()
	
	def load_all(self, load_extensions = None):
		self.logger.debug('Loading all extensions')
		
		self.plugins = []
		for module in self.ext_names:
			module = importlib.import_module('ext.'+module)
			class_info = self._get_class(module)
			
			if class_info is None:
				continue
			if load_extensions != '~~All~~' and class_info[0] not in load_extensions:
				self.logger.debug('Skipping extension %s, not included in load_extensions config value', class_info[0])
				continue
			
			logger = util.logger_factory.instance().getLogger('ext.'+class_info[0])
			class_obj = class_info[1](self.scheduler, self.bot.network_list, self.sql, logger)
			self.plugins.append({'name':class_info[0], 'object':class_obj, 'module': module})

		self._install_plugins()
		self._start_plugins()
		self.sql_conn.commit()
			
	def _get_class(self, module):
		for info in inspect.getmembers(module):
			if issubclass(info[1], api.plugin.Plugin) and info[1] is not api.plugin.Plugin:
				return info
				
	def _install_plugins(self):
		for plugin in self.plugins:
			self.sql.execute('SELECT * FROM `__plugins` WHERE name = ?', (plugin['name'],))
			if self.sql.fetchone() is None:
				self.logger.info('Installing extension %s', plugin['name'])
				plugin['object']._install_()
				self.sql.execute('INSERT INTO `__plugins`(name) values (?)', (plugin['name'],))
		
	def _start_plugins(self):
		for plugin in self.plugins:
			plugin['object']._start_()