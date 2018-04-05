

"""
Current path is used for build start path

CONFIGURATION 
ROUTE
routing 
	source : file in markdown format, check first for index.md or specify a filename
	target : 
	template :
template
	path for jinja template	
static
	path where production site is generated 
staticlocal
	path where local site is generated	
staticrootfile
	root file name generated in root for production and in staticlocal for local

sourceassets
	path where are frameworks opensource file 
sourcecontent
	path where content are source content files
sourcemedia
	path where are source media files

configprofile
	path for configuration profile file
sourcemediaprofile
	path where are shared profile media

"""
route = {
"routing" : [
{ "source" : "rd-agile-scrum/sprint-mars-2018" , "target" : "rd/agile-scrum" ,  "template" : "scrum" },
{ "source" : "rd-emmanuel-sandorfi" , "target" : "rd/emmanuel-sandorfi" ,  "template" : "bio" },
],
"template" : "template",
"static" : "static",
"staticlocal" : "local",
"staticrootfile" : "index.html",
"sourcecassets" : "assets",
"sourcecontent" : "data",
"sourcemedia" : "data-media",
"sourcemediaprofile": "data-media/profile",
"configfile" : "configprofile.md"
};

print(route)