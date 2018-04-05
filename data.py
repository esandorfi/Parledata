"""
Parladata
data.py
"""
# IMPORT
import sys
import os
import datetime
import logging

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
import markdown2
import json
import csv
from pprint import pprint

# parladata package
from .log import logger
from .scan import PlwScan

# OBJECT PLWDATA
#	load
#	write
class PlwData(object):
	def __init__(self, objcfg):
		self.config = objcfg
		self.idxcount = 0
		self.idx = {}
		self.myScan = PlwScan()

	# LOAD
	#	data from argument
	def load(self, curdata):
		self.data = curdata
		#print(self.data)
		return True

	# LOAD_CSV
	#	data from csv file
	def load_csv(self, metakey, fdata):
		datafile = self.source_pathdata+fdata
		if not os.path.exists(datafile):
			logger.critical("skip csv file - doesn't exist :"+datafile)
			return False
		logger.info("load csv file "+ datafile)
		fcsv = open(datafile, 'r', encoding='utf-8')
		try:
			reader = csv.DictReader(fcsv, delimiter=';')
		except ValueError as e:
			logger.critical("CSV ERROR "+str(e))
			return False

		tmplist = []
		for each in reader:
			#logger.debug(each)
			tmplist.append(each)

		self.idx[metakey] = tmplist
		self.idxcount += 1
		logger.debug("data dump [%s] %d:" %(metakey, self.idxcount))
		logger.debug(self.idx[metakey])
		return True

	# LOAD_JSON
	#	data from json file
	def load_json(self, metakey, fdata):
		datafile = fdata
		if not os.path.exists(datafile):
			logger.critical("skip json file - doesn't exist :"+datafile)
			return False
		logger.info("load json file "+ datafile)
		fjson = open(datafile, 'r', encoding='utf-8')
		try:
			buf = json.load(fjson)
		except ValueError as e:
			logger.critical("JSON ERROR "+str(e))
			return False
		self.idx[metakey] = buf
		self.idxcount += 1
		logger.debug("json dump [%s] %d:" %(metakey, self.idxcount))
		logger.debug(self.idx[metakey])
		#pprint(buf)
		return True

	# CHECK_METADATA
	#	ZENCSV 		load csv file
	#	ZENSCAN 	scan and load json
	def check_metadata(self, keyname, keydata, htmlmetadata):
		if keyname[:6] == 'zencsv':
			logger.debug("FIND META zencsv as key %s value %s" % (keyname, keydata))
			if keydata.find('.') == -1:
				logger.warning("META file doesn't have extension !")
			if( self.load_csv(keyname, keydata) == False ):
				return False

		elif keyname[:7] == 'zenscan':
			if keydata.find('.') == -1:
				keydata += '.json'
			try:
				scanname, scanfor = keydata.split(' ')
			except:
				logger.critical("ZENSCAN has two arguments separated by space : [file generated] [extension to search]")
				logger.critical("Example as follow ZENSCAN: FILETOCREATE .MD")
				return False
			sourcedata = htmlmetadata['sourceurl']
			logger.debug("FIND META zenscan as key %s filename %s scanfor %s" % (keyname, scanname, scanfor))
			if( self.zenscan(scanname, scanfor, sourcedata) == False ):
				return False
			else:
				htmlmetadata[keyname] = scanname

		elif keyname[:7] == 'zenjson':
			if keydata.find('.') == -1:
				keydata += '.json'
			logger.debug("FIND META zenjson as key %s value %s" % (keyname, keydata))
			if( self.load_json(keyname, self.idxjson_path+keydata) == False ):
				return False

		return True

	# ZENSCAN
	def zenscan(self, scanname, scanfor, sourcedata):
		idxfilename = self.myScan.scan(sourcedata, scanfor, scanname)
		if idxfilename == '' :
			logger.critical("Error in idx generation with sourcedata "+sourcedata)
			return False
		self.load_json(scanname, idxfilename)
		return True

	# LOAD_MARKDOWN
	#	data from markdown file
	def load_markdown(self, fdata):

		# set data filepath
		tmpsourceurl = fdata.partition('\\')[0]
		self.source_pathdata = self.source_path+tmpsourceurl+'\\'
		datafile = self.source_path+fdata

		"""
		logger.debug("fdata "+fdata)
		logger.debug("tmpsourceurl "+tmpsourceurl)
		logger.debug("source_pathdata "+self.source_pathdata)
		logger.debug("source_path "+self.source_path)
		"""

		# verify if data metadata still in memory
		if self.idxcount > 0:
			self.idxcount = 0
			self.idx.clear()

		# load markdown
		logger.info("load markdown file "+ datafile)
		if not os.path.exists(datafile):
			logger.critical("data file doesn't exist :"+datafile)
			return False
		html = markdown2.markdown_path(datafile, extras=["header-ids", "metadata", "toc"])
		if not html:
			logger.info("error in markdown file :"+datafile)
			return False

		# add keywords
		html.metadata['content'] = html
		html.metadata['rooturl'] = self.root_url
		html.metadata['fwurl'] = self.fw_url
		html.metadata['sourcedata'] = self.source_data
		html.metadata['sourceurl'] = self.content_path+"/"+tmpsourceurl + "/"
		html.metadata['staticurl'] = self.static_url
		html.metadata['webmaster'] = self.webmaster
		logger.debug("sourceurl : "+html.metadata['sourceurl'])
		logger.debug("staticurl : "+html.metadata['staticurl'])

		# check for metadata

		for keyname, keydata in html.metadata.items():
			if( self.check_metadata(keyname, keydata, html.metadata) == False ):
				return False

		# check for index
		if( self.idxcount > 0 ):
			logger.info("number of index "+str(self.idxcount))
			for keyname, datavalue in self.idx.items():
				html.metadata[keyname] = datavalue
				logger.debug(html.metadata[keyname])
		# add profile
		if bool(self.profile):
			html.metadata["profile"] = self.profile

		# put data in memory
		logger.debug(html.metadata)
		self.load(html.metadata)
		return True

	def writejson(self, fout):
		myFile = open(fout, "w", encoding='utf-8')
		try:
			json.dump(self.data, myFile, indent=4)
		except ValueError as e:
			logger.critical("ERROR in json generation "+str(e))
		myFile.close()
		myFileinfo = os.stat(fout)
		logger.info("generate json file %s : %d bytes" % (fout, myFileinfo.st_size))


	# WRITE
	#	data from argument, template file, static file
	def write(self, curdata, curtemplate, curstatic):

		# print("curtemplate "+curtemplate+" static "+curstatic)
		# use template
		# 	check if curtemplate have '.', if not add '.html'
		# 	check if template is in list_templates() if not use index.html
		if( '.' in curtemplate ):
			tmpfile = curtemplate
		else:
			tmpfile = curtemplate + ".html"

		myTemplatefile = next((x for x in self.config.templates_env.list_templates() if x == tmpfile ), "index.html")
		logger.info("use template : "+myTemplatefile)

		# load data
		self.load(curdata)

		# check if javascript file
		if( '.js' in curstatic ):
			writeJson = False
		else:
			writeJson = True

		# write data
		# 	check if curstatic have '.', if not add '.html'
		if( '.' in curstatic ):
			myStaticfile = self.config.static_path+curstatic
			myJsonfile = myStaticfile.partition('.')[-1]+".json"
		else:
			myStaticfile = self.config.static_path+curstatic + ".html"
			myJsonfile = self.config.static_path+curstatic + ".json"

		# generate static html file from data and template
		try:
			myTemplate = self.config.templates_env.get_template(myTemplatefile)
			html = myTemplate.render(self.data)
			#print(html)
			try:
				myFile = open(myStaticfile, "w", encoding='utf-8')
			except FileNotFoundError as e:
				getdir = os.path.dirname(myStaticfile)
				logger.info("create directory "+getdir+" from "+myStaticfile)
				os.mkdir(getdir)
				myFile = open(myStaticfile, "w", encoding='utf-8')
			myFile.write(html)
			myFile.close()
			myFileinfo = os.stat(myStaticfile)
			logger.info("generate html file %s : %d bytes" % (myStaticfile, myFileinfo.st_size))

		except TemplateNotFound as e:
			logger.critical("ERROR JINJA template not found : "+str(e))
			return False

		except TemplateSyntaxError as e:
			logger.critical("ERROR JINJA template syntax error : "+str(e))
			#return False
			#continue jinja exception to get line number information
			raise
		except UndefinedError as e:
			logger.critical("ERROR JINJA variable not defined : "+str(e))
			raise
		except ValueError as e:
			logger.critical("ERROR in generate html "+str(e))
			return False

		# generate json data file
		if writeJson is True:
			self.writejson(myJsonfile)
		return True
