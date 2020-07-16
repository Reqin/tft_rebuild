import os
from modules.creations.Character import loadCharacterHandle, dumpCharacterHandle


def exportLineup(characterHandle, path):
    return dumpCharacterHandle(characterHandle, path)


def importLineup(path):
    try:
        return loadCharacterHandle(path)
    except:
        return False

def getLineupsName(path_dir):
    names = []
    for root, dirs, files in os.walk(path_dir):
        for path_file in files:
            name = os.path.splitext(path_file)[0]
            names.append(name)
    return names