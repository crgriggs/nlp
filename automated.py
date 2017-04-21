import sys
from sklearn.metrics.pairwise import cosine_similarity as cos_sim
from nltk.corpus import wordnet as wn 
import numpy as np
import subprocess
import os.path
import random
import re
import cPickle as pickle
from PIL import Image


people = ['Alice Ashcraft', 'Francis Foster', 'Robert Brown', 'Carol Clark', 'Dave Daniel', 'George Green', 'Evelyn Eckhart', 'Mallory Morgan', 'Peggy Parker', 'Walter Ward']
items = ['trashcan', 'hamburger', 'coffee', 'calendar']


def createItemDict():

    if os.path.isfile("itemDict.p"):
        itemDict = pickle.load( open( "itemDict.p", "rb" ) )
        for item in itemDict:
            for ss in wn.synsets(item):
                for syn in ss.lemma_names():
                    itemDict[item].append(syn)
                for hyp in ss.hypernyms():
                    for syn in hyp.lemma_names():
                        itemDict[item].append(syn)
                    break
                break
        return itemDict

    wordDict = {}
    itemDict = {}

    for line in open("paragram-phrase-XXL.txt"):
        line = line.split()
        key = line.pop(0)
        wordDict[key] = np.asarray(line)

    for line in open("paragram_300_sl999.txt"):
       line = line.split()
       key = line.pop(0)
       wordDict[key] = np.asarray(line)

    for item in items:
        itemDict[item] = findSimWords(item, wordDict)
        for ss in wn.synsets(item):
            for syn in ss.lemma_names():
                itemDict[item].append(syn)
            break

    pickle.dump( itemDict, open( "itemDict.p", "wb" ) )

    return itemDict

def findSimWords(word, wordDict):
    closestItems = []
    if word not in wordDict:
        print "word not recognized"
        return
    wordArray = wordDict[word]
    for key in wordDict:
        if key == word:
            continue
        compareArray = wordDict[key]
        if cos_sim(wordArray.reshape(1, -1), compareArray.reshape(1, -1)) > 0.7:
            closestItems.append(key)
    return closestItems



def pickName(person):
    if random.randint(0,1) == 1:
        name = person.split()[0]
    else:
        name = person
    return name


def write(inputFile, nput):
    with open(inputFile, 'w+') as f:
        f.seek(0)
        f.write(nput)
        f.truncate()
        f.close

def sendCommand(user):
    command = ['python', 'dialog/main.py', 'dialog/', 'offline', str(user)]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.read()

def trainCommand():
    command = ['python', 'dialog/main.py', 'dialog/', 'retrain', str(user)]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def getResponse(text):
    temp = ""
    strs = re.findall('ROBOT: \w*.*',text)
    for match in strs:
        temp = match
    return temp

def shouldBreak(response):
    if "Happy" in response:
        return True
    return False

def setInput(response, person, key):
    if "Are you asking me a question?" in response:
        return "No"
    elif "does that answer your question?" in response:
        return "No"
    elif "You want me to bring" in response:
        return "Yes"
    elif "Could you reword your question?" in response:
        return "Please bring " + person + " a " + key
    elif "Could you reword your original request?" in response:
        return "Please bring " + person + " " + key
    elif "Should I deliver something to " + person.lower() in response:
        return "Yes"
    elif "What did you want me to do with" in response:
        return "Bring"
    elif "Should I bring" in response:
        return "Yes"
    elif "What action did you want me to take" in response:
        return "Bring"


user = 0
itemDict = createItemDict()

for key in itemDict:
    person = people[random.randint(0, len(people)) -1]
    if itemDict[key] == None:
        continue
    for item in itemDict[key]:
        #sometimes uses the first name to provide data for user's who
        #just use the first name
        name = pickName(person)
        #choosing a name for filename's sake
        inputFile = 'dialog/offline_data/inputs/' + str(user) + '_input.txt'
        #first command known response
        sendCommand(user)
        #random input
        nput = "Please bring " + name + " " + item
        #overwrites input file with response
        write(inputFile, nput)
        #following commands have unknown response
        while True:
            text = sendCommand(user)
            response = getResponse(text)
            print response
            if shouldBreak(response):
                break
            nput = setInput(response, person, key)
            print nput
            write(inputFile, nput)
        user += 1
#train model on inputs
trainCommand()




