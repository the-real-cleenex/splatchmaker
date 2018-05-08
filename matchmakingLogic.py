from inputParser import *
import copy
import json
import fileinput
import random
import pprint
import sys

def compareTeamPreference(data, field, teamOne, teamTwo):
    return data[teamOne][field] == data[teamTwo][field]

# Generates a raw weighting value for subsequent transformation based on a 
# comparison between relevant preferences.
def rawWeighting(data, field, teamOne, teamTwo):
    random.seed()
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

def makeMatch(weightingMode, data, teamOne, teamTwo, rounds):
    # Define shorthand strings for looking up specific preferences.
    yesTW = 'Would you like Turf War to be included in your map lists along other modes?'
    onlySZ = 'Do you prefer to play Splat Zones only?'
    modeStrike = 'Strike a ranked mode (optional)'

    # Load relevant JSON data.
    stagesAndModes = json.load(open('./jsons/mapsAndModes.json','r'))
    toPreferences = json.load(open('./jsons/toPreferences.json','r'))
    
    # Generate the base list of valid stages, loading from mapsandModes.json and striking listed
    # stages out of toPreferences.json.
    validStages = list(stagesAndModes['stages'])
    random.shuffle(validStages)
    for strike in toPreferences['rules']['bannedStages']:
        try: # Handle the potential exception for an unlisted stage.
            validStages.remove(strike)
        except:
            pass

    # Generate the base list of valid modes, loading from mapsandModes.json and striking listed
    # modes out of toPreferences.json.
    validModes = list(stagesAndModes['modes'])
    random.shuffle(validModes)
    for strike in toPreferences['rules']['bannedModes']:
        try: # Handle the potential exception for an unlisted mode.
            validModes.remove(strike)
        except:
            pass
    
    # Handle team mode strikes.
    try:
        validModes.remove(data[teamOne][modeStrike])
    except:
        pass
    try:
        validModes.remove(data[teamTwo][modeStrike])
    except:
        pass

    # Handle mode-specific survey questions.
    if compareTeamPreference(data, onlySZ, teamOne, teamTwo) and \
        data[teamOne][onlySZ] == 'Yes':
        validModes = ['Splat Zones']

    if compareTeamPreference(data, yesTW, teamOne, teamTwo) and \
        data[teamOne][yesTW] == 'Yes':
        validModes.append('Turf War')

    # Generate weighting list for stages.
    stageWeighting = {}
    totalStageWeight = 0
    for stage in validStages:
        stageWeight = transformWeighting(weightingMode , \
                        rawWeighting(data, stage, teamOne, teamTwo))
        stageWeighting[stage] = stageWeight
        totalStageWeight = totalStageWeight + stageWeight

    # Pick starting point in modes list.
    currentModeIndex = 0
    if validModes.__len__() > 1:
        currentModeIndex = int(random.uniform(0, validModes.__len__() - 1)) 

    # Generate rounds# of stage:mode pairs.
    setList = teamOne + ',' + teamTwo + ','

    currentRound = 0
    currentStage = validStages[0]
    while currentRound < rounds:
        # Iterate the current mode through the list.  Reset pointer if end is reached.
        currentModeIndex = currentModeIndex + 1

        randomStage = int(random.uniform(0, totalStageWeight - 1)) # Monitor this line for why residuals can appear.
        for stage in validStages:
            randomStage = randomStage - stageWeighting[stage]
            currentStage = stage

            oldValidStages = copy.deepcopy(validStages)
            validStages = []
            if randomStage <= 0:
                #validStages.remove(stage)
                for choice in oldValidStages:
                    if choice != stage:
                        validStages.append(choice)
                break
            validStages = oldValidStages

        if randomStage > 0:
            validStages.remove(currentStage)
        
        # Produce output.
        setList = setList + validModes[currentModeIndex % validModes.__len__()] + ' on ' + currentStage + ','
        currentRound = currentRound + 1

        random.shuffle(validStages)
    print(setList[:-1])
    #print('\n')

############################################################################
sys.stdout = open("c:\\Users\\leech\\Projects\\splatchmaker\\output.csv", "w", encoding='utf-8-sig')
sampleData = parseGoogleFormsCSV("Sendou's tournaments map & mode query.csv")

with open('input.csv', 'r', encoding='utf-8-sig') as matchups:
    matchesRaw = str(matchups.read())
    matchesRaw = matchesRaw.split("\n")

    for match in matchesRaw:
        teams = match.split(',')

        if teams.__len__() != 2:
            break

        makeMatch('yesElim', sampleData, teams[0], teams[1], 9)

#remainingTeams = copy.deepcopy(list(sampleData.keys()))

#for teamOne in list(sampleData.keys()):
#    for teamTwo in remainingTeams:
#        if teamOne != teamTwo and teamOne == 'C Sharp':
#            makeMatch('yesElim', sampleData, teamOne, teamTwo, 9)

            # Without this terrible method of rebuilding remainingTeams, you encounter a bizarre ValueException
            # x not in list, but *only* for the second team in order of the list cast after the current one.
#            oldRemainingTeams = copy.deepcopy(remainingTeams)
#            remainingTeams = []
#            for team in oldRemainingTeams:
#                if team != teamOne:
#                    remainingTeams.append(team)
            #try:
                #remainingTeams.remove(teamOne)
            #except:
            #    pass
#    remainingTeams = copy.deepcopy(list(sampleData.keys()))