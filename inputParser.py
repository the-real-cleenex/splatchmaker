import re
import fileinput
import csv

# Generate a formatted dictionary object from Google Forms CSV output.
# The dictionary is keyed by team name, and by internal field within
# each team's data..

def parseGoogleFormsCSV(fileName):
    with open(fileName, "r") as entryData:
        data = str(entryData.read())

        # Clean out introductory text.
        pattern = re.compile("\"Choose your \w+? preferences \[(?P<content>.*?)\]\",")
        data = re.sub("\"", "", data)
        data = re.sub(pattern, "\g<1>,", data)
        print(data)

        data = data.split("\n")
        preferenceData = {}

        header=True

        for row in data:
            if header:
                fields = row.split(",")
                header = False
            else:
                if row.strip():
                    teamValues = row.split(",")
                    teamDict = {}
                    index = 0
                    for field in fields:
                        if field != 'Team Name':
                            teamDict[field] = teamValues[index]
                        index = index + 1
                    preferenceData[teamValues[1]] = teamDict

        return preferenceData

def compareTeamPreferences(data, field, teamOne, teamTwo):
    return data[teamOne][field] == data[teamTwo][field]

print(parseGoogleFormsCSV("sendou.csv"))
print(compareTeamPreferences(parseGoogleFormsCSV("sendou.csv"),'Team Captain Discord Handle', 'zzz deprived', 'testing'))