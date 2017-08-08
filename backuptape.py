#!/usr/bin/env python3

import time
import subprocess
import os
import yaml
from lxml import etree

######
#
# Loading files to save
#
with open("config.yml", "r") as configuration:
    config = yaml.load(configuration)

directories = config["directories"]
administrator = config["administrator"]

#######
#
# Retrieving date
#
dateBackup = time.strftime('%d%m%y')

#######
#
# Starting check up for modified files
#
listFiles = []

#######
#
# Creating XML File
#

# Creating XML root
root = etree.Element("Backup", date=dateBackup)

#######################################
#
# Defining backup functions
#
#######################################

#######
#
# Function sendmail
#

# Start Backup
def sendMailStr():
    os.system("echo 'Backup starting...' | mailx -s 'Linux Backup Start' {}".format(administrator[mail]))

# Ending Backup
def sendMailEnd():
    os.system("echo 'Backup Ending...' | mailx -s 'Linux Backup Ending' {}".format(administrator[mail]))


########################################################
#
# Starting Backup process
#
sendMailStr()

#########
#
# Entering to each directory and check for modified files
# in the last 24 hours.
#

# Reading directories to save
for x,savdir in directories.items():


	checkCommand = "find {} -type f -mtime -1 -print".format(savdir) #find x -type f -mtime 1 -print
	executingCmd = subprocess.Popen(checkCommand, shell=True, stdout=subprocess.PIPE, executable='/bin/bash')
	modificatedFiles = executingCmd.communicate()[0]
	modificatedFiles = modificatedFiles.splitlines()

	#
	# Creating XML content <directories>
	#
	directory = etree.SubElement(root, "dir", directory=savdir)

	for y in range(0, len(modificatedFiles)):

		filesToBackup = modificatedFiles[y].decode('utf-8')

		# Filling XML with files to save
		file = etree.SubElement(directory, "filename", filename=filesToBackup)

		# Creating list for backup
		listFiles.append('"{}"'.format(filesToBackup))

# Generating file list to backup...
filesToSave = ' '.join(listFiles)

######### STARTING BACKUP ###########

# Starting Backup
# Save file or directory tar -c -v -b128 -f /dev/nst0
os.system("tar -c -v -f /dev/nst0 {}".format(filesToSave))


# Create function to date DDMMYY_dirname
# Writing EOF Mark in tape
os.system("mt -f /dev/nst0 eof {}".format(dateBackup))

# Go to EOD
os.system("mt -f /dev/nst0 seod")

######### ENDING BACKUP ##########

########################################################
#
# Ending Backup process
#
sendMailEnd()

#Creating XML physically
f = open('/var/log/backup/backup-{}.xml'.format(dateBackup),'w')
f.write(etree.tostring(root, pretty_print=True).decode("utf-8"))
f.close()
