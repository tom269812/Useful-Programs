#!/usr/bin/env python

#FILE CLOUD MANAGER

#It directs clients to a specific port in which a server will be deployed
#There will still be the primary server that will be continually running

#FILE CLOUD SERVER CHANGES------------------------------------------------



import socket,os,sys,time,datetime



#SERVER UPTIME
startup_time=datetime.datetime.now()
startup_hour=startup_time.hour
startup_minute=startup_time.minute
startup_month=startup_time.month
startup_day=startup_time.day
startup_year=startup_time.year
#NETWORK VARIABLES
host="192.168.0.199"
#host="127.0.0.1"
port=25777
s=socket.socket()



#got a connection, now before it gets a connection, it should initialise the primary file server , then work from there, with a dictionary stating the status of each server
#when a secondary server finishes, it should close once the connection is dropped, a primary server will know its primary by the info.txt file
#info.txt will contain primary or secondary on the first line
#then the port number , if its primary it uses the default if its secondary the port is specified on the second line, its usually 1 up from the default
#once the connection is dropped, it will send a message to the manager saying its closing

def log(message):
    try:
        f=open("manager_log.txt","a+")
    except Exception:
        f=file("manager_log.txt","w+")
    f.write("%s: %s\n"% (time.asctime(),message))
    f.close()


    

def main():#reprogram this so it works with the file_cloud_server and the manager_interface
    #SETUP THE SERVERS
    servers={}
    f=file("info.txt","w+")
    f.write("Primary")
    f.close()
    os.system("python file_cloud_server.py&")
    servers[0]="READY"#ACTIVE FOR WHEN IT'S BEING USED

    #read the user login times then put them in a dictionary
    fail=0
    try:
    	f=open("user_logtimes.txt","r+")
    except Exception:
    	f=file("user_logtimes.txt","w+")
	fail=1
    logintimes={}
    if fail == 0:#it will be set out like 2 nov 2 o clock or whatever then;thomas
	for x in f:#read each line
		x=x.replace("\n","")
		date,user=x.split(";")
		logintimes[user]=date
    f.close()
   #Finished getting logintimes data
			
    #it started up the primary,now wait for connections

    while True:
        try:
            con,addr=s.accept()
	    #SERVER UPTIME
            now=datetime.datetime.now()
            hour=now.hour
            month=now.month
            day=now.day  
 	    year=now.year
            #calculate uptime
	    month_days={"1":31,"2":30,"3":31,"4":30,"5":31,"6":30,"7":31,"8":31,"9":30,"10":31,"11":30,"12":31}
    	    if startup_year == year:
	    	if startup_month == month:
			uptime_day=day-startup_day
		else:
			if day > startup_day:
				uptime_day=(day-startup_day) + (month-startup_month)*31
	    		else:
				uptime_day=(31-(startup_day-day) + (((month-startup_month)-1)*31))
	    else:
	   	if startup_month > month:
			uptime_year=year-startup_year
			if uptime_year > 1:
				uptime_year=uptime_year-1
				uptime_month=12-startup_month+month
			else:
				uptime_month=12-startup_month+month
			uptime_day=365*uptime_year
			uptime_day+=31*uptime_month
		#hour
	    if startup_hour > hour:
	   	uptime_day-=1
		uptime_hour=24-startup_hour+hour
	    else:
		uptime_hour=hour-startup_hour
		
	    if uptime_day > 1:
		day_identifier="days"
	    else:
		day_identifier="day"
		
	    if uptime_hour > 1:
		hour_identifier="hours"
	    else:
		hour_identifier="hour"

	    server_uptime=r"%s %s, %s %s"% (uptime_day,day_identifier,uptime_hour,hour_identifier)

	    while True:
		status=con.recv(1024)
		#fix up the rest
            	#Initiate
            	#this command is sent from a client, it will simply send a port number then deploy a server to that port
            	#Finish
            	#This command is sent in from a server, it will just receive the port number from the server and it will configure the servers dictionary accordingly
            	if status == "Initiate":
			user_name=con.recv(1024)
			try:
				old_logintime=logintimes[user_name]
			except Exception:
				old_logintime="No previous login"
			#UPDATE THE LOGINTIMES DICTIONARY THEN THE FILE
			logintimes[user_name]=time.asctime()
			#NOW UPDATE THE FILE
			f=file("user_logtimes.txt","w+")
			for user in logintimes:
				f.write("%s;%s\n"% (logintimes[user],user))
			f.close()
			con.send(old_logintime)
			time.sleep(1)
                	con.send(server_uptime) 
			#CHECK IF THE PRIMARY SERVER IS AVAILABLE
                	s_status=servers[0]
                	if s_status == "READY":
                    		con.send("29888")
		    		log("Assigned user to the primary server")
                    		servers[0]="ACTIVE"
                	else:
                    		#PRIMARY SERVER IS BEING USED , SEARCH THE SERVERS DICTIONARY FOR AN AVAILABLE PORT THEN DEPLOY A SERVER AND SEND THE PORT TO THE CLIENT
                    		counter=1	
                    		while True:
                        		if counter not in servers:
               					new_port=29888+counter
                            			break
                        		else:
                            			counter+=1
					
                   		con.send(str(new_port))
		    		log("Assigned user with a secondary server on port %s"% str(new_port))
                    		f=file("info.txt","w+")
                    		f.write("Secondary\n%s"% new_port)
                    		f.close()
                    		os.system("python file_cloud_server.py&")
                    		servers[counter]="ACTIVE"
		    		log(str(servers))

	    	elif status == "interface_refresh":#gets all the data for the manager interface
		#send the server uptime and the active server list
			con.send(server_uptime)
			time.sleep(0.5)
			for server in servers:
				con.send("%s : %s"% (server,servers[server])) #the format should be 1:ACTIVE
				time.sleep(0.3)
			con.send("stop")

	    	elif status == "initialise_server":
			counter=1
			while True:
				#search for an available port number
				if counter not in servers:
					new_port=29888 + counter
					break
				else:
					counter+=1
				con.send(str(new_port))
				f=file("info.txt","w+")
				f.write("Secondary\n%s"% new_port)
				f.close()
				os.system("python file_cloud_server.py&")
				servers[counter]="ACTIVE"
				log(str(servers))
		#start up a server and send back the port number
		

	    	elif status == "restart_server":
		#restart a server with the ID given
		#not sure if this is going to work...it wont be easy
			pass
	
	    	elif status == "restart_manager":
			#Close all servers
			#FIND A WAY TO END ALL THE SERVER PROCESSES
			
			#Create an external program that executes the file_cloud_manager
			f=file("manager_restart.py","w+")
			

			f.close()
			os.system("")#command for changing the allowances
			 


		#restart the manager and all active servers, make a text document
		#with the port numbers of all the active servers
		#then run an external program and exit
		#this program will start up the servers then the manager
		#the manager will then check for a text document
		#the text document will be the same one the manager created
		#then once it reads it and updates its variables
		#it will delete the text document
			pass

	    	elif status == "manager_shutdown":
		#shutdown the manager and all active servers
			pass

	    	elif status == "server_shutdown":
	        #ask for the port number or server ID , then close the server
		#via process.end or whatever
			pass

	    	elif status == "server_list":
			for server in servers:#it should send 1:ACTIVE or something similar
				con.send("%s:%s"% (server,servers[server]))
				time.sleep(0.2)
			con.send("stop")

				
		#return the server list    
			pass                 

		elif status == "Finish":       
			s_port=con.recv(1024)
			s_number=int(s_port)-29888
			log("DEBUG: s_port: %s , s_number: %s"% (s_port,s_number))
			if s_number == 0:
				log("Primary server finished up and is ready for another connection")
				servers[0]="READY"
			else:
				servers.pop(s_number)
				log("Server %s with port %s finished up"% (s_number,str(s_port)))
			con.close()   
			break  	

		elif status == "exit":
			log("Connection closed due to exit call")
			con.close()
			break
		else:
			log("Command Error: %s called"% status)
			con.close()
			break
			  
        except Exception as e:
		log("ERROR OCCURRED: %s"% str(e))
            
                    
                    
                    
            












#PROGRAM INITIALISATION
print "Starting up file cloud manager........."
try:
    s.bind((host,port))
except Exception:
    print "Unable to bind!"
    sys.exit()

print "Successfully bound to port %s"% port
print "File cloud manager up and running........"
log("Starting up...")

try:
    s.listen(10)
except Exception:
    print "Unable to listen for potential clients"



try:
	main()
except Exception as e:
	log("An error occurred: %s"% str(e))
	time.sleep(5)
	sys.exit()#EVENTUALLY MAKE IT COME BACK ONLINE, TOO MUCH STUFF TO WORK AROUND AT THE MOMENT






    

