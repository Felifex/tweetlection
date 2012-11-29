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


def rate_single_tweet(sentdic, tweet):
    wordlist = nltk.word_tokenize(tweet[1])
    sum = 0
    count = 0
    for word in wordlist:
        word = word.strip('.,:;')
        (happiness, stddev) = sentdic.get(word, (0, 0))
        if happiness > 0:
            sum += happiness
            count += 1
    if count != 0:
        average = sum / count
    #normalize from 0-10 to (-1)-1
    average = (average / 5) - 1
    return average

def make_dic():
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