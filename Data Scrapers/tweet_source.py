import tweepy
import time
import sys

#Twitter API credentials
consumer_key = "IoLMjJGbPmZ958v9u8hErw1pT"
consumer_secret = "WGI8wT9YJ1Q0Z6bsImIHAzmwITZL3SJnzrXZsDqAe0IJEGSGwf"
access_key = "1176220916138860545-KsEnoxhjN2OknyiVVgQwF39JZWqgvT"
access_secret = "xBNs5Hikl32Kgg9FB8QZcK0t4HQyjMB9I1U4iVtFsTWt2"

   
#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

iPhone = 0
iPad = 0
Android = 0
Web_App = 0
Web_Client = 0
Websites = 0
Other = 0

fail_list = []

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
                    
                outtweets = [tweet.user.screen_name , iPhone,iPad,Android,Web_App,Web_Client,Websites,Other]
                test.append(outtweets)
                
                p += 1
    return p
    

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
       
        final_sources = final_sources.append(temp_df.loc[[(temp_df.shape[0]-1)]])
        
        print("%d\t--- %s seconds ---\tAPI counter=%d" % (counter, time.time() - start_time, api_counter))
        

    except:
        print("User not available:%d\t--- %s seconds ---\tAPI counter=%d" % (counter, time.time() - start_time, api_counter))
        #print('User not available - append to list')
        fail_list.append(u_id)
        
    #print("%d\t--- %s seconds ---\tAPI counter=%d" % (counter, time.time() - start_time, api_counter))
    counter += 1

    
    #with open('file.txt', 'r+') as f:
    #    for item in user_ids:
    #        f.write("%s\n" % item)
    #        f.truncate()