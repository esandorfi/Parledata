# BUILD V2
# DATA SETTINGS
profile_path = "py-parleweb"
main_path = "c:\\WWW-Git\\"+profile_path
main_localurl = "http://git.l/"+profile_path+"/"
main_produrl = "/"

# IMPORT
import sys, os, argparse
# IMPORT MODULE LOCAL
enginepath = "c:\\WWW-Git\\python";
sys.path.append(enginepath)
print(enginepath)
try:
    import parladata as zen
except ModuleNotFoundError as e:
    print("MODULE NOT FOUND "+str(e))

# MAIN
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--profilepath', help='[sous répertoire] des données à traiter')
parser.add_argument('-c', '--commit', help='[nom de commit] sauvegarde le travail en package pour versionning')
parser.add_argument('-l', '--local', help='[1 = local] [0 = production] génère les fichiers html dans le répertoire local ou production', default=1)
parser.add_argument('-v', '--verbose', help='[1] log en mode debug', default=0)
parser.add_argument('-i', '--idx', help='[1] do just indexes', default=0)
args = parser.parse_args()
logger = zen.loginit(int(args.verbose), "BUILD")
logger.info("--- BUILD PARLADATA (%s)" % (main_path))
if args.commit is not None:
    logger.info("--- COMMIT VERSIONNING SET TO "+args.commit)
if args.profilepath is not None:
    profile_path = args.profilepath
isLocal = args.local
#
logger.info("--- PROFILE PATH SET TO "+profile_path)
#
# URL SETTINGS
data_path = "data"
input_path = main_path + "\\"+data_path
template_path = main_path + "\\template"
if isLocal == 1:
    logger.info("--- LOCAL : "+main_localurl)
    root_url = main_localurl
    fw_url = main_localurl + "assets/"
    static_url = main_localurl + "local/static/"
    static_path = main_path + "\\local"
else:
    logger.info("--- PRODUCTION : "+main_produrl)
    root_url = "/"
    fw_url = "/assets/"
    static_url = "/static/"
    static_path = main_path+"\\"

# tmp dir for plwidx generation
static_idx_path = static_path+"\\static\\idx\\"
input_idx_path = input_path+"\\idx\\"

#
# INITIALIZE
myZen = zen.PlwInit(input_path, profile_path, static_path,
        root_url, fw_url, static_url, template_path, data_path,
        static_idx_path, int(args.verbose))
myZen.stopIfError = True

# SHARED PROFILE
myZen.profile("ui\\configprofile.md")
myZen.pushstatic("static")

# INDEX
#myIdx = zen.PlwIdx(static_idx_path, myZen)
myIdx = zen.PlwScan(static_idx_path)
if args.idx == '1':
    thisidx = "data-index-formation.json"
    idxfilename = myIdx.scan("data\\formation", ".md", thisidx)
    if( idxfilename == ''):
        logger.critical("Error in idx generation")
        sys.exit(1)
    myZen.addidx(thisidx, idxfilename)
    myZen.route("formation\\index.md", "iuadmin-idx", "zen\\formation")
    #del myIdx
    print("SYS EXIT")
    sys.exit(0)


# NEXT PAGES
"""
myZen.openidx("menuprincipal")

myZen.route("plw-vitrine\\landingv2.md", "data", "test")
myZen.route("ui\\vide.md", "ui-media/svg-pattern.html", "svg-pattern")


#myZen.route("plw-vitrine\\vitrine.md", "vitrine-metadata", "vitrine-metadata")
#myZen.route("plw-vitrine\\vitrine.md", "vitrine-simple", "vitrine-simple")
#myZen.route("plw-vitrine\\vitrine.md", "vitrine", "vitrine")
#myZen.route("sandorfi\\sandorfi.md", "vitrine", "sandorfi")
#myZen.route("rd-sandorfi\\aufildutemps.md", "data", "data")
#myZen.route("ui\\form-newsletter.md", "ui-form-newsletter", "newsletter")

myZen.route("ui\\form-newsletter.md", "ui-form-newsletter", "newsletter")
myZen.route("ui\\vide.md", "ui/nav-top", "oo\\navigation")
myZen.route("ui\\vide.md", "ui/js-parladata.js", "oo\\parladata.js")

myZen.route("rd\\emmanuel-sandorfi\\valeurs.md", "page-simple", "rd-emmanuel-sandorfi")
myZen.route("rd\\parladata\\parladata.md", "page-simple", "rd-parladata-python")
myZen.route("rd\\methodologie\\cahier des charges.md", "page-simple", "rd-cahier-des-charges")
myZen.route("rd\\methodologie\\plan de communication.md", "page-simple", "rd-plan-de-communication")
myZen.closeidx()
"""


# FORMATION
myZen.route("formation\\index.md", "page-scan", "formation\\index")
myZen.route("formation\\optimiser prestashop\\index.md", "page-scan", "formation\\prestashop")
myZen.route("formation\\programmation culturelle\\index.md", "page-scan", "formation\\publier-diffuser-une-programmation-culturelle")
myZen.route("formation\\site culturel\\index.md", "page-scan", "formation\\site-culturel")





# BLOG-CODE

myZen.route("blog-code\\index.md", "page-index", "blog\\index")
myZen.route("blog-code\\seo\\index.md", "page-index", "blog\\seo")
myZen.route("blog-code\\outils\\index.md", "page-index", "blog\\outils")
myZen.route("blog-code\\ui-ux\\index.md", "page-index", "blog\\ui-ux")
myZen.route("blog-code\\python\\index.md", "page-index", "blog\\python")


# INDEX HOME PAGE
myZen.pushstatic()

myZen.route("plw-vitrine\\landingv3.md", "landingv3", "index")

if myZen.noError == True:
    logger.info("--- OK, IT IS DONE")
else:
    logger.info("--- ERROR")
