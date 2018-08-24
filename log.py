"""
Parladata
log.py
"""
import os
import logging
from .init import verPackage
global logger


def loginit(fdebug = 0, fname = 'PLD', isConsole = True):

	#logger = logging.getLogger(__name__)
	#if logger.handlers:
	#	return logger

	flevel = logging.INFO if fdebug == 0 else logging.DEBUG
	logname = fname+'.log'
	try:
		os.remove(logname)
	except:
		pass

	logging.basicConfig(filename=logname,
		format='[%(asctime)s] %(filename)s:%(lineno)-4d %(levelname)-6s %(message)s',
		datefmt='%d-%m-%Y:%H:%M:%S',
		level=flevel)

	#fh = logging.FileHandler(logname)

	console = logging.StreamHandler()
	formatter = logging.Formatter('%(filename)s:%(lineno)-4d %(levelname)-6s %(message)s')
	console.setFormatter(formatter)
	if( isConsole ):
		logging.getLogger('').addHandler(console)
	logger = logging.getLogger('ParleData')
	#logger = logging.getLogger(__name__)
	return logger

def loglevel(fdebug = 0):
	flevel = logging.INFO if fdebug == 0 else logging.DEBUG
	logger.setLevel(flevel)
	#logger.info("set level to "+str(flevel))

#logger = logging.getLogger(__name__)
logger = logging.getLogger('ParleData')
#logger = loginit()
