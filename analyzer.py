import sys
import nltk
import mysql.connector as mysql

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

   # Pull the first 100 tweets
   try:
      cursor.execute(
         "SELECT text, retweet_count FROM tweets "
         "WHERE retweet_count > 100 AND text LIKE '%FUCK%' "
         "GROUP BY text "
         "HAVING max(retweet_count)")
      tweets = cursor.fetchall()
      for tweet in tweets:
         print tweet
   except Exception, e:
      raise e

   if tweets:
      print len(tweets)

if __name__ == '__main__':
   sys.exit(main())