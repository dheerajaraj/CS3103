
# An example script to connect to Google using socket 
# programming in Python 
import socket # for socket 
import sys
import os  
import struct	
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
	datab=string[2]
	chunkID=int(float(string[1]))
	filename=processor[:len(processor)-1]
	extension=processor[len(processor)-1]
	filenamestr=''.join(filename)
	extensionstr=''.join(extension)
	newfilenamepath=validateFolder(filenamestr,chunkID,extensionstr)
	
	parameterList=[str(newfilenamepath[0]),str(newfilenamepath[1]),extensionstr,filenamestr]
	paramlist=[struct.pack('%ss' %len(element),str(element)) for element in parameterList]

	#print("Filename: "+str(filename)+" ChunkID: "+str(chunkID))
	#print("newfilenamepath: "+newfilenamepath[0])
	#print("Directory path: "+newfilenamepath[1])
	if(os.path.exists(newfilenamepath[0])):
		print("Works well and fine")

	return paramlist

def validateFolder(filename,chunkID,extension):
	downloads=os.path.expanduser('~/Downloads')
	dirpath=downloads+"/"+filename
	#checkAllFilesPresent(dirpath,maxchunksize,extension,filename)
	print("dirpath: "+dirpath)
	if(os.path.exists(dirpath)==False):
		os.mkdir(dirpath)

	filepath=dirpath+'/'+str(chunkID)+'.'+extension
	dataList=[filepath,dirpath]
	fileAndDir=[struct.pack('%ss' %len(element),str(element)) for element in dataList]
	return fileAndDir;

def checkAllFilesPresent(dirpath,maxchunksize,extension,filename):
	outputfile=dirpath+'/'+filename+'.'+extension
	for x in range (maxchunksize):
		filepath=dirpath+'/'+str(x+1)+'.'+extension
		if(os.path.exists(filepath)==False):
			return
		else:
			print("Filepath exists! : "+filepath)

	with open(outputfile,'w') as outfile:
		for y in range (maxchunksize):
			filepathnew=dirpath+'/'+str(y+1)+'.'+extension
			print("filepathnew: "+filepathnew)
			with open(filepathnew,'r') as infile:
				for line in infile:
					outfile.write(line)
					#print(line)
			os.remove(filepathnew)

	return 

		



def downloadFileFromPeer():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port=6001
	hardcodedMaxChunkSize=4
	chunksize=2**16
	print("chunksize: "+str(chunksize))
	host = "172.25.107.22"
	port = 6001
	s.connect((host, port))

	data="sample2.txt/4"
	datab=data.encode('utf-8')
	s.send(datab)
	count=0
	while True:
		l = s.recv(chunksize)
		if(count==0):
			paramlist=extractParameters(l.decode('utf-8'))
			stringData=l.decode('utf-8').split('/',2)
			f=open(str(paramlist[0]),'wb')
			f.write(stringData[2].encode('utf-8'))
			count=count+1
		else:
			f.write(l)
		if(l.decode('utf-8')==""):
			break
	
	f.close()	
	checkAllFilesPresent(paramlist[1],hardcodedMaxChunkSize,paramlist[2],paramlist[3])

	
	s.close()


downloadFileFromPeer()