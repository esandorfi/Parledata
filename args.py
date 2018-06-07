import sys, os, argparse
import yaml
import logging
from .log import logger, loginit

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
	def __init__(self, profilename = ''):
		#import pdb; pdb.set_trace()
		#global logger

		if( profilename == '' ):
			self.profilename = 'PLDATA'
		else:
			self.profilename = profilename
		logger = loginit(0, profilename)

		dirpath = os.getcwd()
		logger.info("current directory is : " + dirpath)

		parledatapath = os.path.dirname(os.path.realpath(__file__))+"\\templates"
		logger.info("current directory is : " + parledatapath)

		self.config =  {
		'profile' : self.profilename,
		'build' :
		{
		'source_path' : dirpath,
		'profile_path' : '', # NOT USED
		'static_path' : dirpath,
		'root_url' : '',
		'fw_url' : 'http://parle.data/assets/',
		'static_url' : '',
		'template_path' : parledatapath,
		'data_path' : '', #NOT USED
		'static_idx_path' : dirpath,
		'home_url' : '',
		'fdebug' : '',
		'webmaster' : ''
		}
		}

		if( profilename != ''):
			logger.info("--- PARLEDATA BUILD WITH "+profilename)
			self.config = self.read(profilename)
		else:
			logger.info("--- PARLEDATA BUILD WITH CURRENT DIR")

	def save(self, fname, dictcfg):
		if( fname.find('.yaml') == -1):
			fname += '.yaml'

		with open(fname, 'w') as hfile:
			yaml.dump(dictcfg, hfile, default_flow_style=False)

	def read(self, fname):
		profile = fname
		if( fname.find('.yaml') == -1):
			fname += '.yaml'
		try:
			with open(fname, 'r') as hfile:
				dictcfg = yaml.load(hfile)
			self.profilename = profile
			self.config = dictcfg
		except FileNotFoundError as e:
			logger.critical("Can't open configuration file "+fname)
			dictcfg = None
		return dictcfg

	def init(self, input_path ='', profile_path ='', static_path ='', root_url ='', fw_url ='', static_url ='', template_path ='', data_path ='', static_idx_path ='', home_url ='', fdebug = 0, webmaster = 'parladata'):
		dictcfg =  {
		'profile' : self.profilename,
		'build' :
		{
		'source_path' : input_path,
		'profile_path' : profile_path,
		'static_path' : static_path,
		'root_url' : root_url,
		'fw_url' : fw_url,
		'static_url' : static_url,
		'template_path' : template_path,
		'data_path' : data_path,
		'static_idx_path' : static_idx_path,
		'home_url' : home_url,
		'fdebug' : fdebug,
		'webmaster' : webmaster
		}
		}
		self.save(self.profilename, dictcfg)
