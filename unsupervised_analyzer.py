import sys, re, random
import mysql.connector as mysql
import nltk

DEMOC = ['obama', 'biden', 'joe', 'barack', 'michelle']
REPUB = ['romney', 'mitt', 'paul', 'ryan']

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
    cursor.execute(
       "SELECT text, retweet_count FROM tweets "
       "GROUP BY text "
       "HAVING max(retweet_count) "
       "ORDER BY retweet_count")
    tweets = cursor.fetchall()

    if tweets:
        print 'Classifying', len(tweets), 'unlabeled Tweets:'
    sentdic = make_dic()
  
    get_total_average(sentdic, tweets)
            
            
def get_total_average(sentdic, tweets):
    #grab a tweet and analize it using dictionary
    obama_average = 0
    obama_count = 0
    romney_average = 0
    romney_count = 0
    for tweet in tweets:
        wordlist = nltk.word_tokenize(tweet[0])
        average = 0.0
        sum = 0
        count = 0
        contains_obama = False
        contains_romney = False

        for word in wordlist:
            word = word.strip('.,:; ')
            word = word.lower()
            (happiness, stddev) = sentdic.get(word, (0, 0))
            if happiness > 0:
                sum += happiness
                count += 1
            if word == 'obama' or word == 'biden' or word == 'barack':
                contains_obama = True
            if word == 'romney' or word == 'ryan' or word == 'mitt':
                contains_romney = True

        if count != 0:
            average = float(sum) / float(count)
        
        #normalize from 0 to 10 to (-1) to 1
        if count == 0:
            average = 5
      
        average = (average / 5.0) - 1

        if contains_obama:
            obama_average += average
            obama_count += 1
        if contains_romney:
            romney_average += average
            romney_count += 1

    obama_val = obama_average/obama_count
    romney_val = romney_average/romney_count

    print '/-------------------------\\'
    print '|                         |'
    print '| Obama Sentiment:', "%.3f" % obama_val, ' |'
    print '| Romney Sentiment:', "%.3f" % romney_val, '|'
    print '|                         |'
    print '\-------------------------/'

def score_tweet(sentdic, tweet):
    obama_sent = False
    romney_sent = False
    obama_score = -5
    romney_score = -5

    word_list = nltk.word_tokenize(tweet[0])
    for word in word_list:
        word = word.strip('.,:; ').lower()
        if word in DEMOC:
            obama_sent = True
        if word in REPUB:
            romney_sent = True

    if obama_sent:
        obama_score = rate_single_tweet(sentdic, tweet)
    if romney_sent:
        romney_score = rate_single_tweet(sentdic, tweet)

    return (obama_score, romney_score)


def rate_single_tweet(sentdic, tweet):
    wordlist = nltk.word_tokenize(tweet[0])
    sum = 0
    count = 0
    for word in wordlist:
        word = word.strip('.,:; ').lower()
        (happiness, stddev) = sentdic.get(word, (0, 0))
        if happiness > 0:
            sum += happiness
            count += 1
    if count != 0:
        average = float(sum) / count
    #normalize from 0-10 to (-1)-1
    average = (average / 5) - 1
    return average

def make_dic():
    print 'Loading Sentiment Corpus\n'
    #open and read word library
    f = open('sent.csv')
    f = f.readlines()
    word_dict = {}
 
    for index, wordsent in enumerate(f):
        fields = wordsent.split(',')

        try:
            happiness = float(fields[1])
        except Exception, e:
            continue
        
        try:
            stddev = float(fields[2])
        except Exception, e:
            continue
        
        word_dict[fields[0]] = (happiness, stddev)

    return word_dict
