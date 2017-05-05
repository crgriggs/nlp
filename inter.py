import subprocess
import os.path
import random
import re
#from PIL import Image


people = ['Alice Ashcraft', 'Francis Foster', 'Robert Brown', 'Carol Clark', 'Dave Daniel', 'George Green', 'Evelyn Eckhart', 'Mallory Morgan', 'Peggy Parker', 'Walter Ward']


#choosing a name for filename's sake
name = raw_input("What's your name? ")

inputFile = 'dialog/offline_data/inputs/' + name + '_input.txt'
logFile = 'dialog/offline_data/logs/' + name + '_command.txt'

#needs to be a unique name
while(os.path.isfile(inputFile)):
    print "Name already exists, choose another :D" 
    name = raw_input("What's your name? ")
    inputFile = 'dialog/offline_data/inputs/' + name + '_input.txt'
    logFile = 'dialog/offline_data/logs/' + name + '_command.txt'

#beginning dialog with robot
instruct = people[random.randint(0, len(people)-1)] + " wants item no. " + str(random.randint(1,20))
print instruct
#img = Image.open('items.png')
#img.show()

text = ""

while True:

    #starts the python cmd
    command = ['python', 'dialog/main.py', 'dialog/', 'offline', str(name)]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = p.stdout.read()
    temp = ""

    strs = re.findall('ROBOT: \w*.*',text)
    for match in strs:
        temp = match
        print match
    if "Happy" in temp:
        break

    response = raw_input(name + ": ")
    #overwrites input file with response
    with open(inputFile, 'w+') as f:
        f.seek(0)
        f.write(response)
        f.truncate()
        f.close

    with open(logFile, 'w+') as f:
        f.seek(0)
        f.write(instruct)
        f.truncate()
        f.close



