import subprocess
import os.path
import random
import re
from PIL import Image


people = ['Alice Ashcraft', 'Francis Foster', 'Robert Brown', 'Carol Clark', 'Dave Daniel', 'George Green', 'Evelyn Eckhart', 'Mallory Morgan', 'Peggy Parker', 'Walter Ward']


#choosing a name for filename's sake
name = raw_input("What's your name? ")

directDict = {0 : "original", 1 : "syn", 2: "entropy", 3: "synEntropy"}
directory = directDict[random.randint(0,3)] + "/"
inputFile = directory + 'dialog/offline_data/inputs/' + name + '_input.txt'

#needs to be a unique name
while(os.path.isfile(inputFile)):
    print "Name already exists, choose another :D" 
    name = raw_input("What's your name? ")
    inputFile = directory + 'dialog/offline_data/inputs/' + name + '_input.txt'


#beginning dialog with robot
print "Please bring " + people[random.randint(0, len(people)-1)] + " item no. " + str(random.randint(1,5))
img = Image.open('items.png')
img.show()

text = ""

while True:

    #starts the python cmd
    command = ['python', directory +'dialog/main.py', directory +'dialog/', 'offline', str(name)]
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

