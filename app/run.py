import pickle
import os
import numpy as np
import sklearn
import json
import tweepy
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import pandas as pd
import datetime
from datetime import timedelta
import random, string
import joblib
import re
import sys


#with open('pickle//with lex div//ensemble_classifier.pkl', 'rb') as fid:
#    ensemble = pickle.load(fid)
#fid.close()
    
#with open('pickle//with lex div//account_classifier.pkl', 'rb') as fid:
#    account_classifier = pickle.load(fid)
#fid.close()
    
#with open('pickle/with lex div//sentiment_classifier.pkl', 'rb') as fid:
#    sentiment_classifier = pickle.load(fid)
#fid.close()
    
#with open('pickle//with lex div//activity_classifier.pkl', 'rb') as fid:
#    activity_classifier = pickle.load(fid)
#fid.close()
    
#with open('pickle//with lex div//interactiveness_classifier.pkl', 'rb') as fid:
#    interactiveness_classifier = pickle.load(fid)
#fid.close()
    
#with open('pickle//with lex div//tweet_source_classifier.pkl', 'rb') as fid:
#    tweet_source_classifier = pickle.load(fid)
#fid.close()
    
ensemble = joblib.load("joblib//ensemble_classifier.sav")
account_classifier = joblib.load("joblib//account_classifier.sav")
sentiment_classifier = joblib.load("joblib//sentiment_classifier.sav")
activity_classifier = joblib.load("joblib//activity_classifier.sav")
interactiveness_classifier = joblib.load("joblib//interactiveness_classifier.sav")
tweet_source_classifier = joblib.load("joblib//tweet_source_classifier.sav")



def sentiment_scores(tweet): 
  
    # Create a SentimentIntensityAnalyzer object. 
    sid_obj = SentimentIntensityAnalyzer() 
  
    # object gives a sentiment dictionary. 
    sentiment_dict = sid_obj.polarity_scores(tweet) 
    
    return sentiment_dict
    
def luis(alltweets, p, test, tweet_text):#, iPhone,iPad,Android,Web_App,Web_Client,Websites,Other):
    
    global iPhone
    global iPad 
    global Android
    global Web_App
    global Web_Client 
    global Websites 
    global Other
    
    iPhone = 0
    iPad  = 0
    Android = 0
    Web_App = 0
    Web_Client  = 0
    Websites = 0 
    Other = 0
    
    for tweet in alltweets:
        if p<100:
            try:
                t = tweet.retweeted_status
            except:
                
                sentiment_dict = sentiment_scores(tweet._json['text'])
                
                tweet_text.append(tweet._json['text'])
                
                sss = tweet._json['source'][tweet._json['source'].find(">")+1 : tweet._json['source'].find("</a")]
                
                #print(len(alltweets))
                      
                if sss == 'Twitter for iPhone':
                    iPhone += 1
                elif sss =='Twitter for Android':
                    iPad += 1
                elif sss =='Twitter for iPad':
                    Android += 1
                elif sss =='Twitter Web Client':
                    Web_App += 1
                elif sss =='Twitter for Websites':
                    Web_Client += 1
                elif sss =='Twitter Web App':
                    Websites += 1
                else:
                    Other += 1
                
                outtweets = [tweet.user.screen_name , tweet._json['user']['id_str'], tweet.id, tweet.created_at, tweet._json['text'], sentiment_dict['neg'], sentiment_dict['neu'], sentiment_dict['pos'], len(tweet._json['entities']['hashtags']), len(tweet.entities['user_mentions']), tweet._json['favorite_count'], tweet._json['retweet_count'], len(tweet._json['entities']['urls']), iPhone,iPad,Android,Web_App,Web_Client,Websites,Other]
                test.append(outtweets)
                p += 1
    #print('luis exited')
    return p, tweet_text

def score(tweet_text):
    mytext = ' '.join(tweet_text)
    word_list = mytext.split()
    regex = re.compile('^https?:\/\/.*[\r\n]*')
    okay_items = [x for x in word_list if not regex.match(x)]
    words_n_nums = [t.lower() for t in okay_items if t.isalnum()]
    
    if len(words_n_nums) == 0:
        val = 0
        #per_user.append(0)
    else:
        val = len(set(words_n_nums)) / len(words_n_nums)
        
    return val

def prediction(df, account, tweet_text):
    
    
    if 1==1:#try:
        
        
        result = api.get_user(screen_name = account)._json
        
        lex_score = score(tweet_text)
        
        current = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        datetime_object = datetime.datetime.strptime(result['created_at'], '%a %b %d %H:%M:%S %z %Y')
        age = (current-datetime_object).days
        
        if result['location'] == '':
            result['location'] = 0
        else:
            result['location'] = 1
            
        #predicts using RF with all features
        p_label = ensemble.predict([[#result['id'],
                            result['location']
                            ,age
                            ,result['statuses_count']
                            ,result['followers_count']
                            ,result['friends_count']
                            ,result['favourites_count']
                            ,result['verified']
                            ,df['Sentiment_neg'].sum()
                            ,df['Sentiment_neu'].sum()
                            ,df['Sentiment_pos'].sum()
                            ,lex_score
                            ,df['hashtag_count'].sum()
                            ,df['mentions_count'].sum()
                            ,df['likes_count'].sum()
                            ,df['retweets_count'].sum()
                            ,df['url_count'].sum()
                            ,iPhone
                            ,iPad
                            ,Android
                            ,Web_App
                            ,Web_Client
                            ,Websites
                            ,Other]])
        
        global overall_score
        
        overall_score = round(ensemble.predict_proba([[#result['id'],
                            result['location']
                            ,age
                            ,result['statuses_count']
                            ,result['followers_count']
                            ,result['friends_count']
                            ,result['favourites_count']
                            ,result['verified']
                            ,df['Sentiment_neg'].sum()
                            ,df['Sentiment_neu'].sum()
                            ,df['Sentiment_pos'].sum()
                            ,lex_score
                            ,df['hashtag_count'].sum()
                            ,df['mentions_count'].sum()
                            ,df['likes_count'].sum()
                            ,df['retweets_count'].sum()
                            ,df['url_count'].sum()
                            ,iPhone
                            ,iPad
                            ,Android
                            ,Web_App
                            ,Web_Client
                            ,Websites
                            ,Other]])[0][1], 2)
        #probability of prediction using RF with all features
        
        global account_score
        account_score = round(account_classifier.predict_proba([[
                            result['location']
                            ,age
                            ,result['statuses_count']
                            ,result['verified']
                               ]])[0][1], 2)
        #probability of prediction using RF with account features
        
        
        global sentiment_score
        sentiment_score = round(sentiment_classifier.predict_proba([[
                            df['Sentiment_neg'].sum()
                            ,df['Sentiment_neu'].sum()
                            ,df['Sentiment_pos'].sum()
                            ,lex_score
                               ]])[0][1], 2)
        #probability of prediction using RF with sentiment features
        
        global activity_score
        activity_score = round(activity_classifier.predict_proba([[
                            result['followers_count']
                            ,result['friends_count']
                            ,result['favourites_count']
                            ,df['likes_count'].sum()
                               ]])[0][1], 2)
        #probability of prediction using RF with activity features
        
        global interactiveness_score
        interactiveness_score = round(interactiveness_classifier.predict_proba([[
                            df['hashtag_count'].sum()
                            ,df['mentions_count'].sum()
                            ,df['retweets_count'].sum()
                            ,df['url_count'].sum()
                               ]])[0][1], 2)
        #probability of prediction using RF with interactiveness features
        
        global tweet_source_score
        tweet_source_score = round(tweet_source_classifier.predict_proba([[
                            iPhone
                            ,iPad
                            ,Android
                            ,Web_App
                            ,Web_Client
                            ,Websites
                            ,Other
                               ]])[0][1], 2)
        #probability of prediction using RF with interactiveness features
        
        
        pettit = p_label[0]
        
        pettit = pettit.astype('float64')

        
        
        return p_label, overall_score, account_score, sentiment_score, activity_score, interactiveness_score, tweet_source_score

    #except sqlite3.Error as error:
    #    print("Failed to insert Python variable into sqlite table", error)
    #finally:
    #    if (sqliteConnection):
   
            
            
def tweets(account, function, tweet_text):
    
    
    
    if 1==1:#try:
            #initialize a list to hold all the tweepy Tweets
            alltweets = []
            test = []
            p=0
    
            #make initial request for most recent tweets (200 is the maximum allowed count)
            new_tweets = api.user_timeline(screen_name = account, count=200)
            
            if len(new_tweets) != 0:

                #save most recent tweets
                alltweets.extend(new_tweets)

                #print('first luis entered')
                val, tweet_text = luis(alltweets, p, test, tweet_text)

                if val >= 100:
                    pass

                else:
                    #save the id of the oldest tweet less one
                    oldest = alltweets[-1].id - 1

                    #keep grabbing tweets until there are no tweets left to grab
                    while len(new_tweets) > 0 and p < 99:
                    
                        p=0
                        test = []

                        new_tweets = api.user_timeline(screen_name = account,count=200,max_id=oldest)
        
                        alltweets.extend(new_tweets)
            
                        #update the id of the oldest tweet less one
                        oldest = alltweets[-1].id - 1
                        #print('while luis entered')
                        p, tweet_text = luis(alltweets, p, test, tweet_text)
                        
            else:
                
                global iPhone
                global iPad 
                global Android
                global Web_App
                global Web_Client 
                global Websites 
                global Other
    
                iPhone = 0
                iPad  = 0
                Android = 0
                Web_App = 0
                Web_Client  = 0
                Websites = 0 
                Other = 0
                
                outtweets = [account,0,0,0,0,0,0,0,0,0,0,0,0,iPhone,iPad,Android,Web_App,Web_Client,Websites,Other]
                test.append(outtweets)
                
            
            
            
            print('test')
            
            df = pd.DataFrame(data=test, columns=['screen_name', 'user_id', 'ID', 'Created_at', 'Text', 'Sentiment_neg', 'Sentiment_neu', 'Sentiment_pos', 'hashtag_count', 'mentions_count','likes_count','retweets_count','url_count', 'Twitter_for_iPhone' , 'Twitter_for_Android' ,'Twitter_for_iPad' ,'Twitter_for_Web_Client' ,'Twitter_for_Websites' ,'Twitter_for_Web_App' ,'Other'])
    
            df['hashtag_count'] = df['hashtag_count'].astype('float64')
            df['mentions_count'] = df['mentions_count'].astype('float64')
            df['likes_count'] = df['likes_count'].astype('float64')
            df['retweets_count'] = df['retweets_count'].astype('float64')
            df['url_count'] = df['url_count'].astype('float64')
            
            df['Twitter_for_iPhone'] = df['Twitter_for_iPhone'].astype('float64')
            df['Twitter_for_Android'] = df['Twitter_for_Android'].astype('float64')
            df['Twitter_for_iPad'] = df['Twitter_for_iPad'].astype('float64')
            df['Twitter_for_Web_Client'] = df['Twitter_for_Web_Client'].astype('float64')
            df['Twitter_for_Websites'] = df['Twitter_for_Websites'].astype('float64')
            df['Twitter_for_Web_App'] = df['Twitter_for_Web_App'].astype('float64')
            df['Other'] = df['Other'].astype('float64')

            #print('prediction entered')
            p_label, overall_score, account_score, sentiment_score, activity_score, interactiveness_score, tweet_source_score = prediction(df, account, tweet_text)
            
            if p_label == 0:
                predicted_label = '{human}'
            else:
                predicted_label = '{bot}'
                
            if function == 'friends':
                
                #print('rates entered')
                retweet_rate, tweet_rate = rates(account)
                
                return retweet_rate, tweet_rate, predicted_label
           
            elif function == 'result':
                return predicted_label, overall_score, account_score, sentiment_score, activity_score, interactiveness_score, tweet_source_score
        
    #except:
    #    print('User not available')
    
    
def json_graph(account):#, x):
    
    #users = api.friends(screen_name = account, count = 1)
    users = api.friends(screen_name = account, count = 1)
    
    global counter
    counter = 0

    global target
    target = 1
    
    global friend_size
    friend_size = 0
    
    tweet_text = []
    result_human = []
    result_bot = []
    humans = 0
    bots = 0
    
    human_content = 0
    bot_content = 0

    
    json_dict = {
        "directed" : True,
        "graph" : [],
        "links" : [],
        "multigraph" : False,
        "nodes" : []
    }
    
    # get user data for central account
    main = api.get_user(screen_name = account)._json
    print("Started with central node\t%s" % main['screen_name'])

    f_users = []
    #print('tweets entered')
    retweet_rate, tweet_rate, label = tweets(account, 'friends', tweet_text)
    print(label)
    #f_users.append(account)
    #f_users.append(label)
        
    #if label == '{human}':
    #    humans += 1
    #    result_human.append(f_users)
    #else:
    #    bots += 1
    #    result_bot.append(f_users)
    

    # create first node for graph - central account
    main_user = {
        "node_id" : counter,
        "followers_count" : main['followers_count'],
        "friends_count" : main['friends_count'],
        "id" : main['id_str'],
        "name" : main['name'],
        "screen_name" : main['screen_name'],
        "label" : label,
        "retweet_rate" : ' - ',#retweet_rate,
        "tweet_rate" : ' - '#tweet_rate
        ,"hop" : 0
    }

    counter += 1
        
    json_dict['nodes'].append(main_user)
        
    global offset
    offset = 0 
    
    
    
    for i in range(len(users)):
        
        tweet_text = []
        
        name = api.get_user(screen_name = users[i]._json['screen_name'])._json
        
        print("%d:\t%s" % (i,name['screen_name']))
        
        #------------------------
        USED = 0
        #------------------------
        
        existng_node_id, exists = check(name['screen_name'], json_dict)
        
        if exists == False:
                
                
            f_users = []
            
            tweets_var = "Unavailable"
            retweets_var = "Unavailable"
            label = "Protected"
                
            if (api.get_user(screen_name = users[i]._json['screen_name'])._json['protected']) == False:
            
                tweet_text = []
                retweet_rate, tweet_rate, label = tweets(name['screen_name'], 'friends', tweet_text)
                print(label)
                f_users.append(name['screen_name'])
                f_users.append(label)
                
                tweets_var = round(tweet_rate, 2)
                retweets_var = round(retweet_rate, 2)
                    
           
        
                if label == '{human}':
                    humans += 1
                    result_human.append(f_users)
                    human_content += (retweets_var + tweets_var)
                    
                else:
                    bots += 1
                    result_bot.append(f_users)
                    bot_content += (retweets_var + tweets_var)
                    
            else:
                print("-----User not available-----")
                    
                
                    
                    
                
    
        
            temp_nodes = {
                "node_id" : counter,
                "followers_count" : name['followers_count'],
                "friends_count" : name['friends_count'],
                "id" : name['id_str'],
                "name" : name['name'],
                "screen_name" : name['screen_name'],
                "label" : label,
                "retweet_rate" : tweets_var,
                "tweet_rate" : retweets_var
                ,"hop" : 1
                }
    
            
            counter += 1
        
        
    
            temp_links = {
                "source" : 0,
                "target" : target
            }
        
            #------------------------
            USED = target
            #------------------------
            
            target += 1
                
            json_dict['nodes'].append(temp_nodes)
        
        else:
            temp_links = {
                "source" : 0,
                "target" : existng_node_id
            }
            
            #------------------------
            USED = existng_node_id
            #------------------------
    
        json_dict['links'].append(temp_links)
        
        if label == "Protected":
            continue

        #friends_list = api.friends(screen_name = users[i]._json['screen_name'], count = 1)
        friends_list = api.friends(screen_name = users[i]._json['screen_name'], count = 1)
            
        increm = 0
            
       
        for j in range(len(friends_list)):
            name_inner = api.get_user(screen_name = friends_list[j]._json['screen_name'])._json
            print("\t\t%s" % (friends_list[j]._json['screen_name']))

              
            tweet_text = []
                
            existng_node_id, exists = check(name_inner['screen_name'], json_dict)
        
            if exists == False:
                
                    
                f_users = []
                
                tweets_var = "Unavailable"
                retweets_var = "Unavailable"
                label = "Protected"
                
                if (api.get_user(screen_name = friends_list[j]._json['screen_name'])._json['protected']) == False:
                    
                    tweet_text = []
                    retweet_rate, tweet_rate, label = tweets(name_inner['screen_name'], 'friends', tweet_text)
                    print(label)
                    f_users.append(name_inner['screen_name'])
                    f_users.append(label)
                    
                    tweets_var = round(tweet_rate, 2)
                    retweets_var = round(retweet_rate, 2)
        
                    if label == '{human}':
                        humans += 1
                        result_human.append(f_users)
                        human_content += round(tweet_rate, 2)
                    else:
                        bots += 1
                        result_bot.append(f_users)
                        human_content += round(tweet_rate, 2)
                        
                else:
                    print("-----User not available-----")
                    
                
                    
                    
                
    
        
                temp_nodes = {
                    "node_id" : counter,
                    "followers_count" : name_inner['followers_count'],
                    "friends_count" : name_inner['friends_count'],
                    "id" : name_inner['id_str'],
                    "name" : name_inner['name'],
                    "screen_name" : name_inner['screen_name'],
                    "label" : label,
                    "retweet_rate" : tweets_var,
                    "tweet_rate" : retweets_var
                    ,"hop" : 2
                }
            
                counter += 1
            
            
                temp_links = {
                    #"source" : i+1+friend_size,
                    "source" : USED,
                    "target" : target
                    }
                
                    
                
                print("---%d\t%d---" % (i+1+friend_size, target))
            
                target += 1
                    
                json_dict['nodes'].append(temp_nodes)
                    
                    
            
            else:
                temp_links = {
                    #"source" : i+1+friend_size,
                    "source" : USED,
                    "target" : existng_node_id
                    }
                
            json_dict['links'].append(temp_links)
            #friend_size += len(users)
                
                
                
                    
                
        offset += 1
        
                
        json_dict['links'].append(temp_links)
        
        friend_size += len(friends_list)
            
      
            
    
    #name = 'static//' + x + '.json'    
    print('fucking wooo000rks')
        
    with open('static/json_file.json', 'w') as json_file:
    #with open(name, 'w') as json_file:
        json.dump(json_dict, json_file)
    json_file.close()
    
    return humans, bots, result_bot, result_human, human_content, bot_content
    
def check(name, dictionary):
    exists = False
    existing_node_id = -1
    
    for i in range(len(dictionary['nodes'])):
        if name in dictionary['nodes'][i]['screen_name']:
            existing_node_id = dictionary['nodes'][i]['node_id']
            exists = True
        ##else:
           ## print("Distinct node value")

    return existing_node_id, exists
    

def rates(account):
    d = datetime.datetime.now() - timedelta(days=30)

    retweet_count = 0
    tweet_count = 0
    
    retweet_rate = 0
    tweet_rate = 0

    tweets = []
    
    tmpTweets = []#api.user_timeline(screen_name = account, exclude_replies= True)
    
    for tweet in tweepy.Cursor(api.user_timeline,screen_name = account, count = 200, exclude_replies= True).items():
        #print(tweet._json['text'])
        tmpTweets.append(tweet)
    
    if len(tmpTweets) != 0:
         
        for tweet in tmpTweets:
        
            if tweet.created_at > d:
                tweets.append(tweet)
            
                try:
                    t = tweet.retweeted_status
                    retweet_count += 1
           
                except:
                    tweet_count += 1
            
    
        while (tmpTweets[-1].created_at > d):
            #print(tmpTweets[-1].created_at , d)
            #print("Last Tweet @", tmpTweets[-1].created_at, " - fetching some more")
            tmpTweets = api.user_timeline(screen_name = account, max_id = tmpTweets[-1].id, exclude_replies= True)
            ##########print(len(tmpTweets))
            if len(tmpTweets) == 1:
                break
            for tweet in tmpTweets:
            
                if tweet.created_at > d:
                    tweets.append(tweet)
           
                    try:
                        t = tweet.retweeted_status
                        retweet_count += 1
           
                    except:
                        tweet_count += 1
                    
        retweet_rate = retweet_count / 30
        tweet_rate = tweet_count / 30
   
        
    return retweet_rate, tweet_rate


   
 

##Twitter API credentials
#consumer_key = "IoLMjJGbPmZ958v9u8hErw1pT"
#consumer_secret = "WGI8wT9YJ1Q0Z6bsImIHAzmwITZL3SJnzrXZsDqAe0IJEGSGwf"
#access_key = "1176220916138860545-KsEnoxhjN2OknyiVVgQwF39JZWqgvT"
#access_secret = "xBNs5Hikl32Kgg9FB8QZcK0t4HQyjMB9I1U4iVtFsTWt2"

##Twitter API credentials
consumer_key = "0gfYdGZSFqVyR375RzP8JNtbm"
consumer_secret = "VWy2nay4Fpvd9LcC91KyxGpcjtw840K1RsRMSvz8deXBJEPck0"
access_key = "1208029993504260098-RH50AOCuFjGmbIMZuWvaHUhtU0skpx"
access_secret = "wxeVFihwLf88wbwpMcGtVtTGwmERcvYwr41Wxj276HwhO"
    
#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True
                 , retry_count=10, retry_delay=5, retry_errors=set([503]))


   
    
    
currentDirectory = os.getcwd()

file1 = '\static\json_file.json'
file2 = '\static\humans.csv'
file3 = '\static\bots.csv'

try:
	os.remove(currentDirectory+file1)
	print('1 deleted')
except:
	print('1 doesnt exist')
	
try:
	os.remove(currentDirectory+file2)
	print('2 deleted')
except:
	print('2 doesnt exist')
	
try:
	os.remove(currentDirectory+file3)
	print('3 deleted')
except:
	print('3 doesnt exist')
        
       
humans, bots, result_bot, result_human, human_content, bot_content= json_graph(sys.argv[1])
        
        
datat_human = pd.DataFrame(data=result_human, columns=['Account', 'Classification'])
datat_bot = pd.DataFrame(data=result_bot, columns=['Account', 'Classification'])

datat_human.to_csv('\static\humans.csv', index=False)
datat_bot.to_csv('\static\bots.csv', index=False)
        
#subprocess.call("exit 1", shell=True)