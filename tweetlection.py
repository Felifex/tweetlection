import sys
import tweepy

# Application settings
CONSUMER_KEY = 'J0kdwruL0u2dCT5E8CJc9Q'
CONSUMER_SECRET = 'kwr0CnmBpeYvcRMlL7W5kMDd4gaMq7mgxgEWzgL9hTQ'

# Application access token
ACCESS_TOKEN = '14456306-60JDItmIWoHfy8cE2Qw4NP1RujVXnWOwB6yIH4Ks1'
ACCESS_TOKEN_SECRET = 'wMSmg7eSQIshPEZK6yGSbVq3xKmmbMg4dA83f7J3DU'

def main():
   listener = TweetlectionStreamListener()
   auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
   auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

   stream = tweepy.Stream(auth, listener, timeout=60)
   stream.filter(track=['Barack', 'Obama', 'Mitt', 'Romney', 'Joe Biden',
                        'Biden', 'Paul Ryan'])

# Create streamer class
class TweetlectionStreamListener(tweepy.StreamListener):
   """Custom stream listener"""
   def on_status(self, status):
      print status.text

   def on_error(self, status_code):
      print >> sys.stderr, 'Encountered error with status code:', status_code
      return True # Don't kill the stream

   def on_timeout(self):
      print >> sys.stderr, 'Timeout...'
      return True # Don't kill the stream


if __name__ == '__main__':
   sys.exit(main())