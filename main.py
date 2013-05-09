import sys, getopt, json

from reddit import *
from metastats import *
from redditinfo import *

visitedSubreddits = []
metaStats = MetaStats()

class Results:
    def __init__(self):
        #dictionary of connections
        self.networkDict = {}
        #dictionary of subscriber counts
        self.subsDict = {}
        #dictionary of dictionaries of other data
        self.statsDict = {}

    def join(self,other):
        # network dicts should never have entries that disagree
        self.networkDict = joinDicts(self.networkDict,other.networkDict)
        self.subsDict = joinDicts(self.subsDict,other.subsDict)

    def addInfo(self,info):
        self.networkDict[info.name] = info.children
        self.subsDict[info.name] = info.subscribers

    def addStats(self,statName,statDict):
        if statName not in statsDict:
            statsDict[statName] = statDict
        else:
            statsDict[statName] = joinDicts(statsDict[statName],statDict)


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
        return None
        
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


def makeDataDictionary(results):
    dataDict = {}

    (indDict,nodeList) = makeIndexDictionary(results.networkDict)

    nodesList = []
    for item in nodeList:
        if item in results.subsDict:
            subscribers = results.subsDict[item]
        else:
            subscribers = 1
        node = {'name': item, 'subscribers': subscribers}
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
        opts, args = getopt.getopt(argv, 's:f:')
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
        elif opt == '-s':
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
