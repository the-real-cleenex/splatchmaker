from inputParser import *
import json
import fileinput
import pprint

def compareTeamPreference(data, field, teamOne, teamTwo):
    return data[teamOne][field] == data[teamTwo][field]

# Generates a raw weighting value for subsequent transformation based on a 
# comparison between relevant preferences.
def findRawWeighting(data, field, teamOne, teamTwo):
    weight = 0
    for team in [teamOne, teamTwo]:
        if data[team][field] == 'Not preferred':
            weight = weight - 1
        elif data[team][field] == 'Preferred':
            weight = weight + 1
        elif data[team][field] != 'Neutral':
            weight = abs(int(data[team][field]) - 6)
    return weight

def transformWeighting(weightingMode, raw):
    if weightingMode == 'noElim':
        return raw + 2
    else:
        return raw

def generateWeightingTable(weightingMode, entryData):
    mapsAndModes = json.load(open('./jsons/mapsAndModes.json','r'))
    mapWeightTable = {}
    modeWeightTable = {}

    for teamOne in entryData:
        for teamTwo in entryData:
            if teamOne != teamTwo:
                for stage in mapsAndModes['maps']:
                    mapWeightTable[stage] = transformWeighting(weightingMode, findRawWeighting(entryData, stage, teamOne, teamTwo))
                for mode in mapsAndModes['modes']:
                    modeWeightTable[mode] = transformWeighting(weightingMode, findRawWeighting(entryData, mode, teamOne, teamTwo))


    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(modeWeightTable)

def generateSetListArray(weightingTable, teamOne, teamTwo):
    print()

sampleData = parseGoogleFormsCSV("sendou.csv")
print(generateWeightingTable('yesElim',sampleData))
#print(transformWeighting('elim',findRawWeighting(sampleData, 'Port Mackerel', 'zzz deprived', 'testing')))


