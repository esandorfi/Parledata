import sys, os, argparse
import yaml
import logging
from .log import logger, loginit, loglevel




def args():
	parser = argparse.ArgumentParser()
	#parser.add_argument('-p', '--production', help='[0 = local] [1 = production] génère les fichiers html dans le répertoire local ou production', default=0)
	parser.add_argument('-v', '--verbose', help='[1] log en mode debug', default=0)
	parser.add_argument('-a', '--action', help='define wich action to execute, depends on build script', default=0)
	parser.add_argument('-t', '--template', help='specify a template file if source is specified')
	parser.add_argument('-s', '--source', nargs='+', help='define source file(s)')
	args = parser.parse_args()
	return args

class PlwConfig():
	def __init__(self, profile_name = '', profile_dir = '', isConsole = True):
		#import pdb; pdb.set_trace()
		#global logger

		if( profile_name == '' ):
			self.profilename = 'PLDATA'
		else:
			self.profilename = profile_name
		logger = loginit(0, profile_name, isConsole)

		dirpath = os.getcwd()
		logger.info("current directory is : " + dirpath)

		template = dirpath + "\\templates"
		if( os.path.exists(template) ):
			parledatapath = template
		else:
			parledatapath = os.path.dirname(os.path.realpath(__file__))+".templates\\jinja"
		logger.info("template directory is : " + parledatapath)

		self.config =  {
		'profile' : self.profilename,
		'build' :
		{
		'source_path' : dirpath,
		'profile_path' : '', # NOT USED
		'static_path' : dirpath,
		'template_path' : parledatapath,
		'data_path' : '', #NOT USED
		'static_idx_path' : dirpath,
		'fdebug' : '',
		},
		'framework' :
		{
		'root_url' : '',
		'fw_url' : 'http://parle.data/assets/',
		'static_url' : '',
		'home_url' : '',
		'webmaster' : ''
		}
		}

		if( profile_name != ''):
			if( profile_dir != '' ):
				logger.info("--- PARLEDATA BUILD WITH "+profile_dir+profile_name)
				self.config = self.read(profile_dir+profile_name)
			else:
				logger.info("--- PARLEDATA BUILD WITH "+profile_name)
				self.config = self.read(profile_name)
		else:
			logger.info("--- PARLEDATA BUILD WITH CURRENT DIR")

	def initload(self, profile_name, profile_dir, isexist = False):
		#loglevel(0)
		#loginit()
		logger.info("--- PARLEDATA BUILD WITH "+profile_dir+profile_name)
		self.config = self.read(profile_dir+profile_name, isexist)

	def save(self, fname, dictcfg):
		if( fname.find('.yaml') == -1):
			fname += '.yaml'

		with open(fname, 'w', encoding='utf-8') as hfile:
			yaml.dump(dictcfg, hfile, default_flow_style=False)

	def read(self, fname, isexist = False):
		profile = fname
		if( fname.find('.yaml') == -1):
			fname += '.yaml'
		try:
			with open(fname, 'r', encoding='utf-8') as hfile:
				dictcfg = yaml.load(hfile)
			self.profilename = profile
			self.config = dictcfg
		except FileNotFoundError as e:

			logger.critical("No configuration file "+fname)
			if( not isexist ):
				logger.critical("Use default directory")
				return self.config
			else:
				return None
		return dictcfg

	def init(self, input_path ='', profile_path ='', static_path ='', root_url ='', fw_url ='', static_url ='', template_path ='', data_path ='', static_idx_path ='', home_url ='', fdebug = 0, webmaster = 'parladata'):
		dictcfg =  {
		'profile' : self.profilename,
		'build' :
		{
		'source_path' : input_path,
		'profile_path' : profile_path,
		'static_path' : static_path,
		'template_path' : template_path,
		'data_path' : data_path,
		'static_idx_path' : static_idx_path,
		'fdebug' : fdebug,
		},
		'framework' :
		{
		'root_url' : root_url,
		'fw_url' : fw_url,
		'static_url' : static_url,
		'home_url' : home_url,
		'webmaster' : webmaster
		}}
		self.save(self.profilename, dictcfg)
