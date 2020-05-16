import tweepy
import time
import sys

import sqlite3
import pandas as pd
# Create your connection.
cnx = sqlite3.connect('bots_working.db')

df_humans = pd.read_sql_query("SELECT username FROM humans_accounts", cnx)
df_bots = pd.read_sql_query("SELECT username FROM twitter_users", cnx)

cnx.close()

#df_humans['label'] = 1

bot_usernames = df_bots['username'].tolist()
human_usernames = df_humans['username'].tolist()

with open('bots_source.txt', 'w') as f:
    for bot in bot_usernames:
        f.write("%s\n" % bot)
f.close()

#Twitter API credentials
consumer_key = "JNgHwQR00DV28CYmZUwW13jdr"
consumer_secret = "JGMT4Q0EfbOz6Y0SOFjbuJlV3lj1JYMyLXk2hfXzIM5d22M98R"
access_key = "1224149676485640192-hpKJhksxMuCLIl169TFJK8I6DJVNRX"
access_secret = "SCxNEYoQmnVWgbffuvjkfWnspXm1aVetXh7WecCkkrwAu"

   
#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

def luis(alltweets, p, test, iPhone,iPad,Android,Web_App,Web_Client,Websites,Other):
    for tweet in alltweets:
        if p<100:
            try:
                t = tweet.retweeted_status
            except:
                
                sss = tweet._json['source'][tweet._json['source'].find(">")+1 : tweet._json['source'].find("</a")]
                
                #print(sss)
                
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
                    
                outtweets = [tweet.user.screen_name , iPhone,iPad,Android,Web_App,Web_Client,Websites,Other]#tweet._json['source'][tweet._json['source'].find(">")+1 : tweet._json['source'].find("</a")]]
                test.append(outtweets)
                
                p += 1
    return p

iPhone = 0
iPad = 0
Android = 0
Web_App = 0
Web_Client = 0
Websites = 0
Other = 0

fail_list = []
    
with open('luis.txt', 'r') as file:
    user_ids = file.read().splitlines()
    
    list_length = len(user_ids)
    
api_counter = 0   

counter = 1
label_count = 0

for u_id in user_ids:
        
    start_time = time.time()
    
    try:
        #initialize a list to hold all the tweepy Tweets
        alltweets = []
        test = []
        p=0
    
        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = u_id, count=200)
        api_counter += 1

        #save most recent tweets
        alltweets.extend(new_tweets)

        val = luis(alltweets, p, test, iPhone,iPad,Android,Web_App,Web_Client,Websites,Other)
                
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

                new_tweets = api.user_timeline(screen_name = u_id,count=200,max_id=oldest)
                api_counter += 1
        
                alltweets.extend(new_tweets)
            
                #update the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1
        
                p = luis(alltweets, p, test, iPhone,iPad,Android,Web_App,Web_Client,Websites,Other)
            
                #print('within WHILE loop %d' % p)
        

        temp_df = pd.DataFrame(data=test, columns = ['screen_name', 'Twitter for iPhone', 'Twitter for Andriod', 'Twitter for iPad', 'Twitter for Web Client', 'Twitter for Websites', 'Twitter for Web App', 'Other']) 
       
        final_sources = final_sources.append(temp_df.loc[[6(temp_df.shape[0]-1)]])
        
        print("%d\t--- %s seconds ---\tAPI counter=%d" % (counter, time.time() - start_time, api_counter))
        

    except:
        print("User not available:%d\t--- %s seconds ---\tAPI counter=%d" % (counter, time.time() - start_time, api_counter))
        #print('User not available - append to list')
        fail_list.append(u_id)
        
    #print("%d\t--- %s seconds ---\tAPI counter=%d" % (counter, time.time() - start_time, api_counter))
    counter += 1
    
    user_ids = user_ids[1:list_length]
    list_length = list_length - 1
    
    with open('luis.txt', 'r+') as f:
        for item in user_ids:
            f.write("%s\n" % item)
            f.truncate()