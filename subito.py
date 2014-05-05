import sys #for python arguments
import os  #for file paths
import xmlrpclib
import urllib
import zipfile

def selectItem (listOfItems, keys=None):
	item = None
	if(len(listOfItems) == 1):
		item = listOfItems[0]
	else:
		print "\nSelect one:"
		for i in xrange(len(listOfItems)):
				print " ", (i+1), ":",
				if keys is None:
					temp = listOfItems[i]
				else:
					temp = ""
					for key in keys:
						temp += listOfItems[i][key] + " | "

				print temp

		item = listOfItems[int(raw_input())-1]
	return item

class OpenSubtitles:

	accepted_file_formats = (".3g2",".3gp",".3gp2",".3gpp",".60d",\
							 ".ajp",".asf",".asx",".avchd",".avi",\
							 ".bik",".bix",".box",".cam",".dat",\
							 ".divx",".dmf",".dv",".dvr-ms",".evo",\
							 ".flc",".fli",".flic",".flv",".flx",\
							 ".gvi",".gvp",".h264",".m1v",".m2p",\
							 ".m2ts",".m2v",".m4e",".m4v",".mjp",\
							 ".mjpeg",".mjpg",".mkv",".moov",".mov",\
							 ".movhd",".movie",".movx",".mp4",".mpe",\
							 ".mpeg",".mpg",".mpv",".mpv2",".mxf",".nsv",\
							 ".nut",".ogg",".ogm",".omf",".ps",".qt",".ram",\
							 ".rm",".rmvb",".swf",".ts",".vfw",".vid",".video",\
							 ".viv",".vivo",".vob",".vro",".wm",".wmv",".wmx",\
							 ".wrap",".wvx",".wx",".x264",".xvid")

	def __init__(self):
		self.server_url = "http://api.opensubtitles.org/xml-rpc"
		self.server = xmlrpclib.Server(self.server_url)
		self.token = None
		self.subs_found = None
		self.mPath = None


	def setPath(self, path):
		if os.path.exists(path):
			self.mPath = os.path.abspath(path)
		else:
			print "Path doesnot exist"

	def getAllMovies(self, aPath=None):
		path = aPath if aPath is not None else self.mPath

		if os.path.exists(path):
			print "Checking for movies in '%s'..." % (os.path.abspath(path))
			movies = [filee[:-4] for filee in os.listdir(path) if filee.endswith(self.accepted_file_formats) ]

			return movies

	def serverInfo(self):
		return self.server.ServerInfo()

	def logIn(self, username=None, password=None, language=None, appname=None):
		username = username if username is not None else ""
		password = password if password is not None else ""
		language = language if language is not None else "en"
		appname  = appname  if appname  is not None else "OS Test User Agent"

		self.token = self.server.LogIn(username, password, language, appname)
		self.token = self.token['token']
		return self.token

	def logOut(self):
		resp = self.server.LogOut(self.token)
		self.token = None
		return str(resp)

	def searchSubtitles(self, movieName):
		mRequest = []
		mRequest.append({'query':movieName, 'sublanguageid':'eng'})

		mResponse = self.server.SearchSubtitles(self.token, mRequest)
		self.subs_found = mResponse['data']
		return self.subs_found

	def download(self, subDict):
		if subDict is None or type(subDict) != type({}):
			print "Subs must be not none and dictionary."
			return

		url = subDict['ZipDownloadLink']
		urllib.urlretrieve(url, "".join((self.mPath, "/subs.zip")))

	def noOperation(self):
		return str(self.server.NoOperation(self.token))

	def getSubLanguages(self):
		return str(self.server.GetSubLanguages('en'))
		
	def unZip(self, deleteZipFile=False):

		filepath = "".join(((self.mPath), "/subs.zip"))
		with zipfile.ZipFile(filepath, 'r') as z:
			z.extractall(self.mPath)

		if(deleteZipFile):
			os.remove(''.join(((self.mPath), "/subs.zip")))

	def hashFile(self, name): 
		import struct
		try: 	                 
			longlongformat = 'q'  # long long 
			bytesize = struct.calcsize(longlongformat) 

			f = open(name, "rb") 

			filesize = os.path.getsize(name) 
			hash = filesize 

			if filesize < 65536 * 2: 
				return "SizeError" 

			for x in range(65536/bytesize): 
				buffer = f.read(bytesize) 
				(l_value,)= struct.unpack(longlongformat, buffer)  
				hash += l_value 
				hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
			 

			f.seek(max(0,filesize-65536),0) 
			for x in range(65536/bytesize): 
				buffer = f.read(bytesize) 
				(l_value,)= struct.unpack(longlongformat, buffer)  
				hash += l_value 
				hash = hash & 0xFFFFFFFFFFFFFFFF 

			f.close() 
			returnedhash =  "%016x" % hash 
			return returnedhash 

		except(IOError): 
			return "IOError"



if __name__ == '__main__':
	openSubs = OpenSubtitles()
	
	movie = None
	if len(sys.argv) > 1:
		openSubs.setPath(sys.argv[1])
		movie = selectItem(openSubs.getAllMovies())
		print "Movie found: ", movie
	else:
		print "w00t? heeeeeelp meee"

	openSubs.logIn()
	sub = selectItem(openSubs.searchSubtitles(movie), ['SubFileName', 'SubDownloadsCnt'])
	openSubs.download(sub)
	openSubs.unZip(True)