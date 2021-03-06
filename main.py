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

    #TODO add proper joining for stats dict

#d2 has precedence
def joinDicts(d1,d2):
    return dict(d1.items() + d2.items())

def getOtherData(subredditList):
    analyzer = SubredditAnalyzer()
    avgCommentsDict = {}
    ratioDict = {}
    nsfwDict = {}

    i = 1
    n = len(subredditList)

    for name in subredditList:
        print "("+str(i)+"/"+str(n)+")", name.upper()

        print "- getting upvote_ratio"

        try:
            ratio = analyzer.getUpvoteRatioInTop(name)
        except:
            ratio = .5

        print "- getting avg comments"

        try:
            avg = analyzer.getAvgCommentsInTop(name)
        except:
            avg = 1

        print "- getting nsfw-ness"

        try:
            nsfw = analyzer.getNSFWRatioInTop(name)
        except:
            nsfw = 0.0

        avgCommentsDict[name] = avg
        ratioDict[name] = ratio
        nsfwDict[name] = nsfw

        i+=1

    statsDict = {"average_comments": avgCommentsDict, "upvote_ratio": ratioDict, "nsfw": nsfwDict}
    return statsDict

def doStuff(source, depth):
    global metaStats
    metaStats.subreddits += 1

    global visitedSubreddits
    visitedSubreddits += [source]

    if depth == 0:
        return Results()

    info = getSubredditInfo(source)
    if info is None:
        return Results() #None
        
    results = Results()
    results.addInfo(info)

    metaStats.compareChildren(source,len(info.children))

    if depth == 1:
        #results.networkDict = {}
        return results

    for subreddit in info.children:
        if subreddit not in visitedSubreddits:
            r = doStuff(subreddit, depth-1)
            results.join(r)
        else:    
            print "- skipping", subreddit, "already accessed"

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
def makeIndexDictionary(r):
    d = r.subsDict
    indDict = {}
    itemList = d.keys()

    i = 0
    for item in itemList:
        indDict[item] = i
        i += 1

    return (indDict,itemList)

def makeNode(item, subscribers, statsDict):
    node = {'name': item, 'subscribers': subscribers}

    for key in statsDict:
        node[key] = statsDict[key][item]

    return node

def makeDataDictionary(results):
    dataDict = {}

    (indDict,nodeList) = makeIndexDictionary(results)


    nodesList = []
    for item in nodeList:
        if item in results.subsDict:
            subscribers = results.subsDict[item]
        else:
            print item, "not found while subs"
        node = makeNode(item, subscribers, results.statsDict)

        nodesList += [node]

    linksList = []

    items = results.networkDict.items()
    for item in items:
        source = item[0]
        if source not in nodeList:
            print source, "not found as source"
            continue

        for target in item[1]:
            if target not in nodeList:
                print target, "not found as target"
                continue
            link = {'source':indDict[source], 'target':indDict[target]}
            linksList += [link]

    dataDict['nodes'] = nodesList
    dataDict['links'] = linksList
    print nodesList
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


    # here it's a dict of dicts
    statsDict = {}
    nameList = []
    for node in nodesList:
        name = str(node['name'])
        nameList += [name]
        #figure out other data
        for thing in node.keys():
            if thing != 'name':
                if thing not in statsDict:
                    statsDict[thing] = {}
                statsDict[thing][name] = node[thing]
                

    networkDict = {}
    for link in linksList:
        source = nameList[link['source']]
        target = nameList[link['target']]
        if source not in networkDict:
            networkDict[source] = []
        networkDict[source] += [target]

    results.networkDict = networkDict
    results.subsDict = statsDict.pop('subscribers')
    results.statsDict = statsDict #overwritten anyway, I think
    #print linksList

    return results


def usage():
    print "You did it wrong"
    print ""

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
        if opt == '-f':  #filename
            filename = arg
        elif opt == '-s':  #from file
            origFilename = arg
    
    # crawling
    print "     --       crawling       --"
    results = Results()

    if origFilename is not None:
        results = loadDataFile(origFilename)
        #print results.statsDict

    results.join(doStuff(subreddit, depth))

    subredditList = results.subsDict.keys()

    global metaStats
    print metaStats


    # praw data collection
    print "    -- collecting other data --"

    results.statsDict = getOtherData(subredditList)

    print "    --   writing dictionary   --"
    dataDict = makeDataDictionary(results)
    writeDictToFile(filename, dataDict)

if __name__ == "__main__":
    main(sys.argv[1:])
