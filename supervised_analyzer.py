import sys, re, random
import mysql.connector as mysql
import nltk

def main():
   # Connect to the DB
   # host='24.205.232.5'
   conn = mysql.connect(
      host='127.0.0.1',
      user='tweetlection',
      passwd='tweetlection12',
      db='tweetlection'
   )

   cursor = conn.cursor()

   # Parse Labeled Tweets
   labeled_tweets = get_labeled_tweets()

   # Get Accuracy
   # romney_accuracy(labeled_tweets, class_type='nb')
   # obama_accuracy(labeled_tweets, class_type='nb')

   # Get both classifiers for Obama and Romney
   (romney_classifier, obama_classifier) = get_trained_classifiers(labeled_tweets)

  
   print romney_classifier.classify(romney_tweet_features(labeled_tweets[0]))

   # tweets = None;
   # # Pull the first 100 tweets
   # try:
   #    insert_labeled_tweet = (
   #       "INSERT INTO tweets (id, text, retweet_count) "
   #       "VALUES (%s, %s, %s)")
   #    tweet_data = (status.id_str, status.text, status.retweet_count)
   #    self.cursor.execute(insert_tweet, tweet_data)

   #    self.conn.commit() # Commit data


   #    cursor.execute(
   #       "SELECT text, retweet_count FROM tweets "
   #       "WHERE retweet_count > 1000 "
   #       "GROUP BY text "
   #       "HAVING max(retweet_count) "
   #       "ORDER BY retweet_count")
   #    tweets = cursor.fetchall()
   #    for tweet in tweets:
   #       print tweet
   # except Exception, e:
   #    raise e

   # if tweets:
   #    print len(tweets)

def get_trained_classifiers(labeled_tweets):
   romney_feature_set = [], obama_feature_set = []
   for tweet in labeled_tweets:
      romney_feature_set.extend(romney_tweet_features(tweet))
      obama_feature_set.extend(obama_tweet_features(tweet))

   romney_classifier = nltk.NaiveBayesClassifier.train(romney_feature_set)
   obama_classifier = nltk.NaiveBayesClassifier.train(obama_feature_set)
   return (romney_classifier, obama_classifier)

def romney_accuracy(labeled_tweets, class_type='nb'):
   feature_set = []
   for tweet in labeled_tweets:
      feature_set.extend(romney_tweet_features(tweet))

   print 'Romney:'
   train_and_test(feature_set, class_type)
   
def obama_accuracy(labeled_tweets, class_type='nb'):
   feature_set = []
   for tweet in labeled_tweets:
      feature_set.extend(obama_tweet_features(tweet))

   print 'Obama:'
   train_and_test(feature_set, class_type)

def train_and_test(feature_set, class_type='nb'):
   # Randomize
   random.shuffle(feature_set)

   # Split features
   midpoint = len(feature_set) / 2
   train, test = feature_set[:midpoint], feature_set [midpoint:]

   if class_type == 'nb':
      #NLTK's built-in implementation of the Naive Bayes classifier is trained
      classifier = nltk.NaiveBayesClassifier.train(train)
   elif class_type == 'dt':
      classifier = nltk.DecisionTreeClassifier.train(train)
   elif class_type == 'svm':
      classifier = nltk.SklearnClassifier.train(train)

   # Test classifier
   print 'Accuracy:', nltk.classify.accuracy(classifier, test)

   # Print most important features
   if class_type == 'nb':
      classifier.show_most_informative_features(20)

def romney_tweet_features(tweet):
   word_features = []

   word_list = nltk.word_tokenize(tweet['text'])
   for x in range(0, tweet['retweets']):
      for word in word_list:
         if len(word) >= 3 and 'romney' in tweet:
               word_features.append(({'word': word}, get_score_string(tweet['romney'])))

   return word_features

def obama_tweet_features(tweet):
   word_features = []

   word_list = nltk.word_tokenize(tweet['text'])
   for x in range(0, tweet['retweets']):
      for word in word_list:
         if len(word) >= 3 and 'obama' in tweet:
               word_features.append(({'word': word}, get_score_string(tweet['obama'])))

   return word_features


def get_score_string(value):
   if value > 0:
      return 'positive'
   elif value == 0:
      return 'neutral'
   else:
      return 'negative'

def get_labeled_tweets():
   # Open File
   f = open('labeled_tweets.csv')
   f = f.readlines()

   tweets = []
   for index, tweet in enumerate(f):
      labeled_tweet = {}
      tweet = tweet.strip()
      fields = tweet.split(',')

      if len(fields) < 5:
         # print index, 'SKIP: < 5'
         continue

      # Join fields that have commas in text
      if len(fields) > 5:
         temp_fields = []
         temp_fields.append(fields[0])
         combine = len(fields) - 4
         temp_fields.append(', '.join(fields[1:1+combine]))
         temp_fields.extend(fields[1+combine:])
         fields = temp_fields

      if not (fields[0].isdigit() and fields[2].isdigit()):
         # print index, 'SKIP: Bad format'
         continue

      labeled_tweet['text'] = fields[1].lower()
      labeled_tweet['retweets'] = int(fields[2])

      try:
         labeled_tweet['obama'] = int(fields[3])
      except Exception, e:
         pass

      try:
         labeled_tweet['romney'] = int(fields[4])
      except Exception, e:
         pass

      if not 'obama' in labeled_tweet and not 'romney' in labeled_tweet:
         # print index, 'SKIP: No data'
         continue

      tweets.append(labeled_tweet)

   return tweets

if __name__ == '__main__':
   sys.exit(main())
