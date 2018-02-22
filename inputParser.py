import re
import fileinput
import csv

def googleFormsSanitizer(fileName):
    csv = str(open(fileName,"r").read())

    # Clean out introductory text.
    pattern = re.compile("\"Choose your \w+? preferences \[(?P<content>.*?)\]\",")
    csv = re.sub(pattern, "\g<1>,",csv)

    csv = re.sub("\"", "", csv) # Clean out extraneous quotation marks.
    # csv = csv.split("\n")
    print(csv)

googleFormsSanitizer("sendou.csv")