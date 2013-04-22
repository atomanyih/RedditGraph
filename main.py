import sys, getopt, json

from reddit import *
from metastats import *

visitedSubreddits = []
metaStats = MetaStats()

class Results:
    def __init__(self):
        self.networkDict = {}
        self.subsDict = {}

    def join(self,other):
        # network dicts should never have entries that disagree
        self.networkDict = joinDicts(self.networkDict,other.networkDict)
        self.subsDict = joinDicts(self.subsDict,other.subsDict)

    def addInfo(self,info):
        self.networkDict[info.name] = info.children
        self.subsDict[info.name] = info.subscribers

#d2 has precedence
def joinDicts(d1,d2):
    return dict(d1.items() + d2.items())

def doStuff(source, depth):
    global metaStats
    metaStats.subreddits += 1

    global visitedSubreddits
    visitedSubreddits += [source]

    if depth == 0:
        return Results()

    info = getSubredditInfo(source)
    if info is None:
        return Results()
        
    results = Results()
    results.addInfo(info)

    metaStats.compareChildren(source,len(info.children))

    if depth == 1:
        results.networkDict = {}
        return results

    for subreddit in info.children:
        if subreddit not in visitedSubreddits:
            r = doStuff(subreddit, depth-1)
            results.join(r)
            
        print "skipping", subreddit

    return results

#idea: results
# has network dictionary
# has subscriber dictionary
# has index dictionary?

# doStuff
# depth 0:
#   empty
# depth 1:
#   network is source -> chillun
#   subscriber is source (+ chillun?) (will cause problem if some don't have)
# depth >1:
#   network is source + network of each child
#   subscriber is source + subscribers of each child

# from network dict
def makeIndexDictionary(d):
    indDict = {}
    itemList= d.keys()
    valueList = d.values()
    
    for values in valueList:
        for value in values:
            if value not in itemList:
                itemList += [value]

    i = 0
    for item in itemList:
        indDict[item] = i
        i += 1

    return (indDict,itemList) #this sucks

def resultsToString(r):
    s = '{\n'

    nodesString = ' "nodes": [\n'
    linksString = ' "links": [\n'

    (indDict,itemList) = makeIndexDictionary(r.networkDict)

    for i in range(len(itemList)):
        name = itemList[i]
        if(name in r.subsDict):
            subs = r.subsDict[name]
        else:
            subs = 1

        nodesString += makeNodeLine(name,subs)
        if i < len(itemList) - 1:
            nodesString += ',\n'
        else:
            nodesString += '\n'

    #refactor plox
    items = r.networkDict.items()
    for i in range(len(items)):
        st = items[i][0]
        tList = items[i][1]

        for j in range(len(tList)):
            t = tList[j]

            sI = indDict[st]
            tI = indDict[t]

            linksString += makeLinkLine(sI,tI)

            if (i == len(items) - 1) and (j == len(tList) - 1):
                linksString += '\n'
            else:
                linksString += ',\n'


    nodesString += " ],\n"
    linksString += " ]\n"

    s += nodesString + linksString + "}\n"

    return s

def makeDataDictionary(results):
    dataDict = {}

    (indDict,nodeList) = makeIndexDictionary(results.networkDict)

    nodesList = []
    for item in nodeList:
        node = {'name': item, 'subscribers': results.subsDict[item]}
        nodesList += [node]

    linksList = []

    items = results.networkDict.items()
    for item in items:
        source = item[0]
        for target in item[1]:
            link = {'source':indDict[source], 'target':indDict[target]}
            linksList += [link]

    dataDict['nodes'] = nodesList
    dataDict['links'] = linksList
    #print nodesList
    #print linksList

    return dataDict


def makeNodeLine(name,size):
    return '{ "name": "' + name + '", "subscribers":' + str(size) + '}'

def makeLinkLine(sInd,tInd):
    return '  { "source": ' + str(sInd) + ', "target": ' + str(tInd) + '}'

def writeDictToFile(filename,d):
    s = json.dumps(d, indent=2, separators=(',', ': '))
    f = open(filename, 'w')
    f.write(s)

def loadDataFile(filename):
    f = open(filename, 'r')
    d = json.loads(f.read())

    return decodeData(d)
    #return d

# takes the dict loaded from json to result
def decodeData(dataDict):
    results = Results()
    nodesList = dataDict['nodes']
    linksList = dataDict['links']


    subsDict = {}
    nameList = []
    for node in nodesList:
        name = str(node['name'])
        nameList += [name]
        subsDict[name] = node['subscribers']

    networkDict = {}
    for link in linksList:
        source = nameList[link['source']]
        target = nameList[link['target']]
        if source not in networkDict:
            networkDict[source] = []
        networkDict[source] += [target]

    results.networkDict = networkDict
    results.subsDict = subsDict

    return results


def usage():
    print "You did it wrong"

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'c:f:')
    except getopt.GetoptError as err:
        print err
        usage()
        sys.exit(2)

    if len(args) < 2:
        usage()
        sys.exit(2)

    try:
        depth = int(args[1])
    except ValueError as err:
        print err
        print 'Non-numerical depth'
        sys.exit(2)

    subreddit = args[0].lower()
    filename = subreddit + '_' + str(depth) + '.json'
    origFilename = None


    for opt, arg in opts:
        if opt == '-f':
            filename = arg
        elif opt == '-c':
            origFilename = arg
    
    results = Results()

    if origFilename is not None:
        results = loadDataFile(origFilename)  

    results.join(doStuff(subreddit, depth))

    global metaStats
    print metaStats

    dataDict = makeDataDictionary(results)
    writeDictToFile(filename, dataDict)


if __name__ == "__main__":
    main(sys.argv[1:])
