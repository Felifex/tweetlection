import sys
import tweepy
import mysql.connector as mysql

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
   conn = mysql.connect(
      host='127.0.0.1',
      user='tweetlection',
      passwd='tweetlection12',
      db='tweetlection'
   )

   listener = TweetlectionStreamListener(conn)
   stream = tweepy.Stream(auth, listener, timeout=60)
   stream.filter(track=['Barack', 'Obama', 'Mitt', 'Romney', 'Joe Biden',
                        'Biden', 'Paul Ryan'])

# Create streamer class
class TweetlectionStreamListener(tweepy.StreamListener):
   """Custom stream listener"""
   def __init__(self, conn):
      super(TweetlectionStreamListener, self).__init__()
      self.conn = conn
      self.cursor = conn.cursor()

   def on_status(self, status):
      print status.text

      insert_entity = (
         "INSERT INTO entities (tweet, hashtag, start_index, end_index) "
         "VALUES (%s, %s, %s, %s)")
      for ht in status.entities['hashtags']:
         entity_data = (status.id_str, ht['text'], ht['indices'][0], ht['indices'][1])
         self.cursor.execute(insert_entity, entity_data)

      insert_tweet = (
         "INSERT INTO tweets (id, text, retweet_count) "
         "VALUES (%s, %s, %s)")
      tweet_data = (status.id_str, status.text, status.retweet_count)
      self.cursor.execute(insert_tweet, tweet_data)

      self.conn.commit() # Commit data

   def on_error(self, status_code):
      print >> sys.stderr, 'Encountered error with status code:', status_code
      return True # Don't kill the stream

   def on_timeout(self):
      print >> sys.stderr, 'Timeout...'
      return True # Don't kill the stream

if __name__ == '__main__':
   sys.exit(main())