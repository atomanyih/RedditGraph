import sys,urllib2, re
from bs4 import BeautifulSoup

TRIES_LIMIT = 100

class SubredditInfo:
	def __init__(self):
		self.name = ""
		self.children = []
		self.subscribers = 0

def getSubredditInfo(subredditName):
	print "-",subredditName
	page = getPage(subredditName)

	if page is None:
		return None

	soup = BeautifulSoup(page)
	side = getSidebar(soup)

	info = SubredditInfo()

	info.name = subredditName
	info.children = getSubredditsFromSidebar(side)
	info.subscribers = getSubscriberCount(side)

	return info

def getSidebarSubreddits(subredditName):
    soup = getSoupFromSubredditName(subredditName)
    side = getSidebar(soup)

    return getSubredditsFromSidebar(side)

def getSubredditsFromSidebar(side):
	subreddits = []

	for link in side.find_all('a'):

		address = link.get('href')
		if address is not None:
			name = address[3:]
			#print name # some subreddits do this wrong, the butts
			if address[:3] == '/r/' and isValidSubredditName(name): 
				subreddits += [str(name).lower()]

	return subreddits

def getSubscriberCount(side):
	try:
		subscriberString = side.find('span', 'subscribers').find('span', 'number').text
	except AttributeError:
		print "couldn't find subscribers, skipping"
		return 0

	try:
		nSubs = int(subscriberString.replace(",",""))
	except ValueError:
		print "Couldn't find subscriber count, skipping"
		return 0
	return nSubs

def getSidebar(soup):
	return soup.body.contents[1];

def getPage(subredditName):
	url = 'http://www.reddit.com/r/'+subredditName
	sys.stdout.write("Trying to connect...")

	tries = 0

	while 1:
		try:
			page = urllib2.urlopen(url)
			break
		except urllib2.HTTPError:
			sys.stdout.write(".")
			tries += 1

		if tries >= TRIES_LIMIT:
			print "skipping"
			return None

	print "success"
	contents = page.read()
	return contents


# returns whether name is valid
# only alphanumeric
def isValidSubredditName(name):
    return re.match('^[\w-]+$', name) is not None
