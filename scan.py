"""
Parladata
scan.py
"""

# IMPORT
import sys
import os
import datetime, time
import logging

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
import markdown2
import json
import csv
#from pprint import pprint



# parladata package
from .log import logger
from .misc import plw_get_url, PlwWeb, StringMetadata

"""
class StringMetadata(str):
	metadata = None
"""

#
# Generate Index files
#
class PlwScan(object):
	def __init__(self, outpath=''):
		self.static_idx_path = outpath

		self.routeidx = {}
		self.routeidxname = ""
		self.routeisopen = False

		# set by scanoption()
		self.static_path = '' # where html is generated
		self.screenshot_static_path = '' # where screenshot images are generated
		self.screenshot_url = '' # where screenshot images are generated as url

		self.static_url = ''  # which server is used to load web pages
		self.source_path = '' # what is the drive path


		# set by activeurl()
		self.active_url = '' # current url managed by PlwData

		# extension
		self.extload = {
			'.md': self.ext_md,
			'.jpg' : self.ext_img, '.png' : self.ext_img,
			'.avi' : self.ext_video, '.mp4' : self.ext_video,
			'.htm' : self.ext_html, '.html' : self.ext_html
		}

		# use web selenium for screenshot
		self.useweb = 0

	def __del__(self):
		if self.useweb == 1:
			del self.web

	def openidx(self, name):
		if( self.routeisopen == True ):
			#logger.info("SCAN is opened - skip or need to close first")
			return False
		self.routeisopen = True
		self.routeidxname = name
		#logger.info("IDX OPEN for "+name)
		return True

	def closeidx(self):
		if( self.routeisopen == False ):
			#logger.info("SCAN not opened - skip")
			return False
		logger.info("IDX "+self.routeidxname+ " has "+str(len(self.routeidx)))
		print(self.routeidx)
		return True

	def addidx(self, plwd):
		if( self.routeisopen == False ):
			#logger.info("SCAN not opened - skip")
			return False

		info = {}
		url = plwd['sourceurl']
		#print(plwd)
		#print(type(plwd))

		info['sourceurl'] = plwd['sourceurl']
		try:
			info['pagetitle'] = plwd['pagetitle']
		except:
			info['pagetitle'] = 'no title'
		try:
			info['pagedescription'] = plwd['pagedescription']
		except:
			info['pagedescription'] = 'no description'
		self.routeidx[url] = info
		print(self.routeidx)

		return True


	def scan(self, sourcedir, scanfor = '', soption = '@none', jsonfile = "idx.json"):
		#if sourcedir[-1:] == '\\':
		#	sourcedir = sourcedir[:-1]
		#import pdb; pdb.set_trace()

		# scan option :
		#	@none
		#	@files
		#	@screenshot
		#	@from=relative path to add to source dir
		#

		scanoption = soption.lower()
		logger.info("ZENSCAN source %s for %s (option %s)" %(sourcedir, scanfor, scanoption))
		isScanOnlyfiles = scanoption.find('@files')
		isScreenshot = scanoption.find('@screenshot')
		if( isScreenshot == 0 ):
			logger.info("ZENSCAN open selenium Firefox.. takes a little time...")
			try:
				self.web = PlwWeb()
				self.useweb = 1
			except Exception as e:
				logger.critical("Selenium Firefox can not be set up "+str(e))
				logger.critical("No screenshot generated")
				self.useweb = 0
		nbgeneration = -1
		if( scanoption.find('@fromsourcepath') == 0 ):
			if( scanoption.find('@fromsourcepath=') == 0 ):
				sourcedir = self.source_path+scanoption[16:]
			else:
				sourcedir = self.source_path
			logger.debug("change sourcedir for scan to "+sourcedir)
		elif( scanoption.find('@fromabsolutepath=') == 0 ):
			sourcedir = scanoption[18:]
			logger.debug("change sourcedir for scan to "+sourcedir)

		try:
			for dirnum, (dirpath, dirs, files) in enumerate(os.walk(sourcedir)):
				logger.debug("scan find directory : %s", dirpath)
				nbgeneration = dirpath.count('\\')

				# root
				if( dirnum == 0):
					self.idxroot = dirpath
					self.idxgeneration = nbgeneration
					self.generation = 0
					self.parent = 0
					self.idx = self.idxroot
					self.scanid = []
					self.scanid.append(1) # check if ok
					self.lenidbefore = 0
					self.countid = 1
					self.tochtml = []
					self.toclist = {}
					self.breadcrump = []
				else:
				# parent and child numerotation into list scanid as [1, 1, 2, 1...]
					if( self.parent != nbgeneration ):
						if( nbgeneration < self.parent ):
							# previous generation
							idtoremove = self.parent-nbgeneration
							del self.scanid[-idtoremove:]
							logger.info('breadcrump len '+str(len(self.breadcrump)))
							idtoremove += 1
							del self.breadcrump[-idtoremove:]
							logger.info('breadcrump len '+str(len(self.breadcrump)))
							logger.info("previous generation nb to remove "+str(idtoremove))
							self.countid = self.scanid[-1] + 1
							self.scanid[-1] = self.countid
						else:
							# new generation
							self.countid = 1
							self.scanid.append(self.countid)
						self.parent = nbgeneration
					else:
						self.countid += 1
						if len(self.scanid) > 1:
							self.scanid[-1] = self.countid
						else:
							self.scanid.append(self.countid)
						del self.breadcrump[-1:]


					self.generation = nbgeneration
					self.idx = dirpath.split(self.idxroot+'\\')[-1].split('\\')[-1]
					self.curdirnum = dirnum
					self.breadcrump.append(self.idx)
					logger.debug("add breadcrump "+self.idx +" len "+str(len(self.breadcrump))+" breadcrump "+'>'.join(self.breadcrump))

				# add to scan memory the directory
				if( len(files) > 0 ):
					self.scandir(dirpath, dirs, files)
					# just pure number without .
					self.lenidbefore = len(''.join(map(str, self.scanid)))
					if( scanfor != '' ):
						tocid = '.'.join(map(str, self.scanid))
						logger.debug("SCAN "+tocid+" FOR "+scanfor)
						i = 1
						self.toclist[tocid]['scan'] = {}
						for filename in files:
							if filename.rfind(scanfor) != -1:
								if i > 1:
									#self.countid += 1
									#self.scanid.append(self.countid)
									#tocid = '.'.join(map(str, self.scanid))
									logger.debug("SCAN ADD "+tocid+" FOR "+scanfor)
								ok = self.scanfile(tocid, scanfor, dirpath, filename, i)
								if( ok == True ):
									i += 1
								else:
									logger.critical("error walking file : "+filename)
									return ''

				self.toclist[tocid]['breadcrump'] = list(self.breadcrump)
				self.toclist[tocid]['scanlen'] = len(self.toclist[tocid]['scan'])
				if isScanOnlyfiles != -1:
					logger.debug("scan only files - option set with @files")
					break



		#except ValueError as e:
		except Exception as e:
			logger.critical("error walking dir : "+sourcedir+" "+str(e))
			if( self.useweb ):
				self.useweb = 0
				del self.web
			return ''
		if( nbgeneration == -1):
			logger.critical("find nothing in dir "+sourcedir)
			return ''

		# make deep to close and open <ul> analyse
		lastdeep = 1
		for keyid, data in reversed(sorted(self.toclist.items())):
			closelevel = data['deepbefore'] - data['deep']
			if( closelevel < 0 ):
				closelevel = 0
			if( data['deep'] > data['deepbefore'] ):
				openlevel = 1
			if( lastdeep > data['deep'] ):
				openlevel = 1
			else:
				openlevel = 0
			if( data['deep'] == lastdeep ):
				samelevel = 1
			else:
				samelevel = 0
			logger.debug( 'deep %d before %d lastdeep %d close %d open %d same %d - %s' %(data['deep'], data['deepbefore'], lastdeep, closelevel, openlevel, samelevel, keyid))
			data['deepopen'] = openlevel
			data['deepclose'] = closelevel
			data['deepsame'] = samelevel
			lastdeep = data['deep']

		# write json
		#self.htmldir()
		if jsonfile.find('.json') == -1:
			jsonfile += '.json'
		self.jsondir(jsonfile)


		return jsonfile


	def htmldir(self):
		logger.debug("HTML")
		logger.debug(self.tochtml)

	def jsondir(self, fout):
		logger.debug("JSON")
		#logger.info("toclist 2 " + str(self.toclist['2']))
		data = self.toclist
		#data = json.dumps(self.toclist, indent=4, sort_keys=True)
		#logger.debug("JSON DUMP")
		#logger.debug(data)



		#pprint(data)
		try:
			myFile = open(fout, "w", encoding='utf-8')
		except FileNotFoundError as e:
			getdir = os.path.dirname(fout)
			logger.info("create directory "+getdir+" from "+fout)
			try:
				os.makedirs(getdir, 0o777)
				try:
					myFile = open(fout, "w", encoding='utf-8')
				except FileNotFoundError as e:
					logger.critical("impossible to use file "+fout)
					return False
			except:
				raise
			#
			# more error check to add
			#
		try:
			json.dump(data, myFile, indent=4)
		except ValueError as e:
			logger.critical("ERROR in json generation "+str(e))
		myFile.close()
		myFileinfo = os.stat(fout)
		logger.info("generate json file %s : %d bytes" % (fout, myFileinfo.st_size))
		#logger.debug(data)
		return True

	def scandir(self, dirpath, dirs, files):
		nbdirs = len(dirs)
		nbfiles = len(files)
		scanid = '.'.join(map(str, self.scanid))

		info = {}
		info['folder'] = self.idx
		info['nbfiles'] = nbfiles

		# manage deep as
		# <li>
		#	<ul><li>
		#		<ul><li>
		info['deep'] = len(self.scanid)
		# deep previous element
		info['deepbefore'] = self.lenidbefore
		# deep need to close </li></ul> will be managed after everybody is filled
		# for moment, just say no
		logger.debug(info)
		self.toclist[scanid] = info
		#self.toclist[scanid] = ( self.idx, nbfiles, 'url to add' )
		logger.debug("IDX %s %s%s" %(str(self.scanid), self.idx, " ("+str(nbfiles)+")" if nbfiles > 0 else ""))
		self.tochtml.append("%s %s%s" %(str(self.scanid), self.idx, " ("+str(nbfiles)+")" if nbfiles > 0 else ""))
		#return scanid

	def ext_md(self, fname):
		logger.debug("load markdown file")
		html = markdown2.markdown_path(fname, extras=["metadata", "markdown-in-html", "tables"])
		return html

	def ext_img(self, fname):
		logger.debug("load image file")
		html = StringMetadata(fname)
		html.metadata = { 'filetype' : 'image' }
		return html

	def ext_html(self, fname):
		logger.debug("load html file")
		html = StringMetadata(fname)
		html.metadata = { 'filetype' : 'html' }
		#import pdb; pdb.set_trace()
		if self.useweb == 1:
			if( fname.find(self.source_path) != -1 ):
				logger.debug("screenshot "+fname+" "+self.source_path)
				fname = fname[len(self.source_path):]
				logger.debug(" screenshot filename now just is "+fname)

			logger.info("screenshot %s %s %s %s" %(self.static_url, fname, self.screenshot_static_path, self.screenshot_url))
			screenshot = self.web.screenshot(self.static_url, fname, self.screenshot_static_path, self.screenshot_url)
			html.metadata['screenshot'] = self.static_url + screenshot


		return html


	def ext_video(self, fname):
		logger.debug("load video file")
		html = StringMetadata(fname)
		html.metadata = { 'filetype' : 'video' }
		return html


	def scanfile(self, tocid, scanfor, dirpath, filename, i):
		fname = os.path.join(dirpath,filename).lower()
		fnamext = os.path.splitext(fname)[1]
		if fname.endswith(scanfor.lower()):
			try:
				statinfo = os.stat(fname)
				logger.debug(" file: "+fname+" size: "+str(statinfo.st_size))
				#info = self.toclist[tocid]
				#info = {'file':fname}
				#info['file'] = fname
				#info['filesize'] = statinfo.st_size

				# select from extension witch function to load
				loadfunc = self.extload.get(fnamext, lambda fname: None)
				html = loadfunc(fname)
				if not html:
					logger.critical("do not know what to do with : "+fnamext+" file from scan :"+fname)
					logger.critical("extension not found in parladata definition, skip as a warning")
					return True

				logger.debug("load "+fnamext+" file from scan "+ fname)
				url = plw_get_url(fname, self.static_path, self.static_url, self.source_path)
				logger.info('url %s file %s' %(url[0], url[1]))
				html.metadata['url'] = url[0]
				html.metadata['content'] = html
				#html.metadata['scanfile'] = fname
				html.metadata['contentsize'] = statinfo.st_size
				html.metadata['contentdate'] = datetime.datetime.fromtimestamp(statinfo.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
				#time.ctime(statinfo.st_mtime)

				logger.debug('active url %s and %s' %(self.active_url, url[0]))
				if( self.active_url != '' and self.active_url == url[0] ):
					logger.info('not include file as active url : ' + self.active_url)
				else:
					self.toclist[tocid]['scan'][i] = {}
					self.toclist[tocid]['scan'][i] = html.metadata
			except ValueError as e:
				logger.critical("Error as "+str(e))
				return False
			return True
		else:
			return False

	# SCANOPTION
	#	set path for plw_get_url
	def scanoption(self, static_path, static_url, source_path, screenshot_static_path='', screenshot_url ='', static_idx_path = ''):

		logger.debug("scanoption")
		logger.debug("static_path "+static_path)
		logger.debug("static_url "+static_url)
		logger.debug("source_path "+source_path)
		logger.debug("screenshot_static_path "+screenshot_static_path)
		logger.debug("screenshot_url "+screenshot_static_path)
		logger.debug("static_idx_path "+static_idx_path)


		#import pdb; pdb.set_trace()

		if static_idx_path != '':
			self.static_idx_path = static_idx_path

		if static_path != '':
			self.static_path = static_path.lower()

		if screenshot_url != '':
			self.screenshot_url = screenshot_url.lower()


		if screenshot_static_path != '':
			self.screenshot_static_path = screenshot_static_path.lower()
		else:
			self.screenshot_static_path = static_path.lower()
		if( self.screenshot_static_path[-1] != '\\' ):
			self.screenshot_static_path += '\\'


		if static_url != '':
			self.static_url = static_url.lower()
		if source_path != '':
			self.source_path = source_path.lower()

		logger.debug("scanoption")
		logger.debug("static_path "+self.static_path)
		logger.debug("static_url "+self.static_url)
		logger.debug("source_path "+self.source_path)
		logger.debug("screenshot_static_path "+self.screenshot_static_path)
		logger.debug("screenshot_url "+self.screenshot_url)
		logger.debug("static_idx_path "+self.static_idx_path)

	# INITLOAD
	#	loadconfig
	def initload(self, config):
		self.static_idx_path = config['scan']['static_idx_path']
		self.static_path = config['scan']['static_path'].lower()
		self.screenshot_url = config['scan']['screenshot_url'].lower()
		self.screenshot_static_path = config['scan']['screenshot_static_path'].lower()
		if( self.screenshot_static_path[-1] != '\\' ):
			self.screenshot_static_path += '\\'
		self.static_url = config['scan']['static_url'].lower()
		self.source_path = config['scan']['source_path'].lower()

		logger.debug("scanoption")
		logger.debug("static_path "+self.static_path)
		logger.debug("static_url "+self.static_url)
		logger.debug("source_path "+self.source_path)
		logger.debug("screenshot_static_path "+self.screenshot_static_path)
		logger.debug("screenshot_url "+self.screenshot_url)
		logger.debug("static_idx_path "+self.static_idx_path)

	# ACTIVE URL
	#	set active url (for not include in scan)
	def activeurl(self, url):
		self.active_url = url



# MAIN
#
#
