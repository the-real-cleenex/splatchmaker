from inputParser import *
import json
import fileinput
import random
import pprint

def compareTeamPreference(data, field, teamOne, teamTwo):
    return data[teamOne][field] == data[teamTwo][field]

# Generates a raw weighting value for subsequent transformation based on a 
# comparison between relevant preferences.
def findRawWeighting(data, field, teamOne, teamTwo):
    weight = 0
    for team in [teamOne, teamTwo]:
        if data[team][field] == 'Not preferred':
            weight = weight + 1
        elif data[team][field] == 'Preferred':
            weight = weight + 3
        elif data[team][field] == 'Neutral':
            weight = weight + 2
        else: # This weighting is for a mode, not a map.
            weight = abs(int(data[team][field]) - 6)
    return weight

def transformWeighting(weightingMode, raw):
    if weightingMode == 'noElim':
        return raw + 1
    return raw

def makeMatch(weightingMode, entryData, teamOne, teamTwo):
    stagesAndModes = json.load(open('./jsons/mapsAndModes.json','r'))
    validStages = {}
    validModes = {}

    stageSelection = ''
    modeSelection = ''

    totalStageWeight = 0
    totalModeWeight = 0

    if compareTeamPreference(entryData, 'Do you prefer to play Splat Zones only?', teamOne, teamTwo):
        if entryData[teamOne]['Do you prefer to play Splat Zones only?'] == 'Yes':
            validModes['Splat Zones'] = 1
        else:
            for mode in stagesAndModes['modes']:
                if mode == 'Turf War':
                    if compareTeamPreference(entryData, 'Would you like Turf War to be included in your map lists next to other modes?', teamOne, teamTwo):
                        if entryData[teamOne]['Would you like Turf War to be included in your map lists next to other modes?'] == 'Yes':
                            cursorWeight = transformWeighting(weightingMode, findRawWeighting(entryData, mode, teamOne, teamTwo))

                            validModes[mode] = cursorWeight
                            totalModeWeight = totalModeWeight + cursorWeight
                else:
                    cursorWeight = transformWeighting(weightingMode, findRawWeighting(entryData, mode, teamOne, teamTwo))

                    validModes[mode] = cursorWeight
                    totalModeWeight = totalModeWeight + cursorWeight
    else:
        for mode in stagesAndModes['modes']:
            if mode == 'Turf War':
                if compareTeamPreference(entryData, 'Would you like Turf War to be included in your map lists next to other modes?', teamOne, teamTwo):
                    if entryData[teamOne]['Would you like Turf War to be included in your map lists next to other modes?'] == 'Yes':
                        cursorWeight = transformWeighting(weightingMode, findRawWeighting(entryData, mode, teamOne, teamTwo))

                        validModes[mode] = cursorWeight
                        totalModeWeight = totalModeWeight + cursorWeight
            else:
                cursorWeight = transformWeighting(weightingMode, findRawWeighting(entryData, mode, teamOne, teamTwo))

                validModes[mode] = cursorWeight
                totalModeWeight = totalModeWeight + cursorWeight

    for stage in stagesAndModes['stages']:
        cursorWeight = transformWeighting(weightingMode, findRawWeighting(entryData, stage, teamOne, teamTwo))

        validStages[stage] = cursorWeight
        totalStageWeight = totalStageWeight + cursorWeight

    randomMode = int(random.uniform(0, totalModeWeight))
    randomStage = int(random.uniform(0, totalStageWeight))

    for mode in validModes:
        randomMode = randomMode - validModes[mode]
        if randomMode < 0:
            modeSelection = mode
            break

    for stage in validStages:
        randomStage = randomStage - validStages[stage]
        if randomStage < 0:
            stageSelection = stage
            break

    print('{teamOne} vs. {teamTwo} : {mode} on {stage}'.format(teamOne=teamOne, teamTwo = teamTwo, mode=modeSelection, stage=stageSelection))

    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(validModes)
    #pp.pprint(validStages)

def generateSetListArray(weightingTable, teamOne, teamTwo):
    print()

sampleData = parseGoogleFormsCSV("Sendou's tournaments map & mode query.csv")
#makeMatch('yesElim',sampleData, "Team Olive", "SetToDestroyX")

for teamOne in sampleData:
    for teamTwo in sampleData:
        if teamOne != teamTwo:
            makeMatch('yesElim', sampleData, teamOne, teamTwo)