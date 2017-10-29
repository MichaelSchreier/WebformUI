import os
import platform
import subprocess


def buildCommand(language, command, arguments):
	"""
	language:	<string> language to be used
	command:	<string> path to file or command to execute
	arguments:	<2d-array of <string>> in the form [[name, result],...] of the form elements
	"""
	if language.lower() == 'python':
		output_command = buildCommandPython(command, arguments)
	elif language.lower() == 'sas':
		output_command = buildCommandSAS(command, arguments)
	elif language.lower() == 'batch' or language.lower() == 'other executable':
		output_command = buildCommandBatch(command, arguments)
	else:
		raise NotImplementedError("language '" + language + "' not supported")
		
	return output_command
	
	
def buildCommandPython(command, arguments):
	output_command = 'python ' + command
	for arg in arguments:
		output_command += ' ' + arg[1]
	return output_command
	

def buildCommandBatch(command, arguments):
	output_command = command
	for arg in arguments:
		output_command += ' ' + arg[1]
	return output_command
	
	
def buildCommandSAS(command, arguments):
	sas_executable = findSAS()
	if sas_executable:
		output_command = sas_executable + ' ' + command
		if len(arguments):
			output_command += " -SYSPARM '"
			output_command += ','.join([i[0] + '=' + i[1] for i in arguments]) + "'"
		return output_command
	else:
		raise FileExistsError
	
	
def findSAS():
	basedir = None
	ext = None
	
	if platform.system() == "Windows":
		basedir = "C:\\Program Files\\SASHome\\SASFoundation"
		ext = ".exe"
	elif platform.system() == "Linux":
		basedir = "/usr/local/SASHome/SASFoundation"
		ext = ""
	elif platform.system() == "Darwin":
		# basedir = None
		raise FileExistsError
		# SAS is not available on MAC
	
	path_to_sas = None
	
	if os.path.isdir(basedir):
		sub_directories = next(os.walk(basedir))[1]
		sub_directories = sorted(sub_directories, key=str.lower, reverse=True)
		for sub_directory in sub_directories:
			if os.path.isfile(os.path.join(basedir, sub_directory, "sas", ext)):
				path_to_sas = os.path.join(basedir, sub_directory, "sas", ext)
				break
	
	return path_to_sas


def runCommand(command):
	cmd = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
	return cmd
