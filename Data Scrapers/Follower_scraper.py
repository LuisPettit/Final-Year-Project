import tweepy
import time
import sys

start_time = time.time()

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

# used to print account pairs within jupyter
script_list = []

accounts_to_check = ['fearghuswilson']

f = open('fearghus.txt', 'r')
xx = f.read().splitlines()
f.close()

for x in xx:
    accounts_to_check.append(x)

page_count = 0

for account in accounts_to_check:
    
    if (api.get_user(screen_name = account)._json['protected'] == True) or (api.get_user(screen_name = account)._json['followers_count'] > 7000):
        print("Skipped %s for being private or exceeding followers limit" % account)
        continue
        
    else:
    
        for user in tweepy.Cursor(api.followers, screen_name = account, count=200).pages():
    
            max_calls = False
            page_count += 1
            print ('Getting page {} for followers'.format(page_count))
    
            for i in range(len(user)):
        
        
                users.append(user[i]._json['screen_name'])
        
                #if user[i]._json['screen_name'] not in accounts_to_check:
                #    accounts_to_check.append(user[i]._json['screen_name'])
        
                # used to handle account pairs within jupyter
                temp_list = []
                temp_list.append(account)
                temp_list.append(user[i]._json['screen_name'])
                script_list.append(temp_list)
                temp_list = []
        
    
            if page_count%15==0:
            
                max_calls = True
        
                with open('ferg_test3.txt', 'a') as f:
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
        
        if max_calls == False:
            with open('ferg_test3.txt', 'a') as f:
                for peeps in users:
                    f.write("[%s, %s]\n" % (account,peeps))
            f.close()
    
        print("%s's - complete" % account)