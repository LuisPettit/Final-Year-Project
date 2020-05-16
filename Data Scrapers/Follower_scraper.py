# script to get the followers of a provided target account

import tweepy
import sys


#Twitter API credentials
consumer_key = "0gfYdGZSFqVyR375RzP8JNtbm"
consumer_secret = "VWy2nay4Fpvd9LcC91KyxGpcjtw840K1RsRMSvz8deXBJEPck0"
access_key = "1208029993504260098-RH50AOCuFjGmbIMZuWvaHUhtU0skpx"
access_secret = "wxeVFihwLf88wbwpMcGtVtTGwmERcvYwr41Wxj276HwhO"

#Twitter API credentials
#consumer_key = "IoLMjJGbPmZ958v9u8hErw1pT"
#consumer_secret = "WGI8wT9YJ1Q0Z6bsImIHAzmwITZL3SJnzrXZsDqAe0IJEGSGwf"
#access_key = "1176220916138860545-KsEnoxhjN2OknyiVVgQwF39JZWqgvT"
#access_secret = "xBNs5Hikl32Kgg9FB8QZcK0t4HQyjMB9I1U4iVtFsTWt2"
    
#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True
                 , retry_count=10, retry_delay=5, retry_errors=set([503]))

users = []


# targte user
accounts_to_check = ['FoxNews']

page_count = 0

for account in accounts_to_check:
    # handles target account edge cases
    if (api.get_user(screen_name = account)._json['protected'] == True) or (api.get_user(screen_name = account)._json['followers_count'] > 7000):
        print("Skipped %s for being private or exceeding followers limit" % account)
        continue
        
    else:
        # gets followers of target account in increments of 200
        for user in tweepy.Cursor(api.followers, screen_name = account, count=200).pages():
    
            max_calls = False
            page_count += 1
            print ('Getting page {} for followers'.format(page_count))
    
            for i in range(len(user)):
        
        
                users.append(user[i]._json['screen_name'])
            
                # used to handle account pairs within jupyter
                temp_list = []
                temp_list.append(account)
                temp_list.append(user[i]._json['screen_name'])
                script_list.append(temp_list)
                temp_list = []
        
            # the Twitter API followers() method limited to 15 calls per 15 minutes
            # counter prevents call rate being exceeded
            if page_count%15==0:
            
                max_calls = True
                # saves intermediate set of followers in txt file
                with open('FoxNews_follow_pairs.txt', 'a') as f:
                    for peeps in users:
                        f.write("[%s, %s]\n" % (account,peeps))
                f.close()
        
                users = []
        
                for remaining in range(900, 0, -1):
                    sys.stdout.write("\r")
                    sys.stdout.write("{:2d} seconds remaining.".format(remaining)) 
                    sys.stdout.flush()
                    time.sleep(1)
        
                sys.stdout.write("\rComplete!            \n")
        # saves final set of followers
        if max_calls == False:
            with open('FoxNews_follow_pairs.txt', 'a') as f:
                for peeps in users:
                    f.write("[%s, %s]\n" % (account,peeps))
            f.close()
    
        print("%s's - complete" % account)
