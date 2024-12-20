#!/usr/bin/python3

import os
import re

debug = False

def filter_childrens(inputList, path):
	returnList = []
	pathHead = os.path.split(path)[1]
	for path in inputList:
		child = os.path.relpath(path, pathHead)
		if not (child.startswith("..")):
			returnList += [child]
	return returnList

def parse_dir(path, includeReg, excludeReg, preset, parentIncludes = [], parentExcludes = []):
	if (debug): print("Parsing path "+path)
	localInclude = filter_childrens(parentIncludes, path)
	localExclude = filter_childrens(parentExcludes, path)
	try:
		with open(os.path.join(path, preset + ".include")) as f:
			localInclude += [line.rstrip() for line in f.readlines()]
	except:
		pass
	try:
		with open(os.path.join(path, preset + ".exclude")) as f:
			localExclude += [line.rstrip() for line in f.readlines()]
	except:
		pass
	
	playlist = []
	
	for dirEntry in os.scandir(path):
		if (dirEntry.is_dir()):
			playlist += parse_dir(os.path.join(path,dirEntry.name), includeReg, excludeReg, preset, localInclude, localExclude)
		else:
			include = False
			exclude = False
			
			# 1) If the file is in the local include list, we include it no matter what
			for file in localInclude:
				if (file == dirEntry.name):
					if (debug): print("Local include: "+dirEntry.name)
					include = True
					break
			
			if (include):
				playlist.append(os.path.join(path, dirEntry.name))
				continue
			
			# 2) If the file is in the local exclude list, we exclude it no matter what
			for file in localExclude:
				if (file == dirEntry.name):
					if (debug): print("Local exclude: "+dirEntry.name)
					exclude = True
					break
			
			if (exclude): continue
			
			# 3) If the file match a global exclude regex, we exclude it
			
			for regex in excludeReg:
				if (regex.search(dirEntry.name) is not None):
					if (debug): print("Exclude "+ dirEntry.name)
					exclude = True
					break
			if (exclude): continue
			
			# 4) If the file match a global include regex (without being excluded before), we include it
			
			for regex in includeReg:
				if (regex.search(dirEntry.name) is not None):
					if (debug): print("Include "+ dirEntry.name)
					include = True
					break
			
			if (include):
				playlist.append(os.path.join(path, dirEntry.name))
			
			# 5) If nothing matched, we don't include it
	
	return playlist

parsed_presets = dict()
# Used to detect dependencies loop
dependencies_stack = []

def parse_preset(preset, name):
	roots = []
	excludeReg = []
	includeReg = []
	dependencies = []
	write_file = True
	if (name in dependencies_stack):
		print ("ERROR: Dependencies loop detected in "+name+"! Aborting")
		quit()
	if (name in parsed_presets):
		return
	
	try:
		with open(preset,"r") as f:
			for line in f.readlines():
				# Comments support
				if (line.startswith("#")): continue
				# Skip empty lines
				if (len(line.strip()) == 0): continue
				if (line.strip() == "NOWRITE"):
					write_file = False
					continue
				
				try:
					command, arg = line.split(' ', 1)
					arg = arg.rstrip()
					if (command == "ROOT"):
						roots.append(arg)
					elif (command == "INCLUDE"):
						try:
							includeReg.append(re.compile(arg))
						except:
							print(preset +": Error with regex: " + arg)
					elif (command == "EXCLUDE"):
						try:
							excludeReg.append(re.compile(arg))
						except:
							print(preset +": Error with regex: " + arg)
					elif (command == "IMPORT"):
						dependencies.append(arg)
					else:
						print(preset +": Unknown command: " + command)
				except ValueError:
					print(preset + ": Invalid line (must contain command + arg): " + line)
	except:
		print("Error while opening "+preset+". Skipping")
		return

	dependencies_stack.append(name)
	for dep in dependencies:
		parse_preset("presets/"+dep+".preset", dep)
	dependencies_stack.remove(name)
	playlist = []

	for root in roots:
		playlist += parse_dir(root, includeReg, excludeReg, name)
	
	parsed_presets[name] = playlist
	dep_size = 0
	if write_file:
		with open(name + ".m3u8", "w") as f:
			for line in playlist:
				print(line, file=f)
			for dep in dependencies:
				dep_size+=len(dep)
				for line in parsed_presets[dep]:
					print(line, file=f)
	dep_str=""
	if dep_size == 0:
		dep_str = "("+str(len(playlist))+ " songs)"
	else:
		dep_str = "("+str(len(playlist))+ " songs + "+str(dep_size)+" dependencies)"
	if write_file:
		print("Written: " + name + ".m3u8 "+dep_str)
	else:
		print("Generated (not written): "+name+ " "+dep_str)

for dirEntry in os.scandir("./presets"):
	root, ext = os.path.splitext(dirEntry.name)
	if (ext == ".preset"):
		parse_preset(dirEntry.path, root)