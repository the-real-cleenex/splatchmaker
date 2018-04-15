from inputParser import parseGoogleFormsCSV
import json
import copy
import csv
import fileinput
import random
import pprint

def compareTeamPreference(data, field, teamOne, teamTwo):
    return data[teamOne][field] == data[teamTwo][field]

# Generates a raw weighting value for subsequent transformation based on a 
# comparison between relevant preferences.
def rawWeighting(data, field, teamOne, teamTwo):
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
    validStages = stagesAndModes['stages']
    
    if compareTeamPreference(data, onlySZ, teamOne, teamTwo) and \
        data[teamOne][onlySZ] == 'Yes':
        for strike in toPreferences['rules']['bannedStages']:
            try: # Handle the potential exception for an unlisted stage.
                validStages.remove(strike)
            except:
                pass

    # Generate the base list of valid modes, loading from mapsandModes.json and striking listed
    # modes out of toPreferences.json.
    validModes = stagesAndModes['modes']
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
        currentModeIndex = int(random.uniform(0, validModes.__len__() + 1))

    # Generate rounds# of stage:mode pairs.
    setList = ''

    currentRound = 0
    while currentRound < rounds:
        # Iterate the current mode through the list.  Reset pointer if end is reached.
        currentModeIndex = currentModeIndex + 1

        randomStage = int(random.uniform(0, totalStageWeight))
        for stage in validStages:
            randomStage = randomStage - stageWeighting[stage]
            currentStage = stage
            if randomStage <= 0:
                validStages.remove(stage)
                break
        
        # Produce output.
        setList = setList + '{mode} on {stage},'.format(mode = validModes[currentModeIndex % validModes.__len__()], \
                            stage = currentStage)
        currentRound = currentRound + 1
    return setList[:-1]

with open('tournamentSetlist.csv', 'w+') as csvfile:
    #setListWriter = csv.writer(csvfile, delimiter=',')
    sampleData = parseGoogleFormsCSV("Sendou's tournaments map & mode query.csv")
    remainingTeams = copy.deepcopy(list(sampleData.keys()))

    for teamOne in sampleData:
        match = teamOne + ','
        for teamTwo in remainingTeams:
            if teamOne != teamTwo:
                match = match + ',' + teamTwo + ',' + makeMatch('yesElim', sampleData, teamOne, teamTwo, 3) + ','

        csvfile.write(match[:-1] + '\n')
        try:
            remainingTeams.remove(teamOne)
        except:
            pass
        print(match)