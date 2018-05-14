############################## Module Standards ###############################
# * The data table will always be the first argument in any function that is  #
#   using it.                                                                 #
# * The lookup value or field will always be the second argument in any       #
#   function using the return value.                                          #
# * Function modifiers, like elimination mode, are always specified last.     #
###############################################################################

from inputParser import parseGoogleFormsCSV
import copy
import json
import fileinput
import random
import pprint
import sys
import time
from datetime import date

def main():
    #sys.stdout = open("c:\\Users\\leech\\Projects\\splatchmaker\\output.csv", "w", encoding='utf-8-sig')

    with open('input.csv', 'r', encoding='utf-8-sig') as matchups:
        matchesRaw = str(matchups.read())
        matchesRaw = matchesRaw.split("\n")

        for match in matchesRaw:
            teams = match.split(',')

            if teams.__len__() != 2:
                break

            makeSetList(teams[0], teams[1], 9)
    
# This method is the heart of this module.  Given two teams and parsed data,
# it prints a .csv set list with matches# of games being played between 
# teamOne and teamTwo. 

def makeSetList(teamOne, teamTwo, matches):
    # Import the relevant JSONs.  
    stagesAndModes = json.load(open('./jsons/stagesAndModes.json','r'))
    teamData = parseGoogleFormsCSV("Sendou's tournaments map & mode query.csv")
    toPreferences = json.load(open('./jsons/toPreferences.json','r'))

    # This line is critical, and ensures the consistency of program runs across
    # different invokations from week to week.
    random.seed(a=''.join([teamOne,teamTwo,str(getWeekNumber())]))

    # Prepare data structures from the loaded JSONs.
    stagePreferences = getStagePreferences(stagesAndModes, teamOne, teamTwo)
    modeRotation = stagesAndModes['modes']
    random.shuffle(modeRotation)

    # Account for TO preferences.
    for stage in toPreferences['bannedStages']:
        del stagePreferences[stage]

    for mode in toPreferences['bannedModes']:
        modeRotation.remove(mode)

    # Define shorthand strings for looking up specific preferences.
    yesTW = 'Would you like Turf War to be included in your map lists along other modes?'
    onlySZ = 'Do you prefer to play Splat Zones only?'
    modeStrike = 'Strike a ranked mode (optional)'

    # Account for team preferences.
    if teamData[teamOne][yesTW] == 'Yes' and \
       compareTeamPreference(teamData, yesTW, teamOne, teamTwo):
       modeRotation.append('Turf War')
       random.shuffle(modeRotation) # Reshuffle so that turf war is not always
                                    # in the same position.

    # Account for team mode strikes.
    modeStrikes = {}
    if teamData[teamOne][onlySZ] == 'Yes' and \
       compareTeamPreference(teamData, onlySZ, teamOne, teamTwo):
       
       modeRotation = ['Splat Zones']
    else:
        for team in [teamOne, teamTwo]:
            struckMode = teamData[team][modeStrike]
            if len(struckMode) == 0: # No preference for a struck mode.
                break
            elif struckMode in modeStrikes: # Both teams have stricken this mode.
                modeStrikes[struckMode] = 2
            else: # One team has struck this mode.
                modeStrikes[struckMode] = 1

    # Iterate through the match generation procedure for the given number of
    # matches in this set.
    match = 0
    modeIndex = 0
    while match < matches:
        mode = modeRotation[modeIndex]
        while mode in modeStrikes: # The current mode has been stricken by at
                                   # least one team.  This is in a while loop
                                   # because it is possible that randomization
                                   # will produce two adjacent struck modes.
            if modeStrikes[mode] == 0: # Prime the strike for the next go.
                modeStrikes[mode] = 1

            elif modeStrikes[mode] == 1: # Advance the index by one, then put
                                        # the strike on cooldown.
                modeIndex += 1
                modeStrikes[mode] = 0

            elif modeStrikes[mode] == 2: # Automatically strike this mode.
                modeRotation += 1

            if modeIndex == len(modeRotation):
                modeIndex = 0
            mode = modeRotation[modeIndex]

            # # # # Left off point.  Get the subset of stage prefs from toPreferences[rotation][mode], pick a random from there.
        # Iterator.
        match = match + 1

    print(modeRotation)

    
# Utility function to get the current week number.

def getWeekNumber():
    return date.today().isocalendar()[1]

# This is a utility function to determine whether or not two teams share a 
# given preference, denoted by field.  This is in order to avoid having
# to fully write out hash lookups repeatedly.
    
def compareTeamPreference(data, field, teamOne, teamTwo):
    return data[teamOne][field] == data[teamTwo][field]

# Generates a weighted table of two teams' stage preferences, given two team
# names to search and a hashtable of preferences.
#
# To-Do:
# * Consider using global variables.

def getStagePreferences(data, teamOne, teamTwo):
    preferenceTable = {}
    for stage in data['stages']:
            preferenceTable[stage] = combinedFieldWeight(data, stage, teamOne, teamTwo, 'noElim')
    return preferenceTable

# Generates a weight based oncomparison between relevant preferences.
# No Elimination : 2 - 12
# * 1 : A team does not prefer this map.
# * 2 : A team is neutral on this map.
# * 6 : A team prefers this map (3x chance of appearance).
# 
# Elimination : 0 - 6
# * 0 : A team does not prefer this map.
# * 1 : A team is neutral on this map.
# * 3 : A team prefers this map.

def combinedFieldWeight(data, field, teamOne, teamTwo, mode):
    if mode == 'noElim': # Maps cannot be eliminated.
        notPreferred = 1
        neutral = 2
        preferred = 6
    else: # Maps can be eliminated.
        notPreferred = 0
        neutral = 1
        preferred = 3

    fieldWeight = 0
    for team in [teamOne, teamTwo]:
        if data[team][field] == 'Not preferred':
            fieldWeight += notPreferred
        elif data[team][field] == 'Neutral':
            fieldWeight += neutral
        elif data[team][field] == 'Preferred':
            fieldWeight += preferred
        # Weights for modes are calculated by inverting the provided
        # rank out of five, such that 1 = 5 ... 5 = 1.
        else:
            fieldWeight = abs(int(data[team][field]) - 6)
    return fieldWeight

# Returns the weight of a subset of elements in a weighted table.

def getTableWeight(weightedTable):
    tableWeight = 0
    for value, weight in weightedTable.items():
        tableWeight = tableWeight + weight
    return 
    
# Returns a subtable of a table of values, containing all of the keys in a
# provided list of keys.

def getSubTable(table, subsetList):
    subTable = {}
    for item in subsetList:
        subTable[item] = table[item]
    return subTable

# Returns a random element from a weighted table.  A random integer is
# generated from [0, getTableWEight(weightedTable)).  Going from the first
# element returned by an iterator (order is not guaranteed to be consistent),
# subtract the weight from the randomized choice value until the value is at or
# below zero, then return the current selected item.  An optional argument
# (prior) precludes matching table entries from being selected.
#
# To-Do:
# * Check to see whether random.seed generates a consistent order for the order
#   of items returned by iterating over the result of hashtable.items().  Looks
#   like this is desired, but not guaranteed behavior at present.

def getRandomFromWeightedTable(weightedTable, prior=None):
    choice = random.uniform(0, getTableWeight(weightedTable))
    for value, weight in weightedTable.items():
        randomChoice = value
        choice = choice - weight
        if choice <= 0 and randomChoice != prior:
            return randomChoice
    return randomChoice # This is in the event that the end of the list is
                        # reached as a safety catch    

def makeMatchOld(weightingMode, data, teamOne, teamTwo, rounds):
    

    # Load relevant JSON data.
    stagesAndModes = json.load(open('./jsons/mapsAndModes.json','r'))
    toPreferences = json.load(open('./jsons/toPreferences.json','r'))
    
    # Generate the base list of valid stages, loading from mapsandModes.json and striking listed
    # stages out of toPreferences.json.
    validStages = stagesAndModes['stages']
    random.shuffle(validStages)
    for strike in toPreferences['rules']['bannedStages']:
        try: # Handle the potential exception for an unlisted stage.
            validStages.remove(strike)
        except:
            pass

    # Generate the base list of valid modes, loading from mapsandModes.json and striking listed
    # modes out of toPreferences.json.
    validModes = stagesAndModes['modes']
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


main()

############################################################################


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