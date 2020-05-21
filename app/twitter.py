# Import necessary libraries
from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators
import os
import numpy as np
import sklearn
from werkzeug.wrappers import Request, Response
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

# Section below loads pre-trained classifiers and assumes files are stored locally within joblib folder.
# Classifier files are too large to be stored on GitHub but can be downloaded from Google Drive using the 
# following link: https://drive.google.com/open?id=1dCRuEHzK--d3iHvAnVWYGry9i6XOzu8j
   
ensemble = joblib.load("joblib//ensemble_classifier.sav")
account_classifier = joblib.load("joblib//account_classifier.sav")
sentiment_classifier = joblib.load("joblib//sentiment_classifier.sav")
activity_classifier = joblib.load("joblib//activity_classifier.sav")
interactiveness_classifier = joblib.load("joblib//interactiveness_classifier.sav")
tweet_source_classifier = joblib.load("joblib//tweet_source_classifier.sav")

# Global variables
target_followers_count = 0
target_friends_count = 0
target_id = ''
target_name = ''
target_screen_name = ''
target_name = ''
target_label = ''

def sentiment_scores(tweet): 
  
    # Create a SentimentIntensityAnalyzer object. 
    sid_obj = SentimentIntensityAnalyzer() 
  
    # object gives a sentiment dictionary. 
    sentiment_dict = sid_obj.polarity_scores(tweet) 
    
    return sentiment_dict
    
def luis(alltweets, p, test, tweet_text):
    
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
    
	# Iterates through at most 100 latest tweets
    for tweet in alltweets:
        if p<100:
            try:
                t = tweet.retweeted_status
            except:
                
				# Calculate sentiment scores for given tweet
                sentiment_dict = sentiment_scores(tweet._json['text'])
                
                tweet_text.append(tweet._json['text'])
                
                sss = tweet._json['source'][tweet._json['source'].find(">")+1 : tweet._json['source'].find("</a")]
                
				# Increment corresponding counter based on source of tweet				
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
				
    return p, tweet_text

def score(tweet_text):
    mytext = ' '.join(tweet_text)
    word_list = mytext.split()
	# Remove punctuation and links from tweets
    regex = re.compile('^https?:\/\/.*[\r\n]*')
    okay_items = [x for x in word_list if not regex.match(x)]
    words_n_nums = [t.lower() for t in okay_items if t.isalnum()]
    
	# Calculate lex. diversity
    if len(words_n_nums) == 0:
        val = 0

    else:
        val = len(set(words_n_nums)) / len(words_n_nums)
        
    return val

def prediction(df, account, tweet_text):
    
		# Return account info
		result = api.get_user(screen_name = account)._json
        
		# cal function to calculate lex. diversity
		lex_score = score(tweet_text)
        
		# Define current date and time
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
	
def tweets(account, function, tweet_text, protected):
    
	global target_label
    
	# gathers tweets for use unprotceted accounts
	if protected == False:
	
            #initialize a list to hold all the tweepy Tweets
			alltweets = []
			test = []
			p=0
    
			#make initial request for most recent tweets (200 is the maximum allowed count)
			new_tweets = api.user_timeline(screen_name = account, count=200)
            
			if len(new_tweets) != 0:

				#save most recent tweets
				alltweets.extend(new_tweets)

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

			p_label, overall_score, account_score, sentiment_score, activity_score, interactiveness_score, tweet_source_score = prediction(df, account, tweet_text)
            
			if p_label == 0:
				predicted_label = 'Human'
			else:
				predicted_label = 'Bot'
			
			if account == target_screen_name:
                
				target_label = predicted_label
            
			# returns variables used for network graph page of web app
			if function == 'friends':
                
				retweet_rate, tweet_rate = rates(account)
                
				return retweet_rate, tweet_rate, predicted_label
           
			# returns variables used for prediction page of web app
			elif function == 'result':
				return account, predicted_label, overall_score, account_score, sentiment_score, activity_score, interactiveness_score, tweet_source_score
        
	elif protected == True:

		if account == target_screen_name:
                
			target_label = 'Protected'

		predicted_label = 'Protected'
	
		print('User not available')
		return account, predicted_label, ' - ', ' - ', ' - ', ' - ', ' - ', ' - '
    
def json_graph(account):
    
	currentDirectory = os.getcwd()

	file = '\static\json_file.json'
	
	# Check to see if static data file already exists
	try:
		
		os.remove(currentDirectory+file)
		print('exists - deleted')
	except:
		print('doesnt exist - proceed')
    

	protected = 0
    
	global counter
	counter = 0

	global target
	target = 1
    
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

	print("Started with central node\t%s" % target_screen_name)

	f_users = []

	# Creates node for target account provided
	main_user = {
        "node_id" : counter,
        "followers_count" : target_followers_count,
        "friends_count" : target_friends_count,
        "id" : target_id,
        "name" : target_name,
        "screen_name" : target_screen_name,
        "label" : target_label,
        "retweet_rate" : ' - ',
        "tweet_rate" : ' - '
        ,"hop" : 0
	}

	counter += 1
        
	json_dict['nodes'].append(main_user)
        
	global offset
	offset = 0 
    
	if target_label == 'Protected':
        
		with open('static/json_file.json', 'w') as json_file:
			json.dump(json_dict, json_file)
		json_file.close()
    
		return humans, bots, result_bot, result_human, human_content, bot_content
    
	users = api.friends(screen_name = account, count = 1)
    
	# Considers friends of friend
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
				retweet_rate, tweet_rate, label = tweets(name['screen_name'], 'friends', tweet_text, protected)
				print(label)
				f_users.append(name['screen_name'])
				f_users.append(label)
                
				tweets_var = round(tweet_rate, 2)
				retweets_var = round(retweet_rate, 2)
                    
           
        
				if label == 'Human':
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
					retweet_rate, tweet_rate, label = tweets(name_inner['screen_name'], 'friends', tweet_text, protected)
					print(label)
					f_users.append(name_inner['screen_name'])
					f_users.append(label)
                    
					tweets_var = round(tweet_rate, 2)
					retweets_var = round(retweet_rate, 2)
        
					if label == 'Human':
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
					"source" : USED,
					"target" : target
					}
                
            
				target += 1
                    
				json_dict['nodes'].append(temp_nodes)
                    
                    
            
			else:
				temp_links = {
					"source" : USED,
					"target" : existng_node_id
					}
                
			json_dict['links'].append(temp_links)
              
		offset += 1
        
                
		json_dict['links'].append(temp_links)
        
	with open('static/json_file.json', 'w') as json_file:
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

    return existing_node_id, exists
    

# function determines tweet and retweet rates of user within last 30 days
def rates(account):
    d = datetime.datetime.now() - timedelta(days=30)

    retweet_count = 0
    tweet_count = 0
    
    retweet_rate = 0
    tweet_rate = 0

    tweets = []
    
    tmpTweets = []
    
    for tweet in tweepy.Cursor(api.user_timeline,screen_name = account, count = 200, exclude_replies= True).items():
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
            tmpTweets = api.user_timeline(screen_name = account, max_id = tmpTweets[-1].id, exclude_replies= True)
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
   
# Define web app name
app = Flask(__name__)

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

class ReviewForm(Form):
    moviereview = TextAreaField('', [validators.DataRequired(), validators.length(max=15)])

# Prevents web app from caching data e.g. static data files	
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-store"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

# Web app landing page
@app.route('/')
def index():

    form = ReviewForm(request.form)

    data = ["Enter a Twitter account username without the '@' symbol (e.g. BarackObama) to be analyzed", 
            "Select the 'Predict' option first to understand the areas of a Twitter that exhibit signs of 'bot' behaviour. Scores closer to 0 indicate human behaviour and scores closer to 1 indicate bot behaviour",
            "The 'Graph' option can then be selected and displays the immediate following network of the provided account"]
    
    df = pd.DataFrame(data=data, columns=['Instructions'])
    return render_template('reviewform_updated.html', prediction_text = df.to_html(index=False), form=form)

# Network graph page
@app.route('/graph', methods=['GET','POST'])
def graph():

	global target_screen_name
    
	review = request.get_data(as_text=True)[8:]

	print('name entered to graph: %s\t target screen_name: %s' % (review,target_screen_name))

	if (review != target_screen_name) and (target_screen_name == ''):
		text = "Please enter the same target account that was previously provided for the Prediction."
		return render_template('reviewform_updated.html', prediction_text=text)
	
	elif review != target_screen_name:
		text = "Please select the 'Predict' button first for the provided target account."
		return render_template('reviewform_updated.html', prediction_text=text)

	humans, bots, result_bot, result_human, human_content, bot_content= json_graph(review)
    
	print("before loading of static file")
	with open('static/json_file.json') as f:
		users = json.load(f)
	f.close()
	print("after loading of static file")

	humans_num = 0
	bots_num = 0
	
	humans_num = len(result_human)
	bots_num = len(result_bot)
    
	if review in result_human:
		humans_num = humans_num - 1
        
	elif review in result_bot:
		bots_num = bots_num - 1
        
	df_fox_human = pd.DataFrame(data=result_human, columns=['Account', 'Classification'])
	df_fox_bot = pd.DataFrame(data=result_bot, columns=['Account', 'Classification'])

	target_screen_name = ''
        
	print("before render_template call")   
	return render_template('graph_updated.html',humans=humans_num,bots=bots_num,table1 = df_fox_human.to_html(classes='male', index=False), table2 = df_fox_bot.to_html(classes='female', index=False), tables=[df_fox_human.to_html(classes='male', index=False), df_fox_bot.to_html(classes='female', index=False)]) 

# @FoxNews network graph
@app.route('/fox_example', methods=['POST'])
def fox_example():

    with open('static/FOX_9_6_4.json') as f:
        foxnews = json.load(f)
    f.close()
    
    review = 'FoxNews'

    tmp = []
    final_human = []
    final_bot = []

    for i in range(len(foxnews['nodes'])):
    
        tmp = []
    
        tmp.append(foxnews['nodes'][i]['screen_name'])
        tmp.append(foxnews['nodes'][i]['label'])
    
       
        if (foxnews['nodes'][i]['label'] == 'Bot') or (foxnews['nodes'][i]['label'] == '{bot}'):
    
            final_bot.append(tmp)
        
        elif (foxnews['nodes'][i]['label'] == 'Human') or (foxnews['nodes'][i]['label'] == '{human}'):
            final_human.append(tmp)
            
    humans_num = len(final_human)
    bots_num = len(final_bot)
    
    if review in final_human:
        humans_num = humans_num - 1
        
    elif review in final_bot:
        bots_num = bots_num - 1
        
    df_fox_human = pd.DataFrame(data=final_human, columns=['Account', 'Classification'])
    df_fox_bot = pd.DataFrame(data=final_bot, columns=['Account', 'Classification'])
   
    return render_template('fox_example.html',humans=humans_num,bots=bots_num,table1 = df_fox_human.to_html(classes='male', index=False), table2 = df_fox_bot.to_html(classes='female', index=False), tables=[df_fox_human.to_html(classes='male', index=False), df_fox_bot.to_html(classes='female', index=False)]) 

# @MSNBC network graph
@app.route('/msnbc_example', methods=['POST'])
def msnbc_example():

    with open('static/MSNBC_9_6_4.json') as f:
        msnbc = json.load(f)
    f.close()
    
    review = 'MSNBC'

    tmp = []
    final_human = []
    final_bot = []

    for i in range(len(msnbc['nodes'])):
    
        tmp = []
    
        tmp.append(msnbc['nodes'][i]['screen_name'])
        tmp.append(msnbc['nodes'][i]['label'])
    
        if (msnbc['nodes'][i]['label'] == 'Human') or (msnbc['nodes'][i]['label'] == '{human}'):
    
            final_human.append(tmp)
        
        elif (msnbc['nodes'][i]['label'] == 'Bot') or (msnbc['nodes'][i]['label'] == '{bot}'):
            final_bot.append(tmp)
            
    humans_num = len(final_human)
    bots_num = len(final_bot)
    
    if review in final_human:
        humans_num = humans_num - 1
        
    elif review in final_bot:
        bots_num = bots_num - 1
        
    df_fox_human = pd.DataFrame(data=final_human, columns=['Account', 'Classification'])
    df_fox_bot = pd.DataFrame(data=final_bot, columns=['Account', 'Classification'])
       
    return render_template('msnbc_example.html',humans=humans_num,bots=bots_num,table1 = df_fox_human.to_html(classes='male', index=False), table2 = df_fox_bot.to_html(classes='female', index=False), tables=[df_fox_human.to_html(classes='male', index=False), df_fox_bot.to_html(classes='female', index=False)]) 

# Classification output for targte account provived page
@app.route('/results', methods=['GET','POST'])
def results():
    
	review =request.get_data(as_text=True)[8:]
	print(review)

	try:
		result = api.get_user(screen_name = review)._json
	except tweepy.TweepError as error:
		# exception if entered string is not a valid Twitter username
		text = 'User not found. Please enter another Twitter username.'
		
		# excpetion if entered string is a valid username but the account has been suspended
		if error.api_code == 63:
			text = 'User has been suspended. Classification is not possible.'
		# exception if Twitter API call rate has been exceeded
		elif error.api_code == 403:
			text = 'API rate limit reached. Please try again later.'
		
		return render_template('reviewform_updated.html', prediction_text=text)

	global target_screen_name

	target_screen_name = review
    
	result = api.get_user(screen_name = review)._json
    
	global target_followers_count
	global target_friends_count
	global target_id
	global target_name

    
	target_followers_count = result['followers_count']
	target_friends_count = result['friends_count']
	target_id = result['id']
	target_name = result['name']
    
	protected = result['protected']
    
	tweet_text = []
    
	target, y, proba, account_score, sentiment_score, activity_score, interactiveness_score, tweet_source_score = tweets(review, 'result', tweet_text, protected)
           
	data = [['Target Account', target],['Classification', y], ['Classification Score', proba], ['Account Score', account_score], ['Tweet Text Score', sentiment_score], ['Network Score', activity_score], ['Interaction Score', interactiveness_score], ['Tweet Source Score', tweet_source_score]]
    
	df = pd.DataFrame(data=data, columns=['Description','Results'])

    
	print('target screen_name: %s' % target_screen_name)
    
	return render_template('reviewform_updated.html', prediction_text = df.to_html(index=False))
                         


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 9000, app)
