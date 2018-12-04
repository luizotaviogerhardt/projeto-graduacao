import unicodedata


def formatOficialExt(name):
	return name.replace('.','.o')

def formatOficialFolder(name):
	return 'o' + name

def removeExt(name):
	return name.replace('.py', '').replace('.c','')

def unicodeToAscii(code):
	return unicodedata.normalize('NFKD', code).encode('ascii','ignore')