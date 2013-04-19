
class MetaStats:
	def __init__(self):
		self.subreddits = 0
		self.mostChildren = ['',0]

	def __str__(self):
		string = str(self.subreddits)
		string += ' subreddits accessed' + '\n'
		string += str(self.mostChildren[1]) + " - "
		string += self.mostChildren[0] + ' '
		string += 'most children\n'
		return string

	def compareChildren(self,name,nChildren):
		if nChildren > self.mostChildren[1]:
			self.mostChildren = [name,nChildren]
			return True
		return False

