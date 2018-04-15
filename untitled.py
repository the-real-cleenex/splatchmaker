import sys

line = '2 3 7 4 5 9 1'
targetSum = 5
rawInput = line.split()

# Converting data type for efficiency.
integers = []
for value in rawInput:
  integers.append(int(value))

a = 0
b = 0

solutions = []

while a < len(integers):
    while b < len(integers):
        if a != b: # Check to see if a value is being reused.
            if integers[a] + integers[b] == targetSum:
                if integers[a] > integers[b]:
                    solutions.append(str(integers[a]) + ' ' + str(integers[b]))
                else:
                    solutions.append(str(integers[a]) + ' ' + str(integers[b]))
        b = b + 1
    a = a + 1

print solutions