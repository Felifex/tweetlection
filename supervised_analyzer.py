import sys, re, random
import mysql.connector as mysql
import nltk

STOPWORDS = ['...']

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

   tweets = None;
   # Pull the first 100 tweets
   try:
      cursor.execute(
         "SELECT text, retweet_count FROM tweets "
         "GROUP BY text "
         "HAVING max(retweet_count) "
         "ORDER BY retweet_count")
      tweets = cursor.fetchall()
   except Exception, e:
      print e.message
      raise e

   if tweets:
      print 'Classifying', len(tweets), 'unlabeled Tweets:'
      generate_overall_score(tweets, obama_classifier, romney_classifier)

def generate_overall_score(tweets, obama_classifier, romney_classifier):
   obama_score = 0
   romney_score = 0
   total_tweets = 0

   for tweet in tweets:
      (o, r) = obama_romney_score(tweet, obama_classifier, romney_classifier)
      obama_score += o * tweet[1]
      romney_score += r * tweet[1]
      total_tweets += tweet[1]

   obama_score /= total_tweets
   romney_score /= total_tweets

   print '/--------------------------\\'
   print '|                          |'
   print '| Obama Sentiment:', "%.3f" % obama_score, ' |'
   print '| Romney Sentiment:', "%.3f" % romney_score, '|'
   print '|                          |'
   print '\--------------------------/'
   

def obama_romney_score(tweet, obama_classifier, romney_classifier):
   formatted_tweet = {'text': tweet[0],
                      'retweets': tweet[1]}

   obama_features = obama_tweet_features(formatted_tweet, labeled=False)
   romney_features = romney_tweet_features(formatted_tweet, labeled=False)

   return (get_tweet_score(obama_features, obama_classifier), get_tweet_score(romney_features, romney_classifier))


def get_tweet_score(features, classifier):
   tweet_score = 0
   for feature in features:
      tweet_score += get_score(classifier.classify(feature))
   tweet_score = float(tweet_score) / len(features)
   return tweet_score

def get_trained_classifiers(labeled_tweets):
   romney_feature_set = []
   obama_feature_set = []
   for tweet in labeled_tweets:
      romney_feature_set.extend(romney_tweet_features(tweet))
      obama_feature_set.extend(obama_tweet_features(tweet))

   print 'Training on', len(labeled_tweets), 'tweets'
   print 'Found', len(obama_feature_set), 'features from Obama'
   print 'Found', len(romney_feature_set), 'features from Romney\n'
   romney_classifier = nltk.NaiveBayesClassifier.train(romney_feature_set)
   obama_classifier = nltk.NaiveBayesClassifier.train(obama_feature_set)
   return (romney_classifier, obama_classifier)

def romney_accuracy(labeled_tweets, class_type='nb'):
   feature_set = []
   for tweet in labeled_tweets:
      feature_set.extend(romney_tweet_features(tweet))

   print 'Romney:', len(feature_set), 'features'
   train_and_test(feature_set, class_type)
   
def obama_accuracy(labeled_tweets, class_type='nb'):
   feature_set = []
   for tweet in labeled_tweets:
      feature_set.extend(obama_tweet_features(tweet))

   print 'Obama:', len(feature_set), 'features'
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

def romney_tweet_features(tweet, labeled=True):
   word_features = []

   word_list = [w.strip('., ') for w in nltk.word_tokenize(tweet['text'])]
   retweets = tweet['retweets'] if labeled else 1
   for x in range(0, retweets):
      for word in word_list:
         if len(word) >= 3 and not word in STOPWORDS:
            if labeled:
               if 'romney' in tweet:
                  word_features.append(({'word': word}, get_score_string(tweet['romney'])))
            else:
               word_features.append({'word': word})

   return word_features

def obama_tweet_features(tweet, labeled=True):
   word_features = []

   word_list = [w.strip('., ') for w in nltk.word_tokenize(tweet['text'])]
   retweets = tweet['retweets'] if labeled else 1
   for x in range(0, retweets):
      for word in word_list:
         if len(word) >= 3 and not word in STOPWORDS:
            if labeled:
               if 'obama' in tweet:
                  word_features.append(({'word': word}, get_score_string(tweet['obama'])))
            else:
               word_features.append({'word': word})

   return word_features


def get_score_string(value):
   if value > 0:
      return 'positive'
   elif value == 0:
      return 'neutral'
   else:
      return 'negative'

def get_score(label):
   if label == 'positive':
      return 1
   elif label == 'neutral':
      return 0
   else:
      return -1

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
