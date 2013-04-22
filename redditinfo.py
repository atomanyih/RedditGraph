import praw

"""userAgent = ('Subreddit analyzer for RedditGraph by /u/augzodia')

r = praw.Reddit(userAgent)

subreddit = r.get_subreddit('videos')
numSubmissions = 10
top = subreddit.get_top_from_all(limit = numSubmissions)
numComments = 0


for submission in top:
	print submission.title
	print "-",submission.score
	numComments += len(submission.comments)
	#for comment in submission.comments():
	#	numComments += 1
	print "-",len(submission.comments)

print "Average:", numComments/numSubmissions"""

class SubredditAnalyzer:
	userAgent = ('Subreddit analyzer for RedditGraph by /u/augzodia')
	def __init__(self):
		self.reddit = praw.Reddit(self.userAgent)

	#only does top level comments :|
	def getTotalCommentsInTop(self, subredditName, numSubmissions = 10):
		subreddit = self.reddit.get_subreddit(subredditName)
		top = subreddit.get_top_from_all(limit = numSubmissions)
		numComments = 0
		for submission in top:
			numComments += len(submission.comments)
		return numComments

	def getAvgCommentsInTop(self, subredditName, numSubmissions = 10):
		numComments = getTotalCommentsInTop(subredditName, numSubmissions)
		return numComments/numSubmissions


s = SubredditAnalyzer()
print s.getTotalCommentsInTop('videos')
print s.getTotalCommentsInTop('funny')
print s.getTotalCommentsInTop('askreddit')