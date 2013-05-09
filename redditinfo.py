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

"""
data to get:
num upvotes in top
avg upvotes in top
num downvotes in top
avg downvotes in top
upvote/downvote ratio in top

"""

class SubredditAnalyzer:
	userAgent = ('Subreddit analyzer for RedditGraph by /u/augzodia')
	def __init__(self):
		self.reddit = praw.Reddit(self.userAgent)

	def getTotalCommentsInTop(self, subredditName, numSubmissions = 10):
		subreddit = self.reddit.get_subreddit(subredditName)
		top = subreddit.get_top_from_all(limit = numSubmissions)
		numComments = 0
		for submission in top:
			#print numComments
			numComments += submission.num_comments
		return numComments

	def getAvgCommentsInTop(self, subredditName, numSubmissions = 10):
		numComments = self.getTotalCommentsInTop(subredditName, numSubmissions)
		return numComments/float(numSubmissions)

	def getTotalUpvotesInTop(self, subredditName, numSubmissions = 10):
		subreddit = self.reddit.get_subreddit(subredditName)
		top = subreddit.get_top_from_all(limit = numSubmissions)
		numUpvotes = 0
		for submission in top:
			#print numUpvotes
			numUpvotes += submission.ups
		return numUpvotes

	def getAvgUpvotesInTop(self, subredditName, numSubmissions = 10):
		numUpvotes = self.getTotalUpvotesInTop(subredditName, numSubmissions)
		return numUpvotes/float(numSubmissions)

	def getUpvoteRatioInTop(self, subredditName, numSubmissions = 10):
		subreddit = self.reddit.get_subreddit(subredditName)
		top = subreddit.get_top_from_all(limit = numSubmissions)
		upvoteRatio = 0.0
		try:
			for submission in top:
				ups = submission.ups
				total = ups + submission.downs
				upvoteRatio += ups/float(total)
		except:
			print "din't work"
			return -1.0
		return upvoteRatio/numSubmissions

"""
s = SubredditAnalyzer()
print s.getAvgCommentsInTop('videos'), "comments"
#print s.getTotalCommentsInTop('funny')
#print s.getTotalCommentsInTop('askreddit')
print s.getAvgUpvotesInTop('videos'), "upvotes"
print s.getUpvoteRatioInTop('videos'), "percent approval"
print s.getUpvoteRatioInTop('happy'), "percent approval"
print s.getUpvoteRatioInTop('shitredditsays'), "percent approval"
print s.getUpvoteRatioInTop('circlejerk'), "percent approval"
"""
