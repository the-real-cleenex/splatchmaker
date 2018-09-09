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
    sys.stdout = open("output.csv", "w", encoding='utf-8-sig')

    teamListWithExtras = parseGoogleFormsCSV("preferences.csv")
    teamList = list(teamListWithExtras.keys())
    prunedList = copy.deepcopy(teamList)

    # Use this code to generate all permutations of possible matches.
    #for teamOne in teamList:
    #    for teamTwo in prunedList:
    #        if teamOne != teamTwo:
    #            makeSetList(teamOne, teamTwo, 9)
    #    prunedList.remove(teamOne)


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
    teamData = parseGoogleFormsCSV("preferences.csv")
    toPreferences = json.load(open('./jsons/toPreferences.json','r'))

    # Generate blank entries if a team did not submit a splatchmaker form.
    for team in [teamOne, teamTwo]:
        if team not in teamData:
            teamData = makeBlankEntry(teamData, stagesAndModes, team)

    # This line is critical, and ensures the consistency of program runs across
    # different invokations from week to week.
    random.seed(a=''.join([teamOne, teamTwo, str(getWeekNumber())]))

    # Prepare data structures from the loaded JSONs.
    stagePreferences = getStagePreferences(stagesAndModes, teamData, \
                                           teamOne, teamTwo)
    modeRotation = stagesAndModes['modes']
    random.shuffle(modeRotation)

    # Account for TO preferences.
    for stage in toPreferences['rules']['bannedStages']:
        del stagePreferences[stage]

    for mode in toPreferences['rules']['bannedModes']:
        modeRotation.remove(mode)

    # Define shorthand strings for looking up specific preferences.
    yesTW = 'Would you like Turf War to be included in your map lists along other modes?'
    onlySZ = 'Do you prefer to play Splat Zones only?'
    modeStrike = 'Strike a ranked mode (optional)'

    # Account for turf war preferences.
    if teamData[teamOne][yesTW] == 'Yes' and \
       compareTeamPreference(teamData, yesTW, teamOne, teamTwo):
       modeRotation.append('Turf War')
       toPreferences['rules']['rotation']['Turf War'] = stagesAndModes['stages'] # Turf War encompasses all possible stages.
       random.shuffle(modeRotation) # Reshuffle so that turf war is not always
                                    # in the same position.

    # Account for team mode strikes.  The values indicated below signify:
    # * 0 : One team has struck this mode, but the strike is on cooldown.  This
    #       means that the next time the mode is encountered, it will be played
    #       that match, but the next occurrence will be skipped.
    # * 1 : One team has struck this mode, and the strike is primed.  This mode
    #       will be struck for this match, and the strike will be placed on
    #       cooldown (it will be played the next time it appears).
    # * 2 : Both teams have struck this mode, and it will not be played at all.
    modeStrikes = {}
    if teamData[teamOne][onlySZ] == 'Yes' and \
        compareTeamPreference(teamData, onlySZ, teamOne, teamTwo):
        modeRotation = ['Splat Zones']
    else:
        for team in [teamOne, teamTwo]:
            struckMode = teamData[team][modeStrike]
            if len(struckMode) == 0: # No preference for a struck mode.
                pass
            elif struckMode in modeStrikes: # Both teams have stricken this mode.
                modeStrikes[struckMode] = 2
            else: # One team has struck this mode.
                modeStrikes[struckMode] = 1

    # Iteration variable setup.
    match = 0
    modeIndex = 0
    priorStage = None
    setList = teamOne+','+teamTwo+','
    
    # Iterate through the match generation procedure for the given number of
    # matches in this set.
    while match < matches:
        if modeIndex == len(modeRotation): # Reset index if it reaches the end
                                           # of the available modes.
            modeIndex = 0
        mode = modeRotation[modeIndex] # Naive mode selection.  Used either as
                                       # final selection, or to check against
                                       # mode strikes.

        while mode in modeStrikes: # The current mode has been stricken by at
                                   # least one team.  This is in a while loop
                                   # because it is possible that randomization
                                   # will produce two adjacent struck modes.
            if modeStrikes[mode] == 0: # Prime the strike for use in the next
                                       # match.
                modeStrikes[mode] = 1
                break
            elif modeStrikes[mode] == 1: # Skip the current mode for this match
                                         # and place the strike on cooldown.
                modeIndex += 1
                modeStrikes[mode] = 0
            elif modeStrikes[mode] == 2: # Modes that both teams have struck
                                         # are automatically stricken.
                modeIndex += 1
                
            if modeIndex == len(modeRotation): # Reset index if it reaches the
                                               # end of available modes.
                modeIndex = 0
            mode = modeRotation[modeIndex] # Naive mode selection.  If still in
                                           # the strike list, it will be 
                                           # checked on the next iteration.

        # Retrieve the subtable corresponding to the weighted preferences for
        # maps in rotation.  Select a stage from the returned subtable, then
        # note the selection as a prior stage.
        rotationStagePreferences = getSubTable(stagePreferences, \
                                               toPreferences['rules']['rotation'][mode])
        # Handle the worst-case scenario where all selections for a mode are
        # consumed by other modes.  Refreshes the map pool for that mode only.
        if len(rotationStagePreferences) == 0:
            toPreferences['rules']['rotation'][mode] = emergencyModeReload(mode)
            rotationStagePreferences = getSubTable(stagePreferences, \
                                                   toPreferences['rules']['rotation'][mode])

        stage = getRandomFromWeightedTable(rotationStagePreferences, \
                                            priorStage)
        priorStage = stage # A change has been made to prevent all duplicate stages.
        for targetMode in modeRotation:
            try:
                toPreferences['rules']['rotation'][targetMode].remove(stage)
            except:
                pass

        # Produce output to the console or output.csv.
        setList += mode +' on '+stage+','

        # Proceed to the next iteration.
        modeIndex += 1 # List boundary check is conducted at the top of loop.
        match = match + 1
    
    print(setList[:-1])

# Emergency reload function in the event of too many collisions.

def emergencyModeReload(mode):
    toPreferences = json.load(open('./jsons/toPreferences.json','r'))
    return toPreferences['rules']['rotation'][mode]

# Add a blank team entry to provided preference data when a form is not 
# provided.

def makeBlankEntry(teamData, stagesAndModes, team):
    yesTW = 'Would you like Turf War to be included in your map lists along other modes?'
    onlySZ = 'Do you prefer to play Splat Zones only?'
    modeStrike = 'Strike a ranked mode (optional)'
    
    teamData[team] = {}
    teamData[team][yesTW] = 'No'
    teamData[team][onlySZ] = 'No'
    teamData[team][modeStrike] = ''

    for stage in stagesAndModes['stages']:
        teamData[team][stage] = 'Neutral'
    
    return teamData
    

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

def getStagePreferences(data, teamData, teamOne, teamTwo):
    preferenceTable = {}
    for stage in data['stages']:
            preferenceTable[stage] = combinedFieldWeight(teamData, stage, teamOne, teamTwo, 'noElim')
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
    return tableWeight
    
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

main()