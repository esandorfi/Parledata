# -*-coding:utf-8 -*-
"""
PlwTemplate

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
from .data import PlwData



# OBJECT PLWTEMPLATE
#	is_valid
#	load_templates
class PlwTemplate(object):
	# INIT
	def __init__(self, tem, sta):
		self.nbtemplates = 0
		self.templates_path = tem
		self.load_templates()
		logger.info("template_path : %s, load %d templates " %(self.templates_path, self.nbtemplates))
		logger.debug("templates defined : "+str(self.templates_env.list_templates()))
		self.set_staticpath(sta)

	# SET STATIC PATH
	def set_staticpath(self, sta):
		self.static_path = sta
		if not self.static_path.endswith('\\'):
			self.static_path = self.static_path + '\\'
		logger.debug("#")
		logger.debug("# static_path : "+self.static_path)

	# IS_VALID
	def is_valid(self):
		if not self.nbtemplates:
			logger.critical("ERROR : Please put JINJA templates files in directory : "+self.templates_path)
			return False
		return True

	# LOAD_TEMPLATES
	def load_templates(self):
		#print("load_templates")
		#print(self.templates_path)

		self.templates_env = Environment(
    		loader=FileSystemLoader(self.templates_path),
    		autoescape=select_autoescape(['html', 'xml']),
			trim_blocks=True,
			lstrip_blocks=True
		)
		if not self.templates_env.list_templates() :
			return False

		self.nbtemplates = len(self.templates_env.list_templates())
		return True
