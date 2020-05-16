# script to extend dataset by including lexical diversity of target account based on 100 most recent tweets

import tweepy
import time
import sys
import re
import pandas as pd

#Twitter API credentials
consumer_key = "0gfYdGZSFqVyR375RzP8JNtbm"
consumer_secret = "VWy2nay4Fpvd9LcC91KyxGpcjtw840K1RsRMSvz8deXBJEPck0"
access_key = "1208029993504260098-RH50AOCuFjGmbIMZuWvaHUhtU0skpx"
access_secret = "wxeVFihwLf88wbwpMcGtVtTGwmERcvYwr41Wxj276HwhO"
    
#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# create connection to db file
cnx = sqlite3.connect('bots_working.db')

# read data into dataframes that correspond to classification labels
df_humans = pd.read_sql_query("SELECT username FROM humans_accounts", cnx)
df_bots = pd.read_sql_query("SELECT username FROM twitter_users", cnx)

cnx.close()

# create list of user ids
bot_usernames = df_bots['id'].tolist()
human_usernames = df_humans['id'].tolist()
user_ids = bot_usernames + human_usernames    
list_length = len(user_ids)
    
api_counter = 0   

counter = 1
label_count = 0

def iterate_tweets(twisher, p, test, tweet_text):
    for tweet in alltweets:
        if p<100:
            try:
                t = tweet.retweeted_status
            except:
                # extracts text of tweet
                tweet_text.append(tweet._json['text'])
               
                outtweets = [tweet._json['user']['id_str'], tweet.id, tweet.created_at, tweet._json['text']]
                test.append(outtweets)
                p += 1
    return p

# loops through all user ids
for u_id in user_ids:
        
    start_time = time.time()
    
    per_user = []
    
    tweet_text = []
    
    try:
        #initialize a list to hold all the tweepy Tweets
        alltweets = []
        test = []
        p=0
        
        per_user.append(u_id)
    
        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(id = u_id, count=200)
        api_counter += 1

        #save most recent tweets
        alltweets.extend(new_tweets)

        val = iterate_tweets(alltweets, p, test, tweet_text)
                
        #print('First tweets collected %d' % val)

        if val >= 100:
            pass

        else:
            #save the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1

            #keep grabbing tweets until there are no tweets left to grab
            while len(new_tweets) > 0 and p < 99:
                    
                p=0
                test = []

                new_tweets = api.user_timeline(id = u_id,count=200,max_id=oldest)
                api_counter += 1
        
                alltweets.extend(new_tweets)
            
                #update the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1
        
                val = iterate_tweets(alltweets, p, test, tweet_text)
        

        df = pd.DataFrame(data=test, columns=['user_id', 'tweet_id', 'Created_at', 'Text'])
        
        print("%d\t--- %s seconds ---" % (counter, time.time() - start_time))
        
    # handles edge case when user account is restrcited
    except:
        print("User not available:%d\t--- %s seconds ---" % (counter, time.time() - start_time))
        fail_list.append(u_id)
        
    # creates single string of all words used in 100 tweets
    mytext = ' '.join(tweet_text)
    # each word set as individual element in list
    word_list = mytext.split()
    # punctuation removed along any links
    regex = re.compile('^https?:\/\/.*[\r\n]*')
    okay_items = [x for x in word_list if not regex.match(x)]
    words_n_nums = [t.lower() for t in okay_items if t.isalnum()]
    
    # lexical diversity calculation
    if len(words_n_nums) == 0:
        val = 0
    else:
        # distinct words divided by total number of words used
        val = len(set(words_n_nums)) / len(words_n_nums)
        print("\t\t\t\t\t\t%f" % float(val))
        
    per_user.append(val)
    
    final_list.append(per_user)
        
    counter += 1
    
    
    user_ids = user_ids[1:list_length]
    list_length = list_length - 1
    
    with open('ids.txt', 'r+') as f:
        for item in user_ids:
            f.write("%s\n" % item)
            f.truncate()
    
df1 = pd.DataFrame(data=final_list, columns=['user_id', 'lexical diversity'])

with open('ids.txt', 'w') as f:
    for item in fail_list:
        f.write("%d\n" % int(item))
f.close()
