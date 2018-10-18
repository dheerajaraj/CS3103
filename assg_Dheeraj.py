
# An example script to connect to Google using socket 
# programming in Python 
import socket # for socket 
import sys
import os  
	
# try: 
#   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#   print ("Socket successfully created")
# except socket.error as err: 
#   print ("socket creation failed with error %s" %(err)) 
	
# # default port for socket 
# port = 6000
# data="Hi Dheeraj here. THis project is lame"
# datab=data.encode('utf8')

# try: 
#   #'172.25.106.247'
#   host_ip = '172.25.105.168'#socket.gethostbyaddress('') 
# except socket.gaierror: 
	
#   # this means could not resolve the host 
#   print ("there was an error resolving the host")
#   sys.exit() 

# # connecting to the server 
# s.connect((host_ip, port)) 
# s.sendall(datab)  
# print ("the socket has successfully connected to google "+host_ip)
def extractParameters(datab):
	string=datab.split('/',2)
	processor=string[0].split('.')
	chunkID=int(float(string[1]))
	filename=processor[:len(processor)-1]
	extension=processor[len(processor)-1]
	filenamestr=''.join(filename)
	extensionstr=''.join(extension)
	newfilenamepath=validateFolder(filenamestr,chunkID,extensionstr)
	print("Filename: "+str(filename)+" ChunkID: "+str(chunkID))
	print("newfilenamepath: "+newfilenamepath)
	if(os.path.exists(newfilenamepath)):
		print("Works well and fine")

	return newfilenamepath

def validateFolder(filename,chunkID,extension):
	downloads=os.path.expanduser('~/Downloads')
	dirpath=downloads+"/"+filename

	print("dirpath: "+dirpath)
	if(os.path.exists(dirpath)==False):
		os.mkdir(dirpath)

	filepath=dirpath+'/'+str(chunkID)+'.'+extension
	return filepath;
		


def downloadFileFromPeer():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port=6001
	
	chunksize=2**12
	print("chunksize: "+str(chunksize))
	host = "172.25.105.168"
	port = 6001
	s.connect((host, port))

	data="Hi Jing Rui, I am expecting your file!"
	datab=data.encode()
	s.send(datab)
	count=0
	while True:
		l = s.recv(chunksize)
		if(count==0):
			newfilenamepath=extractParameters(l.decode())
			f=open(newfilenamepath,'wb')
		if(l.decode()==""):
			break
		f.write(l)
		count=count+1

	f.close()
	s.close()

downloadFileFromPeer()