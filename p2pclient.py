# Import socket module
import socket
import _thread 
import threading 
import sys
import os  
import struct   
from multiprocessing import Process, Lock
from time import sleep

menu = "1. Connect to server\n" \
       "2. List\n" \
       "3. Find\n" \
       "4. Download\n" \
       "5. Quit\n" \
       "Enter your option: "

portToOpen = 6001
chunkSize=2**16
fileToChunkTracker={}

def connectToTracker():
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
            return "incomplete"
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

    return "completed"

def downloadFileFromPeer(filename,chunkID,totalchunks,ipaddr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = ipaddr #"172.25.105.103"
    port = 6001
    print("Host: "+host)
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
    s.close() 
    return checkAllFilesPresent(paramlist[1].decode('utf-8'),totalchunks,paramlist[2].decode('utf-8'),paramlist[3].decode('utf-8'))
    
# def list_files_in_server(s):

    
# def find_files_in_server(s):

def download_file_from_server(s,filename):
    data="6/"+filename+"/"
    s.send(data.encode('utf-8'))
    l = s.recv(chunkSize)
    decodedData=l.decode('utf-8')
    reply=decodedData.split('/')
    command=reply[0]
    if(reply[0]=='6'):
        if(reply[1]=='1'):
            print("File does not exist in tracker")
        else:
            fileToChunkTracker.update({reply[1]:reply[2]})
            queryForContent(s,reply[1])

def queryForContent(s,filename):
    totalChunks=int(float(fileToChunkTracker.get(filename)))
    data="3/"+filename+"/"
    for x in range(totalChunks):
        temp=(x+1)+","
        data+=temp
    data+="/0"
    s.send(data.encode('utf-8'))
    stringList=[] 
    while True:
        l = s.recv(chunkSize)
        decodedData=l.decode('utf-8')
        if(decodedData[0]=="3"):
            stringList.append(decodedData)
            resultList=p2pclient(stringList)
            #call inform_and_update()
            if(resultList[0]=="completed"): # *rmb list is used for legacy purpose; can also change to a single string 
                fileToChunkTracker.pop(filename)
                ackData="ACK/"+resultList[1]+"/"
                s.send(ackData.encode('utf-8'))
                break

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

def p2pclient(stringList):  
    #totalchunks=4 # *rmb to comment this out  
    for string in stringList:
        querylist=parseDataFromServer(string)
        totaclchunks=fileToChunkTracker(querylist[1].decode('utf-8'))
        if(querylist[0].decode('utf-8')=='3'):
            status=downloadFileFromPeer(querylist[1].decode('utf-8'),querylist[2].decode('utf-8'),totalchunks,querylist[3].decode('utf-8'))
            return [status,querylist[3].decode('utf-8')]

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

def server():
    s = socket.socket()
    myIpAddress = socket.gethostbyname(socket.gethostname())
    print("myIpAddress: "+myIpAddress)
    s.bind((myIpAddress, portToOpen))
    s.listen(5)
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        _thread.start_new_thread(send_chunk,(c,))
    client()

if __name__ == '__main__': 
    lock = Lock()
    stringList=["3/sample2.txt/1,172.25.104.202/","3/sample2.txt/3,172.25.104.202/","3/sample2.txt/2,172.25.104.202/","3/sample2.txt/4,172.25.104.202/"]
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
            pserver=Process(target=server)
            print("Connected to tracker")
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port=6000
            host = "172.17.161.106"
            s.connect((host, port))
            data="1"
            datab=data.encode('utf-8')
            s.send(datab)

            l = s.recv(chunkSize)
            print("wjhjhwejh"+l.decode('utf-8'))
            pserver.start()
            while True:
                option = input(menu)
                if not str.isdigit(option):
                    print("Please enter in option(in digits)!\n")
                    continue

                option = int(option)
                if option < 1 or option > 5:
                    print("Please enter a valid option!\n")
                    continue

                if option == 2:
                    list_files_in_server(s)
                elif option == 3:
                    find_files_in_server(s)
                elif option == 4:
                    filename=input("Enter filename: ")
                    download_file_from_server(s, filename)
                elif option == 5:
                    print("Exiting...")
                    break
            pserver.join()
    s.close()
    


