# Import socket module
import socket
import _thread 
import threading 
import sys
import os  
import struct   
from multiprocessing import Process
from time import sleep

portToOpen = 6001
chunkSize=2**16

def connectToTracker():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port=6001
    chunkSize=2**16
    host = "192.168.1.131"
    s.connect((host, port))
    data="1"
    datab=data.encode('utf-8')
    s.send(datab)

    while True:
        l = s.recv(chunkSize)
        print(l.decode('utf-8'))
        data="22/Avengers/5/1,2,4/Ironman/3/2/"
        datab=data.encode('utf-8')
        s.send(datab)
        l = s.recv(chunkSize)
        print(l.decode('utf-8'))
        data="4/"
        datab=data.encode('utf-8')
        s.send(datab)
        l = s.recv(chunkSize)
        print(l.decode('utf-8'))
        break

    s.close()   

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
    
    parameterList=[newfilenamepath[0].decode('utf-8'),newfilenamepath[1].decode('utf-8'),extensionstr,filenamestr]
    paramlist=[struct.pack('%ss' %len(element),str(element).encode('utf-8')) for element in parameterList]

    if(os.path.exists(newfilenamepath[0])):
        print("Works well and fine")

    return paramlist

def validateFolder(filename,chunkID,extension):
    #downloads=os.path.expanduser('~/Downloads')
    #dirpath=downloads+"/"+filename
    dirpath=os.getcwd()
    dirpath+="/sharedFolder"
    print("dirpath: "+dirpath)
    if(os.path.exists(dirpath)==False):
        os.mkdir(dirpath)

    filepath=dirpath+'/'+str(chunkID)+'.'+extension
    dataList=[filepath,dirpath]
    fileAndDir=[struct.pack('%ss' %len(element),str(element).encode('utf-8')) for element in dataList]
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
            os.remove(filepathnew)

    return 

def downloadFileFromPeer(filename,chunkID,totalchunks,ipaddr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = ipaddr #"172.25.105.103"
    port = 6001
    #print("Host: "+host)
    s.connect((host, port))

    data=filename+"/"+str(chunkID)
    datab=data.encode('utf-8')
    s.send(datab)
    count=0
    while True:
        l = s.recv(chunkSize)
        if(count==0):
            paramlist=extractParameters(l.decode('utf-8'))
            stringData=l.decode('utf-8').split('/',2)
            f=open(str(paramlist[0].decode('utf-8')),'wb')
            f.write(stringData[2].encode('utf-8'))
            count=count+1
        else:
            f.write(l)
        if(l.decode('utf-8')==""):
            break
    
    f.close()   
    checkAllFilesPresent(paramlist[1].decode('utf-8'),totalchunks,paramlist[2].decode('utf-8'),paramlist[3].decode('utf-8'))
    s.close()

def send_chunk(c):
    
    while True:
        # receive data from the server # no need
        data = c.recv(1024)
        info = str(data.decode("utf-8"))
        infoList  = info.split('/')
        fileName = infoList[0]
        chunkNeeded = infoList[1]

        f = open(fileName, 'r')
        print('Prepare to send...')
        chunkNumber = int(float(chunkNeeded))

        position = (chunkNumber - 1) * chunkSize
        f.seek(position, 0)
        fileData = f.read(chunkSize)

        f.close()

        filePacket = fileName + "/" + chunkNeeded + "/"
        filePacket = filePacket + fileData
        print(filePacket)
        byteSent = c.send(filePacket.encode("utf-8"))
        print("byte sent: " + str(byteSent))
        # close connection and socket
        c.close()
    s.close()


def connect_to_server():
    print("1. Connect to server")
    print("2. Inform and update server")



def list_files_in_server():
    print("List files in server")


def find_files_in_server():
    print("Find file in server")


def download_file_from_server():
    print("Download file from server")


def disconnect_from_server():
    print("Disconnect from server")


menu = "1. Connect to server\n" \
       "2. List\n" \
       "3. Find\n" \
       "4. Download\n" \
       "5. Quit\n" \
       "Enter your option: "


def client():
    while True:
        option = input(menu)
        if not str.isdigit(option):
            print("Please enter in option(in digits)!\n")
            continue

        option = int(option)
        if option < 1 or option > 5:
            print("Please enter a valid option!\n")
            continue

        if option == 1:
            connect_to_server()
        elif option == 2:
            list_files_in_server()
        elif option == 3:
            find_files_in_server()
        elif option == 4:
            download_file_from_server()
        elif option == 5:
            disconnect_from_server()

def parseDataFromServer(string):
    stringarray=string.split('/')
    filename=stringarray[1]
    command=stringarray[0]
    temp=stringarray[2].split(',')
    chunkID=temp[0]
    ipaddr=temp[1]

    argList=[command,filename,chunkID,ipaddr]
    querylist=[struct.pack('%ss' %len(element),str(element).encode('utf-8')) for element in argList]    
    return querylist

def server():
    s = socket.socket()
    myIpAddress="172.25.97.72"
    #myIpAddress = socket.gethostbyname(socket.gethostname())
    print("myIpAddress: "+myIpAddress)
    s.bind((myIpAddress, portToOpen))
    s.listen(5)
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        _thread.start_new_thread(send_chunk,(c,))
    client()

def p2pclient(stringList):  
    totalchunks=4
    for string in stringList:
        querylist=parseDataFromServer(string)
        if(querylist[0].decode('utf-8')=='3'):
            downloadFileFromPeer(querylist[1].decode('utf-8'),querylist[2].decode('utf-8'),totalchunks,querylist[3].decode('utf-8'))

#Pls change the ipaddress in the stringlist to that of the server, in my case it's my VM
#Pls change the ipaddress to your host computer ipaddress in the server method

if __name__ == '__main__': 
    stringList=["3/sample2.txt/1,172.25.106.48/","3/sample2.txt/3,72.25.106.48/","3/sample2.txt/2,172.25.106.48/","3/sample2.txt/4,72.25.106.48/"]
    #server()
    pserver=Process(target=server)
    pserver.start()
    p2pclient(stringList)
    pserver.join()

    
#main()