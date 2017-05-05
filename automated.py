from sklearn.metrics.pairwise import cosine_similarity as cos_sim
from nltk.corpus import wordnet as wn 
import numpy as np
import subprocess
import os.path
import random
import re
import cPickle as pickle


people = ['Alice Ashcraft', 'Francis Foster', 'Robert Brown', 'Carol Clark', 'Dave Daniel', 'George Green', 'Evelyn Eckhart', 'Mallory Morgan', 'Peggy Parker', 'Walter Ward']
items = ['wallet', 'purse', 'camera', 'newspaper', 'pencil', 'eraser', 'glasses', 'button', 'fork', 'banana', 'clock', 'cigarette', 'scissors', 'comb', 'mirror','trashcan', 'hamburger', 'coffee', 'calendar', 'cell phone']


#creates a dictionary from John Weiting's word embeddings with the word
#being the key and the vector being the value
def createWordDict():
    if os.path.isfile("itemDict.p") and os.path.isfile("verbDict.p"):
        return {}
    if os.path.isfile("wordDict.p"):
        return pickle.load( open( "wordDict.p", "rb" ) )

    wordDict = {}
    for line in open("paragram-phrase-XXL.txt"):
        line = line.split()
        key = line.pop(0)
        wordDict[key] = np.asarray(line)

    for line in open("paragram_300_sl999.txt"):
       line = line.split()
       key = line.pop(0)
       wordDict[key] = np.asarray(line)

    pickle.dump( wordDict, open( "wordDict.p", "wb" ) )
    return wordDict

#creates a dictionary of words with cosine similarity higher than 0.5
#and synonym and hypernyms with items known to the robot being the key
def createItemDict(wordDict):
    if os.path.isfile("itemDict.p"):    
        return pickle.load( open( "itemDict.p", "rb" ) )

    itemDict = {}

    for item in items:
        itemDict[item] = findSimWords(item, wordDict, 0.5)
        for ss in wn.synsets(item):
            for syn in ss.lemma_names():
                itemDict[item].append(syn)
            for hyp in ss.hypernyms():
                    for syn in hyp.lemma_names():
                        itemDict[item].append(syn)
                    break
            break

    pickle.dump( itemDict, open( "itemDict.p", "wb" ) )

    return itemDict

#finds cosine similarities of the verbs bring and take
def createVerbDict(wordDict):

    if os.path.isfile("verbDict.p"):
        return pickle.load( open( "verbDict.p", "rb" ) )

    verbDict = {}
    verbDict["bring"] = findSimWords("bring", wordDict, 0.5)
    verbDict["take"] = findSimWords("take", wordDict, 0.5)
    pickle.dump( verbDict, open( "verbDict.p", "wb" ) )

    return verbDict

#implementation of cos sim
def findSimWords(word, wordDict, similarity):
    closestItems = []
    if word not in wordDict:
        print "word not recognized"
        return
    wordArray = wordDict[word]
    for key in wordDict:
        if key == word:
            continue
        compareArray = wordDict[key]
        if cos_sim(wordArray.reshape(1, -1), compareArray.reshape(1, -1)) > similarity:
            closestItems.append(key)
    return closestItems

#decides whether to use full name or just first
def pickName(person):
    if random.randint(0,1) == 1:
        name = person.split()[0]
    else:
        name = person
    return name

#writes user input to file
def write(inputFile, nput):
    with open(inputFile, 'w+') as f:
        f.seek(0)
        f.write(nput)
        f.truncate()
        f.close

#sends commands to let robot know the user is ready for their next turn
def sendCommand(user):
    command = ['python', 'dialog/main.py', 'dialog/', 'offline', str(user)]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.read()

#trains the robot on the gathered data
def trainCommand():
    command = ['python', 'dialog/main.py', 'dialog/', 'retrain', str(user)]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#uses regular expressions to find the robot's response to user
#only concerned with last sent because it contains the key word
#that signifies the robot is finished 
def getResponse(text):
    temp = ""
    strs = re.findall('ROBOT: \w*.*',text)
    for match in strs:
        temp = match
    return temp

#this is the ending keyword
def shouldBreak(response):
    if "Happy" in response:
        return True
    return False

#knowing how to respond to all responses is what allows us to train
#authors insert a bit of randomness so we can't just depend on an established 
#pattern to follow
def setInput(response, person, key):
    if "Are you asking me a question?" in response:
        return "No"
    elif "does that answer your question?" in response:
        return "No"
    elif "You want me to bring" in response:
        return "Yes"
    elif "Could you reword your question?" in response:
        return "Please bring " + person + " a " + key 
    elif "Who or what is" in response:
        return "bring " + person + " " + key
    elif "Could you reword your original request?" in response:
        return "Please bring " + person + " a " + key
    elif "Should I deliver something to " + person.lower() in response:
        return "Yes"
    elif "What did you want me to do with" in response:
        return "Bring"
    elif "Should I bring" in response:
        return "Yes"
    elif "To whom should I bring" in response:
        return person
    elif "What should I bring to" in response:
        return key
    elif "What action did you want me to take" in response:
        return "Bring"
    return ""

#this is the main loop for training the model on new items
def trainItems(user, itemDict):
    for key in itemDict:
        person = people[random.randint(0, len(people)) -1]
        if itemDict[key] == None:
            continue
        for item in itemDict[key]:
            #trash-can should be trash can
            item = item.replace("-", " ").replace("_", " ")
            #sometimes uses the first name to provide data for user's who
            #just use the first name
            name = pickName(person)
            #choosing a name for filename's sake
            inputFile = 'dialog/offline_data/inputs/' + str(user) + '_input.txt'
            #first command known response
            text = sendCommand(user)
            response = getResponse(text)
            print response
            #random input
            nput = "Please bring " + name + " a " + item
            print nput
            #overwrites input file with response
            write(inputFile, nput)
            #following commands have unknown response
            while True:
                text = sendCommand(user)
                response = getResponse(text)
                print response
                if shouldBreak(response) or response == None:
                    if response == None:
                        print "error on item" + item
                    break
                nput = setInput(response, person, key)
                print nput
                write(inputFile, nput)
            user += 1

#this is the main loop for training new verbs
def trainVerbs(user, verbDict, itemDict):
    for key in verbDict:
        person = people[random.randint(0, len(people)) -1]
        for verb in verbDict[key]:
            item = random.choice(itemDict.keys())
            #sometimes uses the first name to provide data for user's who
            #just use the first name
            name = pickName(person)
            #choosing a name for filename's sake
            inputFile = 'dialog/offline_data/inputs/' + str(user) + '_input.txt'
            #first command known response
            text = sendCommand(user)
            response = getResponse(text)
            print response
            #random input
            nput = verb + " " + name + " a " + item
            print nput
            #overwrites input file with response
            write(inputFile, nput)
            #following commands have unknown response
            while True:
                text = sendCommand(user)
                response = getResponse(text)
                print response
                if shouldBreak(response) or response == None:
                    if response == None:
                        print "error on verb" + verb
                    break
                nput = setInput(response, person, item)
                print nput
                write(inputFile, nput)
            user += 1

if __name__ == "__main__":
    user = 5000
    wordDict = createWordDict()
    itemDict = createItemDict(wordDict)
    verbDict = createVerbDict(wordDict)
    trainItems(user, itemDict)
    user = 100
    trainVerbs(user, verbDict, itemDict)
    trainCommand()


