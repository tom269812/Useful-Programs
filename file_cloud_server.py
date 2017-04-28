#!/usr/bin/env python

#File Cloud Server

#--------------------SPECIAL NOTE-------------------
#Linux
#Change \ slashes in directories to /
#---------------------------------------------------

#-----------------------------------PROGRAM RUNDOWN---------------------------------------
#The server will mainly wait for connections
#After a connection has been established it will ask for a username
#If the username is valid it will go to that specific folder name on the servers computer
#Various functions will be supplied to the user
#-----------------------------------------------------------------------------------------

import socket,time,sys,os,thread,re,hashlib,shutil,datetime,binascii
from PIL import ImageFile

#---------------------MANAGER DATA----------------------
f=open("info.txt","r+")
s_level=f.readline()
s_level=s_level.replace("\n","")
#Server level:Primary or secondary
if s_level != "Primary":
    port=f.readline()
    port=port.replace("\n","")
    port=int(port)
else:
    port=29888
f.close()
#------------------------------------------------------

#-------------------Network Variables------------------
global con,s
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host="192.168.0.199"
close=0
#------------------------------------------------------

#-------Log Variables--------
global logname
s_number=port-29888
logname="Log%s.txt"% s_number
#---------------------------

#-----Path Variables-----
global default_path
default_path=os.getcwd()
#------------------------

#----Download Function Variables----
global data_bank,d_finish
data_bank=[]
#-----------------------------------

#----------Server Message Variable----------
global s_mes,admins,server_uptime
try:
    f=open("s_mes.txt","r+")
    s_mes=f.readline()
    s_mes=s_mes.replace("\n","")
    f.close()
except Exception:
    s_mes="Welcome to Tom's File Cloud!"
#------------------------------------------

#------------------ADMIN LIST--------------
admins=["THOMAS"]
#------------------------------------------

#--------------------------------------------FUNCTIONS--------------------------------------------
def log_update(message):
    global default_path,logname
    current=os.getcwd()
    os.chdir(default_path)
    try:
        f=open(logname,"a+")
    except(IOError):
        f=file(logname,"w+")
        f.write("Log created\n")
    f.write("%s: %s\n"% (time.asctime(),message))
    f.close()
    os.chdir(current)
    
def threaded_download(x):
	global data_bank,d_finish
	#X is the filename
	d_finish=0
	f=file(x,"wb")
	while True:
	   try:
	      if data_bank[0] == " ":
	         break
	      else:
		 f.write(data_bank[0])
		 data_bank.remove(data_bank[0])
	   except Exception as e:
	   	pass
	f.close()
	d_finish=1

def server_update():
    #global con,s
    global s
    
    if os.path.isfile("server_update.py"):
        log_update("Server_Update: File exists")

        s.settimeout(1)
        time.sleep(1)
        s.close()
        execfile("server_update.py")
        
        
    else:
        log_update("Server_update: File doesnt exist, creating one")
        f=file("server_update.py","w+")#overwrite the old one
        f.write("#!/usr/bin/env python\n")
        f.write("import socket,time,sys,os\n")
        f.write("time.sleep(1)\n")
        f.write("s=socket.socket()\n")
        f.write('host="192.168.0.199"\n')
        f.write("port=26777\n")
        f.write("try:\n")
        f.write("   s.bind((host,port))\n")
        f.write("except(socket.error):\n")
        f.write("   time.sleep(2)\n")
        f.write("   s.bind((host,port))\n")
        f.write("s.settimeout(360)\n")
        f.write("try:\n")
        f.write("   s.listen(1)\n")
        f.write("except(socket.timeout):\n")
        f.write("   time.sleep(1)\n")
        f.write("   con.settimeout(1)\n")
        f.write("   time.sleep(0.7)\n")
        f.write('   execfile("file_cloud_server.py")\n')
        f.write("   sys.exit()\n")
        f.write("con,addr=s.accept()\n")
        f.write('con.send("ready")\n')
        f.write("data=''\n")
        f.write("os.remove('file_cloud_server.py')\n")
        f.write("time.sleep(1)\n")
        f.write('f=file("file_cloud_server.py","w+")\n')
        f.write('con.send("ready")\n')
        f.write("while True:\n")
        f.write("   fail=0\n")
        f.write("   try:\n")
        f.write("       data=con.recv(1024)\n")
        f.write("   except(socket.error,socket.timeout) as e:\n")
        f.write("       fail=1\n")
        f.write("   if fail == 0:\n")
        f.write('       if data == "stop":\n')
        f.write("           break\n")
        f.write("       f.write(data)\n")
        f.write("f.close()\n")
        f.write('con.send("Successfully downloaded")\n')
        f.write("con.settimeout(1)\n")
        f.write('execfile("file_cloud_server.py")\n')
        f.write("sys.exit()\n")
        f.close()
        s.settimeout(1)
        time.sleep(1)
        s.close()
        execfile("server_update.py")
       
def main():
    global default_path
    global s,con
    global s_mes,admins
    global data_bank,d_finish
    
    while True:
        close=0 
        try:
            os.chdir(default_path)
        except(os.error):
            log_update("Main: Unable to change directory to default path") 
        fail=0
	
        try:  
            con,addr=s.accept()
            log_update("Obtained connection from: %s"% str(addr))
            if fail == 0:
                mode=con.recv(1024)
		#File for normal and Update for server update
                log_update("Obtained mode: %s"% str(mode))
                if mode == "update":
                    server_update()
                con.send(s_mes)
                user=con.recv(1024)
                log_update("%s Connected"% user) 
                try:
                    os.chdir(user)
                except(os.error):
                    con.send("Directory not available")
                    try:
                    	os.mkdir(user)
                        log_update("New directory created")
                    except(os.error) as e:
                    	log_update("Unable to create directory due to %s"% str(e))
                        con.send("Unable to make directory!")
                        close=1
                        
                if close == 0:
		    con.send("Directory available")
                    time.sleep(0.2)
		    if user in admins: 
		    	con.send("APPROVED")
		    else:
		    	con.send("DECLINED")
			#Server uptime approval
                    while True:
                        try:
                            check_dir="%s/%s"% (default_path,user)# its a forward slash for linux!!!!!!!!!!!!!!!!!!!!!!!!
                            current=os.getcwd()
                            if check_dir != current:
                                os.chdir(user)
                            con.settimeout(360)
                            status=con.recv(1024)

			    if status  == "change_message":#@
			    	log_update("Change message called")
				fail=0
				default_dir=os.getcwd()
				os.chdir("/home/tom/file_cloud_server")
				if user in admins:
					con.send("Success")	
				else:
					print "fail"
					con.send("Fail")
					fail=1
				if fail == 0:
					s_mes=con.recv(1024)
					f=file("s_mes.txt","w+")
					f.write(s_mes)
					f.close()
					
					log_update("Server message changed to %s by %s"% (s_mes,user))
				else:
					log_update("%s tried changing the server message"% user)
				os.chdir(default_dir)



			    if status == "update_file_cloud":#@
			    	log_update("File cloud client update called")
				fail=0
				if user in admins:
					con.send("Success")
					main_dir=os.getcwd()
					oss=con.recv(1024)#Windows or Linux or Windows-exe(has to have caps at the front)
					try:
						os.chdir("/home/tom/file_cloud_updater/Cloud_Updater/%s"% oss)
					except Exception as e:
						log_update("Error occurred in update_file_cloud whilst changing directory")
						log_update(str(e))
						fail=1
						con.send("no")
					if fail == 0:#changed directory to cloud updater
						f=file("file_cloud_client.py","wb")
						time.sleep(0.5)
						con.send("yes")
						while True:
							data=con.recv(1024)
							if data == " ":
								f.close()
								break
							f.write(data)
						log_update("Successfully updated file cloud client")
					os.chdir(main_dir)#it just changes any
				else:
                                    con.send("Fail") 			


                            if status == "contents":#@
                                log_update("Contents called")
                                content=[]
                                rootDir = '.'
                                time.sleep(0.2)    
                                for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
                                    for fname in fileList:
                                        #Formatting the content values, CLEAN UP
                                        if dirName == ".":
                                        	content.append(fname)
                                        else:
                                            	new_dirName=dirName[2:len(dirName)]
					    	if "/" in new_dirName:
                                            		matchObj=re.search(r"(.*)/.*",new_dirName)
                                       			if matchObj:
                                                		folder_name=matchObj.group(0)
                                                		if folder_name in content:
                                                    			pass
                                                		else:
                                                    			if "/" in folder_name:
										try:
											folder_name=matchObj.group(1)
										except(IndexError):
											log_update("Index error in contents")	
                                                        			if "/" in folder_name:
											pass
										else:
											if folder_name in content:
												pass
											else:
												content.append(folder_name)
									else:
										if folder_name in content:
											pass
										else:
											content.append(folder_name)
                                              		else:
								if folder_name in content:
									pass
								else:
                                                			content.append(folder_name)
						else:
							if new_dirName in content:
								pass
							else:
								content.append(new_dirName)
                                con.send(str(content))


                            if status == "upload":#@
                                log_update("Upload called")
                                f_name=con.recv(1024)
            			log_update("Uploading %s"% f_name)
                                data=""
				data_bank=[]
				thread.start_new_thread(threaded_download,(f_name,))				
				d_finish=0
				packet_count=0
                                while True:
					data=con.recv(5000)
					if data == " ":
						data_bank.append(" ")
						break
					packet_count+=1
					data_bank.append(data)
					
				while True:#waiting for the function to finish up
					if d_finish == 1:
						break
				con.send("File download successful!")
				#md5 check
				md5=con.recv(1024)
				f=open(f_name,"rb")
				try:
					check_md5=hashlib.md5(f.read()).hexdigest()
				except(MemoryError):
					log_update("MemoryError in hash check of upload")
					check_md5=0
				con.send(str(check_md5))
				if md5 == check_md5:
					log_update("Uploaded %s successfully!"% f_name)
				else:
					log_update("Uploaded %s unsuccessfully!"% f_name)
				log_update ("The upload consisted of %s packets"% packet_count)
				

                            if status == "upload_directory":#@
                                log_update("Upload_Directory called")
               			t_dir=con.recv(1024)
				home_dir=os.getcwd()
				fail=0
				if os.path.isdir(t_dir) == True:
					shutil.rmtree(t_dir)
				os.mkdir(t_dir)
				os.chdir(t_dir)
				log_update("Target directory: %s"% t_dir)
				con.send("ready")            	
                                while True:
					msg=con.recv(1024)
					if msg == "Completed":
						break
					#Split data
					mode,fname=msg.split(":")
					if mode == "folder":
						#Ask for the directory
						f_dir=con.recv(1024)
						original_dir=os.getcwd()
						if f_dir != " ":#Will be a space when it's the main directory
							os.chdir(f_dir)
						os.mkdir(fname)
						os.chdir(original_dir)
					if mode == "file":
						#Ask for the directory
						fail=0
						f_dir=con.recv(1024)
						if f_dir != " ":
							original_dir=os.getcwd()
							try:
								os.chdir(f_dir)
							except Exception:
								log_update("Unable to change directory for file download")
								fail=1
						if fail == 0:
							image=0
							formats=[".jpg",".bmp",".png"]
							for form in formats:
								if form in fname:
									image=1
									p=ImageFile.Parser()
							if image == 0:
								f=file(fname,"wb")
							while True:#EVENTUALLY CHANGE THIS TO THREADED WRITING
								data=con.recv(4000)
								if data == "stop":
									break
								if image == 0:
									f.write(data)
								else:
									p.feed(data)
							if image == 0:
								f.close()
							else:
								fail=0
								try:
									im=p.close()
								except Exception:
									log_update("Unable to format picture")
									fail=1
								if fail == 0:
									im.save(fname)
						 	check_md5=con.recv(1024)
                                                        #Send the client an md5 hash of the file
                                                        f=open(fname,"rb")
                                                        try:
                                                                md5=hashlib.md5(f.read()).hexdigest()
                                                        except Exception:
                                                                log_update("Memory error with hash check")
                                                                md5="0"
                                                        f.close()
                                                        con.send(md5)
                                                        if check_md5 == md5:
                                                                log_update("Downloaded %s successfully"% fname)
                                                                log_update("Hash check is valid")
                                                        else:
                                                                log_update("Downloaded %s unsuccessfully"% fname)
                                                                log_update("Hash check is invalid")
						os.chdir(original_dir)
				os.chdir(home_dir)
				log_update("Downloaded %s successfully"% t_dir)

                            if status == "download":#@
                                log_update("Download called")
                                f_name=con.recv(1024)
                                try:
                                    f=open(f_name,"r+")
                                except(IOError,TypeError) as e:
                                    con.send("%s :Doesnt exist!"% f_name)
                                    fail=1
                                if fail == 0:
				    log_update("Downloading %s"% f_name)
                                    time.sleep(0.2)
                                    con.send("Sending")
                                    f_size=0
                                    while True:
                                        data=f.read(1024)
                                        if data == "":
                                            f.close()
                                            break
                                        f_size+=1024
                                    f=open(f_name,"r+")
                                    time.sleep(0.2)
                                    con.send(str(f_size))
                                    time.sleep(1)
                                    while True:
                                        data=f.read(5000)
                                        if data == "":
						f.close()
						break
                                        con.send(data)
				    time.sleep(1)
                                    con.send(" ")
				    md5=con.recv(1024)
				    f=open(f_name,"rb")
				    try:
				    	check_md5=hashlib.md5(f.read()).hexdigest()
				    except(MemoryError):
				    	log_update("Memory Error in hash check of download")
				        check_md5=0
				    con.send(str(check_md5))
				    if check_md5 == md5:
				    	log_update("Downloaded %s successfully"% f_name)
				    else:
				    	log_update("Downloaded %s unsuccessfully"% f_name)

				    

                            
                            if status == "download_directory":
                                log_update("Download_Directory called")
				t_dir=con.recv(1024)
				home_dir=os.getcwd()
				fail=0
				try:
					os.chdir(t_dir)
				except Exception:
					log_update("Target directory doesn't exist")
					con.send("false")
					fail=1
				if fail == 0:
					con.send("true")
					log_update("Target directory: %s"% t_dir)
					con.recv(1024)#Ready status
					rootDir="."
					#Send all the folders first
					for dirName,subdirList,fileList in os.walk(rootDir):
						dirName=dirName[2:]
						for subdir in subdirList:
							time.sleep(0.2)
							con.send("folder:%s"% subdir)
							time.sleep(0.2)
							if dirName == "":#Root directory
								con.send(" ")
							else:
								#If there are any slashes, change them to back slashes for Windows
								dirName=dirName.replace("/","\\")
								con.send(dirName)
					#Send all the files now
					for dirName,subdirList,fileList in os.walk(rootDir):
						dirName=dirName[2:]
						for fi in fileList:
							original_dir=os.getcwd()
							time.sleep(0.3)
							con.send("file:%s"% fi)
							time.sleep(0.2)
							if dirName == "":#Root directory
								con.send(" ")
							else:
								#If there are any slashes, change them to back slashes for Windows
								new_dirName=dirName.replace("/","\\")
								con.send(new_dirName)
								os.chdir(dirName)
							#Get the file size and send it to the client
							f=open(fi,"rb")
							f_size=0
							while True:
								data=f.read(1024)
								if data == "":
									f.close()
									break	
								f_size+=1024
							time.sleep(0.1)
							con.send(str(f_size))
							time.sleep(0.1)
							#Now send the file to the client
							f=open(fi,"rb")
							while True:
								data=f.read(4000)
								if data == "":
									time.sleep(0.2)
									f.close()
									con.send("stop")
									break
								else:
									con.send(data)
							check_md5=con.recv(1024)
							#Send the client an md5 hash of the file
							f=open(fi,"rb")
							try:
								md5=hashlib.md5(f.read()).hexdigest()					
							except Exception:
								log_update("Memory error with hash check")
								md5="0"
							f.close()		
							con.send(md5)
							if check_md5 == md5:
								log_update("Uploaded %s successfully"% fi)
								log_update("Hash check is valid")
							else:
								log_update("Uploaded %s unsuccessfully"% fi)
								log_update("Hash check is invalid")
							os.chdir(original_dir)
					time.sleep(1)
					con.send("Completed")
					os.chdir(home_dir)
					log_update("Uploaded %s successfully"% t_dir)


                            if status == "delete":#@
                                log_update("Delete called")
                                fail=0
                                mode=con.recv(1024)# file or folder
                                if mode == "file":
                                    f_name=con.recv(1024)
                                    try:
                                        os.remove(f_name)
                                    except(OSError,TypeError):
					try:
						os.system("rm -f %s"% f_name)
					except Exception:
                                        	fail=1
						con.send("SERVER: Unable to delete file")
                                    if fail == 0:
                                        con.send("SERVER: Successfully deleted file")
                                else:
                                    fname=con.recv(1024)
                                    if os.path.isdir(fname):
                                        shutil.rmtree(fname)
                                        con.send("SERVER:Successfully deleted file")
                                    else:
                                        con.send("SERVER: Unable to delete file")
                                        


                            if status == "exit":
                                log_update("exit called")
                                con.close()
                                close=1
                                #CONNECT TO THE FILE CLOUD MANAGER AND SEND FINISH WITH THE PORT NUMBER
                                s2=socket.socket()
                                s2.connect(("192.168.0.199",25777))
                                s2.send("Finish")
                                time.sleep(0.5)
                                s2.send(str(port))
                                s2.close()
                                if s_level == "Secondary":
                                    sys.exit()
                                break
                        except Exception as e:
                            log_update("Error occurred with connection  %s"% str(e)) #COULD BE SPAMMING THE LOG WITH THIS
                            con.close()
			    
                            s2=socket.socket()
                            s2.connect(("192.168.0.199",25777))
			    time.sleep(0.2)
                            s2.send("Finish")
                            time.sleep(0.5)
                            s2.send(str(port))
                            s2.close()
			    if s_level == "Secondary":
                            	sys.exit()
                            break
        
        except Exception as e:
            log_update("Error occurred with program: %s" % str(e))#BUG OCCURRED HERE, IT WAS SPAMMING THIS FOR DAYS EVERY 4 MINUTES
            con.close()
	    time.sleep(0.5)
	    s2=socket.socket()
	    s2.connect(("192.168.0.199",25777))
	    time.sleep(0.2)
	    s2.send("Finish")
	    time.sleep(0.5)
	    s2.send(str(port))
	    s2.close()
    	    if s_level == "Secondary":
	    	sys.exit()
  	    break

#-------------------------------------------------------------------------------------------------

    
if s_level == "Primary":
    print "Starting......"
    print "Attempting server bind..."

s=socket.socket()

try:
	s.bind((host,port))
except(socket.error,socket.timeout) as e:
	fail=1
	if s_level == "Primary":
		print "server bind failed: %s"% str(e)
		print "Attempting rebind..."
		time.sleep(60)
		try:
			s.bind((host,port))
		except(socket.error):
			print "ERROR: Closing application"
			s=socket.socket()
			s.connect(("192.168.0.199",25777))
			s.send("Finish")
			time.sleep(0.5)
			s.send(str(port))
			s.close()
			sys.exit()
	else:
		log_update("Server bind failed: %s"% str(e))
		#Consult the manager and make the port available
		s=socket.socket()
		s.connect(("192.168.0.199",25777))
		s.send("Finish")
		time.sleep(0.5)
		s.send(str(port))
		s.close()
		sys.exit()

if s_level == "Primary":
	print "Server bind successfully completed....."
	print "Server up and running!"
try:
	s.listen(10)
except(socket.timeout):
	time.sleep(0.2)
	s.listen(10)
	fail=1

      
    
log_update("Server started up.........")


while True:
	try:
		main()
	except Exception as e:
		log_update("CRUCIAL ERROR: %s"% e)
		if s_level != "Primary":
			break# might change this to tell the manager the server has finished up
