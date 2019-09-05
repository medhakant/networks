import subprocess
import re
import datetime

def remove_duplicates(x):
  return list(dict.fromkeys(x))

# note the time
time = str(datetime.datetime.now())

#get traceroute result from system
tracerouteResult = subprocess.run(['traceroute','www.iitd.ac.in'],stdout=subprocess.PIPE)

#convert the result to string
tracerouteResult = tracerouteResult.stdout.decode('utf-8')

#use regex to find all the IP adresses and refine it to remove duplicates
ipOnRoute = re.findall(r"\d+.\d+.\d+.\d+",tracerouteResult)
ipOnRoute = remove_duplicates(ipOnRoute)

#the first ip on the list is the IITD host ip
iitdHost = ipOnRoute[0]
deviceOS = []

#for every intermediate IP, scan for devices and OS
for i in range(len(ipOnRoute)-1):
	deviceOS.append(subprocess.run(['sudo','nmap','-O',ipOnRoute[i+1]+'/24'],stdout=subprocess.PIPE).stdout.decode('utf-8'))



#append all the data to file
dump = open("dump","a+")
dump.write('*'*100)
dump.write("\n\n")
dump.write("Time: "+time+"\n\n")
dump.write("IITD Host IP: "+iitdHost+"\n\n")
dump.write("Traceroute result:\n")
for i in range(len(ipOnRoute)-1):
	dump.write("IP: "+ipOnRoute[i+1]+"  & Network Distance: "+str(i+1)+" HOP\n")
dump.write('\n') 
dump.write("Other devices on Network:\n\n")
for i in range (len(ipOnRoute)-1):
	dump.write("*"*20+"HOP "+str(i+1)+" Distance"+"*"*20+"\n\n")
	dump.write(deviceOS[i]+"\n")
dump.write("\n")
dump.close()