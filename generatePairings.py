import json
from pprint import pprint
from teamEntry import *

def main():
    mapList = json.load(open("jsons\\maps.json"))["data"]
    toPreferences = json.load(open("jsons\\toPreferences.json"))["data"]

    # Parsing preferences out of toPreferences.json.
    tournamentID = toPreferences["tournamentID"]
    bannedModes = toPreferences["bannedModes"]
    bannedMaps = toPreferences["bannedMaps"]

    validMapPool = []

    # Load valid maps, striking maps in the ban list.
    for stage in mapList:
        if stage["name"] not in bannedMaps:
            validMapPool.append(stage)

    validMapModePool = []

    for validMap in validMapPool:
        for proposedMode in validMap["allowedModes"]:
            if proposedMode not in bannedModes:
                validMapModePool.append("{0} on {1}".format(proposedMode, validMap["name"]))

    pprint(validMapModePool)

main()