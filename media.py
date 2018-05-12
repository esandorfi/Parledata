"""
Parladata
media.py
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
from PIL import Image


from .log import logger


#
# Convert Media files
#
class PlwMedia(object):
	def __init__(self):
		pass

	def __del__(self):
		pass

	# scanimage
	#	copy image to static path
	#	resize
	#	option: @files for only source directory (no subdirs)
	def scanimage(self, foldername, sourcedir, targetdir, resizeimg = 2.5, resizeimgth = 10, scanfor = '.jpg', scanoption = '@files', jsonfile = "scanimage.json"):
		if( targetdir[-1] != '\\' ):
			targetdir += "\\"
		logger.info("SCANIMAGE source %s to %s for %s (option %s)" %(sourcedir, targetdir, scanfor, scanoption))
		nbFiles = 0
		isOk = True
		isScanOnlyfiles = scanoption.lower().find('@files')
		logger.info("isScanOnlyfiles "+str(isScanOnlyfiles))
		imagelist = {}
		try:
			for dirnum, (dirpath, dirs, files) in enumerate(os.walk(sourcedir)):

				for filename in files:
					filenamenoext = filename.split(".")[0].lower()
					filename = filename.lower()
					fname = os.path.join(dirpath,filename).lower()
					if fname.endswith(scanfor):
						nbFiles += 1

						img = Image.open(fname)
						nx, ny = img.size
						logger.debug("image %s format %s width %s mode %s" %(filename, img.format, str(img.size), img.mode))

						if( isScanOnlyfiles == -1 ):
							subdir = dirpath[len(sourcedir):]
							if subdir[-1] != '\\':
								subdir += '\\'
							newfile = targetdir+subdir+filename
							newfileth = targetdir+subdir+"th-"+filename
							logger.debug("dir "+dirpath + " subdir "+subdir+" file "+filename)
						else:
							newfile = targetdir+filename
							newfileth = targetdir+"th-"+filename

						imgresize = img.resize((int(nx/resizeimg), int(ny/resizeimg)), Image.BICUBIC)
						try:
							imgresize.save(newfile,dpi=(100,100))
						except FileNotFoundError:
							getdir = os.path.dirname(newfile)
							logger.info("create directory "+getdir+" from "+newfile)
							try:
								os.makedirs(getdir, 0o777)
								imgresize.save(newfile,dpi=(100,100))
							except:
								raise

						imgresizeth = img.resize((int(nx/resizeimgth), int(ny/resizeimgth)), Image.BICUBIC)
						imgresizeth.save(newfileth,dpi=(72,72))

						imagelist[filenamenoext] = { 'src' : filename, 'srcw' : imgresize.width, 'srch' : imgresize.height,
							'th' : 'th-'+filename, 'thw' : imgresizeth.width, 'thh' : imgresizeth.height }
						logger.info("resize %s in %s and %s" %(filename, str(imgresize.size), str(imgresizeth.size)))

				logger.info("find in directory %s : %d files like %s" %(dirpath, nbFiles, scanfor))
				if isScanOnlyfiles >= 0:
					imagelist['folder'] = foldername
					imagelist['nbfiles'] = nbFiles
					break

		except ValueError as e:
				logger.critical("Error scanimage "+cstr(e))
				isOk = False

		newjson = targetdir+jsonfile
		isOk = self.jsondir(newjson, imagelist)

		return isOk

	def jsondir(self, fout, data):
		logger.debug("JSON DUMP FROM SCANIMAGE")
		logger.debug(data)
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
		try:
			json.dump(data, myFile, indent=4)
		except ValueError as e:
			logger.critical("ERROR in json generation "+str(e))
		myFile.close()
		myFileinfo = os.stat(fout)
		logger.info("generate json file %s : %d bytes" % (fout, myFileinfo.st_size))
		logger.debug(data)
		return True



#
#
