# A script for generating index.json files

import os
import datetime
import struct
import time


defaultFolderList = [
    ["00Notes", "News"],
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

def CreateRootIndex():

    global maxOfMaxTimestampsInt
    file = open("../index.json", "w")

    # Write the header, e.g.
    # {
    # "path":"https://raw.githubusercontent.com/haviital/GameDisk2/master", 
    # "list": [

    file.write("{\n")
    file.write('"path":"https://raw.githubusercontent.com/haviital/GameDisk2/master"\n')
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
        #   "dirtitle": "0Action", 
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


def CreateSubdirIndices():

    global maxOfMaxTimestampsInt

    for folderListIndex in range(len(defaultFolderList)):
        folderListItem = defaultFolderList[folderListIndex]
        dir = folderListItem[0]
        print(dir)

        isNotesForlder = False
        if dir=="Notes": isNotesForlder = True
        
        fileListAll = os.listdir("../"+dir)
        print(fileListAll)

        # Drop other files than *.bin and *.pop
        fileList = []
        maxTimeSinceEpochInSecInt = 0
        for item in fileListAll:
            nameAndExtList = item.split('.')
            ext = nameAndExtList[1]
            if ext == "pop" or ext == "bin" or ext == "txt":
                # Read the timestamp
            	filePath1 = "../"+dir+"/"+item
                timeSinceEpochInSeconds = os.path.getmtime(filePath1) 
                timeSinceEpochInSecInt = int(timeSinceEpochInSeconds)
                timeSinceEpochInSecStr = str(timeSinceEpochInSecInt)
                #print('timeSinceEpochInSecStr',timeSinceEpochInSecStr)

                # Store the newest timestamp
                if timeSinceEpochInSecInt > maxTimeSinceEpochInSecInt:
                    maxTimeSinceEpochInSecInt = timeSinceEpochInSecInt

                fileList.append([item, timeSinceEpochInSecStr])

        # store the timestamp for the folder
        defaultFolderList[folderListIndex] = [folderListItem[0], folderListItem[1], str(maxTimeSinceEpochInSecInt)]
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
        file.write('"path":"https://raw.githubusercontent.com/haviital/GameDisk2/master/' + dir +'"\n')
        file.write('"timestamp":"' + str(maxTimeSinceEpochInSecInt) + '"\n')
        file.write('"list": [\n')
    
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

            ext2 = ext
            if ext=="txt": ext2="note"

            file.write("   {\n")
            file.write('      "type": "' + ext2 + '",\n')
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

### Main

CreateSubdirIndices()

CreateRootIndex()