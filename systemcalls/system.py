# coding=utf-8
from subprocess import Popen, PIPE, STDOUT, check_output, check_call, CalledProcessError
from utilities import mongolog, command_error
import os
import re
import datetime
import pprint
import inspect
#import urllib.parse


#If "newhostname" is not empty sets the hostname, else returns it
def hostname(newhostname=""):
    
    command = ['hostname']
        
    if newhostname:
        logid = mongolog( locals() )
        command.append(newhostname)

    try:
        hostname = check_output(command, stderr=PIPE, universal_newlines=True)
    except CalledProcessError as e:
        return command_error(e, command)

    return (logid if hname else hostname)


#If "towrite" is not empty write the content into the file /etc/hosts, else return the file contents
def etchosts(towrite=""):

    if towrite:
        logid = mongolog( locals() )
        with open('/etc/hosts', 'w') as hostsfile:
            hostsfile.write(towrite)
        return logid
    else:
        with open('/etc/hosts', 'r') as hostsfile:
            return hostsfile.read()



#TODO: Only works on single cpu system
#Information about cpu, memory and processes
def getsysteminfo( getall=True, getproc=False, getcpu=False, getmem=False ):

    #Creating the tuple to return
    toreturn = ()

    

    ##### CPU #####
    if getall or getcpu:

        #Reading cpu stat from /opt files
        with open('/proc/cpuinfo', 'r') as cpuorig:
            cpuraw = cpuorig.read().splitlines()

        #Removing duplicate lines by converting list() to set()
        cpuraw = set(cpuraw)
        
        #Removing empty lines
        cpuraw = list( filter( None, cpuraw ) )
    
        #Removing useless lines
        linestoremove = ('flags', 'apicid', 'processor', 'core id', 'coreid')
        cpuraw = list( filter( lambda line: not any(s in line for s in linestoremove), cpuraw ) )
    
        #Deleting all tabulation and spaces for each line of the cpuraw set cpuraw
        cpuraw = map( lambda line: re.sub('[\t| ]*:[\t| ]*', ':', line), cpuraw )
    
    
        #We got three fields named "cpu Mhz", but to use them as dictionry keys
        #we need to rename them all
        cpuaf = list()
        i = 1
        for line in cpuraw:
            #Adds an incremental number to the key
            if 'mhz' in line.lower():
                cpuaf.append( re.sub('^.*:', 'cpu' + str(i) +' MHz:', line) )
                i += 1
            else: cpuaf.append( line )
    
    
        #Buiding final dictionary cotaining cpu information in the right form
        cpu = dict()
        for line in cpuaf:
            line = line.split(':')
            cpu.update({ line[0]: line[1] })

        #Adding cpu dict to the tuple to return
        toreturn = toreturn + (cpu,)





    ##### MEMORY #####
    if getall or getmem:

        #Reading memory status from /opt files
        with open('/proc/meminfo', 'r') as memorig:
            memraw = memorig.read().splitlines()


        #Filling mem dict with memory information
        mem = dict()
        for line in memraw:
            line = re.sub(' ', '', line)                #Removing spaces for each line
            line = line.split(':')                      #Splitting by colon
            mem.update({ line[0].lower() : line[1] })   #Appending the dictionary to a list to return

        toreturn = toreturn + (mem,)
    




    #### PROCESSES #####
    if getall or getproc:

        #Reading processes status using top command
        try:
            command = ['top', '-b', '-n1'] #Getting processes information
            procraw = check_output(command, stderr=PIPE, universal_newlines=True).splitlines()
        except CalledProcessError as e:
            return command_error(e, command)



        #Removing headers from the output of top command
        i = 0
        while 'PID' not in procraw[i]: i+=1
        procraw = procraw[i:]
    
        #Getting header and splitting fields for use final dictionary keys
        keys = procraw.pop(0).lstrip()
        keys = keys.split()
        
        proc = list()
    
        for line in procraw:
            line = procraw.pop(0).lstrip()          #Removing initial spaces
            line = line.split()                     #Splitting by spaces
            proc.append( dict( zip(keys, line) ) )  #Creating a dictionary for each process and inserting into a list to return

        toreturn = toreturn + (proc,)



    #dict, dict, list
    return toreturn
