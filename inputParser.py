import re
import fileinput
#import csv

# Generate a formatted dictionary object from Google Forms CSV output.
# The dictionary is keyed by team name, and by internal field within
# each team's data.

def parseGoogleFormsCSV(fileName):
    with open(fileName, "r", encoding='utf-8-sig') as entryData:
        toParse = str(entryData.read())

        # Clean out form-only instructional text.
        pattern = re.compile(r'Choose your .{3,4} preferences \[(?P<content>.*?)\]')
        toParse = re.sub(r'\"', "", toParse)
        toParse = re.sub(pattern, r'\g<1>,', toParse)

        pattern = re.compile(r'(?P<content>.*),\n')
        toParse = re.sub(pattern, r'\g<1>\n', toParse)

        toParse = toParse.split("\n")
        preferenceData = {}

        header=True

        for row in toParse:
            if header:
                fields = row.split(",")
                fields = [value for value in fields if value != '']
                header = False
            elif row.strip():
                teamValues = row.split(",")
                teamDict = {}
                index = 0
                for field in fields:
                    if field != 'Team Name':
                        teamDict[field] = teamValues[index]
                    index = index + 1
                preferenceData[teamValues[1]] = teamDict

        return preferenceData

    return