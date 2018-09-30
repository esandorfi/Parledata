# -*-coding:utf-8 -*-
"""
PlwInit
get_v

"""

# IMPORT
import sys
import os
from datetime import datetime


from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
import markdown2
import json
import csv
from pprint import pprint


# parladata global string
verPackage = "parledata"

# parladata package
from parledata.log import logger, loglevel
from .template import PlwTemplate
from .data import PlwData
from .scan import PlwScan

from logging import DEBUG, CRITICAL, INFO
# GLOBAL VARIABLES
# info

WEBMASTER = 'Parle Data from Parle Web'

from datetime import datetime

__all__ = ['whoiam', 'PlwInit', 'get_v']

def whoiam():
    print("[%s] %s" % (datetime.now(), WEBMASTER))

# return dict values
def get_v(data, *args):
	if args and data:
		element  = args[0]
		if element:
			value = data.get(element)
			return value if len(args) == 1 else get_v(value, *args[1:])


# OBJECT PlwInit
#	Use as container for configuration
#	Use as route commands
#
# 	object defined
#		myTemplate (PlwTemplate), myData (PlwData)
#	variables defined
#		stopIfError, noError - route function return
#		static - static output path
#	functions
#		__init__, route, pushstatic
#
class PlwInit(object):
	# INIT
	# SET DEFAULT URLS AND PATH
	def __init__(self, *args):
		# set datetime
		self.dtstart = datetime.now()
		self.stopIfError = True
		self.noError = True
		self.isInit = False
		self.history = []



	def initload(self, config):
		# loglevel
		#loglevel(fdebug)

		# replace url
		"""
		root_url = config['build']['root_url'].replace('\\', '/')
		fw_url = config['build']['fw_url'].replace('\\', '/')
		static_url = config['build']['static_url'].replace('\\', '/')
		home_url = config['build']['home_url'].replace('\\', '/')
		media_url = config['build']['media_url'].replace('\\', '/')
		"""

		self.buildmap = config['profile']

		#import pdb; pdb.set_trace()
		self.writehtml = True
		if 'nohtml' in config['build'] and config['build']['nohtml'] == 1:
			self.writehtml = False
			logger.info("--- NOHTML IS TRUE - NO HTML WILL BE GENERATED, ONLY JSON FILES")


		if not config['build']['static_path'][-1] == '\\':
			config['build']['static_path'] = config['build']['static_path'] + '\\'

		self.static = config['build']['static_path']

		# init plwtemplate object (jinja)
		if( self.writehtml ):
			self.myTemplate = PlwTemplate(config['build']['template_path'], config['build']['static_path'])
		else:
			self.myTemplate = {}

		# init PlwData (data content to html/json)
		self.myData = PlwData(self.myTemplate, self.static)
		self.myData.writehtml = self.writehtml

		# init PlwScan (index content)
		self.myScan = PlwScan()
		self.myScan.initload(config)

		# dict for index generated from plwidx.scan call,
		# used after in plwdata as { idxname : json full pathname }
		self.myData.idxjson = {}



		# directories for geting data and creating html
		# and be sure static has end \
		if not config['build']['source_path'][-1] == '\\':
			config['build']['source_path'] = config['build']['source_path'] + '\\'


		self.myData.static_path = self.static # do a 2nd time after init - just to understand code better

		self.myData.source_path = config['build']['source_path']
		self.myData.original_source_path = config['build']['source_path']
		self.original_source_path = config['build']['source_path']
		self.myData.source_data = config['build']['profile_path']
		# self.myData.content_path = config['build']['data_path']
		# path in static dir where idx json files are generated

		if( 'media_path' in config['build'] ):
			self.myData.media_path = config['build']['media_path']
		else:
			self.myData.media_path = self.static + "media"
		self.media_path = self.myData.media_path


		self.myData.idxjson_path = config['build']['static_idx_path']

		"""
		# url defined for jinja templates
		self.myData.home_url = config['build']['home_url']
		self.myData.root_url = config['build']['root_url']
		self.myData.fw_url = config['build']['fw_url']
		"""

		try:
			self.static_url = config['framework']['static_url'].lower()
		except:
			self.static_url = config['build']['static_url'].lower()
		self.myData.static_url = self.static_url

		"""
		if( 'media_url' in config['build'] ):
			self.myData.media_url = config['build']['media_url']
		else:
			self.myData.media_url = self.static_url + "media"
		self.media_url = self.myData.media_url
		self.myData.webmaster = config['build']['webmaster']
		"""

		self.myData.build_fw = config['framework']

		self.myData.profile = config['build'] # instead of {}



		# stop build if errors
		self.stopIfError = True
		self.noError = True
		self.sharedprofile = self.myData.profile # instead of {}
		#pprint(self.sharedprofile)

		# init loaded
		self.isInit = True

	#def __del__(self):
	def end(self, justClose = False):
		#import pdb; pdb.set_trace()
		self.closeidx()
		if( not justClose ):
			dtend = datetime.now()
			d = dtend - self.dtstart
			logger.info("--- %s end in %s seconds" %("OK" if self.noError == True else "---- ERROR", d))
			if self.noError == True:
				logger.info("--- OK, IT IS DONE")
			else:
				logger.info("--- ERROR")

	def clearhistory(self):
		del self.history
		self.history = []

	def sethistory(self, history, type = INFO):
		if( type == DEBUG ):
			msg = "(debug history) "
			logger.debug(history)
		elif( type == CRITICAL ):
			msg = "(!!!!!!!! history) "
			logger.critical(history)
		else:
			msg = "(history) "
			logger.debug(history)
		if( not self.history ):
			self.history = []
		self.history.append(msg+history)

	def gethistory(self):
		if( self.history ):
			msg = '<br>'.join(self.history)
		else:
			msg = " build did nothing "
		return msg

	# IDX
	def openidx(self, name = ''):
		return self.myScan.openidx(name)
	def closeidx(self):
		if( self.noError == True ):
			try:
				return self.myScan.closeidx()
			except:
				return self.noError
		else:
			return self.noError


	# ROUTE
	# GENERATE HTML FILE
	def route(self, fdata, ftemplate = '', fhtml = '', isprofile = False, isjobending = True):
		if self.isInit == False:
			self.sethistory("No configuration loaded", CRITICAL)
			return False

		if self.stopIfError is True and self.noError is False:
			self.sethistory("Previous error - skip next file : "+fhtml, CRITICAL)
			return False

		if self.writehtml and not self.myTemplate.is_valid():
			self.sethistory("PlwTemplate is not set", CRITICAL)
			return False

		self.myData.myScan = self.myScan
		# WRITE STATIC WITH DATA AND TEMPLATE
		if not self.myData.load_markdown(fdata, isprofile, fhtml, ftemplate):
			self.sethistory("EMPTY DATA OR DATA WENT WRONG", CRITICAL)
			self.noError = False
			return False
		#import pdb; pdb.set_trace()
		if ftemplate == '' and self.myData.template != '':
			ftemplate = self.myData.template
		if isprofile == True:
			self.myData.profile = {}
		if isjobending == True:
			self.noError = self.myData.write(self.myData.data, ftemplate, fhtml, isprofile)

		# for idx
		if( self.noError == True):
			if isprofile == True: #open idx when profile document
				self.openidx()

			if( 'pagetitle' not in self.myData.data ):
				self.myData.data['pagetitle'] = fdata
			self.myData.data['zengabarit'] = ftemplate
			self.myData.data['zensource'] = fdata
			if( 'url' not in self.myData.data ):
				if( isprofile == True):
					self.myData.data['url'] = 'profile.json'
					self.myData.data['type'] = 'profile'
				else:
					self.myData.data['url'] = 'empty'
			self.myScan.addidx(self.myData.data)
			# self.noError = self.myScan.addidx(self.myData.data)

		if( self.noError == True):
			if( isprofile == True ):
				self.sharedprofile = self.myData.data
				#pprint(self.sharedprofile)
				self.sethistory("Initialize shared profile from "+fdata)
			if( isjobending == True ):
				if( self.myData.url ):
					self.sethistory(fdata +" + " +ftemplate +"-> "+self.myData.url[0])
				self.noError = self.myData.ending(self.myScan)

		return self.noError

	# CHANGE DATA PATH
	def sourcepath(self, sou = ''):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False

		if( sou == '' ):
			sou = self.original_source_path
		self.myData.source_path = sou
		if not self.myData.source_path.endswith('\\'):
			self.myData.source_path = self.myData.source_path + '\\'
		logger.info("#")
		logger.info("# source_path : "+self.myData.source_path)

	"""
	# PUSH STATIC
	# 	ADD SUBFOLDER TO STATIC PATH
	#	set variable PWLTEMPLATE static_path
	#	if changecomplete, apply fullpathname, instead relative from PWLINIT
	def pushstatic(self, ffolder = '', fchangecomplete = 0):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False

		#import pdb; pdb.set_trace()

		if self.stopIfError is True and self.noError is False:
			return False
		if ffolder == '':
			tmppath=self.static
		else:
			if( fchangecomplete == 1 ):
				tmppath = ffolder;
			else:
				if( self.static[-1] != '\\' ):
					tmppath = self.static+"\\"+ffolder
				else:
					tmppath = self.static + ffolder
		#no need ## self.myData.static_url = self.static_url +ffolder+"/"
		self.myTemplate.set_staticpath(tmppath)
		self.myData.static_path = self.myTemplate.static_path
	"""

	def getstatic(self):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False
		return self.static

	def getmedia(self):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False
		return self.myData.media_path

	def getsource(self):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False
		return self.original_source_path

	def getjson(self):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False
		return self.myData.idxjson_path

	# PROFILE
	#	SET SHARED COMMUN INFORMATION FROM A SPECIFIC FILE
	def profile(self, fdata):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False


		if self.stopIfError is True and self.noError is False:
			return False
		logger.debug("# load commun profile file : "+fdata)
		self.route(fdata, 'profile', '', True)

	# ADDIDX
	#	ADDIDX
	def addidx(self, idxname, idxpath):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False

		self.myData.idxjson[idxname] = idxpath;
		logger.info("INIT ADD idx [%s] from %s" %(idxname, idxpath))
