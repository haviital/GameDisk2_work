# A script for generating index.json files

import os
import datetime
import struct
import time
import subprocess


# Note the folder name can be max 12 chars, and max 15 folders can exist. This is a memory optimization in PokArcade.
defaultFolderList = [
	["0_1Latest", "Latest"],
	["0_2Notes", "News"],
	["0Action", "Action"],
	["1Adventure", "Adventure"],
	["2Arcade", "Arcade"],
	["3Platformer", "Platformer"],
	["4Puzzle", "Puzzle"],
	["5Racing", "Racing"],
	["6Strategy", "Strategy"],
	["7Demos", "Demos"],
	["8Utils", "Utils"],
]

defaultFolderList_test = [
	"0Action"
]

maxOfMaxTimestampsInt = 0
PlzBlockSizeStr = "500"

def CreateRootIndex():

	global maxOfMaxTimestampsInt
	file = open(rootDir+"/index.json", "w")

	# Write the header, e.g.
	# {
	# "path":"https://raw.githubusercontent.com/haviital/GameDisk2/master", 
	# "list": [

	file.write("{\n")
	file.write('"path":"https://raw.githubusercontent.com/haviital/' + rootFolderName + '/master"\n')
	file.write('"timestamp":"' + str(maxOfMaxTimestampsInt) + '"\n')
	file.write('"list": [\n')

	# write the folders
	for i in range(len(defaultFolderList)):
		folderName = defaultFolderList[i][0]
		prettyName = defaultFolderList[i][1]
		timestamp = defaultFolderList[i][2]



		# Write a folder record, e.g.
		#{ 
		#   "type": "dir", 
		#currDir   "dirtitle": "0Action", 
		#   "file": "0Action"
		#},
 
		file.write("   {\n")
		file.write('      "type": "dir",\n')
		file.write('      "dirtitle": "' + prettyName + '",\n')
		file.write('      "file": "' + folderName + '",\n')
		file.write('      "timestamp": "' + timestamp + '"\n')

		if i < len(defaultFolderList) - 1:
			file.write("   },\n") # Add ','
		else:
			file.write("   }\n")

	# Write the footer, e.g.
	#] 
	#}
	file.write("]\n")
	file.write("}\n")


def ReadTagFromPopFile(popFile):

	nameTagId = 7
	print("popFile=",popFile)
	file=open(popFile, "rb")
	tagBytes = file.read(4)
	while(tagBytes):
		tag = struct.unpack("<i",tagBytes)[0]
		#tag = int.from_bytes(tagBytes, 'little')
		print("tag=", tag)
		lenghtBytes = file.read(4)
		lenght = struct.unpack("<i",lenghtBytes)[0]
		#lenght = int.from_bytes(lenghtBytes, 'little')
		print("lenght=", lenght)
		if tag == nameTagId: 
			# read name
			name = file.read(lenght-1) # exclude the ending null
			return name.encode('utf-8')
			#return str(name, 'utf-8')

		# skip tag            
		file.read(lenght)
		tagBytes = file.read(4)

	return "not found"

def ReadTitleFromTxtFile(filePath):

	print("filePath=",filePath)
	file=open(filePath, "r")
	title = file.readline();

	# Remove any trailing and leading whitespace.
	title = title.strip()

	# truncate to 16 chars
	title = title[0:16]

	return title

def CreateSubdirIndices():

	global maxOfMaxTimestampsInt
	
	# list of all games
	allGamesList = []

	for folderListIndex in range(len(defaultFolderList)):
		
		folderListItem = defaultFolderList[folderListIndex]
		dir = folderListItem[0]
		print(dir)

		# Skip the latest folder for now as it is created at last
		if folderListIndex==0: 
			continue
			
		isNotesForlder = False
		if dir=="Notes": isNotesForlder = True
		
		subdirPath = rootDir+"/"+dir
		fileListAll = os.listdir(subdirPath)
		print(fileListAll)

		# *** iterate over the files and folders the this subdir
		
		# Drop other files than *.bin and *.pop
		fileList = []
		maxTimeSinceEpochInSecInt = 0
		for item in fileListAll:
			nameAndExtList = item.split('.')
			gameName = nameAndExtList[0]
			ext = ""
			if len(nameAndExtList) > 1:
				ext = nameAndExtList[1]
			filePath = subdirPath+"/"+item
			
			# Handle bin and pop files
			if ext == "pop" or ext == "bin" or ext == "txt":
				
				# Make PZL packet for all pop files
				isPlzFile = False
				if ext == "pop":
					# try to find data folders for the pop 
					dataFolderName = gameName+"_data"
					found = False
					for index in range(len(fileListAll)):
						if fileListAll[index]==dataFolderName:
							found = True
							break
					dataFilePath = ""
					if found:
						dataFilePath = subdirPath+"/"+dataFolderName
						
					# make a PLZ file
					MakePlzFile(gameName, dir, filePath, dataFilePath)
					item = gameName+".plz"
					ext = "plz"
					# TODO: Changing just the music file do not update the timestamp as it should. 
					# The timestamp only changes if the pop-file is updated.

				# Read the timestamp
				fullPathItem = "../"+dir+"/"+item
				timeSinceEpochInSeconds = os.path.getmtime(fullPathItem) 
				timeSinceEpochInSecInt = int(timeSinceEpochInSeconds)
				timeSinceEpochInSecStr = str(timeSinceEpochInSecInt)
				#print('timeSinceEpochInSecStr',timeSinceEpochInSecStr)

				# Store the newest timestamp
				if timeSinceEpochInSecInt > maxTimeSinceEpochInSecInt:
					maxTimeSinceEpochInSecInt = timeSinceEpochInSecInt

				# Store the game info to the file list			
				fileList.append([item, timeSinceEpochInSecStr])
				
				# store the game info to the global list
				allGamesList.append([item, dir, timeSinceEpochInSecStr])

		# store the timestamp for the folder
		defaultFolderList[folderListIndex] = [folderListItem[0], folderListItem[1], str(maxTimeSinceEpochInSecInt)]
		print("!!HV", defaultFolderList[folderListIndex])
		if maxTimeSinceEpochInSecInt > maxOfMaxTimestampsInt:
			maxOfMaxTimestampsInt = maxTimeSinceEpochInSecInt

		# Sort alphapetically
		fileList.sort(key=lambda tmp: tmp[0])
		
		# *** Write the subfolder info to the own index.json.

		file = open("../"+dir+"/index.json", "w")

		# Write the header, e.g.
		# {
		# "path":"https://raw.githubusercontent.com/haviital/GameDisk2/master/0Action", 
		# "list": [

		file.write("{\n")
		file.write('"path":"https://raw.githubusercontent.com/haviital/' + rootFolderName + '/master/' + dir +'"\n')
		file.write('"timestamp":"' + str(maxTimeSinceEpochInSecInt) + '"\n')
		file.write('"list": [\n')
		print("!!HV", dir, str(maxTimeSinceEpochInSecInt))

	
		# write games or notes
		for i in range(len(fileList)):

			gameFile = fileList[i][0]
			nameAndExtList = gameFile.split('.')
			name = nameAndExtList[0]
			ext = nameAndExtList[1]

			# Read the long name from pop
			filePath2 = "../"+dir+"/"+gameFile
			if ext == "pop":
				name = ReadTagFromPopFile(filePath2)
				print("pop name=" +  name)
			elif ext == "txt":
				name = ReadTitleFromTxtFile(filePath2)

			# Read the timestamp
			timeSinceEpochInSecStr = fileList[i][1]
			
			#timeSinceEpochInSeconds = os.path.getmtime(filePath2) 
			#timeSinceEpochInSecInt = int(timeSinceEpochInSeconds)
			#timeSinceEpochInSecStr = str(timeSinceEpochInSecInt)
			#print('timeSinceEpochInSecStr',timeSinceEpochInSecStr)

			#struct_timeUTC = time.gmtime(timeSinceEpochInSeconds)
			#dt = datetime.fromtimestamp(mktime(struct_timeUTC))
			#timeISO8601UTC = dt.replace(microsecond=0).isoformat()

			# Write a game record, e.g.
			#{ 
			#   "type": "pop", 
			#   "title": "Ball Bust", 
			#   "file": "B-Bust.pop",
			#   "shots": "B-Bust.bmp", # not yet used
			#   "timestamp": "", 
			#},

			type1 = ext
			if ext=="txt": type1="note"

			file.write("   {\n")
			file.write('      "type": "' + type1 + '",\n')
			file.write('      "title": "' + name + '",\n')
			file.write('      "file": "' + gameFile + '",\n')
			file.write('      "timestamp": "' + timeSinceEpochInSecStr + '"\n')

			if i < len(fileList) - 1:
				file.write("   },\n") # Add ','
			else:
				file.write("   }\n")

		# Write the footer, e.g.
		#] 
		#}
		file.write("]\n")
		file.write("}\n")
		
		# Create the latest items index
		folderListItem = defaultFolderList[0]  # "0_1Latest"
		dir = folderListItem[0]
		CreateLatestSubdirIndex(allGamesList, dir, rootFolderName)
		

# Create the "Latest" subdir index
def CreateLatestSubdirIndex(allGamesList, dir, rootFolderName): 

	file = open("../"+dir+"/index.json", "w")

	# Sort by timestamp, descending
	allGamesList.sort(key=lambda tmp: tmp[2], reverse=True)

	# Update the 
	maxTimestamp = allGamesList[0][2]
	defaultFolderList[0] = [defaultFolderList[0][0], defaultFolderList[0][1], str(maxTimestamp)]

	# Write the header, e.g.
	# {
	# "path":"https://raw.githubusercontent.com/haviital/GameDisk2/master/0Action", 
	# "list": [
	file.write("{\n")
	file.write('"path":"https://raw.githubusercontent.com/haviital/' + rootFolderName + '/master/' + dir +'"\n')
	file.write('"timestamp":"' + maxTimestamp + '"\n')
	file.write('"list": [\n')
	#print("!!HV", dir, str(maxTimeSinceEpochInSecInt))

	# Create new item list. Max 8 items.
	maxItemCount = min(8, len(allGamesList))
	for i in range(maxItemCount):
		
		#print("game: ",allGamesList[i][2], allGamesList[i][1], allGamesList[i][0])
		
		### Write the subfolder info to the own index.json.
		
		gameFile, gameDir, gameTimestampStr = allGamesList[i]

		nameAndExtList = gameFile.split('.')
		name = nameAndExtList[0]
		ext = nameAndExtList[1]

		# Read the long name from pop
		filePath2 = "../"+gameDir+"/"+gameFile
		if ext == "pop":
			name = ReadTagFromPopFile(filePath2)
			print("pop name=" +  name)

		# Write a game record, e.g.
		#{ 
		#   "type": "link", 
		#   "title": "Ball Bust", 
		#   "file": "B-Bust.pop",
		#   "folder": "0Action", 
		#   "timestamp": "12345678", 
		#},

		file.write("   {\n")
		file.write('      "type": "link",\n')
		file.write('      "title": "' + name + '",\n')
		file.write('      "file": "' + gameFile + '",\n')
		file.write('      "folder": "' + gameDir + '",\n')
		file.write('      "timestamp": "' + gameTimestampStr + '"\n')

		if i < maxItemCount - 1:
			file.write("   },\n") # Add ','
		else:
			file.write("   }\n")

	# Write the footer, e.g.
	#] 
	#}
	file.write("]\n")
	file.write("}\n")
		
		
# Make the plz file
def MakePlzFile(gameName, folderName, popFilePath, dataFilePath): 
	
	# create the list file
	listFileName = "logs/PlzListFile_"+folderName+"_"+gameName+".txt"
	file = open(listFileName, "w")
	
	# Add pop file to the filelist
	sdFilePath = popFilePath.split(rootDir, 1)	
	sdFilePathStr = sdFilePath[1]
	line = 'file: "' + popFilePath + '" --> "' + sdFilePathStr[1:] + '"\n'
	print("listfile line=", line)
	file.write(line);
	
	# Check the timestamp
	plzfilepath = popFilePath.replace(".pop", ".plz") 	
	dataFilesHaveBeenUpdated = False
	if not os.path.exists(plzfilepath):
		dataFilesHaveBeenUpdated = True	
	else:
		plzFile_timeSinceEpochInSeconds = os.path.getmtime(plzfilepath) 
		print("Timestamp:",plzfilepath, plzFile_timeSinceEpochInSeconds)
	
	if not dataFilesHaveBeenUpdated:
		timeSinceEpochInSeconds = os.path.getmtime(popFilePath) 
		print("Timestamp:",popFilePath, timeSinceEpochInSeconds)
		if(timeSinceEpochInSeconds) > plzFile_timeSinceEpochInSeconds:
			dataFilesHaveBeenUpdated = True;

	# If exists, add data files to the filelist
	if len(dataFilePath) > 0:
		for root, dirs, files in os.walk(dataFilePath):
			for name in files:
				print("root",root)
				print("dataFilePath",dataFilePath)
				
				# Add the source and target paths to the filelist file.
				filePath = os.path.join(root, name)
				sdFilePath = filePath.split(dataFilePath, 1)	
				print("sdFilePath",sdFilePath) # ('sdFilePath', ['', '/danger.raw'])
				sdFilePathStr = sdFilePath[1]
				if root == dataFilePath:
					sdFilePathStr = "/_ROOT_"+sdFilePathStr
				line = 'file: "' + filePath + '" --> "' + sdFilePathStr[1:] + '"\n'
				print("line",line)
				file.write(line);

				# Check the timestamp
				if not dataFilesHaveBeenUpdated:
					timeSinceEpochInSeconds = os.path.getmtime(filePath) 
					print("Timestamp:",filePath, timeSinceEpochInSeconds)
					if(timeSinceEpochInSeconds) > plzFile_timeSinceEpochInSeconds:
						dataFilesHaveBeenUpdated = True;
	file.close()
	
	# if the data files or the pop file has been updated, create the pzl packet
	print("dataFilesHaveBeenUpdated", dataFilesHaveBeenUpdated)
	if dataFilesHaveBeenUpdated: 
		args = ("./packager",  plzfilepath, listFileName, PlzBlockSizeStr,"-noraw")
		popen = subprocess.Popen(args, stdout=subprocess.PIPE)
		popen.wait()
		output = popen.stdout.read()
		print output

### Main

currDir = os.getcwd()

#print(currDir)
#print(os.path.basename(currDir))
rootDir = os.path.abspath(os.path.join(currDir, os.pardir))  # e.g."/home/hannu/git/GameDisk2"
rootFolderName = os.path.basename(rootDir)
#print(rootDir)
#print(rooFolderName)
#x=input()


CreateSubdirIndices()

CreateRootIndex()
