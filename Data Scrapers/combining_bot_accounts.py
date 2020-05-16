import tweepy
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import pandas as pd
import datetime
import sqlite3
import random

pronbots = pd.read_csv('pronbots.csv', header=0, names=['user', 'label'])
gilani = pd.read_csv('gilani-2017.csv', header=0, names=['user', 'label'])
italy = pd.read_csv('cresci-rtbust-2019.csv', header=0, names=['user', 'label'])
man_labelled = pd.read_csv('botometer-feedback-2019.csv', header=0, names=['user', 'label'])
midterm = pd.read_csv('midterm-2018.csv', header=0, names=['user', 'label'])

df_1 = italy[italy['label'] == 'bot']
df_2 = man_labelled[man_labelled['label'] == 'bot']
df_3 = gilani[gilani['label'] == 'bot']
df_4 = pronbots[pronbots['label'] == 'bot']
df_5 = midterm[midterm['label'] == 'bot']

dfs = [df_1, df_2, df_3, df_4, df_5]
master= pd.DataFrame()

for d in dfs:
    master = master.append(d, ignore_index=True)

user_ids = master['user'].values.tolist()

with open('bots_combined.txt', 'w') as f:
    for item in user_ids:
        f.write("%s\n" % item)
        
with open('bots_combined_copy.txt', 'w') as f:
    for item in user_ids:
        f.write("%s\n" % item)