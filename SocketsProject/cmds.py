# *********************************************************************
# This file illustrates how to execute a command and get it's output
# *********************************************************************
import subprocess

# Run ls command, get output, and print it
for line in subprocess.getstatusoutput('ls -l'):
	print(line) 



