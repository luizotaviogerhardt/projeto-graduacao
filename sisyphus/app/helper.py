import unicodedata
import urllib


def formatOficialExt(name):
	return name.replace('.','.o')

def formatOficialFolder(name):
	return 'o' + name

def removeExt(name):
	return name.replace('.py', '').replace('.c','')

def unicodeToAscii(code):
	return unicodedata.normalize('NFKD', code).encode('ascii','ignore')

def urlDecode(url):
	return urllib.unquote(url).decode('ascii')

def unicodeListToAscii(array):
	asciiList = []

	for entry in array:
		asciiList.append(unicodeToAscii(entry))

	return asciiList