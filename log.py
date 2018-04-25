"""
Parladata
log.py
"""
import os
import logging
from .init import verPackage
global logger


def loginit(fdebug = 0, fname = verPackage):
	logger = logging.getLogger(fname)
	if logger.handlers:
		return logger

	flevel = logging.INFO if fdebug == 0 else logging.DEBUG
	logname = verPackage+'.log'
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
	logging.getLogger('').addHandler(console)
	logger = logging.getLogger(fname)
	return logger

def loglevel(fdebug = 0):
	flevel = logging.INFO if fdebug == 0 else logging.DEBUG
	logger.setLevel(flevel)
	logger.info("set level to "+str(flevel))


logger = loginit()
