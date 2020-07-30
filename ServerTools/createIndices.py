# A script for generating index.json files

import os

defaultFolderList = [
    "0Action",
    "1Adventure",
    "2Arcade",
    "3Platformer",
    "4Puzzle",
    "5Racing",
    "6Strategy",
    "7Demos",
    "8Utils",
]

defaultFolderList_test = [
    "0Action"
]

def CreateRootIndex():

    file = open("../index.json", "w")

    # Write the header, e.g.
    # {
    # "path":"https://raw.githubusercontent.com/haviital/GameDisk2/master", 
    # "list": [

    file.write("{\n")
    file.write('"path":"https://raw.githubusercontent.com/haviital/GameDisk2/master"\n')
    file.write('"list": [\n')

    # write the folders
    for i in range(len(defaultFolderList)):

        folderName = defaultFolderList[i]

        # Write a folder record, e.g.
 	    #{ 
		#   "type": "dir", 
		#   "dirtitle": "0Action", 
		#   "file": "0Action"
	    #},
 
        file.write("   {\n")
        file.write('      "type": "dir",\n')
        file.write('      "dirtitle": "' + folderName + '",\n')
        file.write('      "file": "' + folderName + '"\n')
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
        tag = int.from_bytes(tagBytes, 'little')
        print("tag=", tag)
        lenghtBytes = file.read(4)
        lenght = int.from_bytes(lenghtBytes, 'little')
        print("lenght=", lenght)
        if tag == nameTagId: 
            # read name
            name = file.read(lenght-1) # exclude the ending null
            return str(name, 'utf-8')

        # skip tag            
        file.read(lenght)
        tagBytes = file.read(4)

    return "not found"


def CreateSubdirIndices():

    for dir in defaultFolderList:
        print(dir)
        fileListAll = os.listdir("../"+dir)
        print(fileListAll)

        # Drop other files than *.bin and *.pop
        fileList = []
        for item in fileListAll:
            nameAndExtList = item.split('.')
            ext = nameAndExtList[1]
            if ext == "pop" or ext == "bin":
                fileList.append(item)

        # Sort alphapetically
        fileList.sort()

        file = open("../"+dir+"/index.json", "w")

        # Write the header, e.g.
        # {
        # "path":"https://raw.githubusercontent.com/haviital/GameDisk2/master/0Action", 
        # "list": [

        file.write("{\n")
        file.write('"path":"https://raw.githubusercontent.com/haviital/GameDisk2/master/' + dir +'"\n')
        file.write('"list": [\n')
    


        # write games
        for i in range(len(fileList)):

            gameFile = fileList[i]
            nameAndExtList = gameFile.split('.')
            name = nameAndExtList[0]
            ext = nameAndExtList[1]

            # Read the long name from pop
            if ext == "pop":
                name = ReadTagFromPopFile("../"+dir+"/"+gameFile)

            # Write a game record, e.g.
            #{ 
            #   "type": "pop", 
            #   "title": "Ball Bust", 
            #   "file": "B-Bust.pop",
            #   "shots": "B-Bust.bmp"
            #},

            file.write("   {\n")
            file.write('      "type": "' + ext + '",\n')
            file.write('      "title": "' + name + '",\n')
            file.write('      "file": "' + gameFile + '"\n')
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