"""
Parladata
log.py
"""

import logging
from .init import verPackage
global logger


def loginit(fdebug = 0, fname = ''):
	print("LOGINIT as "+str(fdebug))
	if( fname == ''):
		fname = verPackage
	flevel = logging.INFO if fdebug == 0 else logging.DEBUG
	logging.basicConfig(level=flevel)
	logger = logging.getLogger(fname)
	return logger

def loglevel(fdebug = 0):
	flevel = logging.INFO if fdebug == 0 else logging.DEBUG
	logger.setLevel(flevel)
	logger.info("set level to "+str(flevel))


logger = loginit()
