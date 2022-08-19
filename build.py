#!/usr/bin/python3

import os
import re

debug = False

def parse_dir(path, includeReg, excludeReg, preset):
	localInclude = []
	localExclude = []
	try:
		with open(os.path.join(path, preset + ".include")) as f:
			localInclude = [line.rstrip() for line in f.readlines()]
	except:
		pass
	try:
		with open(os.path.join(path, preset + ".exclude")) as f:
			localExclude = [line.rstrip() for line in f.readlines()]
	except:
		pass
	
	playlist = []
	
	for dirEntry in os.scandir(path):
		if (dirEntry.is_dir()):
			playlist += parse_dir(os.path.join(path,dirEntry.name), includeReg, excludeReg, preset)
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

def parse_preset(preset, name):
	roots = []
	excludeReg = []
	includeReg = []
	f = open(preset,"r")
	for line in f.readlines():
		# Comments support
		if (line.startswith("#")): continue
		# Skip empty lines
		if (len(line.strip()) == 0): continue
		
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
			else:
				print(preset +": Unknown command: " + command)
		except ValueError:
			print(preset + ": Invalid line (must contain command + arg): " + line)
	f.close()

	playlist = []

	for root in roots:
		playlist += parse_dir(root, includeReg, excludeReg, name)
	
	with open(name + ".m3u8", "w") as f:
		for line in playlist:
			print(line, file=f)
	
	print("Written: " + name + ".m3u8 ("+str(len(playlist))+ " songs)")

for dirEntry in os.scandir("./presets"):
	root, ext = os.path.splitext(dirEntry.name)
	if (ext == ".preset"):
		parse_preset(dirEntry.path, root)