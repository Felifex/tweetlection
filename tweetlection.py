import sys
import tweepy
import MySQLdb

# Application settings
CONSUMER_KEY = 'J0kdwruL0u2dCT5E8CJc9Q'
CONSUMER_SECRET = 'kwr0CnmBpeYvcRMlL7W5kMDd4gaMq7mgxgEWzgL9hTQ'

# Application access token
ACCESS_TOKEN = '14456306-60JDItmIWoHfy8cE2Qw4NP1RujVXnWOwB6yIH4Ks1'
ACCESS_TOKEN_SECRET = 'wMSmg7eSQIshPEZK6yGSbVq3xKmmbMg4dA83f7J3DU'

def main():
   auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
   auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

   # Connect to the DB
   conn = MySQLdb.connect(
      host='localhost',
      user='tweetlection',
      passwd='tweetlection12',
      db='tweetlection'
   )
   cursor = conn.cursor()

   listener = TweetlectionStreamListener()
   stream = tweepy.Stream(auth, listener, timeout=60)
   stream.filter(track=['Barack', 'Obama', 'Mitt', 'Romney', 'Joe Biden',
                        'Biden', 'Paul Ryan'])

# Create streamer class
class TweetlectionStreamListener(tweepy.StreamListener):
   """Custom stream listener"""
   def __init__(self, cursor):
      self.cursor = cursor

   def on_status(self, status):
      print status.text.encode('utf8')
      self.cursor.execute("""
         INSERT INTO tweets VALUES
            (tweet.id_str, tweet.text, retweet_count, NULL);
      """)

   def on_error(self, status_code):
      print >> sys.stderr, 'Encountered error with status code:', status_code
      return True # Don't kill the stream

   def on_timeout(self):
      print >> sys.stderr, 'Timeout...'
      return True # Don't kill the stream

if __name__ == '__main__':
   sys.exit(main())