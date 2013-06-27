genderSlurs = ['cunt','bitch','whore','slut','twat']
genderVariants = ['cunts','bitches','whores','sluts','twats']
gsmSlurs = ['fag','faggot','dyke','tranny','shemale']
gsmVariants = ['fags','faggots','dykes','trannies','shemales']
raceSlurs = ['nigger','nigga','nigg','porch monkey','jap','gook','chink','ching chong','dink','chinaman','paki','beaner','spic','wetback']
raceVariants = ['niggers','niggas','niggs','porch monkeys','japs','gooks','chinks','ching chongs','dinks','chinamen','pakis','beaners','spics','wetbacks']
otherSlurs = ['retard','tard','midget']
otherVariants = ['retards','retarded','tards','midgets']

slurs = genderSlurs + genderVariants + gsmSlurs + gsmVariants + raceSlurs + raceVariants + otherSlurs + otherVariants

def containsSlur(string):
	for slur in slurs:
		if slur in string:
			return True
	return False