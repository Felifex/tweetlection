from twython import Twython

t = Twython();
tweets = t.search(q='Obama')
print tweets